---
name: reddit-reader
description: This skill should be used when the user wants to read Reddit, browse a subreddit, fetch posts from a subreddit, search Reddit for a topic, get Reddit discussions about a subject, analyze Reddit content for any given topic, fetch comments on a Reddit post, or find out what people on Reddit think about anything. Use this skill whenever Reddit is mentioned or the user wants community opinions, discussions, or posts — even if they don't say "Reddit" explicitly.
version: 1.1.0
---

# Reddit Reader

Fetch and present Reddit content for any topic or subreddit the user provides.

## When To Use

Use when the user wants to:
- Read posts from a specific subreddit (e.g. "show me r/python")
- Search Reddit for a topic (e.g. "what is Reddit saying about X")
- Get top/hot/new posts from a community
- Find discussions about any subject

## How To Use

### Step 1 — Determine the request type

Identify whether the user wants:
- **Subreddit browse**: they named a subreddit (e.g. "r/machinelearning", "python subreddit")
- **Topic search**: they named a topic or question without a specific subreddit

### Step 2 — Run the fetch script

Use the Bash tool to run the script from the skill directory:

```bash
cd /home/claw/.openclaw/workspace/skills/reddit-reader

# Browse a subreddit (default: 25 hot posts)
python3 scripts/fetch_reddit.py subreddit <name> [--listing hot|new|top|rising] [--limit N] [--time day|week|month|year|all]

# Search Reddit for a topic
# Tip: use --subreddit to restrict to a relevant community — global search quality is poor
python3 scripts/fetch_reddit.py search "<query>" [--subreddit <name>|all] [--sort relevance|top|new|comments] [--limit N] [--time hour|day|week|month|year|all]

# Fetch comments on a specific post
# Get post_id from the URL: reddit.com/r/<sub>/comments/<post_id>/...
python3 scripts/fetch_reddit.py comments <subreddit> <post_id>
```

### Step 3 — Present results

Format the output clearly:
- Show post title, score (upvotes), comment count, and subreddit (for searches)
- Include the post URL so the user can open it
- Group by relevance or score
- Summarize themes if there are many results

### Step 4 — Offer follow-ups

After presenting results, offer to:
- Fetch comments for a specific post — extract the post ID from its URL (e.g. `reddit.com/r/python/comments/abc123/title/` → post_id is `abc123`)
- Search a different time range or sort order
- Drill into a specific subreddit found in results
- Restrict a broad search to a relevant subreddit for better quality results

## Notes

- The script uses Reddit's public JSON API — no credentials needed
- **Search quality**: Reddit's public search API returns low-relevance results for global searches. Prefer `--subreddit <name>` to search within a specific community when possible
- Rate limit: ~10 requests/min; add `time.sleep(1)` between calls if fetching many pages
- Max 100 results per request; Reddit hard-caps listings at 1000 total
- If a subreddit is private or banned, the script will report an error clearly
