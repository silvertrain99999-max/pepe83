import json
import unittest
from pathlib import Path

from catalog import build_plan, channel_values, load, validate


HERE = Path(__file__).parent


class TrekCatalogTests(unittest.TestCase):
    def test_repository_catalog_is_valid(self):
        self.assertEqual(validate(load(HERE / "catalog.json")), [])

    def test_smartstore_discount_is_separate(self):
        value = channel_values({"sku": "1", "regular_price": 45000,
                                "sale_price": 15900, "supplier_stock": 27},
                               "smartstore")
        self.assertEqual(value["regular_price"], 45000)
        self.assertEqual(value["immediate_discount"], 29100)
        self.assertEqual(value["displayed_price"], 15900)

    def test_cafe24_uses_consumer_and_selling_price(self):
        value = channel_values({"sku": "1", "regular_price": 35000,
                                "sale_price": 15900, "supplier_stock": 5},
                               "cafe24")
        self.assertEqual(value["consumer_price"], 35000)
        self.assertEqual(value["selling_price"], 15900)
        self.assertFalse(value["separate_discount"])

    def test_accessory_ignores_store_stock(self):
        value = channel_values({"sku": "1", "regular_price": 10000,
                                "supplier_stock": 3, "store_stock": 9},
                               "smartstore", include_store_stock=False)
        self.assertEqual(value["stock"], 3)


if __name__ == "__main__":
    unittest.main()
