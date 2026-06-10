# World Cup 2026 Sweepstake — Project Context & Instructions

This file is the brief for Claude Code. Read it fully before writing code. Ask me
before doing anything that touches my accounts or credentials (see "What the human
does" at the bottom).

## Goal

A self-updating leaderboard for an office World Cup sweepstake. Each colleague is
randomly assigned a national team (done in person, offline). Teams earn points as
the tournament progresses. Colleagues just open a URL and see the current standings
and per-team stats. **No manual score entry** — data is fetched automatically.

The 2026 FIFA World Cup runs **11 June – 19 July 2026** (48 teams, 104 matches,
hosted by USA/Canada/Mexico).

## Architecture (already decided — build this)

A scheduled job fetches data, computes points, and writes a static site. Nothing
runs live; the page just serves the last computed result.

```
GitHub Actions (cron, a few times/day)
        │  runs build script
        ▼
  API-Football  ──►  compute points  ──►  docs/data.json + docs/index.html
        │                                          │
   (key in Secrets)                        GitHub Pages serves docs/
                                                   │
                                          colleagues open the URL
```

**Critical constraint:** the API key must NEVER reach the browser. All API calls
happen in the GitHub Action (key read from `process.env` / Secrets). The published
page only ever reads the pre-computed `data.json`. Calling the API client-side
would leak the key and blow the daily quota.

### Recommended stack
- **Build script:** Python 3 (clean for the data/scoring work). Node is fine if you
  prefer one language end-to-end — your call, but pick one and be consistent.
- **Page:** plain static HTML + CSS + vanilla JS that `fetch`es `data.json` and
  renders a table. No framework needed. Make it readable on mobile.
- **Hosting:** GitHub Pages serving the `docs/` folder (or use the
  `actions/deploy-pages` action — whichever is cleaner).
- **Schedule:** GitHub Actions `cron`, roughly every 2–3 hours during the
  tournament. Note Actions cron is UTC and can be delayed a few minutes.

## The data source: API-Football (api-sports.io)

- Free tier: **100 requests/day**, all endpoints available, no credit card.
- World Cup 2026 is `league=1`, `season=2026`.
- Base URL (direct, not RapidAPI): `https://v3.football.api-sports.io`
- Auth header (direct): `x-apisports-key: <KEY>` — **confirm the exact header name
  against the dashboard/docs before relying on it**, and confirm whether I signed up
  direct or via RapidAPI (RapidAPI uses different headers).

### Endpoints needed
- `GET /fixtures?league=1&season=2026` — every fixture with scores + status in ONE
  call. Source of goals, wins/draws, clean sheets.
- `GET /fixtures/events?fixture={id}` — match events incl. cards (type `Card`,
  detail `Yellow Card` / `Red Card`) with the team. Source of card points.
- `GET /teams?league=1&season=2026` — team IDs + names. Run ONCE to build the
  mapping below, then hard-code it.

### Quota math (stay well under 100/day)
- 1 call/run for all fixtures.
- Card events only for **newly finished** matches, then **cache them permanently**
  (a finished match never changes — store events in a committed `cache/` JSON and
  never refetch). Group stage is ~4–6 matches/day, so ~6 event calls + 1 fixtures
  call per run. Recompute the full leaderboard each run from cache + new data.

### Caveat to verify on day one
API-Football's free tier has occasionally restricted season access. First thing:
hit `/fixtures?league=1&season=2026` with my key and confirm it returns the
schedule. If it 403s or returns empty, tell me — I may need the $19/mo Pro plan.

## Scoring rules (tweakable — put these in a config object/constant)

| Event | Points |
|---|---|
| Win | +3 |
| Draw | +1 |
| Goal scored | +1 |
| Clean sheet (0 conceded, finished match only) | +2 |
| Yellow card | −1 |
| Red card | −2 |
| Advance a knockout round (bonus) | +5 |

- Clean sheet = `goals.against == 0` on a **finished** fixture only.
- Only count **finished** matches (check fixture status; ignore scheduled/live for
  scoring, or show live separately but don't bank points until final).
- Knockout-advancement bonus: award when a team appears in the next round's fixtures.

## Team → colleague mapping

Build a single lookup keyed by API-Football team ID (stable across seasons).
Leave it as an obvious placeholder for me to fill in after the in-person draw:

```python
# Fill in after the draw. Get team IDs from /teams?league=1&season=2026
ASSIGNMENTS = {
    # team_id: "Colleague Name",
    # 2384: "Alice",
    # 26:   "Bob",
}
```

Teams not in the map should be ignored in the leaderboard.

## Output: docs/data.json shape (suggested)

```json
{
  "updated_at": "2026-06-14T18:00:00Z",
  "leaderboard": [
    {
      "colleague": "Alice", "team": "Brazil", "team_id": 6, "points": 14,
      "played": 3, "wins": 2, "draws": 1, "goals_for": 7,
      "clean_sheets": 2, "yellow_cards": 3, "red_cards": 0
    }
  ]
}
```

The page reads this and renders a sortable table sorted by points desc, plus a
"last updated" line and each team's stat breakdown.

## Optional: Slack/Teams post

Add an optional step that posts the standings to a channel via an incoming webhook
(URL from a `SLACK_WEBHOOK` secret) after each run — e.g. a top-of-table summary.
Make it skip cleanly if the secret isn't set. Ask me before wiring this; I'll create
the webhook.

## Suggested repo layout

```
CLAUDE.md
.github/workflows/update.yml   # cron + run script + deploy
build.py (or build.js)         # fetch, score, write docs/
config.py                      # SCORING + ASSIGNMENTS
cache/                         # committed cached events for finished matches
docs/
  index.html
  styles.css
  app.js
  data.json                    # generated
README.md                      # human setup steps (you write this)
```

## What the human (me) does — do NOT attempt these yourself
- Create the GitHub repo and enable Pages (serve from `docs/`).
- Get my own API-Football key and add it as the `APISPORTS_KEY` Actions secret.
  Never put the key in code or commit it.
- Run the in-person draw and give you the team→colleague assignments.
- Create the Slack/Teams webhook if we add that.

When you reach any of these, pause and prompt me rather than improvising.

## Definition of done
1. `build.py` runs locally with the key in env and produces a valid `docs/data.json`.
2. The page renders a clean, mobile-friendly leaderboard from that JSON.
3. The Action runs on cron, commits/deploys updated output, and respects the cache.
4. A short README tells me exactly how to do my four steps above.