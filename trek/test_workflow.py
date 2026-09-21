import unittest
from pathlib import Path

from workflow import load_tree, next_category, set_state, summary, validate_tree


HERE = Path(__file__).parent


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tree = load_tree(HERE / "categories.json")

    def test_tree_is_valid(self):
        self.assertEqual(validate_tree(self.tree), [])

    def test_next_category_does_not_skip_in_progress(self):
        self.assertEqual(next_category(self.tree)["id"], "gear.components.tubeless")

    def test_excluded_category_is_pruned(self):
        changed = set_state(self.tree, "gear.components.tubeless", scope="exclude")
        self.assertEqual(next_category(changed)["id"], "gear.components.handlebars")

    def test_complete_requires_evidence(self):
        with self.assertRaises(ValueError):
            set_state(self.tree, "gear.components.tubeless", status="complete")

    def test_summary_has_leaf_count(self):
        self.assertGreater(summary(self.tree)["leaf_count"], 50)


if __name__ == "__main__":
    unittest.main()
