# YouTube Transcript Skill — Setup Guide

Transcribe and summarize any YouTube video — just paste the URL.
No pip installs required. Requires a RapidAPI key.

**API:** `youtube-transcript3.p.rapidapi.com`
**Works with:** Videos that have captions (manual or auto-generated)

---

## Prerequisites

- [ ] Python 3 available (`python3 --version` → should show 3.6+)
- [ ] A RapidAPI key subscribed to the `youtube-transcript3` API
- [ ] OpenClaw installed and configured

---

## Step 1 — Add Your RapidAPI Key

Create a `.env` file in the skill root directory:

```
/home/claw/.openclaw/.env
```

Contents:
```
RAPIDAPI_KEY=your_key_here
```

The key is read automatically by the script. It is never committed or logged.

---

## Step 2 — Verify the Script

```bash
python3 /home/claw/.openclaw/workspace/skills/youtube-transcript/scripts/fetch_transcript.py fetch "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Expected output: JSON with `title`, `channel`, `duration`, `transcript_text`,
and `segments`. `error` field should be `null`.

---

## Usage

Just paste a YouTube URL in your OpenClaw chat, or use natural language:

```
Summarize this video: https://youtu.be/abc123
What does this video say? https://www.youtube.com/watch?v=xyz
Give me the key points from [URL]
TL;DR this video: [URL]
Transcribe this: [URL]
What did they discuss in this video? [URL]
[paste a YouTube URL with no other text — Claude will auto-summarize]
```

**Output formats available:**
- **Brief** (default) — TL;DR + 3–5 key points
- **Detailed** — section-by-section breakdown with timestamps
- **Full Transcript** — timestamped paragraphs

Ask Claude to switch formats at any time.

---

## Limitations

- Only works on videos that have captions (manual or YouTube auto-generated)
- Private or age-restricted videos requiring sign-in cannot be accessed
- Subject to RapidAPI plan rate limits

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| `missing_api_key` error | Create the `.env` file with `RAPIDAPI_KEY=your_key_here` |
| `auth_failed` error | Check your RapidAPI key is correct and the `youtube-transcript3` API is active on your plan |
| `no_captions` / `captions_disabled` error | The video has no captions — try a different video |
| `private_video` error | The video requires sign-in — cannot be accessed |
| `video_unavailable` error | The video has been deleted or is region-blocked |
| `rate_limited` error | RapidAPI quota reached — wait and retry, or upgrade your plan |
| Script produces no output | Verify `python3 --version` shows 3.6+ |
