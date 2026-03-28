#!/usr/bin/env python3
"""
fetch_podcast.py — Podcast RSS fetcher for the spotify-podcast-digest skill.

Usage:
  python3 fetch_podcast.py search "<podcast name>"
      Search Apple Podcasts for a podcast and return RSS feed URL + recent episodes.

  python3 fetch_podcast.py episode "<rss_feed_url>" [--latest | --number N | --keyword "word" | --date YYYY-MM-DD]
      Fetch a specific episode from an RSS feed and return full content as JSON.

  python3 fetch_podcast.py from-spotify "<spotify_url>"
      Parse a Spotify show/episode URL and extract the podcast name for use with 'search'.

All output is JSON to stdout. Errors are JSON with an "error" key.
"""

import sys
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import html
import re
from html.parser import HTMLParser
from datetime import datetime


# ─── HTML Stripping ──────────────────────────────────────────────────────────

class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self._parts = []
        self._skip_tags = {'script', 'style'}
        self._block_tags = {'p', 'br', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'tr'}
        self._in_skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._in_skip += 1
        if tag in self._block_tags:
            self._parts.append('\n')

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._in_skip -= 1
        if tag in self._block_tags:
            self._parts.append('\n')

    def handle_data(self, data):
        if self._in_skip == 0:
            self._parts.append(data)

    def get_text(self):
        text = ''.join(self._parts)
        # Collapse multiple blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()


def strip_html(raw: str) -> str:
    if not raw:
        return ''
    raw = html.unescape(raw)
    stripper = _HTMLStripper()
    try:
        stripper.feed(raw)
        return stripper.get_text()
    except Exception:
        # Fallback: crude tag removal
        return re.sub(r'<[^>]+>', ' ', raw).strip()


# ─── Link Extraction ─────────────────────────────────────────────────────────

def extract_links(raw_html: str, max_links: int = 8) -> list:
    """Extract href links with their anchor text from HTML."""
    links = []
    pattern = re.compile(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
    for match in pattern.finditer(raw_html):
        url = match.group(1).strip()
        text = strip_html(match.group(2)).strip()
        if not text:
            text = url
        if url.startswith('http') and len(text) < 200:
            links.append({'text': text, 'url': url})
        if len(links) >= max_links:
            break
    return links


# ─── HTTP Helpers ─────────────────────────────────────────────────────────────

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; PodcastDigestBot/1.0)',
    'Accept': 'application/json, application/xml, text/xml, */*',
}


def fetch_url(url: str, timeout: int = 15) -> bytes:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


# ─── Duration Formatting ──────────────────────────────────────────────────────

def format_duration(raw: str) -> str:
    """Convert iTunes duration (HH:MM:SS or seconds) to human-readable string."""
    if not raw:
        return ''
    raw = raw.strip()
    if ':' in raw:
        parts = raw.split(':')
        try:
            if len(parts) == 3:
                h, m, s = int(parts[0]), int(parts[1]), int(float(parts[2]))
            else:
                h, m, s = 0, int(parts[0]), int(float(parts[1]))
            if h > 0:
                return f'{h}h {m}m'
            return f'{m}m'
        except ValueError:
            return raw
    try:
        secs = int(float(raw))
        h, rem = divmod(secs, 3600)
        m, _ = divmod(rem, 60)
        if h > 0:
            return f'{h}h {m}m'
        return f'{m}m'
    except ValueError:
        return raw


# ─── Date Formatting ──────────────────────────────────────────────────────────

def format_pub_date(raw: str) -> str:
    """Parse RFC 2822 pubDate and return 'Month DD, YYYY'."""
    if not raw:
        return ''
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M:%S',
        '%d %b %Y %H:%M:%S %z',
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(raw.strip(), fmt)
            return dt.strftime('%B %d, %Y')
        except ValueError:
            continue
    # Try extracting just the date portion
    m = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', raw)
    if m:
        try:
            return datetime.strptime(m.group(1), '%d %b %Y').strftime('%B %d, %Y')
        except ValueError:
            pass
    return raw.strip()


