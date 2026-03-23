---
name: reddit-reader
description: This skill should be used when the user wants to read Reddit, browse a subreddit, fetch posts from a subreddit, search Reddit for a topic, get Reddit discussions about a subject, or analyze Reddit content for any given topic.
version: 1.0.0
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

Use the Bash tool to run `scripts/fetch_reddit.py` with the appropriate arguments:

```bash
# Browse a subreddit (hot posts, default 10)
python3 scripts/fetch_reddit.py subreddit <name> [--listing hot|new|top|rising] [--limit N] [--time day|week|month|year|all]

# Search Reddit for a topic
python3 scripts/fetch_reddit.py search "<query>" [--subreddit all] [--sort relevance|top|new|comments] [--limit N] [--time month|week|year|all]
```

Run the script from the skill directory: `cd /Users/akshaydhaliwal/Documents/Claude/Projects/OpenClaw/skills/reddit-reader && python3 scripts/fetch_reddit.py ...`

### Step 3 — Present results

Format the output clearly:
- Show post title, score (upvotes), comment count, and subreddit (for searches)
- Include the post URL so the user can open it
- Group by relevance or score
- Summarize themes if there are many results

### Step 4 — Offer follow-ups

After presenting results, offer to:
- Fetch comments for a specific post (provide the post ID)
- Search a different time range or sort order
- Drill into a specific subreddit found in results

## Notes

- The script uses Reddit's public JSON API — no credentials needed
- Rate limit: ~10 requests/min; add `time.sleep(1)` between calls if fetching many pages
- Max 100 results per request; Reddit hard-caps listings at 1000 total
- If a subreddit is private or banned, the script will report an error clearly
