import datetime
import json
import sys
from typing import Dict

import requests

SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"


def load_scoreboard() -> Dict[str, list]:
    with open("scoreboard.json") as f:
        return json.load(f)


def save_scoreboard(scoreboard: Dict[str, list]):
    with open("scoreboard.json", "w") as f:
        json.dump(scoreboard, f, indent=2)


def fetch_games(date: str) -> list:
    url = SCHEDULE_URL.format(date=date)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("dates", [{}])[0].get("games", [])


def update_for_date(date: str):
    games = fetch_games(date)
    scoreboard = load_scoreboard()

    for game in games:
        for side in ["home", "away"]:
            team = game["teams"][side]["team"]["name"]
            runs = game["teams"][side]["score"]
            if team not in scoreboard:
                continue
            if runs not in scoreboard[team]:
                scoreboard[team].append(runs)
                scoreboard[team].sort()

    save_scoreboard(scoreboard)
    print(f"Updated scores for {date}")


def main():
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    update_for_date(date)


if __name__ == "__main__":
    main()
