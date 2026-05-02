# TEAM.md — OpenClaw Agent Team Charter

This is the shared charter for Manik's three-agent team. Load this file on-demand when coordinating across agents or onboarding a new agent. Not part of the default session-init load (that stays lean: SOUL + USER + IDENTITY + today's memory).

## The Team

| Agent | Name | Emoji | Workspace | Telegram binding |
|---|---|---|---|---|
| `main` | Jarvis | 🎩 | `/home/claw/.openclaw/workspace` | (unbound — DMs and orchestration) |
| `financial-advisor` | FinAdvisor | 📊 | `/home/claw/.openclaw/workspace-financial-advisor` | StockPortfolio group `-1003795983668` |
| `research-agent` | Atlas | 🔬 | `/home/claw/.openclaw/workspace-research` | AI-Research group `-1003732307762` |

Bindings live in `/home/claw/.openclaw/openclaw.json` under `agents.list` and `bindings`. The `main` agent has `subagents.allowAgents: ["financial-advisor", "research-agent"]`, which lets Jarvis dispatch to either specialist.

## Ownership — Who Handles What

### Jarvis (main) owns
- General chat and personal assistance
- Memory curation (`MEMORY.md`), daily log review, heartbeats
- Cron job ownership for workspace-level tasks (daily sync, backup validation, log health)
- **Orchestration**: routing incoming requests to the right specialist; returning results to the user
- YouTube AI daily summary (currently a `main`-owned cron — may migrate to Atlas later)

### FinAdvisor (financial-advisor) owns
- `/home/claw/.openclaw/workspace-financial-advisor/portfolio/manik_portfolio.json` — the source of truth for holdings
- Daily pre-market report, morning brief, Reddit investing digest, Reddit nightly, CNBC Fast Money digest, economic calendar watch, weekly events refresh
- All communication to the StockPortfolio group
- Options strategy suggestions, hedge recommendations, risk warnings

### Atlas (research-agent) owns
- Daily AI Intelligence Brief (9am UTC) to the AI-Research group
- YouTube AI Channel Summary (19:00 UTC) — new content from tracked channels
- X/Reddit/GitHub/web signal synthesis
- All communication to the AI-Research group

## Handoff Rules

**Jarvis → Specialist**
- Dispatch via the subagent tool
- Pass the user's request in plain text; do *not* include your full session history
- Include any file paths, tickers, or sources the specialist needs to start
- Wait for the specialist's response; don't run parallel work on the same request

**Specialist → Jarvis**
- Return a complete, self-contained answer (not a status update)
- Cite sources inline if the request was research-oriented
- If the request can't be handled cleanly, return the error + suggestion, not a stub

**Cross-specialist (rare)**
- Specialists should not dispatch to each other directly. If Atlas needs a portfolio value, it asks Jarvis to coordinate — Jarvis dispatches to FinAdvisor.

## Shared Conventions

### Telegram formatting (all agents)
- **No pipe characters (`|`)** — Telegram rejects messages with pipes as "too long". No tables.
- **Emoji headers** for sections (📊 🔥 🛡️ etc.)
- **Bullet lists only** — no markdown tables
- **Hard limit: 3800 characters per message.** Split into Part 1 / Part 2 if over.
- **Never use `<think>` tags in the response body.** Content inside `<think>` blocks is invisible and causes silent delivery failure. Start the response with the report itself.

### Citations
- Research and digest reports: every claim gets a source link. Atlas enforces this strictly.
- FinAdvisor: quote prices/tickers from tool output, not estimates. Mark `⚠️ NO PRICE` for missing data.

### Rate limits (shared across all agents)
- Daily spend target: $5.00 (warn at 75%, stop at 100%)
- Monthly spend target: $150.00 (warn at 75%, halt at 100%)
- On rate limit: fall back to next model in `agents.defaults.model.fallbacks`, note the switch, retry

If Jarvis hits a rate limit, specialists should assume they're in the same boat — don't start a new expensive job without checking.

### Session initialization (shared across all agents)
- Load only: `SOUL.md`, `USER.md` (if present), `IDENTITY.md`, `memory/YYYY-MM-DD.md`
- Do NOT auto-load: `MEMORY.md`, yesterday's memory, session history, prior tool outputs
- This rule prevents 109k–160k+ token bloat. Each agent's `AGENTS.md` restates it — that's intentional, not a bug.

## Deliverables Schedule (at a glance)

| Time (UTC) | Agent | Job |
|---|---|---|
| 00:00 daily | main | Log health check |
| 06:00 PT weekdays | financial-advisor | Portfolio morning brief |
| 09:00 daily | research-agent | AI Intelligence Brief |
| 10:00 PT daily | main | Workspace sync to GitHub |
| 10:00 PT Mondays | main | Weekly backup validation |
| 12:00 PT daily | research-agent | YouTube AI Channel Summary (currently owned by `main` cron `d4e15581`) |
| 14:00 UTC weekdays | financial-advisor | Daily portfolio report |
| 18:00 PT weekdays | financial-advisor | Reddit investing digest |
| 19:00 PT weekdays | financial-advisor | CNBC Fast Money digest |
| 22:00 PT daily | financial-advisor | Reddit nightly (PFC, dividends, CanadianInvestor, ValueInvesting) |
| 22:00 PT daily | financial-advisor | Reddit nightly WSB/ETF/options |

Full definitions in `/home/claw/.openclaw/cron/jobs.json`.

## When This File Changes

Update `TEAM.md` when:
- A new agent joins the team
- Ownership boundaries shift (e.g., a cron job moves between agents)
- Shared conventions change (new Telegram formatting rule, rate-limit policy change)
- The orchestration pattern changes

Don't update for transient changes — use each agent's own `AGENTS.md` for agent-specific evolution.
