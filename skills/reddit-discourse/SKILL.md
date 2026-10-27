---
name: reddit-discourse
description: Search Reddit for user discourse about a topic, product, provider, or tool. Best single source for "is X any good" — surfaces real user experiences, complaints, and recurring pain points from topic-specific subreddits. Use when the user wants community opinion on consumer products, hosting providers, dev tools, hardware, or services, or asks for "real Reddit feedback".
---

# Reddit Discourse

Reddit is the largest pool of unfiltered user discourse on the open web, and subreddits self-organise by topic, so signal is dense when the search is scoped to the right subreddit.

## Route: Apify, not a fetch

Reddit blocks agents. Each of these failed on 2026-10-27, so don't spend a turn on them:

| Route | Result |
|---|---|
| WebFetch `www.reddit.com` / `old.reddit.com` | blocked |
| curl `…/search.json` | 403 |
| PullPush archive API | rate-limited ("contact the administrator on Discord") |
| WebSearch `site:reddit.com …` | no Reddit URLs returned |
| Exa with `includeDomains: ["reddit.com"]` | 0 results (Reddit is not in Exa's index) |
| Claude in Chrome | "This site is not allowed due to safety restrictions" |

What works: the Apify actor **`trudax/reddit-scraper-lite`**, through `scripts/reddit_scrape.py` in this skill. It needs `APIFY_TOKEN` in the environment (Daniel's machines: Infisical project `residence`, so run it under `with-secrets`).

**Cost:** about $0.004 per item, where posts and comments both count. The 400-item pull for the episode below cost $1.63. `--max-items` is the cost cap, and 200–400 is enough for one topic.

## Steps

1. **Pick 3–6 subreddits** where people who actually use the thing post (hints below). Scoped searches beat a global search, which on 2026-10-27 returned threads about underwear fabric and dubstep for "modal vs runpod".
2. **Write 1–4 short queries**: product names and "X vs Y". Every query runs in every subreddit, so keep the count down.
3. Run it:

   ```bash
   with-secrets python3 <skill-dir>/scripts/reddit_scrape.py \
     --sub LocalLLaMA --sub MachineLearning --query "runpod vast" --query "modal fine-tune" \
     --keyword runpod --keyword vast --keyword modal \
     --time year --max-items 300 --out /tmp/reddit-<slug>/items.json
   ```

   The script starts the run asynchronously and polls it, because the run-sync endpoint returns 502 after a few minutes. It saves the raw items and prints a digest: posts, then matching comments by upvotes. Add `--url <thread>` to pull a specific thread's comments.
4. **Read the strongest threads in full** from the saved JSON (comments carry `postId`). Prefer threads with many comments over many upvotes, because discussion tells you more than endorsement.
5. **Report** with each claim attributed to its subreddit and month ("r/LocalLLaMA, May 2026"), and treat each one as a single person's anecdote. Quote short phrases and paraphrase the rest. Name what was thin: a product that barely appears is itself a finding.

## Subreddit hints

- LLMs, fine-tuning, GPU rental: r/LocalLLaMA, r/MachineLearning, r/unsloth, r/StableDiffusion, r/comfyui
- Self-hosting / infra: r/selfhosted, r/homelab, r/sysadmin, r/devops
- Dev tools: r/programming, r/webdev, language subs
- Consumer: r/BuyItForLife, product-specific subs

## Field notes

- Reddit's search relevance is loose: a query with a dot in it (`vast.ai`) returned unrelated top posts. Always pass `--keyword` so the digest filters, and prefer bare names (`vast`, not `vast.ai`).
- `upVotes` is null on some results, so sort with a fallback.
- Bodies are HTML-escaped; the script unescapes them for the digest.
- r/LocalLLaMA regulars push back on cloud-only questions, so cloud-pricing threads there are fewer and sometimes argumentative.
- First used 2026-10-27 for the My Weird Prompts episode comparing Modal, RunPod and Vast.ai for fine-tuning: 28 posts and 372 comments from five subreddits.
