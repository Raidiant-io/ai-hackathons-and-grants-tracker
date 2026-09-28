import unittest
from rewards import normalize_award, select_award


class RewardTests(unittest.TestCase):
    def award(self, amount=1250, checked='2026-09-28'):
        return dict(max_award_amount=amount, max_award_currency='USD', max_award_kind='cash',
                    max_award_basis='First place; only one ranked prize per entry.',
                    max_award_evidence_url='https://organizer.example/rules', max_award_verified_at=checked)

    def test_pool_text_never_becomes_a_personal_award(self):
        result = normalize_award({'reward':'$1,000,000 cash prize pool'})
        self.assertIsNone(result['max_award_amount'])
        self.assertIsNone(result['max_award_currency'])

    def test_verified_values_require_numeric_amount_currency_and_provenance(self):
        self.assertEqual(normalize_award(self.award())['max_award_amount'], 1250)
        self.assertEqual(normalize_award(self.award(0))['max_award_amount'], 0)
        invalids = [self.award('1250'), self.award(True), self.award(-1), self.award(float('inf')),
                    {**self.award(), 'max_award_currency':None},
                    {**self.award(), 'max_award_evidence_url':'javascript:alert(1)'},
                    {**self.award(), 'max_award_basis':''},
                    {**self.award(), 'max_award_verified_at':'2026-02-30'},
                    {'max_award_amount':None, 'max_award_basis':'No cap', 'max_award_verified_at':'unknown'}]
        for record in invalids:
            with self.subTest(record=record), self.assertRaises(ValueError):
                normalize_award(record)

    def test_newer_assessments_replace_whole_awards_and_can_clear_stale_values(self):
        self.assertEqual(select_award(self.award(1250), self.award(500, '2026-09-27'))['max_award_amount'], 1250)
        self.assertEqual(select_award(self.award(1250), self.award(1500, '2026-09-29'))['max_award_amount'], 1500)
        cleared = dict(max_award_amount=None, max_award_basis='New rules do not establish stacking.', max_award_verified_at='2026-09-29')
        result = select_award(self.award(), cleared)
        self.assertIsNone(result['max_award_amount'])
        self.assertIsNone(result['max_award_currency'])
        self.assertIn('stacking', result['max_award_basis'])
