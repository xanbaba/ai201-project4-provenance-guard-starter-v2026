"""Measurements must fail on incomplete evidence and retain original targets."""
import unittest
from unittest.mock import patch

import experiment_report
import run_eval


SETTINGS = {'human_threshold': .15, 'ai_threshold': .85}


def decision(score, sample_id='R01'):
    guess = run_eval.expected_guess(score, SETTINGS)
    return {'status': 200, 'endpoint': '/submit', 'sample_id': sample_id,
            'response': {'content_id': sample_id, 'confidence': score, 'model_score': score,
                         'style_score': score, 'guess': guess, 'label': run_eval.LABELS[guess]}}


class EvaluationTests(unittest.TestCase):
    def test_missing_or_nonfinite_score_fails(self):
        r = decision(.2)
        del r['response']['model_score']
        self.assertFalse(run_eval.valid_decision(r))
        self.assertFalse(run_eval.valid_decision(decision(float('nan'))))

    def test_gap_and_missing_group(self):
        scenario = {'kind': 'separation'}
        records = [decision(.2, f'R{i}') for i in range(10)] + [decision(.5, f'C{i}') for i in range(10)]
        result = run_eval.measure(scenario, records, [], SETTINGS)
        self.assertTrue(result['passed'])
        self.assertAlmostEqual(result['gap'], .3)
        self.assertFalse(run_eval.measure(scenario, records[:-1], [], SETTINGS)['passed'])

    def test_bad_input_requires_no_decision_and_available_log(self):
        records = [{'status': 400, 'request': {'creator_id': str(i)}, 'response': {'error': 'invalid_input'}} for i in range(5)]
        self.assertTrue(run_eval.measure({'kind': 'invalid'}, records, [], SETTINGS)['passed'])
        self.assertFalse(run_eval.measure({'kind': 'invalid'}, records, [], SETTINGS, False)['passed'])
        entries = [{'creator_id': '1', 'guess': 'ai'}]
        self.assertFalse(run_eval.measure({'kind': 'invalid'}, records, entries, SETTINGS)['passed'])

    def test_coverage_requires_three_labels_and_exact_sentences(self):
        rows = [decision(.1), decision(.5), decision(.95)]
        self.assertTrue(run_eval.measure({'kind': 'coverage'}, rows, [], SETTINGS)['passed'])
        rows[-1]['response']['label'] = 'unrecognized label'
        self.assertFalse(run_eval.measure({'kind': 'coverage'}, rows, [], SETTINGS)['passed'])

    def test_unsure_is_evasion_success_but_not_false_accusation(self):
        row = {'status': 200, 'guess': 'unsure', 'id': 'EV01', 'family': 'evasion'}
        self.assertEqual(experiment_report.assess_attack(row, [])[0], 'BROKE')
        row.update(id='FP01', family='false_positive')
        self.assertEqual(experiment_report.assess_attack(row, [])[0], 'HELD')


if __name__ == '__main__':
    unittest.main()
