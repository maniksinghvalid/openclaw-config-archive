# Reddit Nightly — 2026-08-25

**Status: FAILED — data source down. No digest delivered.**

All 5 sanctioned fetches failed with exit code 1, each returning the identical error:

```
HTTP 404 fetching https://old.reddit.com/r/<subreddit>/<listing>.rss?...
```

- r/PersonalFinanceCanada (top/day) — 404
- r/dividendscanada (top/day) — 404
- r/CanadianInvestor (top/day) — 404
- r/ValueInvesting (top/day) — 404
- r/passive_income (top/day) — 404

Diagnostic: a plain `subreddit PersonalFinanceCanada` call (default `hot.rss`) also returned 404, confirming the failure is at the old.reddit.com RSS endpoint itself, not the script arguments.

**Decision:** No report posted to the group. Per anti-hallucination guardrails, no fabricated posts or YOUR BOOK matches were invented. A transparent short status was sent to the StockPortfolio group instead.

**Action item:** Retry on next scheduled run once old.reddit.com RSS recovers. If 404 persists, investigate whether the source has moved endpoints.
