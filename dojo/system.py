from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Set, Tuple


@dataclass(frozen=True)
class Customer:
    customer_id: str
    name: str


@dataclass(frozen=True)
class Policy:
    policy_id: str
    customer_id: str
    start_date: date
    base_premium_cents: int


@dataclass(frozen=True)
class Quote:
    policy_id: str
    customer_id: str
    premium_cents: int


@dataclass(frozen=True)
class Notification:
    channel: str
    message: str


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    policy_id: str
    customer_id: str
    detail: str


class Store:
    def __init__(self) -> None:
        self._customers: Dict[str, Customer] = {}
        self._policies: Dict[str, Policy] = {}

    def add_customer(self, customer: Customer) -> None:
        self._customers[customer.customer_id] = customer

    def add_policy(self, policy: Policy) -> None:
        self._policies[policy.policy_id] = policy

    def get_customer(self, customer_id: str) -> Customer:
        return self._customers[customer_id]

    def get_policy(self, policy_id: str) -> Policy:
        return self._policies[policy_id]


class SegmentServiceError(Exception):
    pass


class SegmentService:
    def __init__(self, segments: Dict[str, str], failing_customer_ids: Optional[Set[str]] = None) -> None:
        self._segments = dict(segments)
        self._failing_customer_ids = set(failing_customer_ids or set())

    def get_segment(self, customer_id: str) -> str:
        if customer_id in self._failing_customer_ids:
            raise SegmentServiceError(f"segment lookup failed for customer {customer_id}")
        return self._segments.get(customer_id, "STANDARD")


class PricingEngine:
    def price(self, policy: Policy) -> int:
        return policy.base_premium_cents


# Helpers intentionally not used yet by pricing; change requests will make them relevant.
def apply_percent_discount(amount_cents: int, percent: int) -> int:
    return amount_cents - (amount_cents * percent // 100)


def policy_age_in_days(start_date: date, as_of: Optional[date] = None) -> int:
    effective_date = as_of or date.today()
    return (effective_date - start_date).days


class AuditLog:
    def __init__(self) -> None:
        self._events: List[AuditEvent] = []

    def record(self, event_type: str, policy_id: str, customer_id: str, detail: str) -> None:
        self._events.append(AuditEvent(event_type, policy_id, customer_id, detail))

    def find(self, event_type: str, policy_id: str, customer_id: str) -> List[AuditEvent]:
        return [
            event
            for event in self._events
            if event.event_type == event_type
            and event.policy_id == policy_id
            and event.customer_id == customer_id
        ]


class NotificationService:
    def __init__(self) -> None:
        self.sent_notifications: List[Notification] = []

    def send(self, notification: Notification) -> None:
        self.sent_notifications.append(notification)


class QuoteOrchestrator:
    def __init__(
        self,
        store: Store,
        segment_service: SegmentService,
        pricing: PricingEngine,
        notifications: NotificationService,
        audit: AuditLog,
    ) -> None:
        self._store = store
        self._segment_service = segment_service
        self._pricing = pricing
        self._notifications = notifications
        self._audit = audit

    def create_quote(self, policy_id: str) -> Quote:
        policy = self._store.get_policy(policy_id)
        customer = self._store.get_customer(policy.customer_id)

        try:
            segment = self._segment_service.get_segment(customer.customer_id)
        except SegmentServiceError:
            segment = "STANDARD"

        premium_cents = self._pricing.price(policy)
        quote = Quote(policy.policy_id, customer.customer_id, premium_cents)

        detail = "segment=" + segment + ";premium_cents=" + str(premium_cents)
        self._audit.record("QUOTE_CREATED", policy.policy_id, customer.customer_id, detail)

        message = (
            "Quote created for "
            + customer.name
            + " (policy="
            + policy.policy_id
            + ", segment="
            + segment
            + ", premium_cents="
            + str(premium_cents)
            + ")"
        )
        self._notifications.send(Notification(channel="email", message=message))

        return quote


def seed_system() -> Tuple[
    Store,
    SegmentService,
    PricingEngine,
    NotificationService,
    AuditLog,
    QuoteOrchestrator,
]:
    store = Store()

    cust_1 = Customer(customer_id="CUST-1", name="Marelize")
    cust_2 = Customer(customer_id="CUST-2", name="Michelle")
    store.add_customer(cust_1)
    store.add_customer(cust_2)

    pol_1 = Policy(
        policy_id="POL-1",
        customer_id="CUST-1",
        start_date=date(2023, 1, 1),
        base_premium_cents=100_00,
    )
    pol_2 = Policy(
        policy_id="POL-2",
        customer_id="CUST-2",
        start_date=date(2025, 1, 1),
        base_premium_cents=120_00,
    )
    store.add_policy(pol_1)
    store.add_policy(pol_2)

    segment_service = SegmentService(
        segments={"CUST-1": "GOLD", "CUST-2": "STANDARD"},
        failing_customer_ids={"CUST-2"},
    )
    pricing = PricingEngine()
    notifications = NotificationService()
    audit = AuditLog()
    orchestrator = QuoteOrchestrator(store, segment_service, pricing, notifications, audit)

    return store, segment_service, pricing, notifications, audit, orchestrator
