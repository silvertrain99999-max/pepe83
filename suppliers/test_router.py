import json
import unittest
from pathlib import Path
from router import resolve, SUPPLIER_IDS


class SupplierRoutingTest(unittest.TestCase):
    def test_six_suppliers_and_valid_entries(self):
        self.assertEqual(len(SUPPLIER_IDS), 6)
        root = Path(__file__).resolve().parent.parent
        for key in SUPPLIER_IDS:
            config = json.loads(Path(__file__).with_name(key + '.json').read_text(encoding='utf-8'))
            self.assertEqual(config['id'], key)
            for brand in config['brands']:
                route = resolve(key, brand)
                if route['status'] == 'planner_ready':
                    self.assertTrue((root / route['entry']).is_file(), route['entry'])

    def test_wrong_supplier_never_falls_back(self):
        self.assertEqual(resolve('hlsc', 'park_tool')['status'], 'hold')
        self.assertEqual(resolve('sports55', 'topeak')['status'], 'hold')
        self.assertEqual(resolve('../sports55', 'park_tool')['status'], 'hold')

    def test_unimplemented_stays_held(self):
        for supplier, brand in [('trek','trek_bike'), ('odbike','merida'), ('glnco','sram'), ('nnxsports','shimano')]:
            self.assertEqual(resolve(supplier, brand)['status'], 'hold')

    def test_brand_policies_do_not_leak(self):
        self.assertEqual(resolve('sports55','park_tool')['supplier_in_stock_quantity'], 20)
        self.assertEqual(resolve('sports55','finish_line')['discount_policy'], 'preserve_existing')
        self.assertNotIn('supplier_in_stock_quantity', resolve('hlsc','topeak'))
        self.assertEqual(resolve('hlsc','topeak')['runtime'], 'node')
