#!/usr/bin/env python3
"""
Reddit Reader - fetch posts and search results from Reddit's public JSON API.

Usage:
    python3 fetch_reddit.py subreddit <name> [--listing hot|new|top|rising] [--limit N] [--time day|week|month|year|all]
    python3 fetch_reddit.py search "<query>" [--subreddit all] [--sort relevance|top|new|comments] [--limit N] [--time month|week|year|all]
    python3 fetch_reddit.py comments <subreddit> <post_id>
"""

import argparse
import json
import subprocess
import sys
import urllib.parse

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
BASE = "https://www.reddit.com"


def make_request(url, params=None):
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    result = subprocess.run(
        ["curl", "-s", "-A", USER_AGENT, "--max-time", "15", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Request failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"Invalid JSON response from {url}", file=sys.stderr)
        print(result.stdout[:500], file=sys.stderr)
        sys.exit(1)
    if isinstance(data, dict) and data.get("error"):
        print(f"Reddit error {data['error']}: {data.get('message', '')}", file=sys.stderr)
        sys.exit(1)
    return data


def format_post(post, include_subreddit=False):
    score = post.get("score", 0)
    comments = post.get("num_comments", 0)
    title = post.get("title", "(no title)")
    permalink = f"https://reddit.com{post.get('permalink', '')}"
    sub = post.get("subreddit_name_prefixed", "")
    flair = post.get("link_flair_text", "")
    flair_str = f" [{flair}]" if flair else ""

    lines = [f"  {title}{flair_str}"]
    if include_subreddit and sub:
        lines.append(f"    {sub} | {score} pts | {comments} comments")
    else:
        lines.append(f"    {score} pts | {comments} comments")
    lines.append(f"    {permalink}")
    return "\n".join(lines)


def cmd_subreddit(args):
    listing = args.listing or "hot"
    limit = min(args.limit or 25, 100)
    params = {"limit": limit}
    if listing == "top":
        params["t"] = args.time or "week"

    url = f"{BASE}/r/{args.name}/{listing}.json"
    data = make_request(url, params)
    posts = data["data"]["children"]

    if not posts:
        print(f"No posts found in r/{args.name}.")
        return

    print(f"\nr/{args.name} — {listing.upper()} ({len(posts)} posts)\n{'─'*60}")
    for i, child in enumerate(posts, 1):
        print(f"\n{i}.")
        print(format_post(child["data"]))

    # Print pagination token for follow-up fetches
    after = data["data"].get("after")
    if after:
        print(f"\n[Next page token: {after}]")


def cmd_search(args):
    query = args.query
    subreddit = args.subreddit or "all"
    sort = args.sort or "relevance"
    limit = min(args.limit or 25, 100)
    timeframe = args.time or "month"

    if subreddit == "all":
        url = f"{BASE}/search.json"
        params = {"q": query, "sort": sort, "t": timeframe, "limit": limit}
    else:
        url = f"{BASE}/r/{subreddit}/search.json"
        params = {"q": query, "sort": sort, "t": timeframe, "limit": limit, "restrict_sr": 1}

    data = make_request(url, params)
    posts = data["data"]["children"]

    if not posts:
        print(f"No results found for '{query}'.")
        return

    include_sub = subreddit == "all"
    scope = f"r/{subreddit}" if subreddit != "all" else "all of Reddit"
    print(f"\nSearch: \"{query}\" in {scope} — {sort.upper()} / {timeframe} ({len(posts)} results)\n{'─'*60}")
    for i, child in enumerate(posts, 1):
        print(f"\n{i}.")
        print(format_post(child["data"], include_subreddit=include_sub))


def cmd_comments(args):
    url = f"{BASE}/r/{args.subreddit}/comments/{args.post_id}.json"
    data = make_request(url)

    post = data[0]["data"]["children"][0]["data"]
    print(f"\n{post['title']}")
    print(f"r/{post['subreddit']} | {post['score']} pts | {post['num_comments']} comments")
    print(f"https://reddit.com{post['permalink']}\n{'─'*60}\n")

    comments = data[1]["data"]["children"]
    shown = 0
    for child in comments:
        if child["kind"] != "t1":
            continue
        c = child["data"]
        author = c.get("author", "[deleted]")
        score = c.get("score", 0)
        body = c.get("body", "").strip().replace("\n", " ")
        if len(body) > 300:
            body = body[:297] + "..."
        print(f"u/{author} ({score} pts): {body}\n")
        shown += 1
        if shown >= 20:
            break

    if shown == 0:
        print("No comments found.")


def main():
    parser = argparse.ArgumentParser(description="Fetch Reddit content")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # subreddit command
    sub_p = subparsers.add_parser("subreddit", help="Browse a subreddit")
    sub_p.add_argument("name", help="Subreddit name (without r/)")
    sub_p.add_argument("--listing", choices=["hot", "new", "top", "rising"], default="hot")
    sub_p.add_argument("--limit", type=int, default=25)
    sub_p.add_argument("--time", choices=["hour", "day", "week", "month", "year", "all"], default="week")

    # search command
    srch_p = subparsers.add_parser("search", help="Search Reddit for a topic")
    srch_p.add_argument("query", help="Search query")
    srch_p.add_argument("--subreddit", default="all", help="Restrict to subreddit (default: all)")
    srch_p.add_argument("--sort", choices=["relevance", "hot", "top", "new", "comments"], default="relevance")
    srch_p.add_argument("--limit", type=int, default=25)
    srch_p.add_argument("--time", choices=["hour", "day", "week", "month", "year", "all"], default="month")

    # comments command
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
