# HEARTBEAT.md

# Auto-improvement heartbeat

When the agent wakes up, review recent mistakes or suboptimal outcomes from prior sessions and outline concrete improvements. Then:

- Run multiple sub-agents in parallel to handle related tasks concurrently (where safe and beneficial).
- Gather results and log lessons learned to MEMORY.md or a dedicated log file.
- Update a short action plan for the next run based on findings.

Note: If certain tasks must be serialized due to dependencies, parallelization should be gated and logged.

# Idle Heartbeat Check Rotation (every 30 min)

When nothing urgent needs attention, rotate through ONE of these per heartbeat (cycle every ~4h):

1. **Cron check** — Quick `ls -t /home/claw/.openclaw/cron/*.log 2>/dev/null | head -3` to verify recent cron jobs ran
2. **Sync check** — Verify last daily sync completed (check git log for today's commit)
3. **qmd index** — Run `qmd update` if stale (>24h since last index)
4. **Health log** — Quick tail of recent gateway logs for new errors

Keep it lightweight (<10s). If all clear, HEARTBEAT_OK.
