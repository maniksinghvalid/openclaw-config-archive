#!/usr/bin/env python3
"""
Reddit Reader - fetch posts and search results via old.reddit.com Atom/RSS feeds.

www.reddit.com blocks anonymous JSON/RSS with HTTP 403. old.reddit.com still
serves anonymous RSS, so we parse Atom feeds. Trade-off: score and comment
counts are not in RSS; we show author + timestamp instead. Sort by-top/by-day
is still server-side via the listing type and `t` parameter.

Usage:
    python3 fetch_reddit.py subreddit <name> [--listing hot|new|top|rising] [--limit N] [--time hour|day|week|month|year|all]
    python3 fetch_reddit.py search "<query>" [--subreddit all] [--sort relevance|top|new|comments|hot] [--limit N] [--time hour|day|week|month|year|all]
    python3 fetch_reddit.py comments <subreddit> <post_id>
"""

import argparse
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import re
import html

USER_AGENT = "openclaw-reddit-reader/2.0"
BASE = "https://old.reddit.com"
NS = {"a": "http://www.w3.org/2005/Atom"}


def fetch_feed(url, params=None):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/atom+xml,application/xml"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read()
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} fetching {url}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)
    try:
        return ET.fromstring(body)
    except ET.ParseError:
        print(f"Invalid XML response from {url}", file=sys.stderr)
        print(body[:500].decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(1)


def entry_post_id(entry):
    raw = entry.findtext("a:id", default="", namespaces=NS)
    return raw.split("_", 1)[1] if "_" in raw else raw


def entry_subreddit(entry):
    cat = entry.find("a:category", NS)
    return cat.get("label") if cat is not None else ""


def entry_author(entry):
    auth = entry.find("a:author/a:name", NS)
    name = (auth.text or "").strip() if auth is not None else ""
    if name.startswith("/u/"):
        name = name[3:]
    elif name.startswith("u/"):
        name = name[2:]
    return name or "[unknown]"


def entry_link(entry):
    link = entry.find("a:link", NS)
    return link.get("href", "") if link is not None else ""


def entry_published(entry):
    return entry.findtext("a:published", default="", namespaces=NS)[:10]


def format_post(entry, include_subreddit=False):
    title = (entry.findtext("a:title", default="(no title)", namespaces=NS) or "").strip()
    title = html.unescape(title)
    author = entry_author(entry)
    published = entry_published(entry)
    permalink = entry_link(entry)
    sub = entry_subreddit(entry)

    lines = [f"  {title}"]
    meta = []
    if include_subreddit and sub:
        meta.append(sub)
    meta.append(f"by u/{author}")
    if published:
        meta.append(published)
    lines.append(f"    {' | '.join(meta)}")
    lines.append(f"    {permalink}")
    return "\n".join(lines)


def cmd_subreddit(args):
    listing = args.listing or "hot"
    limit = min(args.limit or 25, 100)
    params = {"limit": limit}
    if listing == "top":
        params["t"] = args.time or "week"

    url = f"{BASE}/r/{args.name}/{listing}.rss"
    root = fetch_feed(url, params)
    entries = root.findall("a:entry", NS)

    if not entries:
        print(f"No posts found in r/{args.name}.")
        return

    print(f"\nr/{args.name} — {listing.upper()} ({len(entries)} posts)\n{'─'*60}")
    for i, entry in enumerate(entries, 1):
        print(f"\n{i}.")
        print(format_post(entry))


def cmd_search(args):
    query = args.query
    subreddit = args.subreddit or "all"
    sort = args.sort or "relevance"
    limit = min(args.limit or 25, 100)
    timeframe = args.time or "month"

    if subreddit == "all":
        url = f"{BASE}/search.rss"
        params = {"q": query, "sort": sort, "t": timeframe, "limit": limit}
    else:
        url = f"{BASE}/r/{subreddit}/search.rss"
        params = {"q": query, "sort": sort, "t": timeframe, "limit": limit, "restrict_sr": 1}

    root = fetch_feed(url, params)
    entries = root.findall("a:entry", NS)

    if not entries:
        print(f"No results found for '{query}'.")
        return

    include_sub = subreddit == "all"
    scope = f"r/{subreddit}" if subreddit != "all" else "all of Reddit"
    print(f"\nSearch: \"{query}\" in {scope} — {sort.upper()} / {timeframe} ({len(entries)} results)\n{'─'*60}")
    for i, entry in enumerate(entries, 1):
        print(f"\n{i}.")
        print(format_post(entry, include_subreddit=include_sub))


def strip_html(s):
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def cmd_comments(args):
    url = f"{BASE}/r/{args.subreddit}/comments/{args.post_id}.rss"
    params = {"limit": 25}
    root = fetch_feed(url, params)
    entries = root.findall("a:entry", NS)

    if not entries:
        print("No content found.")
        return

    # First entry is the original post; subsequent entries are comments.
    op = entries[0]
    op_title = (op.findtext("a:title", default="", namespaces=NS) or "").strip()
    print(f"\n{html.unescape(op_title)}")
    print(f"r/{args.subreddit} | by u/{entry_author(op)} | {entry_published(op)}")
    print(f"{entry_link(op)}\n{'─'*60}\n")

    shown = 0
    for entry in entries[1:]:
        author = entry_author(entry)
        body_html = entry.findtext("a:content", default="", namespaces=NS) or ""
        body = strip_html(body_html).replace("\n", " ")
        if len(body) > 300:
            body = body[:297] + "..."
        if not body:
            continue
        print(f"u/{author}: {body}\n")
        shown += 1
        if shown >= 20:
            break

    if shown == 0:
        print("No comments found.")


def main():
    parser = argparse.ArgumentParser(description="Fetch Reddit content via old.reddit.com RSS")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sub_p = subparsers.add_parser("subreddit", help="Browse a subreddit")
    sub_p.add_argument("name", help="Subreddit name (without r/)")
    sub_p.add_argument("--listing", choices=["hot", "new", "top", "rising"], default="hot")
    sub_p.add_argument("--limit", type=int, default=25)
    sub_p.add_argument("--time", choices=["hour", "day", "week", "month", "year", "all"], default="week")

    srch_p = subparsers.add_parser("search", help="Search Reddit for a topic")
    srch_p.add_argument("query", help="Search query")
    srch_p.add_argument("--subreddit", default="all", help="Restrict to subreddit (default: all)")
    srch_p.add_argument("--sort", choices=["relevance", "hot", "top", "new", "comments"], default="relevance")
    srch_p.add_argument("--limit", type=int, default=25)
    srch_p.add_argument("--time", choices=["hour", "day", "week", "month", "year", "all"], default="month")

    cmt_p = subparsers.add_parser("comments", help="Fetch comments for a post")
    cmt_p.add_argument("subreddit", help="Subreddit name")
    cmt_p.add_argument("post_id", help="Post ID (alphanumeric, from post URL)")

    args = parser.parse_args()

    if args.command == "subreddit":
        cmd_subreddit(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "comments":
        cmd_comments(args)


if __name__ == "__main__":
    main()
