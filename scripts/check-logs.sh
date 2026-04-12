#!/bin/bash

# Configuration
LOG_FILE="/home/claw/.openclaw/agents/main/sessions/4021db13-698c-4602-8864-8d6caf843445.jsonl"
SUMMARY_FILE="/home/claw/.openclaw/workspace/memory/logs/analysis-$(date +%Y-%m-%d).md"

mkdir -p /home/claw/.openclaw/workspace/memory/logs

echo "# Log Health Analysis - $(date)" > "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file $LOG_FILE not found." >> "$SUMMARY_FILE"
    exit 1
fi

echo "## 🚨 Error Summary (Last 500 lines)" >> "$SUMMARY_FILE"
tail -n 500 "$LOG_FILE" | grep -i "ERROR" | sed 's/.*"0":"//;s/","_meta.*//' | sort | uniq -c >> "$SUMMARY_FILE"

echo "" >> "$SUMMARY_FILE"
echo "## 🔍 Detected Issues & Patterns" >> "$SUMMARY_FILE"

# Check for Brave Search 422
if tail -n 500 "$LOG_FILE" | grep -q "Brave Search API error (422)"; then
    echo "- **ISSUE:** Brave Search Query Limit exceeded." >> "$SUMMARY_FILE"
    echo "  - **Remediation:** Shorten search queries in the calling skill/cron job. Stick to < 40 words." >> "$SUMMARY_FILE"
fi

# Check for Spotify Skill path issues
if tail -n 500 "$LOG_FILE" | grep -q "spotify-podcast-digest"; then
    if tail -n 500 "$LOG_FILE" | grep -q "No such file or directory"; then
        echo "- **ISSUE:** Podcast skill path mismatch." >> "$SUMMARY_FILE"
        echo "  - **Remediation:** Check SKILL.md for absolute paths that don't match the current environment." >> "$SUMMARY_FILE"
    fi
fi

# Check for Bun/Runtime issues
if tail -n 500 "$LOG_FILE" | grep -q "bun: No such file or directory"; then
    echo "- **ISSUE:** Bun runtime not found." >> "$SUMMARY_FILE"
    echo "  - **Remediation:** Ensure /home/claw/.bun/bin is in the PATH or use the absolute path in the skill." >> "$SUMMARY_FILE"
fi

echo "" >> "$SUMMARY_FILE"
echo "Analysis complete. Sent to agent for review." >> "$SUMMARY_FILE"
