# Implement Change 2: Idempotent Notifications

## Objective

Make notifications idempotent in the quote creation flow. The idempotency key is `(customer_id, policy_id, event_type="QUOTE_CREATED")`. If a duplicate notification would be sent:
- **Do NOT send** the notification
- **Record** an audit event with `event_type="NOTIFICATION_SKIPPED"` and `detail` containing `reason=idempotent`

## Context

<context>
<codebase-structure>
Python 3 project at the root directory with:
- `dojo/system.py` — all domain entities, services, and orchestration (207 lines)
- `tests/test_system.py` — unittest-based test suite (68 lines)
</codebase-structure>

<notification-service>
`NotificationService` (lines 113-118 of `dojo/system.py`) is a simple append-only list:
```python
class NotificationService:
    def __init__(self) -> None:
        self.sent_notifications: List[Notification] = []

    def send(self, notification: Notification) -> None:
        self.sent_notifications.append(notification)
```
It has no awareness of customer_id, policy_id, or event_type — it just stores `Notification(channel, message)`.
</notification-service>

<orchestrator-notification-flow>
In `QuoteOrchestrator.create_quote()` (lines 136-164), after creating the quote and recording the `QUOTE_CREATED` audit event, the orchestrator builds a message string and calls:
```python
self._notifications.send(Notification(channel="email", message=message))
```
The orchestrator has access to `customer.customer_id`, `policy.policy_id`, and the audit log (`self._audit`).
</orchestrator-notification-flow>

<audit-log>
`AuditLog` (lines 96-110) supports:
- `record(event_type, policy_id, customer_id, detail)` — appends an AuditEvent
- `find(event_type, policy_id, customer_id)` — returns matching events

The orchestrator already uses `self._audit` for recording `QUOTE_CREATED` events.
</audit-log>

<existing-tests>
Three tests in `tests/test_system.py`:
1. `test_quote_creation_gold_segment_with_age_discount` — POL-1, asserts 1 notification sent
2. `test_segment_fallback_on_failure` — POL-2, asserts 1 notification sent
3. `test_standard_segment_young_policy_no_discounts` — custom setup, asserts premium only
</existing-tests>
</context>

## Implementation Steps

<steps>
<step number="1" file="dojo/system.py">
Add idempotency tracking to `NotificationService`. Add a `_sent_keys: Set[Tuple[str, str, str]]` to track `(customer_id, policy_id, event_type)` tuples. Add a method `has_been_sent(customer_id: str, policy_id: str, event_type: str) -> bool` that checks this set, and update `send()` to accept and record the idempotency key. The `send()` signature should become:
```python
def send(self, notification: Notification, customer_id: str, policy_id: str, event_type: str) -> bool
```
It should:
- Check if `(customer_id, policy_id, event_type)` is already in `_sent_keys`
- If yes: return `False` (not sent)
- If no: add to `_sent_keys`, append notification, return `True`
</step>

<step number="2" file="dojo/system.py">
Update the notification call in `QuoteOrchestrator.create_quote()` (around line 162) to:
1. Call `self._notifications.send(notification, customer.customer_id, policy.policy_id, "QUOTE_CREATED")`
2. Check the return value
3. If `False` (duplicate), record an audit event: `self._audit.record("NOTIFICATION_SKIPPED", policy.policy_id, customer.customer_id, "reason=idempotent")`
</step>

<step number="3" file="tests/test_system.py">
Add a test `test_duplicate_quote_notification_is_idempotent`:
1. Use `seed_system()` to get the system
2. Call `orchestrator.create_quote("POL-1")` twice
3. Assert only 1 notification was sent (not 2)
4. Assert a `NOTIFICATION_SKIPPED` audit event exists for POL-1/CUST-1
5. Assert the NOTIFICATION_SKIPPED event detail contains `reason=idempotent`
</step>

<step number="4" file="tests/test_system.py">
Verify existing tests still pass — they all call `create_quote` only once per policy, so they should be unaffected. The `send()` signature change requires updating the call site in the orchestrator only (not in tests, since tests check `sent_notifications` list directly).
</step>
</steps>

## Verification

<verification>
Run the full test suite and confirm all tests pass:
```bash
python -m unittest -v
```

Expected: 4 tests pass (3 existing + 1 new idempotency test).
</verification>

## Constraints

<constraints>
- The idempotency check lives in `NotificationService`, not in the orchestrator — the orchestrator just reacts to the return value
- Keep the `Notification` dataclass unchanged (channel, message only) — the idempotency key is separate metadata
- The `NOTIFICATION_SKIPPED` audit event must have `detail` containing `reason=idempotent`
- Do not change the `QUOTE_CREATED` audit recording or pricing logic
- Maintain the existing test structure — add new tests, don't restructure existing ones
</constraints>
