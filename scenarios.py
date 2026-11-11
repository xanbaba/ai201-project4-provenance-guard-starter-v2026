"""Frozen experiment inputs; source provenance is kept with the corpus."""
import json
from pathlib import Path
CORPUS_PATH = Path(__file__).parent / 'evaluation_data' / 'corpora.json'
CORPUS = json.loads(CORPUS_PATH.read_text(encoding='utf-8'))
REFERENCE = CORPUS['reference']
COMPARISON = CORPUS['comparison']
SCENARIOS = [
    {'criterion': 1, 'name': 'False positives on my writing', 'kind': 'false_positive',
     'target': 'at most 1 of 10 ai guesses', 'samples': REFERENCE,
     'original_eligible': CORPUS['provenance']['original_personal_writing_requirement_satisfied']},
    {'criterion': 2, 'name': 'Score separation', 'kind': 'separation',
     'target': 'comparison mean minus reference mean >= 0.15', 'samples': REFERENCE + COMPARISON,
     'original_eligible': CORPUS['provenance']['original_personal_writing_requirement_satisfied']},
    {'criterion': 3, 'name': 'All three labels are reachable', 'kind': 'coverage',
     'target': '3 guesses; exact labels and score ranges', 'samples': REFERENCE + COMPARISON + CORPUS['coverage_extra']},
    {'criterion': 4, 'name': 'Appeals are recorded and put under review', 'kind': 'appeals',
     'target': '5/5 recorded appeals and original decisions', 'samples': REFERENCE[:5]},
    {'criterion': 5, 'name': 'Invalid submission input is rejected', 'kind': 'invalid',
     'target': '5/5 HTTP 400 invalid_input, no decision entry',
     'bodies': [{}, {'text': ''}, {'text': '   '}, {'text': None}, {'text': 'x' * 10001}]},
]


def validate():
    problems = []
    for name in ('reference', 'comparison'):
        samples = CORPUS[name]
        if len(samples) != 10 or len({s['text'] for s in samples}) != 10:
            problems.append(f'{name} must contain ten distinct pieces')
        if any(not isinstance(s['text'], str) or not s['text'].strip() or len(s['text']) > 10000 for s in samples):
            problems.append(f'{name} contains invalid text')
    if len(SCENARIOS[2]['samples']) > 30:
        problems.append('coverage set exceeds 30 pieces')
    return problems
