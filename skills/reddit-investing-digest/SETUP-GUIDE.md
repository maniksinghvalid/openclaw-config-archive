# Reddit Investing Digest — Setup Guide

Get a daily AI-powered investing digest from Reddit's top investing communities delivered to your Telegram at 6:00 PM every day.

**Subreddits:** r/wallstreetbets · r/options · r/investing · r/stocks
**Delivery:** Telegram
**Schedule:** Daily at 6:00 PM

---

## Prerequisites

Before setting up the digest, make sure you have:

- [ ] OpenClaw installed (`npm install -g openclaw@latest`)
- [ ] OpenClaw Gateway running (`openclaw gateway --port 18789`)
- [ ] Telegram channel connected (`openclaw onboard` or see [Telegram docs](https://docs.openclaw.ai/channels/telegram))
- [ ] Browser tool enabled in your config (needed to fetch Reddit data)

---

## Step 1 — Install the Skill

Copy the skill folder into your OpenClaw workspace:

```bash
# Create the skills directory if it doesn't exist
mkdir -p ~/.openclaw/workspace/skills/reddit-investing-digest

# Copy the skill file
cp path/to/reddit-investing-digest/SKILL.md \
   ~/.openclaw/workspace/skills/reddit-investing-digest/SKILL.md
```

Verify it's in place:

```bash
ls ~/.openclaw/workspace/skills/reddit-investing-digest/
# Should show: SKILL.md
```

---

## Step 2 — Enable the Browser Tool

The skill uses Reddit's public JSON API via the browser tool. Make sure it's enabled in your `~/.openclaw/openclaw.json`:

```json5
{
  "browser": {
    "enabled": true
  }
}
```

---

## Step 3 — Configure the Cron Job

Open `~/.openclaw/openclaw.json` in your editor and add the `cron` block:

```bash
nano ~/.openclaw/openclaw.json
```

Add (or merge) the following into your config:

```json5
{
  // ... your existing config ...

  "cron": {
    "jobs": [
      {
        "name": "reddit-investing-digest",
        "schedule": "0 18 * * *",
        "message": "Run the Reddit Investing Digest skill: fetch top posts from r/wallstreetbets, r/options, r/investing, and r/stocks for the past 24 hours. Analyze for trending posts, most-mentioned tickers, market sentiment, notable options plays, and notable comments. Format the full digest report and send it via Telegram.",
        "session": "main",
        "thinking": "high"
      }
    ]
  }
}
```

**Cron schedule reference:**

| Schedule | Cron expression |
|----------|----------------|
| Every day at 6:00 PM | `0 18 * * *` |
| Every day at 7:00 AM | `0 7 * * *` |
| Weekdays only at 6:00 PM | `0 18 * * 1-5` |
| Every day at 9:00 PM | `0 21 * * *` |

---

## Step 4 — Configure Telegram

Ensure your Telegram bot token is set:

```json5
{
  "channels": {
    "telegram": {
      "botToken": "YOUR_TELEGRAM_BOT_TOKEN_HERE"
    }
  }
}
```

If you haven't set up Telegram yet:
1. Create a bot via [@BotFather](https://t.me/BotFather) on Telegram
2. Copy the bot token
3. Add it to your `openclaw.json` as shown above
4. Start a conversation with your bot and send `/start`
5. Run `openclaw doctor` to verify Telegram is connected

---

## Step 5 — Restart the Gateway

Apply your config changes:

```bash
# If running as a daemon:
openclaw gateway restart

# Or if running manually, stop and restart:
# Ctrl+C to stop, then:
openclaw gateway --port 18789 --verbose
```

---

## Step 6 — Test It Manually

Run the digest on demand to verify everything works before waiting for the 6 PM trigger:

```bash
openclaw agent --message "Run the Reddit Investing Digest skill and send the report via Telegram" --thinking high
```

You should see the agent fetch Reddit data, analyze it, format the report, and deliver it to Telegram within a few minutes.

---

## Step 7 — Verify with Doctor

```bash
openclaw doctor
```

Check for:
- ✅ Telegram channel connected
- ✅ Browser tool enabled
- ✅ Cron jobs registered (the `reddit-investing-digest` job should appear)
- ✅ Gateway running

---

## Customization

### Change which subreddits are monitored

Edit `SKILL.md` and update the four URLs in Step 1. Some alternatives:

| Subreddit | Focus |
|-----------|-------|
| r/SecurityAnalysis | Deep fundamental analysis |
| r/ValueInvesting | Long-term value plays |
| r/StockMarket | General market discussion |
| r/Superstonk | GME / meme stock community |
| r/Pennystocks | Small-cap and penny stocks |
| r/thetagang | Options premium selling strategies |
| r/SPACs | SPAC deals and mergers |

### Change the delivery time

Update the `schedule` field in your cron config. Uses standard cron syntax (UTC or local time depending on your system).

### Pause the digest temporarily

Comment out or remove the job from your `cron.jobs` array in `openclaw.json` and restart the gateway.

### Run on weekdays only

Change the schedule to: `"0 18 * * 1-5"` (Monday–Friday only)

---

## Troubleshooting

**Digest not arriving at 6 PM**
- Run `openclaw doctor` to check the cron job is registered
- Confirm the gateway is running (`openclaw gateway --port 18789`)
- Check gateway logs for cron trigger messages

**Reddit fetch returning errors**
- Reddit may rate-limit requests — the skill handles this with a retry
- Try running the digest manually: `openclaw agent --message "Run the Reddit Investing Digest skill"`

**Telegram not receiving messages**
- Check your bot token is correct in `openclaw.json`
- Ensure you've started a conversation with the bot (send `/start` to it)
- Verify with: `openclaw doctor`

**Report too long / split incorrectly**
- The skill automatically splits messages over 4096 characters
- Adjust the number of posts per subreddit in SKILL.md (reduce `limit=25` to `limit=10`)

---

## File Reference

```
~/.openclaw/workspace/skills/reddit-investing-digest/
└── SKILL.md          ← Main skill instructions (the agent reads this)

~/.openclaw/
└── openclaw.json     ← Add cron job and browser config here
```

---

## Disclaimer

This digest is generated from public Reddit posts and is for informational purposes only. It does not constitute financial advice. Always conduct your own research (DYOR) before making any investment decisions.
