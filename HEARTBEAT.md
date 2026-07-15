# HEARTBEAT.md

# Auto-improvement heartbeat

When the agent wakes up, review recent mistakes or suboptimal outcomes from prior sessions and outline concrete improvements. Then:

- Run multiple sub-agents in parallel to handle related tasks concurrently (where safe and beneficial).
- Gather results and log lessons learned to MEMORY.md or a dedicated log file.
- Update a short action plan for the next run based on findings.

Note: If certain tasks must be serialized due to dependencies, parallelization should be gated and logged.

# Idle Heartbeat Check Rotation (every 30 min)

When nothing urgent needs attention, run the automated executor:
- Run `node /home/claw/.openclaw/workspace/scripts/heartbeat-executor.js`
- If result is a routine "OK" or "healthy" status, reply HEARTBEAT_OK.
- If result is an "ALERT" or "Error", report it to the user.

# Guardrails

- Treat heartbeat executor output as internal by default. Do not surface routine strings like "Cron check: healthy." to chat.
- Only send a visible alert when the issue is actionable or user-impacting.
- Do not treat heartbeat poll metadata, suppressed outbound attempts, or compaction summaries as failures that require messaging the user.
- Log non-user-facing heartbeat failures to `memory/YYYY-MM-DD.md` with timestamp, check name, raw error, whether an outward message was attempted/suppressed, retry/reset action, and any next step.
