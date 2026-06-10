SCORING = {
    "win": 3,
    "draw": 1,
    "goal_scored": 1,
    "clean_sheet": 2,
    "yellow_card": -1,
    "red_card": -2,
    "knockout_advance": 5,
}

# Fill in after the draw. Get team IDs by running:
#   python -c "import os,requests; r=requests.get('https://v3.football.api-sports.io/teams',params={'league':1,'season':2026},headers={'x-apisports-key':os.environ['APISPORTS_KEY']}); [print(t['team']['id'],t['team']['name']) for t in r.json()['response']]"
ASSIGNMENTS = {
    # team_id: "Colleague Name",
    # 2384: "Alice",
    #   26: "Bob",
}
