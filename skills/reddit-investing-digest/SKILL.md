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

Use `mcp__MCP_DOCKER__browser_navigate` to retrieve the top posts from each subreddit using Reddit's public JSON API (no authentication required). Fetch **top posts from the past 24 hours** (`t=day`), up to 25 posts each.

Fetch these four URLs:

```
https://www.reddit.com/r/wallstreetbets/top.json?t=day&limit=25
https://www.reddit.com/r/options/top.json?t=day&limit=25
https://www.reddit.com/r/investing/top.json?t=day&limit=25
https://www.reddit.com/r/stocks/top.json?t=day&limit=25
```

For each post, extract:
- `title`
- `score` (upvotes)
- `num_comments`
- `url` (the permalink, prefixed with `https://reddit.com`)
- `selftext` (body text, first 300 characters)
- `subreddit`
- `permalink` (for constructing comment URLs in Step 1b)

If a fetch returns a 429 rate-limit error, wait 3 seconds and retry once. If a subreddit is unavailable, skip it and note it in the report.

#### Step 1b — Fetch Top Comments for Top 3 Posts

After collecting all posts, identify the 3 highest-scoring posts overall. For each of those 3 posts, fetch the comments thread:

```
https://www.reddit.com/r{permalink}.json?limit=5&sort=top
```

Extract the top comment (highest score) from the response: its `body` text and `score`. You'll use this in Step 2E. If comment fetching fails for any post, skip gracefully.

---

### Step 2 — Analyze the Data

Process all posts across all four subreddits and identify:

**A. Trending Posts**
- Top 5 highest-scored posts overall (any subreddit)
- Rank them by `score`

**B. Most-Mentioned Tickers**
- Scan all titles and body text for stock ticker symbols
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
   ⬆️ {score} upvotes | 💬 {comments} comments

2. [{post title}]({url}) — r/{subreddit}
   ⬆️ {score} upvotes | 💬 {comments} comments

3. [{post title}]({url}) — r/{subreddit}
   ⬆️ {score} upvotes | 💬 {comments} comments

4. [{post title}]({url}) — r/{subreddit}
   ⬆️ {score} upvotes | 💬 {comments} comments

5. [{post title}]({url}) — r/{subreddit}
   ⬆️ {score} upvotes | 💬 {comments} comments

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
- Every post in TOP TRENDING POSTS must use `[{post title}]({url})` with the exact Reddit URL from the `permalink` field (prefixed with `https://reddit.com`). Never write a bare title.
- Every NOTABLE COMMENT must use `[{post title}]({url})` for the Post line — same URL rule.
- Every NOTABLE OPTIONS PLAY must link to the source post using `[r/{subreddit}]({url})`.
- Upvote counts and comment counts must come from actual API data — do not estimate or omit.
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

- Reddit's public JSON API does not require authentication for `top` posts
- Always use `t=day` to get posts from the last 24 hours
- Do not store or log individual Reddit usernames in any persistent memory
- Telegram Markdown: use `*bold*`, `_italic_`, `` `code` `` — avoid unsupported tags like `**` or `###`
- Always include the disclaimer footer on every report
