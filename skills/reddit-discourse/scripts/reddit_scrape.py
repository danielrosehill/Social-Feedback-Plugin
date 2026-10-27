#!/usr/bin/env python3
"""Scrape subreddit-scoped Reddit searches (or thread URLs) via Apify and print a digest.

Reddit blocks agent fetches (403 on www/old.reddit.com JSON, PullPush rate-limited,
Exa returns no reddit.com results, the Chrome extension refuses reddit.com — all
observed 2026-10-27). Apify's `trudax/reddit-scraper-lite` actor works.

Needs APIFY_TOKEN in the environment. Stdlib only.

    reddit_scrape.py --sub LocalLLaMA --sub MachineLearning \
        --query "runpod vast" --query "modal fine-tune" \
        --keyword runpod --keyword vast --time year --out /tmp/reddit/items.json

Cost: pay per result, about $0.004 per item (400 items = $1.63, 2026-10-27).
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ACTOR = "trudax~reddit-scraper-lite"
API = "https://api.apify.com/v2"


def call(method, path, token, body=None):
    url = f"{API}{path}{'&' if '?' in path else '?'}token={token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sub", action="append", default=[], help="subreddit without r/ (repeatable)")
    ap.add_argument("--query", action="append", default=[], help="search query; run in every --sub (repeatable)")
    ap.add_argument("--url", action="append", default=[], help="extra thread or listing URL (repeatable)")
    ap.add_argument("--time", default="year", choices=["hour", "day", "week", "month", "year", "all"])
    ap.add_argument("--sort", default="relevance", choices=["relevance", "hot", "top", "new", "comments"])
    ap.add_argument("--max-items", type=int, default=300, help="hard cap on posts+comments (the cost cap)")
    ap.add_argument("--max-posts", type=int, default=8, help="posts per search URL")
    ap.add_argument("--max-comments", type=int, default=25, help="comments per post")
    ap.add_argument("--keyword", action="append", default=[], help="digest: only show comments matching any (regex, case-insensitive)")
    ap.add_argument("--top", type=int, default=40, help="digest: comments to print")
    ap.add_argument("--out", required=True, help="where to save the raw items JSON")
    a = ap.parse_args()

    token = os.environ.get("APIFY_TOKEN")
    if not token:
        sys.exit("APIFY_TOKEN not set")
    if not (a.sub and a.query) and not a.url:
        sys.exit("give --sub with --query, and/or --url")

    urls = [{"url": f"https://www.reddit.com/r/{s}/search/?q={urllib.parse.quote(q)}"
                    f"&restrict_sr=1&sort={a.sort}&t={a.time}"}
            for s in a.sub for q in a.query] + [{"url": u} for u in a.url]
    run_input = {"startUrls": urls, "maxItems": a.max_items, "maxPostCount": a.max_posts,
                 "maxComments": a.max_comments, "skipComments": False, "includeNSFW": False}

    # Async run + poll: the run-sync endpoint 502s on runs longer than a few minutes.
    run = call("POST", f"/acts/{ACTOR}/runs", token, run_input)["data"]
    print(f"run {run['id']} started, {len(urls)} start URLs", file=sys.stderr)
    while run["status"] in ("READY", "RUNNING"):
        time.sleep(15)
        run = call("GET", f"/actor-runs/{run['id']}", token)["data"]
    print(f"run {run['status']}, ${run.get('usageTotalUsd') or 0:.2f}", file=sys.stderr)
    items = call("GET", f"/datasets/{run['defaultDatasetId']}/items?clean=1", token)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(items, open(a.out, "w"))

    posts = [i for i in items if i.get("dataType") == "post"]
    comments = [i for i in items if i.get("dataType") == "comment"]
    print(f"\n{len(posts)} posts, {len(comments)} comments -> {a.out}\n")
    for p in posts:
        print(f"P {p.get('createdAt', '')[:10]} {p.get('communityName')} c={p.get('numberOfComments')} | "
              f"{html.unescape(p.get('title') or '')[:110]}\n  {p.get('url')}")
    kw = re.compile("|".join(a.keyword), re.I) if a.keyword else None
    hits = [c for c in comments if not kw or kw.search(c.get("body") or "")]
    hits.sort(key=lambda c: -(c.get("upVotes") or 0))
    print(f"\n{len(hits)} matching comments, top {a.top} by upvotes:")
    for c in hits[:a.top]:
        body = html.unescape(c.get("body") or "").replace("\n", " ")
        print(f"- {c.get('createdAt', '')[:10]} {c.get('communityName')} +{c.get('upVotes')} | {body[:300]}")


if __name__ == "__main__":
    main()
