---
name: youtube-transcript
description: >
  Use this skill when the user wants to summarize, transcribe, or learn about a
  YouTube video. Trigger on: any YouTube URL pasted in chat (youtube.com/watch,
  youtu.be, youtube.com/shorts), "summarize this video", "transcribe this YouTube",
  "what does this video say", "what is this video about", "give me the key points
  from [URL]", "tldr this video", "what did [person] say in [URL]", "summarize
  this youtube video", "break down this video". Also trigger when the user pastes
  a YouTube URL with no other context — they likely want a summary.
version: 1.0.0
compatibility:
  tools:
    - Bash
---

# YouTube Transcript Skill

## Purpose

Given a YouTube URL, fetch the video's caption/transcript data via the
RapidAPI `youtube-transcript3` endpoint, then synthesize a structured summary
or transcript for the user.

The skill directory is at:
`/home/claw/.openclaw/workspace/skills/youtube-transcript/`

All transcript fetching is handled by `scripts/fetch_transcript.py` (Python 3
stdlib only — no pip installs required). The script reads `RAPIDAPI_KEY` from the `.env`
file in the skill root directory. Run all script commands from the skill directory.

---

## Instructions

Follow these steps **in order**:

### Step 1 — Parse the Input

Extract the YouTube URL from the user's message. Accepted forms:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/shorts/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID`

If no URL is present but the user asks about a video by description, ask them to
provide the URL before continuing.

Identify the desired output format. Default to **Brief** if not specified:
- **Brief** — TL;DR sentence + 3–5 key points (default)
- **Detailed** — section-by-section breakdown with timestamps
- **Full Transcript** — timestamped, paragraph-grouped transcript

---

### Step 2 — Fetch the Transcript

```bash
cd /home/claw/.openclaw/workspace/skills/youtube-transcript
python3 scripts/fetch_transcript.py fetch "<youtube_url>"
```

The script returns JSON with:
- `title`, `channel`, `duration`, `url`
- `caption_type` — `"manual"` or `"auto_generated"`
- `caption_language` — language code (e.g. `"en"`)
- `transcript_text` — full plain-text transcript (primary input for summarisation)
- `segments` — array of `{start, end, text}` objects (used for timestamped formats)
- `segment_count` — total number of caption segments
- `error` — `null` on success, or an error code string on failure

---

### Step 3 — Check for Errors

If `error` is not `null`, handle per the **Error Handling** table below before
continuing.

---

### Step 4 — Generate the Summary

Use `transcript_text` as the primary source. If `caption_type` is
`"auto_generated"`, note that accuracy may vary for names, technical terms, and
numbers.

---

#### Brief Format (default)

```
## [Title]
[Channel] • [Duration]

**TL;DR:** One sentence capturing the core message or purpose of the video.

**Key Points:**
• [Most important point]
• [Second point]
• [Third point]
(up to 5 bullets — include only what's substantive)

_Captions: [Manual / Auto-generated ([language])]_
```

---

#### Detailed Format

Divide the transcript into logical sections based on topic shifts (use content
analysis and timestamp gaps in `segments`). For each section:

```
### [Section Topic] ([M:SS] – [M:SS])
[2–4 sentence summary of what's covered in this section]
```

Follow the sections with:

```
---
**Key Takeaways** (5–8 bullets of the most important points overall)

**TL;DR:** One sentence.
```

---

#### Full Transcript Format

Format the `segments` array as readable prose with timestamps. Group consecutive
segments with gaps < 2 seconds into a paragraph. Start each paragraph with the
timestamp of its first segment:

```
[0:00] First segment text continues into second and third naturally forming
a paragraph until there is a natural pause.

[0:15] New paragraph begins here after the gap.
```

Do not dump raw JSON — format as clean readable text.

---

### Step 5 — Offer Follow-ups

After delivering the summary, offer:
- Switch to a different format (Brief / Detailed / Full Transcript)
- Answer specific questions about the video content
- Extract quotes or statements on a specific topic
- List all resources, tools, or links mentioned in the video
- Provide a timestamped outline of the video structure

---

## Error Handling

| Error | Action |
|-------|--------|
| `missing_api_key` | Halt and ask the user to add `RAPIDAPI_KEY` to the `.env` file in the skill directory |
| `auth_failed` | Halt and ask the user to verify their `RAPIDAPI_KEY` is correct and active |
| `invalid_url` | Ask the user to paste the full YouTube URL |
| `fetch_failed` | Report the network error; suggest checking the URL and retrying |
| `private_video` | Inform the user the video is private and cannot be accessed |
| `video_unavailable` | Inform the user the video is unavailable (deleted or region-blocked) |
| `no_captions` | Inform the user this video has no captions; cannot transcribe |
| `captions_disabled` | Same — inform the user captions are disabled for this video |
| `rate_limited` | Inform the user the RapidAPI rate limit has been reached; suggest retrying later |
| `parse_error` | Report a response parsing error; suggest retrying |

---

## Notes

- Transcript quality depends on caption type: manual captions are accurate;
  auto-generated captions may have errors on proper nouns, technical terms,
  and numbers
- Very long videos (3+ hours) produce large transcripts; focus the Brief/Detailed
  summary on the most content-dense segments rather than summarising equally
- YouTube's page structure changes occasionally; if the script fails with
  `bot_detection`, retry once — transient bot-detection responses are common
- The script only reads caption text — it does not download audio or video
- Non-English videos: the script selects English captions if available, otherwise
  falls back to the first available caption track in any language
