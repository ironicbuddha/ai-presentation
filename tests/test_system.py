import unittest

from dojo.system import seed_system


class QuoteSystemTests(unittest.TestCase):
    def test_quote_creation_baseline(self) -> None:
        _, _, _, notifications, audit, orchestrator = seed_system()

        quote = orchestrator.create_quote("POL-1")

        self.assertEqual(100_00, quote.premium_cents)
        self.assertEqual(1, len(notifications.sent_notifications))

        events = audit.find("QUOTE_CREATED", "POL-1", "CUST-1")
        self.assertEqual(1, len(events))

    def test_segment_fallback_on_failure(self) -> None:
        _, _, _, notifications, audit, orchestrator = seed_system()

        quote = orchestrator.create_quote("POL-2")

        self.assertEqual(120_00, quote.premium_cents)

        events = audit.find("QUOTE_CREATED", "POL-2", "CUST-2")
        self.assertEqual(1, len(events))
        self.assertIn("segment=STANDARD", events[0].detail)

        self.assertEqual(1, len(notifications.sent_notifications))


if __name__ == "__main__":
    unittest.main()
