---
name: spotify-podcast-digest
description: >
  Summarizes a podcast episode and delivers a clean digest via Telegram. Use this skill when the
  user asks to summarize a podcast, recap a podcast episode, get a podcast digest, or find out
  what was discussed on a podcast. Accepts a Spotify URL (open.spotify.com/show/... or
  open.spotify.com/episode/...) OR a plain podcast name with an optional episode descriptor
  (e.g. "latest", an episode number, a keyword from the title, or a date). Finds the podcast's
  RSS feed, extracts the full episode show notes, generates a structured digest of key insights
  and significant views, and sends it to Telegram. Also trigger for: "recap last week's episode
  of X", "what did they talk about on Y podcast", "send me a digest of episode 42 of Z",
  "summarize the Huberman Lab episode on sleep", or "what's the latest episode of [podcast]".
compatibility:
  tools:
    - Bash
---

# Spotify Podcast Digest Skill

## Purpose

Given a podcast name or Spotify URL, find its RSS feed, extract the target episode's full show
notes, generate a digest of key insights and views expressed, and deliver it via Telegram.

The skill directory is at:
`/Users/akshaydhaliwal/Documents/Claude/Projects/OpenClaw/skills/spotify-podcast-digest/`

All data fetching is handled by `scripts/fetch_podcast.py` (Python stdlib only, no installs needed).
Run all script commands from the skill directory.

---

## Instructions

Follow these steps **in order**:

### Step 1 — Parse the Input

Identify what the user provided:

**A. Spotify URL** — matches `open.spotify.com/show/...` or `open.spotify.com/episode/...`
**B. Plain podcast name** — text string, optionally with an episode descriptor:
  - No descriptor / "latest" → most recent episode
  - Episode number → e.g. "episode 42" or "#42"
  - Keyword → a word/phrase likely in the episode title (e.g. "the sleep episode")
  - Date → YYYY-MM-DD or natural language like "last Thursday"

If the input is very ambiguous (a one-word name that could match many shows), note that you'll
confirm the best match with the user after searching.

---

### Step 2 — Resolve the Podcast to an RSS Feed

**If input is a Spotify URL:**

```bash
cd /Users/akshaydhaliwal/Documents/Claude/Projects/OpenClaw/skills/spotify-podcast-digest
python3 scripts/fetch_podcast.py from-spotify "<spotify_url>"
```

This returns JSON with a `search_term` field — use that as the query for the next command.

**Then (always), search Apple Podcasts for the RSS feed:**

```bash
python3 scripts/fetch_podcast.py search "<podcast name or search_term>"
```

This returns a `results` array. Pick the best match (closest name, highest episode count).
If multiple results are similarly named, use the one with the most episodes or the most
recent `latest_episode_date`. If confidence is low, show the top 3 to the user and ask them
to pick before continuing.

Note the `feed_url` from the chosen result — you'll use it in Step 3.

---

### Step 3 — Fetch the Target Episode

Use the `feed_url` from Step 2 with the appropriate selector flag:

```bash
# Latest episode (default when no descriptor given):
python3 scripts/fetch_podcast.py episode "<feed_url>"

# By episode number:
python3 scripts/fetch_podcast.py episode "<feed_url>" --number 42

# By keyword in title or description:
python3 scripts/fetch_podcast.py episode "<feed_url>" --keyword "sleep"

# By publish date (YYYY-MM-DD):
python3 scripts/fetch_podcast.py episode "<feed_url>" --date 2026-03-20
```

The output JSON includes:
- `episode_title`, `podcast_name`, `pub_date_formatted`, `duration`
- `content` — full show notes, HTML-stripped, up to 8000 chars
- `description` — short episode description (up to 500 chars)
- `links` — notable URLs extracted from show notes
- `episode_url` and `enclosure_url`

If `error` is `"episode_not_found"`, the response includes `recent_episodes` — show those to
the user and ask which one they meant.

---

### Step 4 — Generate the Digest

Using the episode data from Step 3, produce the digest. The primary source is `content`
(full show notes). If `content` is short or thin (under ~200 chars), supplement from
`description` and the episode title itself.

