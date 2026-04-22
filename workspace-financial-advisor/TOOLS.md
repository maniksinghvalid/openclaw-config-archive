# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## YouTube Videos

**Never use the `browser` tool or `web_search` to handle YouTube links. No browser is installed on this server.**

For any YouTube video URL shared in chat or found via RSS, fetch the transcript directly:

```
python3 /home/claw/.openclaw/workspace/skills/youtube-transcript/scripts/fetch_transcript.py fetch "<VIDEO_URL>"
```

Then summarize from the transcript.

## Scripts

- `scripts/yt_rss_checker.py` — fetches latest videos from MeetKevin and Mike Jones via YouTube RSS. Usage: `python3 /home/claw/.openclaw/workspace-financial-advisor/scripts/yt_rss_checker.py <window_hours>`

## Skills

- `youtube-transcript` — symlinked into `skills/youtube-transcript/` from the main workspace.
  - **Exact invocation** (use this in subagent prompts — do not let the agent guess):
    ```
    python3 /home/claw/.openclaw/workspace/skills/youtube-transcript/scripts/fetch_transcript.py fetch "<VIDEO_URL>"
    ```
  - Entry point is `scripts/fetch_transcript.py`, subcommand `fetch`, takes a full YouTube URL as positional arg. No `main.py`, no `--video-id` flag.

Add whatever helps you do your job. This is your cheat sheet.
