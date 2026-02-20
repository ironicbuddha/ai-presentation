import unittest
from datetime import date, timedelta

from dojo.system import (
    Customer,
    Policy,
    Store,
    SegmentService,
    PricingEngine,
    NotificationService,
    AuditLog,
    QuoteOrchestrator,
    seed_system,
)


class QuoteSystemTests(unittest.TestCase):
    def test_quote_creation_gold_segment_with_age_discount(self) -> None:
        _, _, _, notifications, audit, orchestrator = seed_system()

        quote = orchestrator.create_quote("POL-1")

        # GOLD: 10% off 100_00 = 90_00, then age > 365 days: 5% off 90_00 = 85_50
        self.assertEqual(85_50, quote.premium_cents)
        self.assertEqual(1, len(notifications.sent_notifications))

        events = audit.find("QUOTE_CREATED", "POL-1", "CUST-1")
        self.assertEqual(1, len(events))

    def test_segment_fallback_on_failure(self) -> None:
        _, _, _, notifications, audit, orchestrator = seed_system()

        quote = orchestrator.create_quote("POL-2")

        # STANDARD (fallback): no segment discount, age > 365 days: 5% off 120_00 = 114_00
        self.assertEqual(114_00, quote.premium_cents)

        events = audit.find("QUOTE_CREATED", "POL-2", "CUST-2")
        self.assertEqual(1, len(events))
        self.assertIn("segment=STANDARD", events[0].detail)

        self.assertEqual(1, len(notifications.sent_notifications))

    def test_standard_segment_young_policy_no_discounts(self) -> None:
        store = Store()
        store.add_customer(Customer(customer_id="C-NEW", name="Test"))
        store.add_policy(
            Policy(
                policy_id="P-NEW",
                customer_id="C-NEW",
                start_date=date.today() - timedelta(days=100),
                base_premium_cents=200_00,
            )
        )
        segment_service = SegmentService(segments={"C-NEW": "STANDARD"})
        pricing = PricingEngine()
        notifications = NotificationService()
        audit = AuditLog()
        orchestrator = QuoteOrchestrator(store, segment_service, pricing, notifications, audit)

        quote = orchestrator.create_quote("P-NEW")

        # STANDARD segment + age <= 365 days: no discounts
        self.assertEqual(200_00, quote.premium_cents)


    def test_duplicate_quote_notification_is_idempotent(self) -> None:
        _, _, _, notifications, audit, orchestrator = seed_system()

        orchestrator.create_quote("POL-1")
        orchestrator.create_quote("POL-1")

        self.assertEqual(1, len(notifications.sent_notifications))

        skipped = audit.find("NOTIFICATION_SKIPPED", "POL-1", "CUST-1")
        self.assertEqual(1, len(skipped))
        self.assertIn("reason=idempotent", skipped[0].detail)


if __name__ == "__main__":
    unittest.main()
