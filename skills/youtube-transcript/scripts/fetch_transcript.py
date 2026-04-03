#!/usr/bin/env python3
"""
fetch_transcript.py — YouTube transcript fetcher for the youtube-transcript skill.

Usage:
  python3 fetch_transcript.py fetch "<youtube_url>"
      Fetch the transcript and metadata for a YouTube video. Returns JSON.

All output is JSON to stdout. Errors are JSON with an "error" key.

Dependencies:
  Python 3 stdlib only — no pip installs required.

Configuration:
  Reads RAPIDAPI_KEY from the openclaw root .env file:
    /home/claw/.openclaw/.env

  .env format:
    RAPIDAPI_KEY=your_key_here
"""

import sys
import json
import argparse
import re
import html
import os
import urllib.request
import urllib.error
import urllib.parse


# ─── Constants ────────────────────────────────────────────────────────────────

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(SKILL_DIR))), ".env")
RAPIDAPI_HOST = "youtube-transcriptor.p.rapidapi.com"
RAPIDAPI_URL = f"https://{RAPIDAPI_HOST}/transcript"


# ─── .env Loader ─────────────────────────────────────────────────────────────

def load_env(path):
    """
    Parse a simple KEY=value .env file.
    Returns a dict. Lines starting with # and blank lines are ignored.
    Values may optionally be quoted with single or double quotes.
    """
    env = {}
    if not os.path.isfile(path):
        return env
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Strip surrounding quotes
            if len(value) >= 2 and value[0] in ('"', "'") and value[-1] == value[0]:
                value = value[1:-1]
            env[key] = value
    return env


def get_api_key():
    """
    Load RAPIDAPI_KEY from .env file, then fall back to environment variable.
    Returns the key string, or None if not found.
    """
    env = load_env(ENV_FILE)
    return env.get("RAPIDAPI_KEY") or os.environ.get("RAPIDAPI_KEY") or None


# ─── URL Normalisation ─────────────────────────────────────────────────────────

def extract_video_id(url):
    """Extract the 11-character video ID from any YouTube URL form."""
    pattern = re.compile(r'(?:v=|youtu\.be/|shorts/)([A-Za-z0-9_-]{11})')
    m = pattern.search(url)
    return m.group(1) if m else None


# ─── Duration Formatting ───────────────────────────────────────────────────────

def format_duration(secs):
    try:
        secs = int(secs)
    except (TypeError, ValueError):
        return ""
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


# ─── RapidAPI Transcript Fetch ────────────────────────────────────────────────

def fetch_transcript_rapidapi(video_id, api_key):
    """
    Fetch transcript via the RapidAPI youtube-transcriptor endpoint.
    Returns the parsed JSON response dict.
    Raises urllib.error.HTTPError on HTTP errors.
    """
    params = urllib.parse.urlencode({"video_id": video_id})
    url = f"{RAPIDAPI_URL}?{params}"

    req = urllib.request.Request(url, headers={
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": api_key,
        "Accept": "application/json",
    })

    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8", errors="replace")

    return json.loads(body)


# ─── Metadata Fetch ────────────────────────────────────────────────────────────

