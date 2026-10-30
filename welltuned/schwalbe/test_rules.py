import unittest
from rules import plan_option, validate_seo_patch, verification_status


class RulesTest(unittest.TestCase):
    def setUp(self):
        self.current = dict(model="Rocket Ron", grade="Performance", construction="TLR",
                            size="29x2.25", color="black")
        self.supplier = dict(self.current, stock="재고있음", retail=66000)

    def test_supply_and_soldout_channels(self):
        self.assertEqual(plan_option(self.current, self.supplier, channel="cafe24")["changes"]["quantity"], 5)
        self.supplier["stock"] = "재고없음"
        result = plan_option(self.current, self.supplier, channel="smartstore")
        self.assertEqual(result["changes"]["quantity"], 0)
        self.assertEqual(result["changes"]["option_use"], "Y")
        self.assertNotIn("product_stop", result["changes"])

    def test_unconfirmed_is_not_soldout(self):
        for supplier in (None, dict(self.supplier, color="classic skin"),
                         dict(self.supplier, construction="tube"),
                         dict(self.supplier, stock="unknown")):
            self.assertEqual(plan_option(self.current, supplier, channel="cafe24")["status"], "hold")

    def test_store_stock_requires_new_policy(self):
        self.assertEqual(plan_option(self.current, self.supplier, channel="cafe24", store_stock=1)["status"], "hold")

    def test_seo_preserves_pm(self):
        with self.assertRaises(ValueError):
            validate_seo_patch("smartstore", {"quantity": 0})
        self.assertEqual(validate_seo_patch("cafe24", {"meta_author": "YBBIKE"}), {"meta_author": "YBBIKE"})

    def test_save_is_not_reopen(self):
        self.assertEqual(verification_status(save_notice=True, reopened=False, fields_match=False), "saved_pending_reopen")
        self.assertEqual(verification_status(save_notice=True, reopened=True, fields_match=True), "verified")


if __name__ == "__main__":
    unittest.main()