def pub_date_to_iso(raw: str) -> str:
    """Return YYYY-MM-DD for a pubDate string, for date-based filtering."""
    formats = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M:%S',
        '%d %b %Y %H:%M:%S %z',
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(raw.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    m = re.search(r'(\d{4}-\d{2}-\d{2})', raw)
    if m:
        return m.group(1)
    return ''


# ─── RSS Namespaces ───────────────────────────────────────────────────────────

ITUNES_NS = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
CONTENT_NS = 'http://purl.org/rss/1.0/modules/content/'

NS = {
    'itunes': ITUNES_NS,
    'content': CONTENT_NS,
}


def _tag(ns_key: str, name: str) -> str:
    return f'{{{NS[ns_key]}}}{name}'


def _get_text(el, tag: str, default: str = '') -> str:
    child = el.find(tag)
    return (child.text or '').strip() if child is not None else default


def _get_ns_text(el, ns_key: str, name: str, default: str = '') -> str:
    child = el.find(_tag(ns_key, name))
    return (child.text or '').strip() if child is not None else default


# ─── RSS Parsing ──────────────────────────────────────────────────────────────

def parse_episode(item: ET.Element, podcast_name: str) -> dict:
    title = _get_text(item, 'title')
    pub_date_raw = _get_text(item, 'pubDate')
    link = _get_text(item, 'link')
    description_raw = _get_text(item, 'description')
    content_encoded_raw = _get_ns_text(item, 'content', 'encoded')
    duration_raw = _get_ns_text(item, 'itunes', 'duration')
    ep_number_raw = _get_ns_text(item, 'itunes', 'episode')
    guid = _get_text(item, 'guid')

    # Prefer content:encoded for richer show notes
    raw_html = content_encoded_raw or description_raw
    content_text = strip_html(raw_html)
    links = extract_links(raw_html) if raw_html else []

    # Enclosure (audio file)
    enclosure = item.find('enclosure')
    enclosure_url = enclosure.get('url', '') if enclosure is not None else ''

    # Episode number
    try:
        ep_number = int(ep_number_raw) if ep_number_raw else None
    except ValueError:
        ep_number = None

    return {
        'podcast_name': podcast_name,
        'episode_title': title,
        'episode_number': ep_number,
        'pub_date': pub_date_to_iso(pub_date_raw),
        'pub_date_formatted': format_pub_date(pub_date_raw),
        'duration': format_duration(duration_raw),
        'description': strip_html(description_raw)[:500],
        'content': content_text[:8000],
        'links': links,
        'episode_url': link or guid,
        'enclosure_url': enclosure_url,
        'spotify_url': '',  # populated if known from input
        'error': None,
    }


# ─── Command: from-spotify ────────────────────────────────────────────────────

def cmd_from_spotify(spotify_url: str) -> dict:
    """
    Parse a Spotify URL and extract the podcast/episode name by fetching
    the Open Graph metadata from the Spotify web page.
    """
    # Validate URL shape
    url = spotify_url.strip()
    m = re.match(r'https?://open\.spotify\.com/(show|episode)/([A-Za-z0-9]+)', url)
    if not m:
        return {'error': 'invalid_spotify_url', 'message': 'Expected open.spotify.com/show/... or open.spotify.com/episode/...'}

    resource_type = m.group(1)   # 'show' or 'episode'
    resource_id = m.group(2)

    try:
        data = fetch_url(url, timeout=10).decode('utf-8', errors='replace')
    except Exception as e:
        return {'error': 'fetch_failed', 'message': str(e)}

    # Extract og:title
    og_title_m = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]*content=["\']([^"\']+)["\']', data)
    if not og_title_m:
        og_title_m = re.search(r'<title>([^<]+)</title>', data)

    podcast_name = ''
    episode_title = ''
    episode_spotify_url = ''

    if og_title_m:
        raw_title = html.unescape(og_title_m.group(1).strip())
        # Spotify og:title for episodes is usually "Episode Title | Podcast Name"
        if resource_type == 'episode' and ' | ' in raw_title:
            parts = raw_title.split(' | ', 1)
            episode_title = parts[0].strip()
            podcast_name = parts[1].strip()
            episode_spotify_url = url
        else:
            podcast_name = raw_title

    # Clean " | Spotify" suffix
    for suffix in [' | Spotify', '- Spotify']:
        if podcast_name.endswith(suffix):
            podcast_name = podcast_name[:-len(suffix)].strip()

    # Build search term: just the podcast name, cleaned up
    search_term = podcast_name.strip()

    return {
        'resource_type': resource_type,
        'resource_id': resource_id,
        'podcast_name': podcast_name,
        'episode_title': episode_title,
        'episode_spotify_url': episode_spotify_url,
        'spotify_show_url': f'https://open.spotify.com/show/{resource_id}' if resource_type == 'show' else '',
        'search_term': search_term,
        'error': None,
    }


# ─── Command: search ─────────────────────────────────────────────────────────

def cmd_search(query: str) -> dict:
    """Search Apple Podcasts for a podcast and return RSS feed candidates."""
    encoded = urllib.parse.quote(query)
    url = f'https://itunes.apple.com/search?term={encoded}&entity=podcast&limit=5'

    try:
        raw = fetch_url(url, timeout=10)
        data = json.loads(raw)
    except urllib.error.HTTPError as e:
        return {'error': 'api_error', 'message': f'HTTP {e.code}'}
    except Exception as e:
        return {'error': 'fetch_failed', 'message': str(e)}

    results_raw = data.get('results', [])
    if not results_raw:
        return {'error': 'no_results', 'message': f'No podcasts found for "{query}"', 'results': []}

    results = []
    for i, r in enumerate(results_raw):
        feed_url = r.get('feedUrl', '')
        if not feed_url:
            continue
        results.append({
            'rank': i + 1,
            'name': r.get('collectionName', ''),
            'artist': r.get('artistName', ''),
            'feed_url': feed_url,
            'itunes_url': r.get('collectionViewUrl', ''),
            'episode_count': r.get('trackCount', 0),
            'latest_episode_date': r.get('releaseDate', '')[:10] if r.get('releaseDate') else '',
            'artwork_url': r.get('artworkUrl100', ''),
        })

    return {'query': query, 'results': results, 'error': None}


