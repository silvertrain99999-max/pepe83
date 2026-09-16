import unittest
from rules import build_plan, inventory_target, model_candidates


class RulesTest(unittest.TestCase):
    def test_supplier_stock_overrides_physical_quantity(self):
        self.assertEqual(inventory_target(True, 3), 20)
        self.assertEqual(inventory_target(False, 3), 3)
        self.assertEqual(inventory_target(False, 0), 0)
        self.assertIsNone(inventory_target(None, 0))

    def test_empty_model_cannot_match_anything(self):
        for value in (None, "", " "):
            with self.assertRaises(ValueError):
                model_candidates(value, "파크툴 SR-18.2", [{"name": "TSB-4 베이스"}])

    def test_versions_and_packages_are_not_interchangeable(self):
        catalog = [{"name": "DT-2.2 포크"}, {"name": "SW-16.3 렌치"},
                   {"name": "GP-2 수퍼 패치 키트 - 카운터 디스플레이 박스"}]
        self.assertEqual(model_candidates("DT-2", "파크툴 DT-2", catalog), [])
        self.assertEqual(model_candidates("SW-16", "파크툴 SW-16", catalog), [])
        self.assertEqual(model_candidates("GP-2", "파크툴 GP-2 패치", catalog), [])

    def test_category_prefix_does_not_hide_confirmed_model(self):
        catalog = [{"name": "SR-18.2 스프라켓 리무버-체인윕", "price": "52,000원"}]
        self.assertEqual(len(model_candidates("SR-18.2", "파크툴 카세트 공구 SR-18.2", catalog)), 1)

    def test_exact_pack_matches(self):
        item = {"name": "TL-4.2C 타이어 레버 세트 - 카드 패킹"}
        self.assertEqual(model_candidates("TL-4.2C", "파크툴 TL-4.2C 카디드", [item]), [item])

    def test_confirmed_model_must_also_be_in_listing(self):
        self.assertEqual(model_candidates("TSB-4", "파크툴 SR-18.2", [{"name": "TSB-4 베이스"}]), [])

    def test_documented_alias_is_accepted(self):
        item = {"name": "MW-SET.2 메트릭 렌치 세트"}
        self.assertEqual(model_candidates("MW-SET2", "파크툴 MW-SET2", [item]), [item])

    def test_missing_supplier_does_not_zero_stock_or_change_price(self):
        result = build_plan(channel="smartstore", current={"name": "상품★"}, source=None)
        self.assertEqual(result["changes"], {"name": "상품"})
        self.assertEqual(result["status"], "hold")

    def test_user_hold_makes_no_changes(self):
        result = build_plan(channel="smartstore", current={"name": "GG-1★"}, source=None, hold=True)
        self.assertEqual(result["changes"], {})

    def test_discount_is_preserved_and_cafe_soldout_is_explicit(self):
        current = {"name": "도구★", "discount_rate": 15, "discount_end": "2031-12-31"}
        plan = build_plan(channel="cafe24", current=current, source={"price": "34,000원", "soldout": True}, confirmed_match=True)
        self.assertEqual(plan["changes"]["sale_price"], 34000)
        self.assertEqual(plan["changes"]["stock"], 0)
        self.assertEqual(plan["changes"]["replacement_text"], "[품절]")
        self.assertNotIn("discount_rate", plan["changes"])
        self.assertEqual(current["name"], "도구★")

    def test_partial_option_soldout_does_not_hide_whole_cafe_price(self):
        plan = build_plan(channel="cafe24", current={}, source={"price": 76000, "soldout": False},
                          confirmed_match=True, option_status={"15.1": False, "15.2": True})
        self.assertEqual(plan["changes"]["option_stock"], {"15.1": 0, "15.2": 20})
        self.assertFalse(plan["changes"]["replacement_enabled"])

    def test_unknown_option_status_is_held(self):
        plan = build_plan(channel="smartstore", current={}, source={"price": 76000, "soldout": False},
                          confirmed_match=True, option_status={"15.1": None})
        self.assertEqual(plan["status"], "hold")
        self.assertEqual(plan["changes"], {})


if __name__ == "__main__":
    unittest.main()
