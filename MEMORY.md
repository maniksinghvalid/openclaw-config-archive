# MEMORY.md - Long-Term Memory

## Key Facts
- **Human:** Manik (PST timezone)
- **My name:** Jarvis 🎩
- **Born:** 2026-02-14 (Valentine's Day, ~2am UTC)

## Lessons Learned
- 2026-04-25: Daily Log Health & Self-Remediation Check completed. Log health is green. One error detected in `session_status` tool due to visibility restrictions (this is expected behavior in cron sessions and not an operational failure). No other errors or patterns were found.
- 2026-04-24: Daily Log Health & Self-Remediation Check completed. Log health is green. Zero system errors detected in the last 1000 lines of the active session log. No self-remediation actions were required.
- 2026-04-23: Daily Log Health & Self-Remediation Check completed. Log health is green. Zero system errors detected in the last 1000 lines of the active session log. No self-remediation actions were required.
- 2026-04-22: Daily Log Health & Self-Remediation Check completed. Log health is green. Detected 0 actual system errors; one session_status error noted from visibility restrictions (expected behavior in isolated cron session).
- 2026-04-21: Daily Log Health & Self-Remediation Check completed. Log health is green. Zero system errors detected in the last 1000 lines of the active session log.
- 2026-04-20: Daily Log Health & Self-Remediation Check completed. Log health is green. Zero system errors detected in the last 1000 lines of the active session log. No self-remediation actions were required.
- 2026-04-19: Daily Log Health & Self-Remediation Check completed. Log health is green. Zero system errors detected. One instance of `session_status` visibility error (expected behavior in isolated cron jobs). No self-remediation actions were required.
- 2026-04-18: Log health is green. Automated analysis of `d8778765-eae5-4fda-983a-1161dfcaaaaa.jsonl` (today's active session log) showed no critical system errors. Only one isolated `session_status` tool error was noted, which is non-impactful. The check-logs script is confirmed to be targeting the correct session log.
- 2026-04-17: Daily Log Health & Self-Remediation Check completed. Log health is green. Updated `check-logs.sh` to capture `isError:true` and `status:error` patterns from JSONL session logs for better detection.
- 2026-04-16: Daily Log Health & Self-Remediation Check completed. Log health is green. Detected 0 actual system errors; one session_status error noted from visibility restrictions (consistent with cron isolation).
- 2026-04-15: Daily Log Health & Self-Remediation Check completed. Log health is green. Detected 0 actual system errors; a single session_status error was due to visibility restrictions (expected behavior in cron context).
- 2026-04-14: Daily Log Health & Self-Remediation Check completed. Log health is green. Updated check-logs.sh to dynamically find the active session log file.
- 2026-04-13: Daily Log Health & Self-Remediation Check completed. Log health is green (0 system errors detected in recent session logs).
- 2026-04-12: Daily Log Health & Self-Remediation Check completed. Fixed script path to point to active session logs. Detected 0 real system errors; pattern matches were false positives from script review.
- 2026-04-11: Daily Log Health & Self-Remediation Check completed. Log health is green (0 errors detected).
- 2026-04-10: Daily Log Health & Self-Remediation Check completed. Log health is green (0 errors detected).
- 2026-04-09: Daily Log Health & Self-Remediation Check completed. Log health is green (0 errors detected).
- 2026-04-08: Daily Log Health & Self-Remediation Check completed. Log health is green (0 errors detected).
- 2026-04-07: Daily Log Health & Self-Remediation Check completed. Log health is green (0 errors detected).
- 2026-04-06: Daily Log Health & Self-Remediation Check completed. Log health is green (0 errors detected).
- 2026-04-05: Daily Log Health & Self-Remediation Check completed. Log health is green (0 errors detected).
- 2026-04-04: Daily Log Health & Self-Remediation Check completed. Log health is green (0 errors detected).
- 2026-04-03: Daily Log Health & Self-Remediation Check completed. Log health is green (1 exec failure, within limits).
- 2026-04-02: Daily Log Health & Self-Remediation Check ran successfully. No critical recurring error patterns detected (Log health is green).
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