# ─── Command: episode ─────────────────────────────────────────────────────────

def cmd_episode(feed_url: str, selector: dict) -> dict:
    """
    Fetch and parse an RSS feed, then return the target episode as JSON.

    selector is one of:
      {'mode': 'latest'}
      {'mode': 'number', 'value': 42}
      {'mode': 'keyword', 'value': 'machine learning'}
      {'mode': 'date', 'value': '2026-03-15'}
    """
    try:
        raw_xml = fetch_url(feed_url, timeout=15)
    except urllib.error.HTTPError as e:
        return {'error': 'feed_fetch_failed', 'message': f'HTTP {e.code} from {feed_url}'}
    except Exception as e:
        return {'error': 'feed_fetch_failed', 'message': str(e)}

    try:
        root = ET.fromstring(raw_xml)
    except ET.ParseError as e:
        return {'error': 'feed_parse_error', 'message': str(e)}

    channel = root.find('channel')
    if channel is None:
        return {'error': 'invalid_feed', 'message': 'No <channel> element found in RSS'}

    podcast_name = _get_text(channel, 'title') or _get_ns_text(channel, 'itunes', 'author')
    items = channel.findall('item')

    if not items:
        return {'error': 'no_episodes', 'message': 'RSS feed contains no episodes', 'podcast_name': podcast_name}

    mode = selector.get('mode', 'latest')

    if mode == 'latest':
        return parse_episode(items[0], podcast_name)

    elif mode == 'number':
        target = selector['value']
        for item in items:
            ep_num_raw = _get_ns_text(item, 'itunes', 'episode')
            try:
                if ep_num_raw and int(ep_num_raw) == target:
                    return parse_episode(item, podcast_name)
            except ValueError:
                pass
        # Fallback: count from end of feed (some feeds don't use itunes:episode)
        if 1 <= target <= len(items):
            return parse_episode(items[-target], podcast_name)
        return _not_found(podcast_name, items, f'episode #{target}')

    elif mode == 'keyword':
        kw = selector['value'].lower()
        for item in items:
            title = _get_text(item, 'title').lower()
            desc = _get_text(item, 'description').lower()
            if kw in title or kw in desc:
                return parse_episode(item, podcast_name)
        return _not_found(podcast_name, items, f'keyword "{selector["value"]}"')

    elif mode == 'date':
        target_date = selector['value']  # YYYY-MM-DD
        for item in items:
            raw_pub = _get_text(item, 'pubDate')
            iso = pub_date_to_iso(raw_pub)
            if iso == target_date:
                return parse_episode(item, podcast_name)
        return _not_found(podcast_name, items, f'date {target_date}')

    else:
        return {'error': 'invalid_selector', 'message': f'Unknown mode: {mode}'}


def _not_found(podcast_name: str, items: list, descriptor: str) -> dict:
    """Return an error with recent episode titles for user disambiguation."""
    recent = []
    for item in items[:5]:
        title = _get_text(item, 'title')
        pub = format_pub_date(_get_text(item, 'pubDate'))
        ep_num = _get_ns_text(item, 'itunes', 'episode')
        recent.append({'title': title, 'pub_date': pub, 'episode_number': ep_num or None})
    return {
        'error': 'episode_not_found',
        'message': f'Could not find episode matching {descriptor} in "{podcast_name}"',
        'podcast_name': podcast_name,
        'recent_episodes': recent,
    }


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Podcast RSS fetcher for spotify-podcast-digest.')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # from-spotify
    p_fs = subparsers.add_parser('from-spotify', help='Resolve a Spotify URL to podcast info')
    p_fs.add_argument('url', help='Spotify show or episode URL')

    # search
    p_search = subparsers.add_parser('search', help='Search Apple Podcasts for an RSS feed')
    p_search.add_argument('query', help='Podcast name to search for')

    # episode
    p_ep = subparsers.add_parser('episode', help='Fetch an episode from an RSS feed')
    p_ep.add_argument('feed_url', help='RSS feed URL')
    group = p_ep.add_mutually_exclusive_group()
    group.add_argument('--latest', action='store_true', help='Fetch the latest episode (default)')
    group.add_argument('--number', type=int, metavar='N', help='Fetch episode by number')
    group.add_argument('--keyword', metavar='WORD', help='Fetch episode matching keyword in title/description')
    group.add_argument('--date', metavar='YYYY-MM-DD', help='Fetch episode published on this date')

    args = parser.parse_args()

    if args.command == 'from-spotify':
        result = cmd_from_spotify(args.url)

    elif args.command == 'search':
        result = cmd_search(args.query)

    elif args.command == 'episode':
        if args.number is not None:
            selector = {'mode': 'number', 'value': args.number}
        elif args.keyword:
            selector = {'mode': 'keyword', 'value': args.keyword}
        elif args.date:
            selector = {'mode': 'date', 'value': args.date}
        else:
            selector = {'mode': 'latest'}
        result = cmd_episode(args.feed_url, selector)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
