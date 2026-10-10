import unittest
from copy import deepcopy
from bike_policy import inventory_plan, seo_plan, stock_target, validate_scope, verified


def proof():
    return dict(reference="synthetic-test", checked_at="2026-10-10T10:00:00+09:00", revision="test-1", confirmed=True)


def fixture():
    return dict(match=proof(), product_state="selling", product_ids=dict(cafe24="c1", smartstore="s1"),
        expected_option_ids=dict(cafe24=["co1"], smartstore=["so1"]),
        stock_basis=dict(proof(), mode="store_only"), option_resume_authorization=proof(),
        rows=[dict(sku="DEMO-SKU", model="DEMO", year=2027, generation="n/a", color="black", size="M",
                   supplier=dict(proof(), state="archived", quantity=None),
                   store=dict(proof(), state="known", quantity=2),
                   channels=dict(cafe24=dict(product_id="c1", option_id="co1", option_selling=False),
                                 smartstore=dict(product_id="s1", option_id="so1", option_selling=True)))])


class BikePolicyTests(unittest.TestCase):
    def test_archived_supplier_can_use_explicit_store_only(self):
        result = inventory_plan(fixture())
        self.assertEqual(result["rows"][0]["quantity"], 2)
        self.assertIs(result["rows"][0]["option_selling"], True)

    def test_unknown_supplier_never_becomes_zero(self):
        item = fixture()
        item["stock_basis"]["mode"] = "supplier_only"
        with self.assertRaises(ValueError):
            inventory_plan(item)

    def test_no_implicit_stock_sum(self):
        item = fixture()
        item["stock_basis"].pop("mode")
        with self.assertRaises(ValueError):
            inventory_plan(item)

    def test_resume_requires_instruction(self):
        item = fixture()
        item.pop("option_resume_authorization")
        with self.assertRaises(ValueError):
            inventory_plan(item)

    def test_missing_option_or_duplicate_sku_blocks_entire_plan(self):
        for mutate in (lambda x: x["expected_option_ids"]["cafe24"].append("missing"),
                       lambda x: x["rows"].append(deepcopy(x["rows"][0]))):
            item = fixture()
            mutate(item)
            with self.assertRaises(ValueError):
                inventory_plan(item)

    def test_bad_quantity_and_stopped_product(self):
        for value in (-1, True, None):
            item = fixture()
            item["rows"][0]["store"]["quantity"] = value
            with self.assertRaises(ValueError):
                inventory_plan(item)
        item = fixture()
        item["product_state"] = "stopped"
        with self.assertRaises(ValueError):
            inventory_plan(item)

    def test_seo_requires_exact_spec_and_same_channel_name(self):
        spec = dict(source=proof(), year=2027, model="DEMO", drivetrain="TEST", rear_speed=10,
                    frame_material="알루미늄", bike_type="하이브리드자전거", use_terms=["출퇴근자전거"])
        result = seo_plan(spec)
        self.assertEqual(result["cafe24"]["name"], result["smartstore"]["name"])
        self.assertIn("TEST 10단 알루미늄", result["cafe24"]["name"])
        spec.pop("source")
        with self.assertRaises(ValueError):
            seo_plan(spec)

    def test_seo_cannot_touch_stock(self):
        with self.assertRaises(ValueError):
            validate_scope("cafe24", "seo", {"stock": 2})

    def test_both_channels_exact_readback_required(self):
        ids = dict(cafe24="c1", smartstore="s1")
        expected = {c: {"quantity": 2, "option_selling": True} for c in ids}
        records = [dict(channel=c, product_id=pid, workflow="inventory", actor="assistant",
                        status="reverified", save=proof(), reread=proof(), actual=deepcopy(expected[c]))
                   for c, pid in ids.items()]
        self.assertTrue(verified(records, ids, "inventory", expected))
        for field, value in (("status", "user_reported"), ("actual", {"quantity": 2}),
                             ("product_id", "wrong"), ("workflow", "seo"), ("reread", {})):
            changed = deepcopy(records)
            changed[0][field] = value
            self.assertFalse(verified(changed, ids, "inventory", expected))
        self.assertFalse(verified([records[0], records[0]], ids, "inventory", expected))


if __name__ == "__main__":
    unittest.main()
