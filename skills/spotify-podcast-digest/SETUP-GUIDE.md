# Spotify Podcast Digest — Setup Guide

Get an AI-powered podcast digest delivered to your Telegram — just say the podcast name or drop a Spotify URL.

**Data source:** RSS feed (via Apple Podcasts) — no Spotify API credentials required
**Delivery:** Telegram
**Trigger:** On-demand or scheduled via cron

---

## Prerequisites

- [ ] OpenClaw installed (`npm install -g openclaw@latest`)
- [ ] OpenClaw Gateway running (`openclaw gateway --port 18789`)
- [ ] Telegram channel connected (`openclaw onboard` or see [Telegram docs](https://docs.openclaw.ai/channels/telegram))
- [ ] Python 3 available (`python3 --version`)

---

## Step 1 — Install the Skill

Copy the skill folder into your OpenClaw workspace:

```bash
mkdir -p ~/.openclaw/workspace/skills/spotify-podcast-digest/scripts

cp path/to/spotify-podcast-digest/SKILL.md \
   ~/.openclaw/workspace/skills/spotify-podcast-digest/SKILL.md

cp path/to/spotify-podcast-digest/scripts/fetch_podcast.py \
   ~/.openclaw/workspace/skills/spotify-podcast-digest/scripts/fetch_podcast.py
```

Verify:

```bash
ls ~/.openclaw/workspace/skills/spotify-podcast-digest/scripts/
# Should show: fetch_podcast.py
```

---

## Step 2 — Configure Telegram

Ensure your Telegram bot token and chat ID are set in `~/.openclaw/openclaw.json`:

```json5
{
  "channels": {
    "telegram": {
      "botToken": "YOUR_TELEGRAM_BOT_TOKEN_HERE",
      "chatId": "YOUR_TELEGRAM_CHAT_ID_HERE"
    }
  }
}
```

If you haven't set up Telegram yet:
1. Create a bot via [@BotFather](https://t.me/BotFather) on Telegram
2. Copy the bot token
3. Start a conversation with your bot and send `/start`
4. Get your chat ID: message [@userinfobot](https://t.me/userinfobot) on Telegram
5. Add both to `openclaw.json` as shown above
6. Run `openclaw doctor` to verify Telegram is connected

---

## Step 3 — Test It Manually

Run a digest on demand to verify everything works:

```bash
openclaw agent --message "Summarize the latest episode of Huberman Lab and send it to Telegram" --thinking high
```

Or with a Spotify URL:

```bash
openclaw agent --message "Summarize this podcast episode and send to Telegram: https://open.spotify.com/show/2MAi0BvDc6GTFvKFPXnkCL" --thinking high
```

You should see the agent search for the RSS feed, extract the episode, generate the digest, and deliver it to Telegram.

---

## Step 4 — (Optional) Schedule a Daily Digest

To automatically receive a digest of a specific podcast every day, add a cron job to `~/.openclaw/openclaw.json`:

```bash
nano ~/.openclaw/openclaw.json
```

Add (or merge) the `cron` block from `cron-config.json5` — update the podcast name and schedule to your preference:

```json5
{
  // ... your existing config ...

  "cron": {
    "jobs": [
      {
        "name": "podcast-digest",
        "schedule": "0 8 * * *",
        "message": "Summarize the latest episode of [YOUR PODCAST NAME HERE] and send the digest to Telegram.",
        "session": "main",
        "thinking": "high"
      }
    ]
  }
}
```

**Cron schedule examples:**

| Schedule | Cron expression |
|----------|----------------|
| Every day at 8:00 AM | `0 8 * * *` |
| Every day at 6:00 PM | `0 18 * * *` |
| Weekdays only at 9:00 AM | `0 9 * * 1-5` |
| Every Monday at 7:00 AM | `0 7 * * 1` |

---

## Step 5 — Restart the Gateway

Apply your config changes:

```bash
# If running as a daemon:
openclaw gateway restart

# Or stop and restart manually:
openclaw gateway --port 18789 --verbose
```

---

## Step 6 — Verify with Doctor

```bash
openclaw doctor
```

Check for:
- ✅ Telegram channel connected
- ✅ Cron jobs registered (if configured)
- ✅ Gateway running

---

## Usage Examples

Once installed, you can trigger the skill with natural language:

```
"Summarize the latest episode of Lex Fridman"
"Recap episode 42 of The Tim Ferriss Show"
"What did they discuss on Huberman Lab this week?"
"Summarize this: https://open.spotify.com/episode/..."
"Send me a digest of the My First Million episode about AI"
```

---

## Customization

### Change the podcast for scheduled digests

Update the `message` field in your cron job with a different podcast name.

### Summarize a specific episode by keyword

Trigger manually: `"Summarize the Lex Fridman episode with Elon Musk"`

### Adjust number of key insights

The skill generates 5–8 insights by default. You can ask for more or fewer:
`"Summarize the latest Huberman Lab episode, give me 10 key insights"`

---

## Troubleshooting

**"No podcasts found"**
- Try a more specific podcast name, or provide the Spotify URL directly
- Some podcasts are not on Apple Podcasts — in that case, provide the RSS feed URL manually

**Digest not arriving via Telegram**
- Check bot token and chat ID in `openclaw.json`
- Ensure you've sent `/start` to your bot
- Run `openclaw doctor` to verify Telegram connection

**Show notes look thin / summary is vague**
- Some podcasts have minimal show notes in their RSS feed
- The skill will note this in the digest
- For richer summaries, look for podcasts that publish detailed show notes

**Scheduled digest not running**
- Run `openclaw doctor` to confirm the cron job is registered
- Confirm the gateway is running

---

## File Reference

```
~/.openclaw/workspace/skills/spotify-podcast-digest/
├── SKILL.md                ← Main skill instructions
└── scripts/
    └── fetch_podcast.py    ← Data fetching script (RSS, Apple Podcasts API)

~/.openclaw/
└── openclaw.json           ← Telegram config + optional cron job
```

---

## Disclaimer

This skill summarizes content from publicly available podcast RSS feeds. Summaries are AI-generated and may not perfectly represent the original content. Always refer to the original episode for accuracy.
