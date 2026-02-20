# Policy Quote Coding Dojo

Small Python 3 dojo codebase that intentionally demonstrates tight coupling and integration blast radius.

## Run tests

```bash
python -m unittest
```

## Current architecture (intentionally a bit wrong)

The core flow is implemented by a "God orchestrator" (`QuoteOrchestrator`) that directly coordinates:
- data retrieval from `Store`
- segmentation lookup from `SegmentService` (with fallback)
- pricing via `PricingEngine`
- audit formatting and recording via `AuditLog`
- email message formatting and sending via `NotificationService`

This is intentional so later changes have a visible impact area.

## Domain entities

- `Customer(customer_id, name)`
- `Policy(policy_id, customer_id, start_date, base_premium_cents)`
- `Quote(policy_id, customer_id, premium_cents)`

## Seed data

`seed_system()` creates and returns:
`(store, segment_service, pricing, notifications, audit, orchestrator)`

Seeded records:
- Customer `CUST-1` / Marelize (segment `GOLD`)
- Customer `CUST-2` / Michelle (segment `STANDARD` but configured to fail segment lookup)
- Policy `POL-1` for `CUST-1`, start `2023-01-01`, base premium `100_00`
- Policy `POL-2` for `CUST-2`, start `2025-01-01`, base premium `120_00`

## CHANGE REQUESTS (do not implement yet)

- Change 1: pricing now depends on segment (GOLD 10% discount) and policy age > 365 days (additional 5% discount)
- Change 2: notifications must be idempotent: key=(customer_id, policy_id, event_type='QUOTE_CREATED'); if duplicate, do not send and record audit event NOTIFICATION_SKIPPED reason=idempotent

Refactor goal: reduce integration blast radius by introducing a seam (`QuoteContext`/`PricingContext`) and moving responsibilities behind boundaries.
