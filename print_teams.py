#!/usr/bin/env python3
"""
Fetches all World Cup 2026 teams and prints a ready-to-paste ASSIGNMENTS block.

Usage:
    FOOTBALL_API_KEY=your_key python print_teams.py

Copy the output into config.py, then replace None with the colleague's name
for each team that has been picked in the draw.
"""
import os
import sys

import requests

key = os.environ.get("FOOTBALL_API_KEY")
if not key:
    sys.exit("FOOTBALL_API_KEY env var not set")

resp = requests.get(
    "https://v3.football.api-sports.io/teams",
    params={"league": 1, "season": 2026},
    headers={"x-apisports-key": key},
    timeout=30,
)
resp.raise_for_status()
body = resp.json()

if body.get("errors"):
    sys.exit(f"API error: {body['errors']}")

teams = sorted(body["response"], key=lambda t: t["team"]["name"])

if not teams:
    sys.exit("No teams returned — your key may not have access to this season.")

print(f"# {len(teams)} teams found\n")
print("ASSIGNMENTS = {")
for t in teams:
    tid = t["team"]["id"]
    name = t["team"]["name"]
    print(f"    {tid:<6}: None,  # {name}")
print("}")
