# TOOLS.md - Research Agent Tool Notes

## YouTube Videos

**Never use the `browser` tool or `web_search` to handle YouTube links. No browser is installed on this server.**

For any YouTube video URL shared in chat or found via RSS, fetch the transcript directly:

```
python3 /home/claw/.openclaw/workspace/skills/youtube-transcript/scripts/fetch_transcript.py fetch "<VIDEO_URL>"
```

Then summarize from the transcript. This works without a browser and gives full content.

## Web Search

Keep `web_search` queries under **40 words / 350 characters** to avoid Brave Search API 422 errors. Split long queries into multiple short searches.

## Skills

- `qmd search <term>` — keyword search across memory/workspace index
- Run `qmd update` after file changes to refresh the index
- PATH must include `/home/claw/.bun/bin` for bun-based skills
