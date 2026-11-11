"""Build the Part 2 README from preserved experiment artifacts."""
import json
from pathlib import Path

import run_eval


def latest(pattern):
    return max(Path('results').glob(pattern))


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def block(value):
    return '```json\n' + json.dumps(value, indent=2, ensure_ascii=True) + '\n```\n'


def criteria_table(data):
    lines = ['| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |', '|---|---|---|---|---|---|']
    for row in data['criteria']:
        cells = [f'{row["criterion"]}. {row["name"]}', row['target']]
        cells += [run_eval.metric_text(t['measurement']) for t in row['trials']]
        cells += [row['verdict']]
        lines.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines) + '\n'


def main():
    before = read(Path('results/reviewed_attacks_before.json'))
    after = read(Path('results/reviewed_attacks_after.json'))
    eval_before_path, eval_after_path = latest('run_*_before.json'), latest('run_*_after.json')
    eval_before, eval_after = read(eval_before_path), read(eval_after_path)
    audit_path = latest('attacks_before_*.audit.jsonl')
    entries = [json.loads(s) for s in audit_path.read_text(encoding='utf-8').splitlines() if s]
    selected_ids = ['EV01', 'EV02', 'EV07', 'FP03', 'PI05', 'MF03', 'MF04', 'MF06', 'MF07']
    content_ids = {r['content_id'] for r in before['rows'] if r['id'] in selected_ids}
    selected = [e for e in entries if e.get('content_id') in content_ids]
    selected += [e for e in entries if e.get('reason') == 'rate_limited'][:1]
    assert len(selected) == 10
    lines = ['## Rate Limiting', '',
             '**Limits:** 10 submissions per minute and 200 per day on `/submit`.', '',
             'Ten per minute permits ordinary revisions while constraining rapid threshold probing; 200 per day limits sustained use by one claimed identity. These are operational choices, not measured production capacity.', '',
             '**Declared stretch feature:** Per-creator limits use the existing starter key function. A non-blank string `creator_id` is the key; otherwise requests count against their address. This separates writers at a shared address, but an unauthenticated creator ID can be rotated. In-memory counts reset on restart and are not shared across workers.', '',
             '**Recorded flood:** The model was warmed before the burst. `run_attacks.py::run_flood` returned:', '',
             '```text', '200 200 200 200 200 200 200 200 200 200 429 429 429 429 429', '```', '',
             'Five 429 rejections were logged. Unit tests also verified the daily cap while advancing through minute windows, creator separation, and address fallback.', '',
             'Decisions contain all nine required fields. Validation refusals, short-text failures, model unavailability, and limiter refusals leave rejection entries; rejections have fewer fields because no decision exists. Appeals append `under_review` events without overwriting decisions.', '',
             'Each phase used a fresh service process with limiting enabled. No counter reset occurred inside either attack run. Evaluation requests used a unique creator per phase, criterion, trial, and sample, preventing unrelated rate limits from replacing the intended tests.', '',
             '## Attack Run - Before', '',
             '**All 56 staff inputs were attempted, with no skipped rows or crashes: 42 HELD, 14 BROKE.** The CSV contains 12 flood rows even though their target description says 20; every supplied row was run, and none was invented.', '',
             '**Verdict rules:** An evasion breaks the check when its successful response avoids the AI label, including `unsure`. A false-positive example breaks it only when accused as AI. Controls, punctuation-only, repeated-word, and emoji junk break it when accepted for an authorship decision. Arabic is legitimate writing; its high-confidence accusation, rather than acceptance of its script, is the failure. Injection cases check normal scoring, fixed labels, and one intact decision log entry. Flood requests are allowed within the budget and rejected above it.', '',
             'Raw responses are preserved separately from the reviewed verdicts: [baseline review](results/reviewed_attacks_before.md), [baseline raw results](' + before['source'].replace('\\', '/') + ').', '',
             'The following table includes every supplied attack, with both phases side by side. Scores are unchanged between phases.', '',
             '| ID | Family | Before status / guess | Score | Before | After status / guess | After |', '|---|---|---|---|---|---|---|']
    for b, a in zip(before['rows'], after['rows']):
        lines.append(f'| {b["id"]} | {b["family"]} | {b["status"]} / {b["guess"] or "-"} | {b["confidence"] if b["confidence"] is not None else "-"} | {b["verdict"]} | {a["status"]} / {a["guess"] or "-"} | {a["verdict"]} |')
    lines += ['', '**Ten exact audit entries from the baseline attack run, including a rejection:**', '', block(selected),
              '**Single worst attack outcome:** MF07 accepted Arabic writing and accused it of being AI at 0.8804. Its model score was 0.9064 and style score 0.7762. The English-oriented model and ASCII-only word tokenizer do not establish authorship in Arabic, yet their weighted score produced a confident accusation.', '',
              '## Run Log and Verdicts', '',
              'This personal project uses ten varied reference fixtures, including two plain ones, and ten structured comparison fixtures. Their origin does not establish personal authorship. The original criteria are preserved: criteria 1 and 2 remain **NOT EVALUATED** as authorship claims, while their numeric fixture measurements are shown separately. They are not silently marked MET.', '',
              'The corpus was frozen before the baseline evaluation and reused byte-for-byte afterward. Each criterion has three recorded trials in each phase. Matching results are expected from the deterministic model in evaluation mode and deterministic text statistics.', '',
              '### Before', '', criteria_table(eval_before), '',
              '### After', '', criteria_table(eval_after), '',
              f'Complete requests, responses, content IDs, and relevant audit entries: [before evidence]({eval_before_path.as_posix()}) and [after evidence]({eval_after_path.as_posix()}). Produced by `run_eval.py::main`, `run_trial`, and `measure`.', '',
              '**Real output from trial 1 for each criterion, before and after:**', '']
    for b, a in zip(eval_before['criteria'], eval_after['criteria']):
        lines += [f'**Criterion {b["criterion"]}: {b["name"]}**', '',
                  block({'before': b['trials'][0]['measurement'], 'after': a['trials'][0]['measurement']}),
                  'One actual baseline request and response (the linked evidence contains the full trial):', '',
                  block(b['trials'][0]['requests'][0])]
    lines += ['### Diagnoses and verdict reasoning', '',
              '- Criteria 1 and 2: the route and scores were exercised, but the personal-authorship prerequisite was not established. All three fixture trials had 0/10 reference AI flags and a score gap of 0.23268 (reference mean 0.39535, comparison mean 0.62803). These measurements do not resolve the original authorship claims.',
              '- Criterion 3: MET before because all three guesses and exact label/range matches occurred in all trials. MISSED after: only human and unsure remained in the frozen set, although every returned label still matched its range. The stage is label mapping; moving the cutoff above L02 at 0.8895 removes the only AI result from that set.',
              '- Criterion 4: MET in both phases. Every trial recorded all five appeals with the exact reason, retained the original decision, and placed the matching item under review.',
              '- Criterion 5: MET in both phases. Every trial returned five HTTP 400 invalid_input responses, wrote rejection events, and created no decision for those requests.', '',
              'Every broken baseline attack is diagnosed below; the same explanations apply to the unchanged failures after the improvement:', '',
              '| Attack | Stage | Mechanism |', '|---|---|---|']
    for row in before['rows']:
        if row['verdict'] == 'BROKE':
            lines.append(f'| {row["id"]} | {row["stage"]} | {row["mechanism"]} |')
    lines += ['', 'The strongest repeated patterns are evasion inputs exploiting predictability/surface statistics, and validation admitting non-prose strings. The model is a perplexity scorer, not an instruction-following reviewer: the injection strings were treated as content, and fixed labels and JSON log serialization held. These observations are limited to this attack set.', '',
              '## The Improvement', '',
              '**One behavior change:** Raise only `AI_THRESHOLD` from 0.85 to 0.8896. The model, style signal, weights (0.8/0.2), human cutoff (0.15), validation, label sentences, and limiter are unchanged.', '',
              '**Selection:** The human-written historical reference L02 scored 0.8895, higher than all eight staff false-positive examples. The new cutoff is one four-decimal increment above that confirmed-human calibration maximum. Because the reference fixtures do not verify personal authorship, they were excluded from this calibration pool. The diagnosis and exact value were committed before the after runs; see [baseline diagnosis](results/baseline_diagnosis.md). This tunes observed examples and provides no unseen-data accuracy estimate.', '',
              '### Attack Run - After', '',
              '**All 56 rows were rerun: 43 HELD, 13 BROKE; no crashes.** MF07 changed from AI to unsure. All other attack statuses, guesses, and verdicts were unchanged. All model, style, and combined scores were identical across the attack runs.', '',
              '[After review](results/reviewed_attacks_after.md) and [after raw responses](' + after['source'].replace('\\', '/') + ').', '',
              '| Measure | Before | After |', '|---|---|---|',
              '| Staff attacks held | 42/56 | 43/56 |',
              '| Staff attacks broken | 14/56 | 13/56 |',
              '| Evasions avoiding the AI label | 9/10 | 9/10 |',
              '| Staff false-positive examples accused | 0/8 | 0/8 |',
              '| Arabic attack MF07 | AI, 0.8804 | unsure, 0.8804 |',
              '| Historical human control L02 | AI, 0.8895 | unsure, 0.8895 |',
              '| Criterion 3 labels reached | 3/3 in every trial | 2/3 in every trial |',
              '| Appeal and invalid-input targets | MET | MET |', '',
              '**Did it help?** It removed the unsupported accusation on MF07 and the historical human control, while causing the label-coverage criterion to miss. The supplied evasion outcomes did not change; no additional AI detection benefit is claimed.', '',
              '## What\'s Still Broken', '',
              '- EV01-EV09 still avoid the AI label. Next, measure the effect of the specific typo, sentence, punctuation, and opening edits against matched controls before considering another signal or weight change. Those were deferred to keep this one-change experiment interpretable.',
              '- MF03-MF06 still receive authorship decisions on control characters, punctuation-only text, a repeated single word, or emoji. Next, add a supported-writing/input-quality gate and test legitimate edge cases; validation was deliberately not changed alongside the threshold.',
              '- Criterion 3 now misses on the frozen set. Keep that honest result; assess a new, separately versioned coverage set to distinguish sample coverage from global label reachability. Do not replace the original examples to repair this verdict.',
              '- The original personal-writing conditions in criteria 1 and 2 remain unverified. A new experiment with documented personal pieces is needed to evaluate those authorship claims; the present fixture results exercise scoring behavior only.',
              '- Per-creator limits can be bypassed by changing IDs, and the counters reset with the process. Authentication and shared persistent limiter storage would be needed for real deployment. Both are outside this local experiment.',
              '- MF07 now receives unsure, but the system still lacks validated multilingual authorship support. A threshold change does not fix either signal\'s language limitations.', '',
              '**The production trade:** I would favor fewer accusations against real writers, accepting that more AI text would receive unsure and require moderation. The site and its reviewers would bear that extra work rather than make writers bear unsupported accusations.', '',
              '### Reproducing the experiments', '',
              'With the virtual environment active and no service already on port 5000:', '',
              '```text', 'python test.py', 'python -m unittest discover -s tests -v',
              'python run_experiment.py flood --label before',
              'python run_experiment.py attacks --set attack_set/attack_set --label after',
              'python run_experiment.py criteria --label after',
              'python verify_experiments.py', '```', '',
              'The final checkout uses the after cutoff. To reproduce the original baseline, use the committed baseline revision before the threshold change in a separate checkout; a `before` label alone does not change service settings. Every run manifest records the actual configuration, source hashes, package versions, corpus hashes, and its exact audit range. Existing raw experiment files are not overwritten.', '',
              'The same repository is used throughout. Results and audit history are committed. Course-portal submission remains manual.', '']
    path = Path('README.md')
    original = path.read_text(encoding='utf-8')
    prefix = original[:original.index('## Rate Limiting')]
    if '**Part 2 AI-use update:**' in prefix:
        prefix = prefix[:prefix.index('**Part 2 AI-use update:**')]
    old = 'The full three-trial acceptance evaluation, including the user\'s own writing, remains for Unit 8.'
    prefix = prefix.replace(old, 'Part 2 below records the later three-trial experiment and its corpus limitations.')
    prefix = prefix.replace('which falls in the AI band: a real false positive',
                            'which fell in the original 0.85 AI band: a real false positive')
    prefix = prefix.replace('All three labels were returned by live submissions.',
                            'At the original 0.85 AI cutoff, all three labels were returned by live submissions.')
    marker = '<!-- '
    boundary = prefix.rfind(marker)
    if boundary >= 0 and 'UNIT 8' in prefix[boundary:]:
        prefix = prefix[:boundary]
    prefix += '**Part 2 AI-use update:** I asked the assistant to implement the planned instrumentation, harness, and experiment. It preserved raw responses, calculated the trial metrics, diagnosed failures, and measured the single threshold change. The resulting write-up retains the coverage regression and distinguishes fixture metrics from unverified authorship claims.\n\n'
    path.write_text(prefix + '\n'.join(lines), encoding='utf-8')
    print('Updated README from the preserved before/after evidence.')


if __name__ == '__main__':
    main()
