---
name: reddit-investing-digest
description: >
  Fetches trending posts from key investing subreddits (r/wallstreetbets, r/options, r/investing, r/stocks),
  analyzes them for market sentiment, top tickers, notable options plays, and produces a full digest report —
  then delivers it via Telegram. Use this skill whenever the user asks to run the investing digest, fetch the
  Reddit report, send the daily stock report, check what's trending on Reddit today, or when triggered
  automatically by the daily cron job at 6:00 PM. Also trigger this skill for requests like "what are people
  saying about stocks on Reddit", "give me the WSB summary", or "run the daily market digest".
compatibility:
  tools:
    - mcp__MCP_DOCKER__browser_navigate
    - mcp__MCP_DOCKER__browser_snapshot
---

# Reddit Investing Digest Skill

## Purpose
Fetch trending posts from key investing subreddits, analyze them for market sentiment, top tickers, notable options plays, and produce a full digest report — then deliver it via Telegram.

---

## Instructions

When this skill is triggered, follow these steps **in order**:

### Step 1 — Fetch Reddit Posts

Use the `reddit-reader` skill's `fetch_reddit.py` script. The `www.reddit.com` JSON endpoint is blocked from this host (returns 403/HTML); the script uses `old.reddit.com` Atom feeds and is the only sanctioned path.

Run these four commands and parse the output:

```bash
python3 /home/claw/.openclaw/workspace/skills/reddit-reader/scripts/fetch_reddit.py subreddit wallstreetbets --listing top --time day --limit 25
python3 /home/claw/.openclaw/workspace/skills/reddit-reader/scripts/fetch_reddit.py subreddit options --listing top --time day --limit 25
python3 /home/claw/.openclaw/workspace/skills/reddit-reader/scripts/fetch_reddit.py subreddit investing --listing top --time day --limit 25
python3 /home/claw/.openclaw/workspace/skills/reddit-reader/scripts/fetch_reddit.py subreddit stocks --listing top --time day --limit 25
```

For each post, extract from the script output:
- `title`
- `author`
- `url` (the reddit.com permalink the script prints)
- `subreddit`

Note: the Atom-feed source does **not** expose `score` or `num_comments` — do not invent these. Rank posts by feed order (subreddit-sorted top-of-day) and cite engagement only when available downstream. If a subreddit returns no entries, skip it and note it in the report.

#### Step 1b — Fetch Top Comments for Top 3 Posts

After collecting all posts, identify 3 posts you want to dig deeper on (highest interest by title/topic). For each, extract the `post_id` from the URL (e.g. `reddit.com/r/wallstreetbets/comments/abc123/...` → `abc123`) and run:

```bash
python3 /home/claw/.openclaw/workspace/skills/reddit-reader/scripts/fetch_reddit.py comments <subreddit> <post_id>
```

Extract the top comment from the response. If comment fetching fails for any post, skip gracefully.

---

### Step 2 — Analyze the Data

Process all posts across all four subreddits and identify:

**A. Trending Posts**
- Top 5 most notable posts overall (any subreddit)
- The Atom feed does not expose `score` or `num_comments` — rank by feed order (each subreddit is fetched `top`/`day`, so earlier entries rank higher) combined with topical relevance

**B. Most-Mentioned Tickers**
- Scan all post titles for stock ticker symbols (post body text is not available from the Atom feed — titles only)
- Match: `$TICKER` format, or standalone ALL-CAPS words 2–5 letters that look like tickers (e.g. AAPL, NVDA, SPY, QQQ, TSLA)
- Exclude common non-ticker words: I, A, AI (context-dependent), DD, WSB, OTM, ITM, ATM, CEO, IPO, ETF, NYSE, NASDAQ, GDP, CPI, FED, IMO, TBH, EOD, YTD
- List the top 10 most-mentioned tickers with mention count

**C. Market Sentiment**
- Classify overall tone per subreddit as: Bullish / Bearish / Mixed
- Base this on: ratio of positive vs. negative language, calls vs. puts mentions, words like "moon", "rocket", "squeeze", "short", "crash", "puts", "bear", "bull"
- Give a 1-sentence sentiment summary per subreddit
- Give a 1-sentence overall summary

**D. Notable Options Activity**
- From r/wallstreetbets and r/options specifically, extract posts mentioning:
  - Specific options contracts (e.g. "NVDA $500 calls 4/18")
  - Expiry dates, strike prices, keywords: "yolo", "0DTE", "FDs", "LEAPS", "spread", "straddle"
- List up to 5 notable options plays. If none found, write "No specific options plays identified today."

**E. Notable Comments**
- Use the top comments fetched in Step 1b
- Summarize each top comment in 1 sentence (what is the commenter saying / their key point)

---

### Step 3 — Format the Report

