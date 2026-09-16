import json
import unittest
from copy import deepcopy
from pathlib import Path
from policy import plan, verified, USER_ONLY


class PolicyTest(unittest.TestCase):
    def setUp(self):
        self.item = json.loads(Path(__file__).with_name('example.json').read_text(encoding='utf-8'))['items'][0]

    def test_user_owned_actions(self):
        for action in USER_ONLY:
            with self.subTest(action=action):
                self.item['actions'] = [action]
                result = plan(self.item)
                self.assertEqual(result['status'], 'handoff')
                self.assertEqual(result['changes'], {})

    def test_stopped_listing_untouched(self):
        self.item['current']['status'] = '판매중지'
        self.assertEqual(plan(self.item)['changes'], {})

    def test_missing_is_not_soldout(self):
        self.item['source']['listed'] = False
        self.assertEqual(plan(self.item)['changes'], {})

    def test_store_missing_not_zero(self):
        del self.item['rows'][0]['store_quantity']
        self.assertEqual(plan(self.item)['changes'], {})

    def test_sports55_and_discount_preservation(self):
        before = deepcopy(self.item)
        self.item['rows'][0]['supplier_in_stock'] = True
        result = plan(self.item)
        self.assertEqual(result['changes']['options']['default']['stock'], 20)
        self.assertNotIn('discount', result['changes'])
        self.assertEqual(self.item['current'], before['current'])

    def test_no_policy_leak_to_topeak(self):
        self.item.update(supplier='hlsc', brand='topeak')
        self.item['rows'][0]['supplier_in_stock'] = True
        self.assertEqual(plan(self.item)['changes'], {})

    def test_whole_and_partial_soldout(self):
        result = plan(self.item)['changes']
        self.assertEqual(result['replacement_text'], '[품절]')
        self.item['current']['option_ids'].append('green')
        row = deepcopy(self.item['rows'][0])
        row.update(id='green', store_quantity=1)
        self.item['rows'].append(row)
        result = plan(self.item)['changes']
        self.assertEqual(result['availability'], '판매중')
        self.assertFalse(result['replacement_enabled'])
        self.assertEqual(result['options']['default']['stock'], 0)

    def test_missing_option_holds_everything(self):
        self.item['current']['option_ids'].append('missing')
        self.assertEqual(plan(self.item)['changes'], {})

    def test_ambiguous_match_no_changes(self):
        self.item['match_confirmed'] = False
        result = plan(self.item)
        self.item['match_confirmed'] = True
        self.assertEqual(plan(self.item, result)['status'], 'hold')
        self.item['evidence_revision'] = 'new-verified-evidence'
        self.assertEqual(plan(self.item, result)['status'], 'ready_for_review')

    def test_seo_cannot_smuggle_discount_or_delete(self):
        self.item.update(actions=['seo'], seo={'confirmed': True, 'fields': {'discount': 20}})
        self.assertEqual(plan(self.item)['changes'], {})

    def test_shipping_requires_stock_and_cutoff(self):
        self.item.update(actions=['today_shipping'], shipping={'store_confirmed': True, 'store_quantity': 1})
        self.assertEqual(plan(self.item)['status'], 'hold')

    def test_verified_requires_save_and_reread(self):
        result = plan(self.item)
        self.assertEqual(verified(result, saved=True)['status'], 'ready_for_review')
        self.assertEqual(verified(result, saved=True, reread=True)['status'], 'verified')


if __name__ == '__main__':
    unittest.main()
