# World Cup 2026 Sweepstake

A self-updating leaderboard for an office sweepstake. GitHub Actions fetches live data, computes points, and publishes a static page — colleagues just open a URL.

## Your four setup steps

### 1. Enable GitHub Pages

In your repo: **Settings → Pages → Source: Deploy from a branch → Branch: `main` / folder: `/docs`**. Save. GitHub will show you the URL (e.g. `https://<org>.github.io/<repo>`).

### 2. Add the API key secret

- Sign up free at [api-sports.io](https://api-sports.io) and copy your key from the dashboard.
- In the repo: **Settings → Secrets and variables → Actions → New repository secret**
  - Name: `APISPORTS_KEY`
  - Value: your key

**First-run check:** hit the endpoint manually to confirm your free tier can see the 2026 World Cup:

```bash
curl -s "https://v3.football.api-sports.io/fixtures?league=1&season=2026" \
  -H "x-apisports-key: YOUR_KEY" | python3 -m json.tool | head -40
```

If it 403s or returns zero fixtures, you may need the $19/mo Pro plan — let me know.

### 3. Fill in team assignments after the draw

First, generate the full team list (run once with your key set):

```bash
APISPORTS_KEY=your_key python print_teams.py
```

This prints the complete `ASSIGNMENTS` block with every team ID and name pre-filled. Paste it into `config.py`, then replace `None` with the colleague's name for each team that was picked:

```python
ASSIGNMENTS = {
    6:    "Alice",   # Brazil
    26:   "Bob",     # Argentina
    9:    None,      # Spain — not yet picked (shows in "still to be picked" list)
}
```

Teams left as `None` appear on the page under "Teams still to be picked". Commit and push — the next scheduled run will pick up the assignments.

### 4. (Optional) Slack/Teams notifications

If you want a top-5 post to a channel after each run:

1. Create an incoming webhook for your workspace and give me the URL.
2. Add it as a repo secret named `SLACK_WEBHOOK`.

The step is already in the workflow and skips silently if the secret isn't set.

---

## Running locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export APISPORTS_KEY=your_key_here
python build.py
open docs/index.html
```

Cache files for finished matches are written to `cache/` and committed by the Action, so subsequent runs only fetch new matches.

## Scoring

| Event | Points |
|---|---|
| Win | +3 |
| Draw | +1 |
| Goal scored | +1 |
| Clean sheet (0 conceded) | +2 |
| Knockout round advancement | +5 |
| Yellow card | −1 |
| Red card | −2 |

Scoring constants live in `config.py` — tweak and redeploy at any time.
