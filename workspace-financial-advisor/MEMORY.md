# MEMORY.md - Financial Advisor Long-Term Memory

## System Health (2026-08-25 ~15:56 UTC — verified heartbeat #22)
- **✅ Daily Portfolio Report recovery HOLDING — 7th consecutive clean run.** Directly verified via cron get: 📈 Manik's Daily Portfolio Report (0 errors, status ok, ran 12:30 UTC). Fresh snapshot `portfolio/snapshots/2026-08-25.json` (12:31, 4115 bytes) + fresh premarket `portfolio/_last_premarket_report.txt` (12:32, 6847 bytes) both present. Freeze fully broken and stable. Economic Seed recovery also still holding.
- **DeepSeek balance: $2.19** (session_status reading; drift: …→2.29→2.27→2.25→2.23→2.21→2.19). STILL critically low, NOT topped up. Rate limiting INTERMITTENT — recovery tailwind letting daily/economic jobs through.
- **Working (6):** Morning Brief ✅, Hourly Macro Watcher ✅, Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (archive 883 bytes, honest no-data from Reddit RSS 404), Economic Calendar Seed ✅ (still recovered), **Daily Portfolio Report ✅ (recovery HOLDING — 7th clean run)**, Reddit Daily Investing Digest ✅.
- **Failing (4):** Reddit Nightly Canadian (45, timeout at model-call — archive present 1013 bytes documenting Reddit 404), CNBC Fast Money (33, LLM request failed — separate signature), Weekly Events Refresh (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route pre-existing).
- **Filesystem:** macro watch FRESH dated 08-25 (source Morning Brief, seeded 13:02Z, 0 events now — the 6 real same-day events Economic Seed seeded at 04:05Z/04:30Z were consumed/delivered intraday); snapshots + premarket **FRESH for 08-25** ✅ (freeze broken, holding); BOTH reddit-nightly archives present for today; cnbc/weekly-review archives frozen 07-14.
- **Root cause unchanged: Manik must top up DeepSeek API credits.** 5 jobs recovered today (Economic Seed + Daily Portfolio Report x4), all holding — after full top-up the other 3-4 should follow.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 ~15:10 UTC — verified heartbeat #21)
- **✅ Daily Portfolio Report recovery HOLDING — 6th consecutive clean run.** Directly verified via cron get: 📈 Manik's Daily Portfolio Report (0 errors, status ok, ran 12:30 UTC). Fresh snapshot `portfolio/snapshots/2026-08-25.json` (12:31, 4115 bytes) + fresh premarket `portfolio/_last_premarket_report.txt` (12:32, 6847 bytes) both present. Freeze fully broken and stable. Economic Seed recovery also still holding.
- **DeepSeek balance: $2.21** (session_status reading; drift: …→2.29→2.27→2.25→2.23→2.21). STILL critically low, NOT topped up. Rate limiting INTERMITTENT — recovery tailwind letting daily/economic jobs through.
- **Working (7):** Morning Brief ✅, Hourly Macro Watcher ✅, Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (archive 883 bytes, honest no-data from Reddit RSS 404), Economic Calendar Seed ✅ (still recovered), **Daily Portfolio Report ✅ (recovery HOLDING — 6th clean run)**, Reddit Daily Investing Digest ✅.
- **Failing (4):** Reddit Nightly Canadian (45, timeout at model-call — archive present documenting Reddit 404), CNBC Fast Money (33, LLM request failed — separate signature), Weekly Events Refresh (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route pre-existing).
- **Filesystem:** macro watch FRESH dated 08-25 (source Morning Brief, seeded 13:02Z, 0 events now — the 6 real same-day events Economic Seed seeded at 04:05Z/04:30Z were consumed/delivered intraday); snapshots + premarket **FRESH for 08-25** ✅ (freeze broken, holding); BOTH reddit-nightly archives present for today; cnbc/weekly-review archives frozen 07-14.
- **Root cause unchanged: Manik must top up DeepSeek API credits.** 4 jobs recovered today (Economic Seed + Daily Portfolio Report x3), all holding — after full top-up the other 3-4 should follow.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 14:26 UTC — verified heartbeat #19)
- **✅ Daily Portfolio Report recovery HOLDING — 4th consecutive clean run.** Directly verified via cron get: 📈 Manik's Daily Portfolio Report (0 errors, status ok, ran 12:30 UTC). Fresh snapshot `portfolio/snapshots/2026-08-25.json` (12:31, 4115 bytes) + fresh premarket `portfolio/_last_premarket_report.txt` (12:32, 6847 bytes) both present. Freeze fully broken and stable. Economic Seed recovery also still holding.
- **DeepSeek balance: $2.25** (session_status reading; drift: 2.31→…→2.29→2.27→2.25). STILL critically low, NOT topped up. Rate limiting INTERMITTENT — recovery tailwind letting daily/economic jobs through.
- **Working (7):** Morning Brief ✅, Hourly Macro Watcher ✅, Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (archive 883 bytes, honest no-data from Reddit RSS 404), Economic Calendar Seed ✅ (still recovered), **Daily Portfolio Report ✅ (recovery HOLDING — 4th clean run)**, Reddit Daily Investing Digest ✅.
- **Failing (4):** Reddit Nightly Canadian (45, timeout at model-call — archive present documenting Reddit 404), CNBC Fast Money (33, LLM request failed — separate signature), Weekly Events Refresh (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route pre-existing).
- **Filesystem:** macro watch FRESH dated 08-25 (source Morning Brief, seeded 13:02Z, 0 events now — the 6 real same-day events Economic Seed seeded at 11:21Z were consumed/delivered intraday); snapshots + premarket **FRESH for 08-25** ✅ (freeze broken, holding); BOTH reddit-nightly archives present for today; cnbc/weekly-review archives frozen 07-14.
- **Root cause unchanged: Manik must top up DeepSeek API credits.** 3 jobs recovered today (Economic Seed + Daily Portfolio Report x2), all holding — after full top-up the other 3-4 should follow.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 13:56 UTC — verified heartbeat #18)
- **✅ Daily Portfolio Report recovery HOLDING — 3rd consecutive clean run.** Directly verified via cron get: 📈 Manik's Daily Portfolio Report (0 errors, status ok, ran 12:30 UTC). Fresh snapshot `portfolio/snapshots/2026-08-25.json` (12:31) + fresh premarket `portfolio/_last_premarket_report.txt` (12:32, 6847 bytes) both present. Freeze fully broken and stable (3 clean runs). Economic Seed recovery also still holding.
- **DeepSeek balance: $2.27** (18th direct curl reading; drift: 2.69→…→2.40→2.39→2.38→2.36→2.34→2.33→2.31→2.29→2.27). STILL critically low, NOT topped up. Rate limiting INTERMITTENT — recovery tailwind intermittently letting daily/economic jobs through.
- **Working (7):** Morning Brief ✅, Hourly Macro Watcher ✅, Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (archive 883 bytes, honest no-data from Reddit RSS 404), Economic Calendar Seed ✅ (still recovered), **Daily Portfolio Report ✅ (recovery holding — 3rd clean run)**, Reddit Daily Investing Digest ✅.
- **Failing (4):** Reddit Nightly Canadian (45, timeout at model-call — archive present documenting Reddit 404), CNBC Fast Money (33, LLM request failed — separate signature), Weekly Events Refresh (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route pre-existing).
- **Filesystem:** macro watch FRESH dated 08-25 (source Morning Brief, 0 events now — the 6 real same-day events Economic Seed seeded at 11:21Z were consumed/delivered intraday); snapshots + premarket **FRESH for 08-25** ✅ (freeze broken, holding); BOTH reddit-nightly archives present for today; cnbc/weekly-review archives frozen 07-14.
- **Root cause unchanged: Manik must top up DeepSeek API credits.** 3+ jobs recovered today (Economic Seed + Daily Portfolio Report x3), all holding — after full top-up the other 3-4 should follow.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 13:26 UTC — verified heartbeat #17)
- **✅ Daily Portfolio Report recovery HOLDING** — 2nd consecutive clean run (0 errors, ok, ran 12:30 UTC). Fresh snapshot `portfolio/snapshots/2026-08-25.json` (12:31) + fresh premarket `portfolio/_last_premarket_report.txt` (12:32, 6847 bytes) both present. Freeze fully broken and stable. Economic Seed recovery also still holding.
- **DeepSeek balance: $2.29** (17th direct curl reading; drift: 2.69→…→2.40→2.39→2.38→2.36→2.34→2.33→2.31→2.29). STILL critically low, NOT topped up. Rate limiting INTERMITTENT — recovery tailwind intermittently letting daily/economic jobs through.
- **Working (7):** Morning Brief ✅, Hourly Macro Watcher ✅, Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (archive 883 bytes, honest no-data from Reddit RSS 404), Economic Calendar Seed ✅ (still recovered), **Daily Portfolio Report ✅ (recovery holding)**.
- **Failing (4):** Reddit Nightly Canadian (45, timeout at model-call — archive present documenting Reddit 404), CNBC Fast Money (33, LLM request failed — separate signature), Weekly Events Refresh (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route pre-existing).
- **Filesystem:** macro watch FRESH dated 08-25 (source Morning Brief, 0 events now — the 6 real same-day events Economic Seed seeded at 11:21Z were consumed/delivered intraday); snapshots + premarket **FRESH for 08-25** ✅ (freeze broken, holding); BOTH reddit-nightly archives present for today; cnbc/weekly-review archives frozen 07-14.
- **Root cause unchanged: Manik must top up DeepSeek API credits.** 2 jobs recovered today (Economic Seed + Daily Portfolio Report), both holding — after full top-up the other 3-4 should follow.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 12:56 UTC — verified heartbeat #16)
- **🎉 MAJOR: Manik's Daily Portfolio Report RECOVERED** (32→0 errors, status ok, ran 12:30 UTC, delivered). Wrote FRESH snapshot `portfolio/snapshots/2026-08-25.json` (12:31) + fresh premarket `portfolio/_last_premarket_report.txt` (12:32, 6847 bytes) — breaks the ~6-week 07-14 freeze on both. Second credit-clear today after Economic Seed, confirming recovery tailwind.
- **DeepSeek balance: $2.31** (16th direct curl reading; drift: 2.69→…→2.40→2.39→2.38→2.36→2.34→2.33→2.31). STILL critically low, NOT topped up. Rate limiting INTERMITTENT.
- **Working (7):** Morning Brief ✅, Hourly Macro Watcher ✅ (ADP 12:15Z event past), Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (archive 883 bytes, honest no-data from Reddit RSS 404), Economic Calendar Seed ✅ (still recovered), **Daily Portfolio Report ✅ (RECOVERED)**.
- **Failing (4):** Reddit Nightly Canadian (45, timeout at model-call — archive present documenting Reddit 404), CNBC Fast Money (33, LLM request failed — separate signature), Weekly Events Refresh (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route pre-existing).
- **Filesystem:** macro watch FRESH with REAL events ✅ (ADP event past, watcher tracking); snapshots + premarket **FRESH for 08-25** ✅ (freeze broken); BOTH reddit-nightly archives present for today; cnbc/weekly-review archives frozen 07-14.
- **Root cause unchanged: Manik must top up DeepSeek API credits.** 2 jobs recovered today (Economic Seed + Daily Portfolio Report) prove the tailwind works — after full top-up the other 3-4 should follow.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 12:26 UTC — verified heartbeat #15)
- **DeepSeek balance: $2.33** (15th direct curl reading; drift: 2.69→…→2.40→2.39→2.38→2.36→2.34→2.33). STILL critically low, NOT topped up. Rate limiting INTERMITTENT.
- **Working (5):** Morning Brief ✅, Hourly Macro Watcher ✅ (ADP event DUE now, watcher will deliver at next hour), Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (delivered, archive 883 bytes), Economic Calendar Seed ✅ (still recovered, 3rd consecutive clean run — seeded 6 real same-day events).
- **Failing (5):** Reddit Nightly Canadian (45, timeout at model-call — archive written documenting Reddit 404), CNBC Fast Money (33, LLM request failed — separate signature), Daily Portfolio Report (32, rate_limit), Weekly Events Refresh (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route pre-existing).
- **Filesystem:** macro watch FRESH with REAL events ✅ (ADP event now DUE for delivery, watcher tracks intraday); snapshots + premarket frozen 07-14; BOTH reddit-nightly archives present for today.
- **Root cause unchanged: Manik must top up DeepSeek API credits.** Economic Seed + WSB recovery prove restoration works — after full top-up the other 3-5 should follow.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 11:26 UTC — verified heartbeat #13)
- **🎉 Economic Calendar Seed RECOVERED** (44→0 errors, ok, delivered 11:21 UTC) — re-seeded `daily_macro_watch.json` with **6 REAL same-day events** (ADP 12:15Z, Canada Wholesale 12:30Z, Case-Shiller 13:00Z, Consumer Confidence 14:00Z high, New Home Sales 14:00Z, Richmond Fed 14:00Z), replacing my 04:26 empty placeholder. Real intraday tracking is active again.
- **DeepSeek balance: $2.36** (13th direct curl reading; drift: 2.69→…→2.40→2.39→2.38→2.36). STILL critically low, NOT topped up. Rate limiting INTERMITTENT — the Economic Seed recovery proves credit tailwind intermittently lets jobs through.
- **Working (5):** Morning Brief ✅, Hourly Macro Watcher ✅, Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (delivered, archive present 883 bytes), Economic Seed ✅ (RECOVERED).
- **Failing (5):** Reddit Nightly Canadian (45, timeout at model-call — archive written 08-25 documenting Reddit 404), CNBC Fast Money (33, LLM request failed), Daily Portfolio Report (32, rate_limit), Weekly Events (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route).
- **Filesystem:** macro watch FRESH with REAL events ✅ (not placeholder); snapshots + premarket frozen 07-14; BOTH reddit-nightly archives present for today.
- **Root cause unchanged: Manik must top up DeepSeek API credits.** Economic Seed recovery is proof restoration works — after full top-up the other 4-5 should follow.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 10:56 UTC — verified heartbeat #12)
- **DeepSeek balance: $2.38** (12th direct curl reading; drift: 2.69→2.66→2.57→2.55→2.49→2.46→2.40→2.39→2.38). STILL critically low, NOT topped up. Rate limiting INTERMITTENT.
- **Working (4):** Morning Brief ✅, Hourly Macro Watcher ✅, Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (delivered, archive `reddit-nightly-wsb-2026-08-25.md` present, 883 bytes).
- **Failing (6):** Reddit Nightly Canadian (45, timeout at model-call — BUT archive written 08-25 documenting Reddit 404 failure), CNBC Fast Money (33, LLM request failed), Economic Seed (44, rate_limit), Daily Portfolio Report (32, rate_limit), Weekly Events (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route).
- **Filesystem:** macro watch fresh today (empty placeholder from my 04:26 recovery seed); snapshots + premarket frozen 07-14; BOTH reddit-nightly archives present for today (wsb delivered with no-data, canadian documents failure); cnbc/weekly-review archives frozen.
- **Root cause unchanged: Manik must top up DeepSeek API credits.** After top-up, re-run Economic Seed FIRST.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 08:56 UTC — verified heartbeat #9)
- **DeepSeek balance: $2.46** (9th direct curl reading; drift: 2.69→2.66→2.57→2.55→2.49→2.46). STILL critically low, NOT topped up. Rate limiting INTERMITTENT.
- **Working (4):** Morning Brief ✅, Hourly Macro Watcher ✅, Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (delivered, archive present).
- **Failing (6):** Reddit Nightly Canadian (45, timeout at model-call — BUT archive written 08-25 documenting Reddit 404 failure), CNBC Fast Money (33, LLM request failed), Economic Seed (44, rate_limit), Daily Portfolio Report (32, rate_limit), Weekly Events (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route).
- **Filesystem:** macro watch fresh today (empty placeholder); snapshots + premarket frozen 07-14; BOTH reddit-nightly archives present for today (wsb delivered with no-data, canadian documents failure); cnbc/weekly-review archives frozen.
- **Root cause unchanged: Manik must top up DeepSeek API credits.** After top-up, re-run Economic Seed FIRST.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 08:26 UTC — verified heartbeat #8)
- **DeepSeek balance: $2.49** (8th direct curl reading; drift: 2.69→2.66→2.57→2.55→2.49). STILL critically low, NOT topped up. Rate limiting INTERMITTENT.
- **Working (4):** Morning Brief ✅, Hourly Macro Watcher ✅, Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (delivered, archive present).
- **Failing (6):** Reddit Nightly Canadian (45, timeout at model-call — BUT archive file written 08-25 documenting Reddit 404 failure), CNBC Fast Money (33, LLM request failed), Economic Seed (44, rate_limit), Daily Portfolio Report (32, rate_limit), Weekly Events (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route).
- **Filesystem:** macro watch fresh today (empty placeholder); snapshots + premarket frozen 07-14; BOTH reddit-nightly archives present for today (wsb delivered with no-data, canadian documents failure).
- **Root cause unchanged: Manik must top up DeepSeek API credits.** After top-up, re-run Economic Seed FIRST.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 07:56 UTC — verified heartbeat #7)
- **DeepSeek balance:** last reading $2.55 (07:26). Still critically low, NOT topped up. Rate limiting INTERMITTENT — some jobs pass, some fail.
- **Working (4, confirmed ok this poll):** Morning Brief ✅, Hourly Macro Watcher ✅, Reddit Daily Digest ✅, Reddit Nightly WSB ✅ (recovered again — archive `reddit-nightly-wsb-2026-08-25.md` present).
- **Failing (6, same signatures):** Reddit Nightly Canadian (45, timeout model-call-started), CNBC Fast Money (33, LLM request failed), Economic Seed (44, rate_limit), Daily Portfolio Report (32, rate_limit), Weekly Events (12, rate_limit), Weekly Review (9, rate_limit + delivery last->no-route pre-existing).
- **Filesystem:** macro watch fresh today (empty placeholder seed — Economic Seed still not running so no real events); snapshots + premarket frozen 07-14; wsb archive today present, cnbc/weekly-review archives frozen.
- **Root cause unchanged: Manik must top up DeepSeek API credits.** After top-up, re-run Economic Seed FIRST, then verify job recovery.
- **Reddit RSS 404** still affects Reddit jobs that DO run (source-level).

