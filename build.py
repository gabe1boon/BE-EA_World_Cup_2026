#!/usr/bin/env python3
"""
World Cup 2026 sweepstake build script.
Run with APISPORTS_KEY in environment. Writes docs/data.json.
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from config import ASSIGNMENTS, SCORING

API_BASE = "https://v3.football.api-sports.io"
LEAGUE_ID = 1
SEASON = 2026
CACHE_DIR = Path("cache")
DOCS_DIR = Path("docs")
DATA_JSON = DOCS_DIR / "data.json"

# Fixture statuses that count as a completed match
FINISHED = {"FT", "AET", "PEN"}

GROUP_STAGE_PREFIX = "Group Stage"


def _key():
    k = os.environ.get("APISPORTS_KEY")
    if not k:
        sys.exit("APISPORTS_KEY env var not set")
    return k


def _get(path, params, key):
    resp = requests.get(
        f"{API_BASE}{path}",
        params=params,
        headers={"x-apisports-key": key},
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()
    errs = body.get("errors")
    if errs and errs != [] and errs != {}:
        sys.exit(f"API error on {path}: {errs}")
    return body["response"]


def _cached_events(fixture_id):
    p = CACHE_DIR / f"events_{fixture_id}.json"
    return json.loads(p.read_text()) if p.exists() else None


def _store_events(fixture_id, events):
    CACHE_DIR.mkdir(exist_ok=True)
    (CACHE_DIR / f"events_{fixture_id}.json").write_text(json.dumps(events, indent=2))


def compute(fixtures, key):
    assigned = set(ASSIGNMENTS)
    if not assigned:
        print("WARNING: ASSIGNMENTS is empty in config.py — fill it in after the draw.")

    stats = {
        tid: {
            "points": 0,
            "played": 0,
            "wins": 0,
            "draws": 0,
            "goals_for": 0,
            "clean_sheets": 0,
            "yellow_cards": 0,
            "red_cards": 0,
            "_rounds": set(),  # tracks knockout rounds awarded (not serialised)
        }
        for tid in assigned
    }

    for fx in fixtures:
        home_id = fx["teams"]["home"]["id"]
        away_id = fx["teams"]["away"]["id"]
        round_name = fx["league"]["round"]
        status = fx["fixture"]["status"]["short"]
        fx_id = fx["fixture"]["id"]
        is_knockout = not round_name.startswith(GROUP_STAGE_PREFIX)

        # Knockout advancement bonus — awarded once per round when a team is scheduled
        if is_knockout:
            for tid in (home_id, away_id):
                if tid in stats and round_name not in stats[tid]["_rounds"]:
                    stats[tid]["_rounds"].add(round_name)
                    stats[tid]["points"] += SCORING["knockout_advance"]

        if status not in FINISHED:
            continue

        home_g = fx["goals"]["home"] or 0
        away_g = fx["goals"]["away"] or 0

        for tid, my_g, opp_g in ((home_id, home_g, away_g), (away_id, away_g, home_g)):
            if tid not in stats:
                continue
            s = stats[tid]
            s["played"] += 1
            s["goals_for"] += my_g
            s["points"] += my_g * SCORING["goal_scored"]
            if my_g > opp_g:
                s["wins"] += 1
                s["points"] += SCORING["win"]
            elif my_g == opp_g:
                s["draws"] += 1
                s["points"] += SCORING["draw"]
            if opp_g == 0:
                s["clean_sheets"] += 1
                s["points"] += SCORING["clean_sheet"]

        if not (home_id in stats or away_id in stats):
            continue

        events = _cached_events(fx_id)
        if events is None:
            print(f"  Fetching events for fixture {fx_id}...")
            time.sleep(0.3)
            events = _get("/fixtures/events", {"fixture": fx_id}, key)
            _store_events(fx_id, events)

        for ev in events:
            if ev["type"] != "Card":
                continue
            tid = ev["team"]["id"]
            if tid not in stats:
                continue
            if ev["detail"] == "Yellow Card":
                stats[tid]["yellow_cards"] += 1
                stats[tid]["points"] += SCORING["yellow_card"]
            elif ev["detail"] == "Red Card":
                stats[tid]["red_cards"] += 1
                stats[tid]["points"] += SCORING["red_card"]

    return stats


def build_output(stats, fixtures):
    names = {}
    for fx in fixtures:
        for side in ("home", "away"):
            t = fx["teams"][side]
            names[t["id"]] = t["name"]

    rows = []
    for tid, s in stats.items():
        rows.append({
            "colleague": ASSIGNMENTS[tid],
            "team": names.get(tid, f"Team {tid}"),
            "team_id": tid,
            "points": s["points"],
            "played": s["played"],
            "wins": s["wins"],
            "draws": s["draws"],
            "goals_for": s["goals_for"],
            "clean_sheets": s["clean_sheets"],
            "yellow_cards": s["yellow_cards"],
            "red_cards": s["red_cards"],
        })

    rows.sort(key=lambda r: (-r["points"], -r["wins"], -r["goals_for"]))

    assigned_ids = set(ASSIGNMENTS)
    all_teams = sorted(
        [{"team_id": tid, "team": name} for tid, name in names.items()
         if tid not in assigned_ids],
        key=lambda t: t["team"],
    )

    return {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "leaderboard": rows,
        "available_teams": all_teams,
    }


def post_slack(webhook, leaderboard, updated_at):
    if not leaderboard:
        return
    lines = ["*World Cup 2026 Sweepstake — standings*"]
    for i, row in enumerate(leaderboard[:5], 1):
        lines.append(f"{i}. {row['colleague']} ({row['team']}) — {row['points']} pts")
    lines.append(f"_Updated {updated_at}_")
    requests.post(webhook, json={"text": "\n".join(lines)}, timeout=10)
    print("Slack notification sent.")


def main():
    key = _key()
    DOCS_DIR.mkdir(exist_ok=True)

    print("Fetching all fixtures...")
    fixtures = _get("/fixtures", {"league": LEAGUE_ID, "season": SEASON}, key)
    print(f"  {len(fixtures)} fixtures returned")

    stats = compute(fixtures, key)
    output = build_output(stats, fixtures)

    DATA_JSON.write_text(json.dumps(output, indent=2))
    print(f"Done. {len(output['leaderboard'])} entries -> {DATA_JSON}")

    webhook = os.environ.get("SLACK_WEBHOOK")
    if webhook:
        post_slack(webhook, output["leaderboard"], output["updated_at"])


if __name__ == "__main__":
    main()
