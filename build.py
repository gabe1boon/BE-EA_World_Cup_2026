#!/usr/bin/env python3
"""
World Cup 2026 sweepstake build script.
Run with APISPORTS_KEY in environment. Writes docs/data.json.
"""
import json
import os
import sys
import time
import zoneinfo
from datetime import datetime, timezone
from pathlib import Path

import requests

from config import ASSIGNMENTS, FIFA_GROUPS, SCORING, UPSET_BONUS

API_BASE = "https://v3.football.api-sports.io"
LEAGUE_ID = 1
SEASON = 2026
CACHE_DIR = Path("cache")
DOCS_DIR = Path("docs")
DATA_JSON = DOCS_DIR / "data.json"
SNAPSHOTS_DIR = Path("snapshots")
GENEVA_TZ = zoneinfo.ZoneInfo("Europe/Zurich")

# Fixture statuses that count as a completed match
FINISHED = {"FT", "AET", "PEN"}

GROUP_STAGE_PREFIX = "Group Stage"


def _key():
    k = os.environ.get("FOOTBALL_API_KEY")
    if not k:
        sys.exit("FOOTBALL_API_KEY env var not set")
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
    # Only teams with a real colleague name count toward the leaderboard
    assigned = {tid for tid, name in ASSIGNMENTS.items() if name}
    if not assigned:
        print("WARNING: No colleagues assigned yet in config.py — fill in after the draw.")

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
            "upset_bonus": 0,
            "_rounds": set(),  # tracks knockout rounds awarded (not serialised)
        }
        for tid in assigned
    }

    # Build FIFA group rank lookup: team_name_lower → int (A=1, B=2, C=3, D=4)
    _group_rank = {}
    for _grp_idx, _grp_teams in enumerate(FIFA_GROUPS.values(), 1):
        for _tname in _grp_teams:
            _group_rank[_tname.lower()] = _grp_idx

    # Build team-ID → name mapping from fixture data
    _fx_names = {}
    for _fx in fixtures:
        for _side in ("home", "away"):
            _t = _fx["teams"][_side]
            _fx_names[_t["id"]] = _t["name"]

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
                # Upset bonus: extra points for beating a higher-ranked FIFA group
                _opp_id = away_id if tid == home_id else home_id
                _my_grp = _group_rank.get(_fx_names.get(tid, "").lower(), 0)
                _opp_grp = _group_rank.get(_fx_names.get(_opp_id, "").lower(), 0)
                if _my_grp > _opp_grp > 0:
                    _diff = min(_my_grp - _opp_grp, len(UPSET_BONUS) - 1)
                    _bonus = UPSET_BONUS[_diff]
                    s["points"] += _bonus
                    s["upset_bonus"] += _bonus
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

    # Find the next scheduled fixture for each assigned team
    now = datetime.now(timezone.utc)
    next_matches = {}
    for fx in fixtures:
        if fx["fixture"]["status"]["short"] not in ("NS", "TBD"):
            continue
        raw_date = fx["fixture"].get("date")
        if not raw_date:
            continue
        try:
            fx_dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
        except ValueError:
            continue
        if fx_dt <= now:
            continue
        home_id = fx["teams"]["home"]["id"]
        away_id = fx["teams"]["away"]["id"]
        for my_id, opp_id in ((home_id, away_id), (away_id, home_id)):
            if my_id not in stats:
                continue
            if my_id not in next_matches or fx_dt < next_matches[my_id]["dt"]:
                next_matches[my_id] = {
                    "dt": fx_dt,
                    "utc": fx_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "vs": names.get(opp_id, ""),
                }

    rows = []
    for tid, s in stats.items():
        nm = next_matches.get(tid)
        rows.append({
            "colleague": ASSIGNMENTS[tid],
            "team": names.get(tid, f"Team {tid}"),
            "team_id": tid,
            "next_match_utc": nm["utc"] if nm else None,
            "next_match_vs": nm["vs"] if nm else None,
            "points": s["points"],
            "played": s["played"],
            "wins": s["wins"],
            "draws": s["draws"],
            "goals_for": s["goals_for"],
            "clean_sheets": s["clean_sheets"],
            "yellow_cards": s["yellow_cards"],
            "red_cards": s["red_cards"],
            "upset_bonus": s["upset_bonus"],
        })

    rows.sort(key=lambda r: (-r["points"], -r["wins"], -r["goals_for"]))

    # Available = teams listed in ASSIGNMENTS with no colleague yet,
    # plus any fixture team not mentioned in ASSIGNMENTS at all.
    picked_ids = {tid for tid, name in ASSIGNMENTS.items() if name}
    available_ids = set()
    for tid in names:
        if tid not in picked_ids:
            available_ids.add(tid)

    available_teams = sorted(
        [{"team_id": tid, "team": names[tid]} for tid in available_ids],
        key=lambda t: t["team"],
    )

    # Reverse FIFA group lookup: team_name_lower → group letter
    _grp_lookup = {}
    for _grp, _grp_teams in FIFA_GROUPS.items():
        for _tname in _grp_teams:
            _grp_lookup[_tname.lower()] = _grp

    # Upcoming fixtures (next 30, soonest first)
    upcoming = []
    for fx in fixtures:
        if fx["fixture"]["status"]["short"] not in ("NS", "TBD"):
            continue
        raw_date = fx["fixture"].get("date")
        if not raw_date:
            continue
        try:
            fx_dt = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
        except ValueError:
            continue
        if fx_dt <= now:
            continue
        home = fx["teams"]["home"]
        away = fx["teams"]["away"]
        venue_info = fx["fixture"].get("venue") or {}
        upcoming.append({
            "date": fx_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "home_team": home["name"],
            "away_team": away["name"],
            "home_group": _grp_lookup.get(home["name"].lower(), ""),
            "away_group": _grp_lookup.get(away["name"].lower(), ""),
            "venue": venue_info.get("name") or "",
            "city": venue_info.get("city") or "",
            "round": fx["league"]["round"],
        })
    upcoming.sort(key=lambda x: x["date"])
    upcoming = upcoming[:30]

    return {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "leaderboard": rows,
        "available_teams": available_teams,
        "upcoming_fixtures": upcoming,
    }


def maybe_snapshot(output):
    now_geneva = datetime.now(GENEVA_TZ)
    if now_geneva.hour < 9:
        return
    date_str = now_geneva.strftime("%Y-%m-%d")
    SNAPSHOTS_DIR.mkdir(exist_ok=True)
    snapshot_path = SNAPSHOTS_DIR / f"{date_str}.json"
    if snapshot_path.exists():
        return
    snapshot = {
        "date": date_str,
        "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "leaderboard": [
            {**row, "rank": i + 1}
            for i, row in enumerate(output["leaderboard"])
        ],
    }
    snapshot_path.write_text(json.dumps(snapshot, indent=2))
    print(f"Snapshot saved: {snapshot_path}")


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
    output["fifa_groups"] = FIFA_GROUPS

    DATA_JSON.write_text(json.dumps(output, indent=2))
    print(f"Done. {len(output['leaderboard'])} entries -> {DATA_JSON}")
    maybe_snapshot(output)

    webhook = os.environ.get("SLACK_WEBHOOK")
    if webhook:
        post_slack(webhook, output["leaderboard"], output["updated_at"])


if __name__ == "__main__":
    main()
