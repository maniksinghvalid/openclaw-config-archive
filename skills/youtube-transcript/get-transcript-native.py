#!/usr/bin/env python3
"""
Fetch YouTube transcript without external dependencies (no API, no pip packages)
"""
import sys
import json
import re
import urllib.request
import urllib.parse
from html import unescape

def get_video_id(url_or_id):
    """Extract video ID from URL or return as-is if already an ID"""
    if 'youtube.com' in url_or_id or 'youtu.be' in url_or_id:
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be\/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
    return url_or_id

def fetch_transcript(video_id):
    """Fetch transcript from YouTube page source"""
    try:
        url = f'https://www.youtube.com/watch?v={video_id}'
        
        # Fetch the page
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
        
        # Extract caption tracks from page JSON
        pattern = r'"captions":\s*({[^}]+?"captionTracks":\s*\[[^\]]+\][^}]+})'
        match = re.search(pattern, html)
        
        if not match:
            return None, "No captions found for this video"
        
        captions_json = match.group(1)
        # Fix nested JSON
        captions_json = re.sub(r'}\s*,\s*"', '},"', captions_json)
        
        try:
            captions_data = json.loads(captions_json)
        except:
            # Try to extract the captionTracks array directly
            tracks_match = re.search(r'"captionTracks":\s*(\[[^\]]+\])', captions_json)
            if not tracks_match:
                return None, "Could not parse caption data"
            
            tracks = json.loads(tracks_match.group(1))
            if not tracks:
                return None, "No caption tracks available"
            
            # Get the first English track or any track
            caption_url = None
            for track in tracks:
                if 'baseUrl' in track:
                    caption_url = track['baseUrl']
                    break
            
            if not caption_url:
                return None, "No caption URL found"
            
            # Fetch the caption XML
            with urllib.request.urlopen(caption_url, timeout=10) as response:
                caption_xml = response.read().decode('utf-8')
            
            # Extract text from XML
            texts = re.findall(r'<text[^>]*>([^<]+)</text>', caption_xml)
            transcript = ' '.join([unescape(t) for t in texts])
            
            return transcript, None
            
    except Exception as e:
        return None, f"Error fetching transcript: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: get-transcript-native.py <VIDEO_ID_OR_URL>", file=sys.stderr)
        sys.exit(1)
    
    video_id = get_video_id(sys.argv[1])
    transcript, error = fetch_transcript(video_id)
    
    if error:
        print(error, file=sys.stderr)
        sys.exit(1)
    
    print(transcript)

if __name__ == '__main__':
    main()
