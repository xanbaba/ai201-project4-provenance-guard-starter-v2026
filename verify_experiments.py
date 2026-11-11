"""Check that recorded comparisons differ only in the intended service setting."""
import json
import hashlib
from pathlib import Path
import subprocess

from run_eval import measure
import scenarios


def latest(pattern):
    return max(Path('results').glob(pattern))


def load(pattern):
    return json.loads(latest(pattern).read_text(encoding='utf-8'))


def main():
    for phase in ('attacks', 'criteria'):
        before = load(f'{phase}_before_*.manifest.json')
        after = load(f'{phase}_after_*.manifest.json')
        assert before['exit_code'] == after['exit_code'] == 0
        differences = {key for key in before['settings'] if before['settings'][key] != after['settings'][key]}
        assert differences == {'AI_THRESHOLD'}, differences
        for source in ('app.py', 'audit.py', 'detector.py', 'stylometry.py', 'scoring.py', 'criteria.md'):
            assert before['files'][source] == after['files'][source], (phase, source)
            assert after['files'][source] == hashlib.sha256(Path(source).read_bytes()).hexdigest()
    before = load('attack_run_*_before.json')
    after = load('attack_run_*_after.json')
    assert len(before['rows']) == len(after['rows']) == 56
    for b, a in zip(before['rows'], after['rows']):
        assert b['id'] == a['id']
        for key in ('status', 'model_score', 'style_score', 'confidence'):
            assert b[key] == a[key], (b['id'], key)
    for label in ('before', 'after'):
        attacks = load(f'attack_run_*_{label}.json')
        audit = [json.loads(line) for line in latest(f'attacks_{label}_*.audit.jsonl').read_text(encoding='utf-8').splitlines()]
        assert len(audit) == len(attacks['rows'])
        required = {'timestamp', 'content_id', 'creator_id', 'guess', 'model_score', 'style_score',
                    'combined_score', 'label', 'status'}
        for row, event in zip(attacks['rows'], audit):
            if row['status'] == 200:
                assert required <= event.keys()
                assert row['content_id'] == event['content_id']
                assert row['confidence'] == event['combined_score']
            else:
                assert event['status'] == 'rejected'
        data = load(f'run_*_{label}.json')
        assert len(data['criteria']) == 5
        for row, scenario in zip(data['criteria'], scenarios.SCENARIOS):
            assert len(row['trials']) == 3
            for trial in row['trials']:
                calculated = measure(scenario, trial['requests'], trial['audit_entries'],
                                     data['settings'], trial['audit_available'])
                assert calculated == trial['measurement'], (label, row['criterion'], trial['trial'])
        if label == 'before':
            corpus_hash = data['corpus_sha256']
        else:
            assert corpus_hash == data['corpus_sha256']
    historical = subprocess.check_output(['git', 'show', 'eec1cf9:logs/audit.jsonl']).decode('utf-8').splitlines()
    current = Path('logs/audit.jsonl').read_text(encoding='utf-8').splitlines()
    assert current[:len(historical)] == historical
    print('Verified: 56 attacks per phase, 3 trials per criterion, identical corpus and signals, only AI_THRESHOLD changed.')


if __name__ == '__main__':
    main()
