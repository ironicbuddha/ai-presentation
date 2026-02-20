# Implement Change 1: Segment & Age-Based Pricing Discounts

## Objective

Modify the Policy Quote Coding Dojo so that pricing depends on customer segment and policy age:
- **GOLD segment**: 10% discount on base premium
- **Policy age > 365 days**: additional 5% discount (applied after segment discount)

## Context

<context>
<codebase-structure>
This is a small Python 3 project with two source files:
- `dojo/system.py` — all domain entities, services, and orchestration
- `tests/test_system.py` — unittest-based test suite
</codebase-structure>

<current-pricing>
`PricingEngine.price(policy)` at line 76-78 of `dojo/system.py` currently returns `policy.base_premium_cents` unchanged. It takes only a `Policy` object and has no awareness of customer segment.
</current-pricing>

<existing-helpers>
Two helper functions exist at lines 82-88 of `dojo/system.py` but are intentionally unused:
- `apply_percent_discount(amount_cents: int, percent: int) -> int` — applies percentage discount using integer arithmetic
- `policy_age_in_days(start_date: date, as_of: Optional[date] = None) -> int` — calculates days since policy start date
</existing-helpers>

<orchestrator-flow>
`QuoteOrchestrator.create_quote(policy_id)` at line 131-159:
1. Fetches Policy and Customer from Store
2. Resolves segment via SegmentService (with STANDARD fallback on error)
3. Calls `self._pricing.price(policy)` — segment is already available but NOT passed
4. Creates Quote, records audit event, sends notification
</orchestrator-flow>

<seed-data>
- CUST-1 "Marelize": segment=GOLD, POL-1 start_date=2023-01-01, base_premium=100_00
- CUST-2 "Michelle": segment=STANDARD (but configured to fail lookup → fallback STANDARD), POL-2 start_date=2025-01-01, base_premium=120_00
</seed-data>

<existing-tests>
Two tests in `tests/test_system.py`:
1. `test_quote_creation_baseline` — POL-1, asserts premium=100_00
2. `test_segment_fallback_on_failure` — POL-2, asserts premium=120_00, segment=STANDARD in audit
</existing-tests>
</context>

## Implementation Steps

<steps>
<step number="1" file="dojo/system.py" lines="76-78">
Update `PricingEngine.price()` to accept a `segment: str` parameter and apply discounts:
- If segment is "GOLD", apply 10% discount using `apply_percent_discount`
- If `policy_age_in_days(policy.start_date)` > 365, apply 5% discount using `apply_percent_discount`
- Discounts stack sequentially (segment first, then age)
</step>

<step number="2" file="dojo/system.py" line="140">
Update the call in `QuoteOrchestrator.create_quote()` from `self._pricing.price(policy)` to `self._pricing.price(policy, segment)`. The `segment` variable is already resolved at lines 136-138.
</step>

<step number="3" file="tests/test_system.py">
Update existing test assertions to reflect new pricing:
- `test_quote_creation_baseline` (POL-1): GOLD 10% off 100_00 = 90_00, age discount 5% off 90_00 = 85_50. Update expected to 85_50.
- `test_segment_fallback_on_failure` (POL-2): STANDARD no segment discount, age > 365 days so 5% off 120_00 = 114_00. Update expected to 114_00.
</step>

<step number="4" file="tests/test_system.py">
Add a new test `test_standard_segment_young_policy_no_discounts` that creates a fresh system with a policy whose start_date is less than 365 days ago and STANDARD segment, verifying that no discounts are applied and premium equals base_premium_cents.
</step>
</steps>

## Verification

<verification>
Run the full test suite and confirm all tests pass:
```bash
python -m unittest -v
```

Expected results:
- `test_quote_creation_baseline` (or renamed): premium = 85_50
- `test_segment_fallback_on_failure`: premium = 114_00
- New no-discount test: premium = base_premium unchanged
</verification>

## Constraints

<constraints>
- Use the existing `apply_percent_discount` and `policy_age_in_days` helper functions — do not reimplement discount logic
- Keep changes minimal: only modify `PricingEngine.price()`, its call site in the orchestrator, and tests
- Do not refactor the orchestrator architecture (that is a separate goal)
- Maintain integer arithmetic throughout (cents, no floats)
</constraints>
