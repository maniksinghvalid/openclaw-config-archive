# Jarvis Self-Improvement Plan (May 2026)

## 1. High-Signal Heartbeats
**Goal:** Stop returning repetitive `HEARTBEAT_OK` without action.
- **Action:** Update `scripts/heartbeat-check.sh` (or create it) to handle the rotation defined in `HEARTBEAT.md`.
- **Action:** Maintain `memory/heartbeat-state.json` to track last check times.
- **Success Metric:** 90% reduction in "Idle Heartbeat" noise; heartbeats only notify on state changes or scheduled tasks.

## 2. Automated Session Recap (The "Journaling Fix")
**Goal:** Close the 20-day journaling gap and ensure continuity.
- **Action:** Create a post-session hook or routine that appends a 3-bullet summary to `memory/$(date +%Y-%m-%d).md` after any turn with >3 tool calls.
- **Action:** At 23:55 UTC daily, a cron job will summarize these session snippets into a clean daily journal entry.
- **Success Metric:** No gaps in `memory/` files for more than 24 hours.

## 3. Proactive Self-Repair (Tooling Hygiene)
**Goal:** Proactively fix common minor friction points.
- **Action:** Weekly "Hygiene" sub-agent run (Sunday 00:00 UTC) to:
    - Update `qmd` index for all managed folders.
    - Prune temp files and `.bak` files older than 7 days (outside protected sync dirs).
    - Validate `openclaw.json` against schema.
- **Success Metric:** Zero "failed to index" or "outdated schema" errors.

---
*Plan created by Jarvis on 2026-05-19 per request by Manik.*
