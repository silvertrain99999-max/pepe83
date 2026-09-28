import unittest

from channel_workflow import (
    SMARTSTORE_SEARCH_DEFAULTS,
    ChannelTask,
    advance,
    is_complete,
    product_complete,
)


class ChannelWorkflowTests(unittest.TestCase):
    def test_smartstore_searches_all_registration_periods(self):
        self.assertEqual(SMARTSTORE_SEARCH_DEFAULTS["registration_period"], "all")
        self.assertEqual(
            SMARTSTORE_SEARCH_DEFAULTS["search_order"],
            ("product_number", "sku", "exact_product_name"),
        )

    def test_cannot_skip_save_and_reverification(self):
        task = ChannelTask("5308469", "smartstore", product_number="9365723140")
        with self.assertRaises(ValueError):
            advance(task, "reverified", evidence="reopened")

    def test_saved_is_not_complete(self):
        task = ChannelTask("5308469", "smartstore", "saved", "9365723140")
        self.assertFalse(is_complete(task))
        self.assertTrue(is_complete(advance(task, "reverified", evidence="reopened-and-read")))

    def test_both_channels_must_be_reverified(self):
        smartstore = ChannelTask("5308469", "smartstore", "reverified", "9365723140", "read-back")
        cafe24 = ChannelTask("5308469", "cafe24", "saved", "13252")
        self.assertFalse(product_complete([smartstore, cafe24]))
        cafe24 = advance(cafe24, "reverified", evidence="read-back")
        self.assertTrue(product_complete([smartstore, cafe24]))


if __name__ == "__main__":
    unittest.main()

