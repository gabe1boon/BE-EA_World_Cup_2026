# World Cup 2026 Sweepstake — Claude Code notes

Full project brief is in `context.md`. Key facts for future sessions:

- **Build script:** `build.py` (Python 3) — reads `config.py`, writes `docs/data.json`
- **Config:** `config.py` — `SCORING` dict (tweakable) and `ASSIGNMENTS` (team_id → colleague name, filled in after the draw)
- **Cache:** `cache/events_{fixture_id}.json` — permanently stores finished-match events; never re-fetched
- **API:** API-Football direct (`https://v3.football.api-sports.io`), header `x-apisports-key`, league=1, season=2026
- **Key must never reach the browser** — all API calls happen in the Action or locally
- **Hosting:** GitHub Pages serving `docs/` from `main`
- **Workflow:** `.github/workflows/update.yml` — cron every 3 h, commits `docs/data.json` + `cache/`

Do not touch GitHub secrets, API accounts, or the in-person draw. Prompt the user for those.