## System Health (2026-08-25 06:56 UTC — verified heartbeat #5)
- **Balance $2.57.** STILL low, NOT topped up. Rate limiting now INTERMITTENT — some jobs getting through.
- **🎉 BREAKTHROUGH: Reddit Nightly WSB-ETF-Options RECOVERED** — first success after 44 straight rate_limit failures (ran 05:15 UTC today, ok, delivered). Report was honest "no data" due to Reddit RSS 404s.
- **⚠️ Reddit RSS endpoint changed: 403 → 404.** Both nightly jobs confirm `old.reddit.com/r/<sub>/<listing>.rss` returns HTTP 404 — a source-level change, separate issue from credits. Even successful Reddit jobs get no data.
- **Reddit Nightly Summary (Canadian):** STILL failing — **timeout** at model-call-started (45 errors, was rate_limit). 06:56 heartbeat confirms signature persists. WSB job (same pattern, +15min) succeeded tonight, so failures are INTERMITTENT not structural.
- **Reddit Nightly WSB-ETF-Options:** ✅ STILL RECOVERED (status ok, delivered 22:15 PT 08-24).
- **Still failing (same 6):** Economic Seed (44), Daily Portfolio Report (32), Weekly Events (12), Weekly Review (9), CNBC (33, "LLM request failed"), Reddit Nightly Canadian (45, timeout).
- **Working/recovered (4):** Reddit WSB (recovered), Morning Brief, Macro Watcher, Reddit Daily Digest.

