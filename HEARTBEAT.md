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
