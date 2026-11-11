"""Run one experiment against a fresh local service, preserving audit history."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

import requests
import config


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['flood', 'attacks', 'criteria'])
    parser.add_argument('--label', choices=['before', 'after'], default='before')
    parser.add_argument('--set', default='attack_set')
    args = parser.parse_args()
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    prefix = config.RESULTS_DIR / f'{args.phase}_{args.label}_{stamp}'
    start = len(config.AUDIT_LOG.read_text(encoding='utf-8').splitlines()) if config.AUDIT_LOG.exists() else 0
    tracked = ['app.py', 'audit.py', 'config.py', 'detector.py', 'stylometry.py', 'scoring.py',
               'criteria.md', 'scenarios.py', 'run_eval.py', 'run_attacks.py']
    tracked += [str(p) for p in Path('evaluation_data').glob('*.json')]
    if args.phase == 'attacks':
        tracked += [str(p) for p in Path(args.set).glob('*.csv')]
    manifest = {
        'phase': args.phase, 'label': args.label, 'started_utc': stamp,
        'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'files': {p: sha256(p) for p in tracked},
        'packages': {p: importlib.metadata.version(p) for p in ['Flask', 'Flask-Limiter', 'torch', 'transformers']},
        'settings': {p: getattr(config, p) for p in ['DETECTOR_MODEL', 'DETECTOR_MAX_TOKENS',
                     'WEIGHT_MODEL_SIGNAL', 'WEIGHT_STYLE_SIGNAL', 'HUMAN_THRESHOLD', 'AI_THRESHOLD',
                     'RATE_LIMITING_ENABLED', 'RATE_LIMIT_PER_MINUTE', 'RATE_LIMIT_PER_DAY']},
        'audit_start_line': start + 1,
    }
    url = f'http://{config.HOST}:{config.PORT}'
    try:
        requests.get(url + '/health', timeout=1)
    except requests.RequestException:
        pass
    else:
        raise SystemExit('A service already occupies this port; stop it before a controlled run.')
    with prefix.with_suffix('.server.log').open('w', encoding='utf-8') as log:
        # Load the model before listening, so the flood measures the limiter rather than warm-up.
        code = 'import detector; detector.warm_up(); import app; app.app.run(host=app.config.HOST, port=app.config.PORT, debug=False)'
        proc = subprocess.Popen([sys.executable, '-c', code], env={**os.environ, 'AI201_DEBUG': '0'},
                                stdout=log, stderr=log, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        try:
            for _ in range(240):
                if proc.poll() is not None:
                    raise RuntimeError(f'Service startup failed; see {log.name}')
                try:
                    health = requests.get(url + '/health', timeout=1).json()
                    if health.get('detector_loaded') and health.get('rate_limiting'):
                        manifest['health'] = health
                        break
                except requests.RequestException:
                    pass
                time.sleep(.5)
            else:
                raise RuntimeError('Service did not become ready within two minutes.')
            if args.phase == 'flood':
                command = [sys.executable, 'run_attacks.py', '--flood', '15', '--creator', f'flood_{stamp}']
            elif args.phase == 'attacks':
                command = [sys.executable, 'run_attacks.py', '--set', args.set, '--label', args.label]
            else:
                command = [sys.executable, 'run_eval.py', '--label', args.label]
            manifest['command'] = command
            completed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace',
                                       env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
            prefix.with_suffix('.console.log').write_text(completed.stdout + completed.stderr, encoding='utf-8')
            print(completed.stdout, flush=True)
            if completed.stderr:
                print(completed.stderr, file=sys.stderr, flush=True)
            manifest['exit_code'] = completed.returncode
            manifest['health_after'] = requests.get(url + '/health', timeout=5).json()
        finally:
            proc.terminate()
            proc.wait(timeout=15)
    lines = config.AUDIT_LOG.read_text(encoding='utf-8').splitlines()
    manifest['audit_end_line'] = len(lines)
    prefix.with_suffix('.audit.jsonl').write_text('\n'.join(lines[start:]) + '\n', encoding='utf-8')
    manifest['audit_extract_sha256'] = sha256(prefix.with_suffix('.audit.jsonl'))
    prefix.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Preserved experiment: {prefix.name}', flush=True)
    return manifest['exit_code']


if __name__ == '__main__':
    sys.exit(main())
