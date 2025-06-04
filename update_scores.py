import datetime
import json
import logging
import os
import sys
from typing import Dict

import requests

SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
SCOREBOARD_FILE = os.environ.get("SCOREBOARD_FILE", "scoreboard.json")

logger = logging.getLogger(__name__)


def load_scoreboard() -> Dict[str, list]:
    logger.debug("Loading scoreboard from %s", SCOREBOARD_FILE)
    with open(SCOREBOARD_FILE) as f:
        return json.load(f)


def save_scoreboard(scoreboard: Dict[str, list]):
    logger.debug("Saving scoreboard to %s", SCOREBOARD_FILE)
    with open(SCOREBOARD_FILE, "w") as f:
        json.dump(scoreboard, f, indent=2)


def fetch_games(date: str) -> list:
    url = SCHEDULE_URL.format(date=date)
    logger.debug("Fetching games from %s", url)
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    games = data.get("dates", [{}])[0].get("games", [])
    logger.debug("Fetched %d games", len(games))
    return games


def update_for_date(date: str):
    logger.debug("Updating scores for %s", date)
    games = fetch_games(date)
    scoreboard = load_scoreboard()

    for game in games:
        for side in ["home", "away"]:
            team = game["teams"][side]["team"]["name"]
            runs = game["teams"][side]["score"]
            if team not in scoreboard:
                logger.debug("Skipping untracked team %s", team)
                continue
            if runs not in scoreboard[team]:
                logger.debug("Adding run total %s for %s", runs, team)
                scoreboard[team].append(runs)
                scoreboard[team].sort()

    save_scoreboard(scoreboard)
    print(f"Updated scores for {date}")


def main():
    logging.basicConfig(level=logging.DEBUG if os.environ.get("LOG_LEVEL") == "DEBUG" else logging.INFO)
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    update_for_date(date)


if __name__ == "__main__":
    main()