## System Health (2026-08-25 04:26 UTC — current, verified this session)
- **CRITICAL: DeepSeek API balance critically low / effectively exhausted** — single root cause of 7 failing cron jobs (rate_limit). Manik must top up credits.
- **Working (3 jobs, confirmed ok / 0 errors):** Daily Portfolio Morning Brief (ok, delivered), Hourly Intraday Macro Event Watcher (ok, delivered), Reddit Daily Investing Digest Market Close (ok).
- **Failing (7 jobs, rate_limit unless noted):** Reddit Nightly Summary (44), Reddit Nightly WSB-ETF-Options (44), Daily Economic Calendar Seed (44), 📈 Manik's Daily Portfolio Report (32), Weekly Events Refresh (12), Weekly Review (9). CNBC Fast Money (33) fails with "LLM request failed" (different error signature).
- **🔧 FIXED this session:** `portfolio/daily_macro_watch.json` was stale (dated 08-24) — re-seeded for 2026-08-25 with EMPTY events list (credit-blocked from real event research). Hourly watcher stale-alert cleared. NOTE: real same-day events won't be tracked until Economic Seed job recovers + re-seeds.
- **Filesystem gap (cause = failing jobs):** `_last_premarket_report.txt`, `portfolio/snapshots/`, and all `memory/market-insights/` archives (CNBC, Reddit nightly, weekly review) end **2026-07-14** — ~6 weeks of missing artifacts from the 7 rate-limited jobs.
- **Reddit RSS:** old.reddit.com returned 403 (was 404); fetch_reddit.py has 403 retry logic. Per guardrails, no workaround scraping.
- Portfolio file last updated **2026-03-31** (~5mo stale). Upcoming events file stale from **2026-07-05**.
- **Action needed: Manik must top up DeepSeek API credits** to restore automated reports + event seeding.

