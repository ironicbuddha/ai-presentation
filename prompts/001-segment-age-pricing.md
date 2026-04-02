<objective>
Implement segment-based and policy-age-based pricing discounts in the Policy Quote Coding Dojo.

Currently, `PricingEngine.price()` returns `base_premium_cents` unchanged. After this change, pricing must apply two sequential discounts:
1. **Segment discount**: GOLD customers receive a 10% discount
2. **Age discount**: Policies older than 365 days receive an additional 5% discount

Discounts are applied in order: segment first, then age on the already-discounted amount.
</objective>

<context>
This is a small Python 3 dojo codebase demonstrating tight coupling via a "God orchestrator" pattern. The codebase lives in two files:

- `./dojo/system.py` — all domain entities, services, and orchestration
- `./tests/test_system.py` — unittest-based test suite

Read both files thoroughly before making any changes. Understand the full flow of `QuoteOrchestrator.create_quote()` and how data flows between components.

Key observations to verify when reading:
- `PricingEngine.price()` currently only accepts `policy` — it has no awareness of segment or date
- `QuoteOrchestrator.create_quote()` already fetches `segment` from `SegmentService` but only uses it in audit/notification strings, not pricing
- Two helper functions already exist but are unused: `apply_percent_discount()` and `policy_age_in_days()`
- `policy_age_in_days()` defaults to `date.today()` when no `as_of` parameter is given
</context>

<requirements>
1. **Modify `PricingEngine.price()`** to accept segment and an optional `as_of` date:
   - If segment is `"GOLD"`, apply a 10% discount using the existing `apply_percent_discount()` helper
   - If `policy_age_in_days(policy.start_date, as_of)` exceeds 365, apply an additional 5% discount using the same helper
   - Apply segment discount first, then age discount on the result
   - Return the final discounted amount as an integer (cents)

2. **Update `QuoteOrchestrator.create_quote()`** to pass the resolved `segment` to `self._pricing.price()`. The orchestrator already has `segment` in scope — just thread it through to the pricing call.

3. **Update existing tests** to reflect new expected premiums. Because `policy_age_in_days` uses `date.today()` by default, tests will produce different results depending on when they run. To make tests deterministic, use `unittest.mock.patch` to freeze `date.today()` to `2026-02-20` in each test that exercises pricing.

4. **Add new test cases** covering all four discount scenarios:
   - Both discounts (GOLD + age > 365): POL-1 → expected 8550 cents
   - Segment only (GOLD + age ≤ 365): Requires a test-local GOLD policy with recent start date
   - Age only (non-GOLD + age > 365): POL-2 → expected 11400 cents
   - No discounts (non-GOLD + age ≤ 365): Requires a test-local STANDARD policy with recent start date
</requirements>

<constraints>
- Do NOT create new files. All changes go in `./dojo/system.py` and `./tests/test_system.py`.
- Do NOT modify the existing helper functions `apply_percent_discount()` or `policy_age_in_days()` — they are already correct for this use case.
- Do NOT change the `Quote` dataclass, seed data, or any service other than `PricingEngine`.
- Keep the orchestrator's audit and notification behavior unchanged — segment must still appear in audit detail and notification message strings exactly as before.
- Use `unittest.mock.patch` to freeze dates in tests rather than adding `as_of` parameters to `create_quote()`, because threading `as_of` through the orchestrator would expand the change scope unnecessarily. The `as_of` parameter on `PricingEngine.price()` is sufficient for direct unit testing of the engine, while integration tests through the orchestrator should mock `date.today()`.
</constraints>

<implementation>
Follow these steps in order:

1. Read `./dojo/system.py` and `./tests/test_system.py` completely
2. Modify `PricingEngine.price()` signature and body — add `segment: str` and `as_of: Optional[date] = None` parameters, implement discount logic using existing helpers
3. Update the pricing call in `QuoteOrchestrator.create_quote()` to pass `segment`
4. Update existing test assertions with correct expected values (freeze date to 2026-02-20)
5. Add new test methods for all four discount combinations
6. Run `python -m unittest` to verify all tests pass
</implementation>

<verification>
Run the test suite and confirm:

```bash
python -m unittest -v
```

All tests must pass. Specifically verify:
- POL-1 (GOLD, started 2023-01-01, as_of 2026-02-20): 10000 → 9000 (10% GOLD) → 8550 (5% age) = **8550 cents**
- POL-2 (STANDARD fallback, started 2025-01-01, as_of 2026-02-20): 12000 → 12000 (no segment discount) → 11400 (5% age, 416 days > 365) = **11400 cents**
- Audit events still contain `segment=GOLD` / `segment=STANDARD` in their detail strings
- Notifications still contain segment and premium information
</verification>

<success_criteria>
- `python -m unittest` exits with 0 failures, 0 errors
- At least 6 test methods exist (2 original updated + 4 new scenario tests)
- `PricingEngine.price()` uses both `apply_percent_discount()` and `policy_age_in_days()` helpers
- No new files created
- Existing audit and notification behavior preserved
</success_criteria>