Format the final report exactly as shown below. Use Telegram-compatible markdown (bold with `*`, italic with `_`, inline code with `` ` ``).

```
📊 *Daily Reddit Investing Digest*
📅 {Today's date, e.g. March 26, 2026} | 🕕 6:00 PM

━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 *TOP TRENDING POSTS TODAY*
━━━━━━━━━━━━━━━━━━━━━━━━━

1. [{post title}]({url}) — r/{subreddit}
2. [{post title}]({url}) — r/{subreddit}
3. [{post title}]({url}) — r/{subreddit}
4. [{post title}]({url}) — r/{subreddit}
5. [{post title}]({url}) — r/{subreddit}

━━━━━━━━━━━━━━━━━━━━━━━━━
📈 *MOST-MENTIONED TICKERS*
━━━━━━━━━━━━━━━━━━━━━━━━━

`$TICKER` — {X} mentions
`$TICKER` — {X} mentions
`$TICKER` — {X} mentions
... (top 10)

━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 *MARKET SENTIMENT*
━━━━━━━━━━━━━━━━━━━━━━━━━

🐂 r/wallstreetbets: {Bullish/Bearish/Mixed} — {1-sentence summary}
📉 r/options: {Bullish/Bearish/Mixed} — {1-sentence summary}
💼 r/investing: {Bullish/Bearish/Mixed} — {1-sentence summary}
📊 r/stocks: {Bullish/Bearish/Mixed} — {1-sentence summary}

Overall: {🟢 Bullish / 🔴 Bearish / 🟡 Mixed} — {1-sentence overall summary}

━━━━━━━━━━━━━━━━━━━━━━━━━
🎰 *NOTABLE OPTIONS PLAYS*
━━━━━━━━━━━━━━━━━━━━━━━━━

• {Contract / play description} — [r/{subreddit}]({url})
• {Contract / play description} — [r/{subreddit}]({url})
(up to 5 plays, or "No specific options plays identified today." if none)

━━━━━━━━━━━━━━━━━━━━━━━━━
💬 *NOTABLE COMMENTS*
━━━━━━━━━━━━━━━━━━━━━━━━━

• *Post:* [{post title}]({url})
  💬 {Summary of top comment}

• *Post:* [{post title}]({url})
  💬 {Summary of top comment}

• *Post:* [{post title}]({url})
  💬 {Summary of top comment}

━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ _This digest is for informational purposes only. Not financial advice. Always do your own research (DYOR)._
━━━━━━━━━━━━━━━━━━━━━━━━━
```

**CITATION RULES (mandatory — do not skip or reformat):**
- Every post in TOP TRENDING POSTS must use `[{post title}]({url})` with the exact Reddit URL the script prints for that post. Never write a bare title.
- Every NOTABLE COMMENT must use `[{post title}]({url})` for the Post line — same URL rule.
- Every NOTABLE OPTIONS PLAY must link to the source post using `[r/{subreddit}]({url})`.
- The Atom feed provides no upvote or comment counts — never invent, estimate, or display these numbers.
- Do not deviate from the section structure above. Do not replace it with freeform analysis or narrative prose. The format is fixed.
- If a section has no qualifying content, write the section header and "Nothing notable today." — do not skip the section.

---

### Step 4 — Deliver via Telegram

Send the formatted report using the **Telegram Bot API** directly.

Construct a POST request to:
```
https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage
```

With JSON body:
```json
{
  "chat_id": "{TELEGRAM_CHAT_ID}",
  "text": "{report text}",
  "parse_mode": "Markdown",
  "disable_web_page_preview": true
}
```

Use `mcp__MCP_DOCKER__browser_navigate` to send this request, or construct it as a curl-style call if a script tool is available.

**Bot token and chat ID:** These should be set as environment variables `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`, or found in the OpenClaw config at `~/.openclaw/openclaw.json` under `channels.telegram`.

**Message length:** If the formatted report exceeds 4096 characters, split into two messages:
- Part 1: `[Part 1/2]` header + Trending Posts + Tickers
- Part 2: `[Part 2/2]` header + Sentiment + Options Plays + Comments + Disclaimer

Send Part 1 first, then Part 2. Confirm each send returned HTTP 200 before proceeding.

---

### Step 5 — Log Completion

After sending, output a brief confirmation:

```
✅ Reddit Investing Digest sent via Telegram at {timestamp}.
Subreddits covered: r/wallstreetbets, r/options, r/investing, r/stocks
Posts analyzed: {total count}
Top comment threads fetched: {count}
Report parts sent: {1 or 2}
```

---

## Error Handling

| Error | Action |
|-------|--------|
| Reddit API rate limit (429) | Wait 3 seconds and retry once |
| Subreddit unavailable / private | Skip that subreddit, note in report header |
| No posts found for a subreddit | Show "No posts found today." for that section |
| Comment thread fetch fails | Skip notable comments for that post, don't halt |
| Telegram send failure (non-200) | Retry once after 3 seconds; if still failing, log the error and skip delivery |
| Bot token / chat ID missing | Halt and ask the user to provide `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` |

---

## Notes

- The skill reads `old.reddit.com` Atom feeds via `fetch_reddit.py` — no authentication required. `www.reddit.com` JSON/RSS is firewalled from this host (returns 403/HTML)
- Always use `--time day` to get posts from the last 24 hours
- Do not store or log individual Reddit usernames in any persistent memory
- Telegram Markdown: use `*bold*`, `_italic_`, `` `code` `` — avoid unsupported tags like `**` or `###`
- Always include the disclaimer footer on every report