def fetch_metadata(video_id):
    """
    Fetch video title, channel, and duration from the YouTube page.
    Falls back gracefully — these fields supplement the transcript data.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    req = urllib.request.Request(url, headers={
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            page = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return {"title": "", "channel": "", "duration": "", "duration_seconds": 0}

    pattern = re.compile(
        r'var ytInitialPlayerResponse\s*=\s*(\{.+?\});\s*(?:var |</script)',
        re.DOTALL
    )
    m = pattern.search(page)
    if not m:
        return {"title": "", "channel": "", "duration": "", "duration_seconds": 0}

    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return {"title": "", "channel": "", "duration": "", "duration_seconds": 0}

    vd = data.get("videoDetails", {})
    title = html.unescape(vd.get("title", ""))
    channel = vd.get("author", "")
    duration_secs = vd.get("lengthSeconds", 0)

    return {
        "title": title,
        "channel": channel,
        "duration": format_duration(duration_secs),
        "duration_seconds": int(duration_secs) if duration_secs else 0,
    }


# ─── Transcript Processing ────────────────────────────────────────────────────

def process_transcript(api_response):
    """
    Normalise the RapidAPI response into segments and transcript_text.

    The API returns either a list of dicts (v2/v3 styles) or a single dict.
    We need to find the 'transcription' or 'transcript' key.
    """
    title_from_api = ""
    raw_segments = []
    
    # Identify structure
    if isinstance(api_response, list) and len(api_response) > 0:
        # Check for nested transcription list (v3 style)
        first_item = api_response[0]
        if isinstance(first_item, dict):
            title_from_api = first_item.get("title", "")
            raw_segments = first_item.get("transcription", [])
            # Fallback for other list formats
            if not raw_segments and "transcript" in first_item:
                raw_segments = first_item.get("transcript", [])
    elif isinstance(api_response, dict):
        title_from_api = api_response.get("title", "")
        raw_segments = api_response.get("transcription", api_response.get("transcript", []))

    segments = []
    for s in raw_segments:
        # Handles both 'subtitle' (v3) and 'text' (v2) keys
        text = s.get("subtitle", s.get("text", ""))
        text = html.unescape(str(text).strip())
        if not text:
            continue
            
        try:
            start = float(s.get("start", 0))
            # Handles both 'dur' (v3) and 'duration' (v2) keys
            dur = float(s.get("dur", s.get("duration", 0)))
        except (ValueError, TypeError):
            start = 0
            dur = 0
            
        segments.append({
            "start": round(start, 2),
            "end": round(start + dur, 2),
            "text": text,
        })

    total_count = len(segments)

    # Build transcript text
    parts = []
    for i, seg in enumerate(segments):
        parts.append(seg["text"])
        if i + 1 < len(segments):
            gap = segments[i + 1]["start"] - seg["end"]
            parts.append("\n\n" if gap > 2.0 else " ")
    transcript_text = "".join(parts).strip()

    return title_from_api, segments[:500], transcript_text, total_count


# ─── Main Command ─────────────────────────────────────────────────────────────

def cmd_fetch(url):
    # 1. Check API key
    api_key = get_api_key()
    if not api_key:
        print(json.dumps({
            "error": "missing_api_key",
            "message": (
                f"RAPIDAPI_KEY not found. Add it to {ENV_FILE} as:\n"
                "  RAPIDAPI_KEY=your_key_here\n"
                "or set the RAPIDAPI_KEY environment variable."
            ),
        }, indent=2, ensure_ascii=False))
        return

    # 2. Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        print(json.dumps({
            "error": "invalid_url",
            "message": "Could not extract a YouTube video ID from the provided URL.",
            "url": url,
        }, indent=2, ensure_ascii=False))
        return

    canonical_url = f"https://www.youtube.com/watch?v={video_id}"

    # 3. Fetch transcript via RapidAPI
    try:
        api_response = fetch_transcript_rapidapi(video_id, api_key)
    except urllib.error.HTTPError as e:
        if e.code == 401 or e.code == 403:
            print(json.dumps({
                "error": "auth_failed",
                "message": f"RapidAPI key rejected (HTTP {e.code}). Check your RAPIDAPI_KEY.",
                "video_id": video_id,
            }, indent=2, ensure_ascii=False))
        elif e.code == 429:
            print(json.dumps({
                "error": "rate_limited",
                "message": "RapidAPI rate limit reached. Try again later.",
                "video_id": video_id,
            }, indent=2, ensure_ascii=False))
        elif e.code == 404:
            print(json.dumps({
                "error": "video_unavailable",
                "message": "Video not found or unavailable.",
                "video_id": video_id,
            }, indent=2, ensure_ascii=False))
        else:
            print(json.dumps({
                "error": "fetch_failed",
                "message": f"HTTP {e.code} from RapidAPI.",
                "video_id": video_id,
            }, indent=2, ensure_ascii=False))
        return
    except urllib.error.URLError as e:
        print(json.dumps({
            "error": "fetch_failed",
            "message": f"Network error: {e.reason}",
            "video_id": video_id,
        }, indent=2, ensure_ascii=False))
        return
    except json.JSONDecodeError:
        print(json.dumps({
            "error": "parse_error",
            "message": "RapidAPI returned non-JSON response.",
            "video_id": video_id,
        }, indent=2, ensure_ascii=False))
        return

    # 4. Check for API-level errors in the response body
    if isinstance(api_response, dict) and (api_response.get("error") or "message" in api_response):
        err_msg = api_response.get("message", str(api_response))
        err_lower = err_msg.lower()
        if "disabled" in err_lower or "no captions" in err_lower:
            error_code = "captions_disabled"
        elif "unavailable" in err_lower or "not found" in err_lower:
            error_code = "video_unavailable"
        elif "private" in err_lower:
            error_code = "private_video"
        else:
            error_code = "fetch_failed"
        print(json.dumps({
            "error": error_code,
            "message": err_msg,
            "video_id": video_id,
        }, indent=2, ensure_ascii=False))
        return

    # 5. Process transcript
    title_from_api, segments, transcript_text, total_count = process_transcript(api_response)

    if not transcript_text:
         print(json.dumps({
            "error": "no_captions",
            "message": f"No transcript text found in API response.",
            "video_id": video_id,
        }, indent=2, ensure_ascii=False))
         return

    # 6. Fetch metadata to supplement (title fallback, channel, duration)
    meta = fetch_metadata(video_id)
    title = meta["title"] or title_from_api

    # 7. Output result
    result = {
        "video_id": video_id,
        "title": title,
        "channel": meta["channel"],
        "url": canonical_url,
        "duration": meta["duration"],
        "duration_seconds": meta["duration_seconds"],
        "transcript_text": transcript_text,
        "segments": segments,
        "segment_count": total_count,
        "error": None,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch YouTube video transcript and metadata via RapidAPI."
    )
    subparsers = parser.add_subparsers(dest="command")
    fetch_parser = subparsers.add_parser("fetch", help="Fetch transcript for a YouTube URL")
    fetch_parser.add_argument("url", help="YouTube video URL")

    args = parser.parse_args()
    if args.command == "fetch":
        cmd_fetch(args.url)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