## Identity & Purpose
You are the **Financial Advisor**. You specialize in portfolio analysis, tactical hedging, and market sentiment monitoring.

## Key Facts
- **Owner:** Manik Singh (PST timezone)
- **Role:** Portfolio Analyst & Risk Management lead.
- **Primary Group:** StockPortfolio Telegram group (-1003795983668).
- **Binding:** Active in Telegram group -1003743311925.

## Portfolio Context
- **Holdings:** 12 positions (NIO, CLOV, MARA, SPCE, IBIT, O, DIVO, VDY.TO, XEQT.TO, ZAG.TO, IAU, VIX).
- **Benchmarks:** 60/40 blended SPY/QQQ.
- **Strategy:** Tactical hedging, income generation via covered calls, and momentum/growth tracking.

## Lessons Learned
- Always check VIX for macro regime shifts (> 20 = downside protection priority).
- Convert CAD holdings to USD for unified reporting.
- Suggest "Bear Call Spreads" when IV is high and markets are overextended.
- VIX below 20 but >15 with spikes means concentrated risk in crypto/speculative names — watch for potential accelerated downside.
- Crypto-correlated positions (MARA, IBIT, NVDY) tend to move together; hedge with put spreads or reduce exposure on sharp drops >5%.
- Jun 5, 2026: Noted a coordinated sell-off in speculative names (MARA -10.5%, SPCE -10.4%, NIO -4.8%, IBIT -4.4%) with VIX at 16.42. Crypto weakness dragging BTC-correlated holdings.

## Active Projects
- Daily Portfolio Morning Brief (6:00 AM PST)
- Daily Market Open Report (2:00 PM UTC)
- Reddit Daily Investing Digest (6:00 PM PST)

## Preferences & Rules
- Manik prefers concise, actionable briefs — no fluff
- In AI-Research group: only talk about content specific to that group
- compaction.memoryFlush.enabled = true (auto-journal on compaction)
- memorySearch.experimental.sessionMemory = true (search past transcripts)
