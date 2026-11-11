"""Contract checks independent of the large detector model."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app
import audit
import config
import detector
import scoring
import stylometry


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.log_patch = patch.object(config, 'AUDIT_LOG', Path(self.directory.name) / 'audit.jsonl')
        self.log_patch.start()
        self.addCleanup(self.log_patch.stop)
        self.client = app.app.test_client()
        if config.RATE_LIMITING_ENABLED:
            app.limiter.reset()
        self.body = {'text': 'One sentence here. Another sentence appears.', 'creator_id': 'writer'}

    def test_decision_and_repeated_appeal(self):
        with patch.object(detector, 'model_signal', return_value=0.9):
            response = self.client.post('/submit', json=self.body)
        self.assertEqual(response.status_code, 200)
        item = response.get_json()
        self.assertEqual(item['confidence'], scoring.combine_signals(item['model_score'], item['style_score']))
        self.assertEqual((item['guess'], item['label']), scoring.score_to_label(item['confidence']))
        for reason in ('First explanation', 'Second explanation'):
            result = self.client.post('/appeal', json={'content_id': item['content_id'], 'reasoning': reason})
            self.assertEqual(result.status_code, 200)
            self.assertEqual(result.json['status'], 'under_review')
        entries = audit.entries_for(item['content_id'])
        self.assertEqual([x['status'] for x in entries], ['decided', 'under_review', 'under_review'])
        self.assertEqual([x['reasoning'] for x in entries[1:]], ['First explanation', 'Second explanation'])

    def test_invalid_inputs_do_not_log_decisions(self):
        bodies = [{'creator_id': 'writer'}, {'text': '', 'creator_id': 'writer'},
                  {'text': '   ', 'creator_id': 'writer'}, {'text': None, 'creator_id': 'writer'},
                  {'text': 'x' * 10001, 'creator_id': 'writer'}, [],
                  {'text': 'Valid text here', 'creator_id': ''}]
        for body in bodies:
            with self.subTest(body=str(body)[:100]):
                r = self.client.post('/submit', json=body)
                self.assertEqual(r.status_code, 400)
                self.assertEqual(r.json['error'], 'invalid_input')
        self.assertTrue(all(e['status'] == 'rejected' for e in audit.read_entries()))
        self.assertEqual(len(audit.read_entries()), len(bodies))
        self.assertEqual(self.client.post('/appeal', json={'content_id':'missing', 'reasoning':'review'}).status_code, 404)

    def test_detector_errors(self):
        with patch.object(detector, 'model_signal', side_effect=detector.DetectorUnavailable('not installed')):
            self.assertEqual(self.client.post('/submit', json=self.body).status_code, 503)
        with patch.object(detector, 'model_signal', side_effect=ValueError('short')):
            self.assertEqual(self.client.post('/submit', json=self.body).status_code, 400)
        self.assertEqual([e['reason'] for e in audit.read_entries()], ['detector_unavailable', 'invalid_input'])

    def test_rate_limit_and_creator_separation(self):
        with patch.object(detector, 'model_signal', return_value=.5):
            responses = [self.client.post('/submit', json=self.body) for _ in range(11)]
            self.assertEqual([r.status_code for r in responses], [200] * 10 + [429])
            another = self.client.post('/submit', json={**self.body, 'creator_id': 'another'})
            self.assertEqual(another.status_code, 200)
        rejected = [e for e in audit.read_entries() if e.get('reason') == 'rate_limited']
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]['creator_id'], 'writer')

    def test_invalid_json_uses_address_budget(self):
        codes = [self.client.post('/submit', data='{', content_type='application/json').status_code
                 for _ in range(11)]
        self.assertEqual(codes, [400] * 10 + [429])
        self.assertEqual(audit.read_entries()[-1]['reason'], 'rate_limited')

    def test_daily_limit_across_minute_windows(self):
        now = [2000000000.0]
        with patch('limits.storage.memory.time.time', side_effect=lambda: now[0]), \
                patch.object(detector, 'model_signal', return_value=.5):
            for i in range(200):
                if i and i % 10 == 0:
                    now[0] += 61
                self.assertEqual(self.client.post('/submit', json=self.body).status_code, 200)
            now[0] += 61
            self.assertEqual(self.client.post('/submit', json=self.body).status_code, 429)
        self.assertEqual(audit.read_entries()[-1]['reason'], 'rate_limited')

    def test_label_boundaries_and_style_edge_cases(self):
        for score, guess in [(0, 'human'), (.15, 'human'), (.1501, 'unsure'), (.51, 'unsure'),
                             (.85, 'unsure'), (.8895, 'unsure'), (.8896, 'ai'), (.95, 'ai'), (1, 'ai')]:
            self.assertEqual(scoring.score_to_label(score)[0], guess)
        for text in ('', 'One sentence.', 'One. Two very different sentences!'):
            self.assertTrue(0 <= stylometry.style_signal(text) <= 1)
        self.assertEqual(stylometry.sentence_length_spread('One sentence.'), 0)


if __name__ == '__main__':
    unittest.main()
