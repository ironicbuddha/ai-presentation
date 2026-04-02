# Meta-Prompt: Implement Change 1 — Segment & Age-Based Pricing

## Objective

Modify the Policy Quote Coding Dojo so that pricing depends on:
1. **Segment discount**: GOLD customers get a 10% discount
2. **Policy age discount**: Policies older than 365 days get an additional 5% discount

Discounts are applied sequentially (segment first, then age).

## Context

### Codebase
- Single module: `dojo/system.py`
- Tests: `tests/test_system.py`
- Run tests: `python -m unittest`

### Current State
- `PricingEngine.price(policy)` returns `policy.base_premium_cents` unchanged — it ignores segment and policy age
- `QuoteOrchestrator.create_quote()` fetches segment from `SegmentService` but only uses it for audit/notification strings — it does NOT pass segment to pricing
- Two unused helper functions already exist:
  - `apply_percent_discount(amount_cents, percent)` — applies a percentage discount to a cent amount
  - `policy_age_in_days(start_date, as_of)` — returns days between start_date and as_of (defaults to today)

### Seed Data
| Policy | Customer | Segment | Start Date | Base Premium |
|--------|----------|---------|------------|-------------|
| POL-1 | CUST-1 (Marelize) | GOLD | 2023-01-01 | 10000 cents |
| POL-2 | CUST-2 (Michelle) | STANDARD (fallback) | 2025-01-01 | 12000 cents |

### Expected Pricing After Change (as_of=2026-02-20)
- **POL-1**: GOLD (10% off) → 9000, age=1147 days >365 (5% off) → 8550 cents
- **POL-2**: STANDARD (no segment discount), age=416 days >365 (5% off) → 11400 cents

## Implementation Steps

### Step 1: Modify `PricingEngine.price()` signature and logic

Change the method signature to accept segment and policy age:

```python
def price(self, policy: Policy, segment: str, as_of: Optional[date] = None) -> int:
    amount = policy.base_premium_cents
    if segment == "GOLD":
        amount = apply_percent_discount(amount, 10)
    if policy_age_in_days(policy.start_date, as_of) > 365:
        amount = apply_percent_discount(amount, 5)
    return amount
```

### Step 2: Update `QuoteOrchestrator.create_quote()` to pass segment to pricing

Change the pricing call from:
```python
premium_cents = self._pricing.price(policy)
```
to:
```python
premium_cents = self._pricing.price(policy, segment)
```

### Step 3: Update existing tests

The existing tests assert old premium values. Update them:
- `test_quote_creation_baseline`: POL-1 premium changes from `100_00` to `85_50` (GOLD + age discount, assuming test runs after 2024-01-01)
- `test_segment_fallback_on_failure`: POL-2 premium changes from `120_00` to `114_00` (no segment discount, but age discount applies if test runs after 2026-01-01)

**Important**: Because `policy_age_in_days` uses `date.today()` by default, test values depend on when the test runs. To make tests deterministic, pass an explicit `as_of` date. This requires either:
- (a) Adding `as_of` as a parameter to `create_quote()` and threading it through, OR
- (b) Using `unittest.mock.patch` to freeze `date.today()`

Option (b) is less invasive. Use `unittest.mock.patch` to freeze the date to `2026-02-20`.

### Step 4: Add new test cases

Add tests that verify:
1. **GOLD segment discount only** (policy age ≤ 365 days) — create a test with a recent GOLD policy
2. **Age discount only** (non-GOLD segment, age > 365) — POL-2 with frozen date after 2026-01-01
3. **Both discounts** (GOLD + age > 365) — POL-1 with frozen date
4. **No discounts** (non-GOLD, age ≤ 365) — create a fresh STANDARD policy

## Verification Criteria

- [ ] `python -m unittest` passes with all tests green
- [ ] POL-1 with as_of=2026-02-20 produces premium of 8550 cents
- [ ] POL-2 with as_of=2026-02-20 produces premium of 11400 cents
- [ ] Existing audit and notification behavior is unchanged (segment still appears in audit detail and notification message)
- [ ] No new files created — all changes in `dojo/system.py` and `tests/test_system.py`
