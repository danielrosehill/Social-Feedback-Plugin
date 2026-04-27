---
name: check-discourse
description: Orchestrator — when the user wants to know "what do people say about X" (a provider, product, service, library, tool), pick which source-specific sub-skills to invoke and synthesize a balanced summary across them. Triggers on phrases like "what's the consensus on", "is X any good", "what are people saying about", "should I use X", "spec out a provider".
---

# Check Discourse (orchestrator)

> TODO: Daniel will fill in detailed instructions.

## Purpose

Decide which of the source-specific sub-skills in this plugin are worth running for the user's query, run them, then synthesize a single answer that distinguishes:

- recurring praise
- recurring complaints
- known failure modes / gotchas
- comparative alternatives people mention

## Source selection heuristic (stub)

| Query shape | Likely sources |
|---|---|
| Dev tool / library / SaaS | Reddit, Hacker News, Lobsters, Stack Exchange |
| Consumer product / service | Reddit, Trustpilot, YouTube |
| Hosting / infra provider | Reddit (r/selfhosted, r/sysadmin), Hacker News, Trustpilot |
| Hardware / gear | Reddit, YouTube, Trustpilot |
| Programming problem / API quirk | Stack Exchange, Hacker News |

## Output shape (stub)

- **TL;DR** — one-line consensus
- **What people praise**
- **What people complain about**
- **Caveats / failure modes**
- **Sources consulted** — links