**OVERVIEW** (1 sentence)
- State who is on the episode and the central subject
- Example: "Lex Fridman interviews Andrej Karpathy on the future of AI agents and neural net interpretability."

**KEY INSIGHTS** (5–8 bullet points)
- Each bullet expresses a **significant view, opinion, argument, or claim** made in the episode
- Write each point as a clear, standalone takeaway in plain English
- Be specific — cite the position taken, not just the topic area
- Good: "Guest argues that most people are training LLMs with too little data diversity, not too little compute"
- Bad: "Training data and compute discussed"
- If a notable guest quote or framing stands out in the show notes, include it

**RESOURCES** (up to 5 links)
- Pull from the `links` array
- Prioritize links that are genuinely useful to the listener: guest websites, referenced papers/books, tools mentioned, companion content
- Skip generic links (e.g. Spotify homepage, generic social profiles unrelated to episode content)
- If no useful links exist, omit this section

---

### Step 5 — Format the Telegram Report

Use Telegram-compatible Markdown: bold with `*`, italic with `_`, inline code with `` ` ``.
Do **not** use `**` (double asterisk) or `###` (headers) — these do not render in Telegram.

```
🎙️ *Podcast Digest*
📅 {pub_date_formatted} | ⏱️ {duration}

*{podcast_name}*
🎧 *{episode_title}*

_{One-sentence overview}_

━━━━━━━━━━━━━━━━━━━━━━━━━
💡 *KEY INSIGHTS*
━━━━━━━━━━━━━━━━━━━━━━━━━
• {Significant view or claim — clear, plain-English takeaway}
• {Significant view or claim}
• {Significant view or claim}
• {Significant view or claim}
• {Significant view or claim}
(5–8 bullets)

━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 *RESOURCES*
━━━━━━━━━━━━━━━━━━━━━━━━━
• [{link text}]({url})
• [{link text}]({url})

[🎵 Listen on Spotify]({episode_url or enclosure_url})
━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Notes:**
- Omit `⏱️ {duration}` if duration is empty
- Omit the RESOURCES section entirely if no useful links exist
- Omit the listen link if no episode URL is available
- If the show notes were thin, add a small italic note at the end: `_⚠️ Summary based on episode description — full transcript not available._`
- If the message exceeds 4096 characters, split into two parts:
  - Part 1: `[Part 1/2]` + OVERVIEW + KEY INSIGHTS
  - Part 2: `[Part 2/2]` + remaining insights (if any) + RESOURCES + listen link

---

### Step 6 — Deliver via Telegram

Load credentials from environment variables `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`,
or from `~/.openclaw/openclaw.json` under `channels.telegram`.

If credentials are missing, halt and ask the user to provide them before continuing.

Send via curl:

```bash
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"${TELEGRAM_CHAT_ID}\", \"text\": \"...\", \"parse_mode\": \"Markdown\", \"disable_web_page_preview\": false}"
```

Confirm the response contains `"ok": true`. If it returns `"ok": false`, retry once after
3 seconds. If still failing, log the error response and stop.

For two-part messages, send Part 1 first and confirm delivery before sending Part 2.

---

### Step 7 — Log Completion

Output a brief confirmation:

```
✅ Podcast Digest sent via Telegram at {timestamp}.
Podcast: {podcast_name}
Episode: {episode_title}
Report parts sent: {1 or 2}
```

---

## Error Handling

| Error | Action |
|-------|--------|
| `no_results` from search | Ask user to confirm podcast name, or provide a Spotify URL |
| Multiple ambiguous search results | Show top 3 (name + episode count) and ask user to pick |
| `feed_fetch_failed` | Note the failure; try alternative feed if user can provide one |
| `episode_not_found` | Show `recent_episodes` from the response, ask user to pick |
| Thin show notes (content < 200 chars) | Generate insights from title + description; flag in report |
| Telegram credentials missing | Halt and ask user to provide `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` |
| Telegram send fails | Retry once after 3s; log error if still failing |

---

## Notes

- The RSS feed (via Apple Podcasts Search) is the data source — not the Spotify audio
- `content` field in episode JSON is HTML-stripped show notes, up to 8000 chars
- Summaries are generated by Claude from the show notes — quality depends on how detailed the host's show notes are
- Do not store or log any personal user data
