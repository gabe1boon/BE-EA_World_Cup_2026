SCORING = {
    "win": 3,
    "draw": 1,
    "goal_scored": 1,
    "clean_sheet": 2,
    "yellow_card": -1,
    "red_card": -2,
    "knockout_advance": 2,
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
    2382: "Willem",    # Ecuador
    775:  "Valeria",   # Austria
    1508: "Sebastian", # Congo DR
    3:    "Mark",      # Croatia
    27:   "Mark",      # Portugal
    4673: "Gabe",      # New Zealand
    1568: "Tobias",    # Uzbekistan
    2380: "Tobias",    # Paraguay
    1569: "Krystian",  # Qatar
    1504: "Achille",   # Ghana
    1533: "Achille",   # Cape Verde Islands
    12:   "Dusan",     # Japan
    16:   "Iga",       # Mexico
    1108: "Koums",     # Scotland
    23:   "Koums",     # Saudi Arabia
    15:   "Koums",     # Switzerland
    9:    "Naini",     # Spain
    1113: "Adele",     # Bosnia & Herzegovina
    26:   "Sachin",    # Argentina
    2386: "Basiten",   # Haiti
    1567: "Xavier",    # Iraq
    32:   "Deepti",    # Egypt
    31:   "Eva",       # Morocco
    2384: "Iliasse",   # USA
    1501: "Oliver",    # Ivory Coast
    1548: "Jiří",      # Jordan
    7:    "Euan",      # Uruguay
    5:    "Nicolas",   # Sweden
    17:   "Francisco", # South Korea
    1532: "Daniel",    # Algeria
}

# FIFA ranking groups for WC2026 (A = highest-ranked, D = lowest).
# Team names must match the API-Football names exactly.
# 48 teams split into 4 tiers of 12 by approximate FIFA World Ranking.
FIFA_GROUPS = {
    "A": [
        "Argentina", "France", "England", "Brazil", "Portugal", "Spain",
        "Belgium", "Netherlands", "Germany", "Croatia", "Morocco", "Colombia",
    ],
    "B": [
        "USA", "Mexico", "Japan", "Senegal", "Uruguay", "Switzerland",
        "South Korea", "Ecuador", "Canada", "Austria", "Norway", "Sweden",
    ],
    "C": [
        "Türkiye", "Scotland", "Ivory Coast", "Egypt", "Ghana", "Iran",
        "Czech Republic", "Tunisia", "Australia", "Iraq", "Saudi Arabia", "Panama",
    ],
    "D": [
        "Paraguay", "Algeria", "Congo DR", "Jordan", "South Africa", "Qatar",
        "Uzbekistan", "Cape Verde Islands", "Bosnia & Herzegovina",
        "New Zealand", "Curaçao", "Haiti",
    ],
}

# Bonus points for beating a team from a higher-ranked group.
# Index = number of tiers above: [same=0, 1 tier=+1, 2 tiers=+3, 3 tiers=+5]
UPSET_BONUS = [0, 1, 3, 5]
