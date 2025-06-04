import json
import random
import sys

TEAMS = [
    "Arizona Diamondbacks",
    "Atlanta Braves",
    "Baltimore Orioles",
    "Boston Red Sox",
    "Chicago White Sox",
    "Chicago Cubs",
    "Cincinnati Reds",
    "Cleveland Guardians",
    "Colorado Rockies",
    "Detroit Tigers",
    "Houston Astros",
    "Kansas City Royals",
    "Los Angeles Angels",
    "Los Angeles Dodgers",
    "Miami Marlins",
    "Milwaukee Brewers",
    "Minnesota Twins",
    "New York Mets",
    "New York Yankees",
    "Oakland Athletics",
    "Philadelphia Phillies",
    "Pittsburgh Pirates",
    "San Diego Padres",
    "San Francisco Giants",
    "Seattle Mariners",
    "St. Louis Cardinals",
    "Tampa Bay Rays",
    "Texas Rangers",
    "Toronto Blue Jays",
    "Washington Nationals",
]


def main(participants_file: str):
    with open(participants_file) as f:
        participants = [line.strip() for line in f if line.strip()]

    if len(participants) != 30:
        raise SystemExit("Exactly 30 participants are required")

    random.shuffle(TEAMS)

    assignments = dict(zip(participants, TEAMS))

    # Save participant assignments
    with open("participants.json", "w") as f:
        json.dump(assignments, f, indent=2)

    # Initialize scoreboard
    scoreboard = {team: [] for team in TEAMS}
    with open("scoreboard.json", "w") as f:
        json.dump(scoreboard, f, indent=2)

    print("Draft complete. Assignments written to participants.json")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python draft.py PARTICIPANTS_FILE")
        sys.exit(1)
    main(sys.argv[1])
