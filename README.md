# Social Feedback

Check what people are actually saying about a topic, product, or provider by searching curated social-discourse sources.

When evaluating a SaaS provider, a piece of hardware, a library, or a service, the most useful signal often lives in community discussions rather than vendor pages or first-page Google results. This plugin gives Claude a set of source-specific skills, plus an orchestrator that picks the right ones for a given query and synthesizes the findings.

## Skills

- `check-discourse` — orchestrator. Picks which sources to consult and synthesizes a balanced summary.
- `reddit-discourse` — Reddit (subreddit-scoped). Best single source for "is X any good".
- `hackernews-discourse` — Hacker News via Algolia. Technical / founder audience.
- `stackexchange-discourse` — Stack Overflow / Server Fault / etc. Problem-shaped discourse and failure modes.
- `trustpilot-reviews` — Trustpilot. Consumer reviews for businesses and services.
- `youtube-reviews` — YouTube. Hands-on demos plus long-term follow-up in comments.
- `lobsters-discourse` — Lobsters. Curated dev tooling / systems software discussion.

## Installation

```bash
claude plugins marketplace add danielrosehill/Claude-Code-Plugins
claude plugins install social-feedback@danielrosehill
```

## License

MIT
