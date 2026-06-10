SCORING = {
    "win": 3,
    "draw": 1,
    "goal_scored": 1,
    "clean_sheet": 2,
    "yellow_card": -1,
    "red_card": -2,
    "knockout_advance": 5,
}

# Team → colleague assignments.
#
# HOW TO USE:
#   1. Run `python print_teams.py` (with APISPORTS_KEY set) to generate this
#      block pre-filled with every World Cup 2026 team ID and name.
#   2. Paste the output here.
#   3. After the draw, replace None with the colleague's name for each team.
#      Teams left as None will appear in the "still to be picked" list on the page.
#
# Example once populated:
#     6:    "Alice",   # Brazil
#     26:   "Bob",     # Argentina
#     9:    None,      # Spain — not yet picked
#
ASSIGNMENTS = {
    10: "Alice",    # England
    6:  "Bob",      # Brazil
    2:  "Charlie",  # France
}
