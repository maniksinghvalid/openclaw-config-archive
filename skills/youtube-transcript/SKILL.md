# YouTube Transcript Skill

Get transcripts from YouTube videos and summarize them.

## Setup Required

Before using this skill, you need to subscribe to a YouTube transcript API on RapidAPI.

👉 **See [SETUP.md](./SETUP.md) for instructions** (takes 2 minutes)

## When to Use

- User shares a YouTube URL and asks for a summary
- User says "summarize this video"
- User wants transcript text extracted

## How It Works

1. Extract video ID from YouTube URL
2. Fetch transcript using RapidAPI
3. Summarize the content

## Usage

```bash
./get-transcript.sh <VIDEO_ID_OR_URL>
```

## Flow

1. Call `get-transcript.sh` with the video URL/ID
2. Script returns the full transcript as text
3. Summarize the transcript using your language model
4. Present key points to the user

## Examples

**User:** "Summarize this: https://www.youtube.com/watch?v=dQw4w9WgXcQ"

**You:**
1. Run: `./get-transcript.sh dQw4w9WgXcQ`
2. Read the transcript
3. Provide a concise summary with key takeaways

## Error Handling

- If no transcript available: "This video doesn't have a transcript available"
- If video ID invalid: "Couldn't find that video"
- If RapidAPI fails: "Transcript service is unavailable right now"

## Notes

- Works best with videos that have captions/subtitles
- Auto-generated transcripts may have errors
- Very long videos (>2h) may need chunked summaries
