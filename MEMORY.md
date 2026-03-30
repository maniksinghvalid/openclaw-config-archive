# MEMORY.md - Long-Term Memory

## Key Facts
- **Human:** Manik (PST timezone)
- **My name:** Jarvis 🎩
- **Born:** 2026-02-14 (Valentine's Day, ~2am UTC)

## Lessons Learned
- 2026-03-20: MEMORY.md and daily memory files were never created — memory_search returned nothing. Fix: create MEMORY.md and start daily journaling.
- 2026-03-20: Daily Portfolio Morning Brief cron job failed repeatedly (Mar 6–19) due to openrouter/auto model returning errors before producing output. Fix: pinned cron to flash (Gemini) model.
- 2026-03-20: Brave Search API free tier hits rate limits when fetching 12+ stock prices sequentially. Fix: switching to Yahoo Finance for price data.
- 2026-03-20: qmd index may go stale — run `qmd update` periodically.
- 2026-03-22: Sample heartbeat run revealed MEMORY.md and daily memory files were missing. Addressed by creating MEMORY.md and updating qmd index. Need to establish daily journaling.

## Active Projects

## Preferences & Rules
- Manik prefers concise, actionable briefs — no fluff
- In AI-Research group: only talk about content specific to that group
- compaction.memoryFlush.enabled = true (auto-journal on compaction)
- memorySearch.experimental.sessionMemory = true (search past transcripts)
