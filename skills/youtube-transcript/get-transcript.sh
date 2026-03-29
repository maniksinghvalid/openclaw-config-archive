#!/bin/bash
# Fetch YouTube transcript using RapidAPI

set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Usage: $0 <VIDEO_ID_OR_URL>"
    exit 1
fi

INPUT="$1"

# Extract video ID from URL if needed
if [[ "$INPUT" =~ ^https?:// ]]; then
    # Extract video ID from various YouTube URL formats
    VIDEO_ID=$(echo "$INPUT" | sed -E 's/.*[?&]v=([^&]+).*/\1/' | sed -E 's/.*youtu\.be\/([^?]+).*/\1/')
else
    VIDEO_ID="$INPUT"
fi

# Load API key from environment
RAPIDAPI_KEY="${RAPIDAPI_KEY:-}"
if [ -z "$RAPIDAPI_KEY" ]; then
    # Try loading from .env
    if [ -f /home/claw/.openclaw/.env ]; then
        source /home/claw/.openclaw/.env
    fi
fi

if [ -z "$RAPIDAPI_KEY" ]; then
    echo "Error: RAPIDAPI_KEY not set"
    exit 1
fi

# Try multiple RapidAPI endpoints for YouTube transcripts

# Option 1: YouTube Transcript by Glavier
RESPONSE=$(curl -s -X GET \
    "https://youtube-transcriptor.p.rapidapi.com/transcript?video_id=${VIDEO_ID}" \
    -H "X-RapidAPI-Key: ${RAPIDAPI_KEY}" \
    -H "X-RapidAPI-Host: youtube-transcriptor.p.rapidapi.com" 2>&1)

if echo "$RESPONSE" | jq -e '.transcript' > /dev/null 2>&1; then
    echo "$RESPONSE" | jq -r '.transcript[] | .text' | tr '\n' ' '
    exit 0
fi

# Option 2: YouTube Transcriptor (alternative format)
RESPONSE=$(curl -s -X GET \
    "https://youtube-transcriptor.p.rapidapi.com/transcript?video_id=${VIDEO_ID}&lang=en" \
    -H "X-RapidAPI-Key: ${RAPIDAPI_KEY}" \
    -H "X-RapidAPI-Host: youtube-transcriptor.p.rapidapi.com" 2>&1)

if echo "$RESPONSE" | jq -e '.[].text' > /dev/null 2>&1; then
    echo "$RESPONSE" | jq -r '.[].text' | tr '\n' ' '
    exit 0
fi

# Option 3: YouTube Data API Alternative
RESPONSE=$(curl -s -X GET \
    "https://yt-api.p.rapidapi.com/subtitles?id=${VIDEO_ID}" \
    -H "X-RapidAPI-Key: ${RAPIDAPI_KEY}" \
    -H "X-RapidAPI-Host: yt-api.p.rapidapi.com" 2>&1)

if echo "$RESPONSE" | jq -e '.subtitles' > /dev/null 2>&1; then
    echo "$RESPONSE" | jq -r '.subtitles[] | .text' | tr '\n' ' '
    exit 0
fi

# If we got here, something went wrong
echo "Error: Could not fetch transcript. You may need to subscribe to a YouTube Transcript API on RapidAPI."
echo "Recommended: Subscribe to 'YouTube Transcriptor' or 'YouTube Transcript' API"
echo "Last API Response: $RESPONSE" >&2
exit 1
