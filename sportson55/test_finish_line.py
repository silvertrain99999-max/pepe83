import unittest
from sportson55.finish_line import plan, package_price, option_plan


class FinishLineTest(unittest.TestCase):
    def args(self, **overrides):
        identity = dict(family='dry', formulation='dry', capacity=120, unit='ml')
        return dict(channel='smartstore', current={'discount_rate': 15},
                    listing={**identity, 'units': 1},
                    source={**identity, 'units': 12, 'price': 168000, 'soldout': False},
                    source_current=True, confirmed_match=True, homogeneous_pack=True,
                    **overrides)

    def test_pack_to_single_and_discount(self):
        p = plan(**self.args())
        self.assertEqual(p['changes'], {'sale_price': 14000, 'stock': 20})
        self.assertNotIn('discount_rate', p['changes'])

    def test_capacity_formulation_and_mass_volume_mismatch(self):
        for k, v in [('capacity', 240), ('formulation', 'mineral'), ('unit', 'g')]:
            args = self.args()
            args['listing'][k] = v
            self.assertEqual(plan(**args)['status'], 'hold')

    def test_soldout_requires_known_physical_inventory(self):
        args = self.args()
        args['source']['soldout'] = True
        self.assertEqual(plan(**args)['status'], 'hold')
        args.update(channel='cafe24', store_confirmed=True, store_quantity=3)
        p = plan(**args)['changes']
        self.assertEqual(p['stock'], 3)
        self.assertFalse(p['replacement_enabled'])
        args['store_quantity'] = 0
        self.assertEqual(plan(**args)['changes']['replacement_text'], '[품절]')

    def test_unconfirmed_or_old_or_missing_source_is_held(self):
        for k, v in [('source', None), ('source_current', False),
                     ('confirmed_match', False), ('homogeneous_pack', False), ('hold', True)]:
            args = self.args()
            args[k] = v
            self.assertEqual(plan(**args)['changes'], {})

    def test_pack_rounding_is_not_guessed(self):
        for count in (0, -1, True):
            with self.assertRaises(ValueError):
                package_price(100, count, 1)
        with self.assertRaises(ValueError):
            package_price(100, 3, 1)

    def test_options_require_full_mapping_and_keep_partial_sale(self):
        a = self.args()
        for k in ('channel', 'current'):
            a.pop(k)
        b = self.args()
        for k in ('channel', 'current'):
            b.pop(k)
        b['source']['soldout'] = True
        b.update(store_confirmed=True, store_quantity=0)
        rows = [dict(id='120ml', **a), dict(id='60ml', **b)]
        rows[1]['source']['capacity'] = rows[1]['listing']['capacity'] = 60
        rows[1]['source']['price'] = 108000
        p = option_plan(channel='cafe24', current={}, rows=rows, expected_option_ids=['120ml','60ml'])
        self.assertEqual(p['changes']['option_stock'], {'120ml':20, '60ml':0})
        self.assertEqual(p['changes']['option_total_prices'], {'120ml':14000, '60ml':9000})
        self.assertFalse(p['changes']['replacement_enabled'])
        self.assertEqual(option_plan(channel='cafe24', current={}, rows=rows[:1],
                                    expected_option_ids=['120ml','60ml'])['status'], 'hold')
