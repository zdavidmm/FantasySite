import datetime
import json
import logging
import os
import sys
from typing import Dict

import requests

SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={date}"
SCOREBOARD_FILE = os.environ.get("SCOREBOARD_FILE", "scoreboard.json")

# Opening Day for the season. Used when no start date is supplied.
OPENING_DAY = "2024-03-28"

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


def update_for_date(date: str, scoreboard: Dict[str, list] | None = None) -> Dict[str, list]:
    """Update the scoreboard for a single date.

    If *scoreboard* is provided it will be updated in place and **not** saved to
    disk. Otherwise the scoreboard file is loaded and written back out.
    """
    logger.debug("Updating scores for %s", date)
    games = fetch_games(date)
    save_after = False
    if scoreboard is None:
        scoreboard = load_scoreboard()
        save_after = True

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

    if save_after:
        save_scoreboard(scoreboard)
        print(f"Updated scores for {date}")

    return scoreboard


def update_since(start_date: str):
    """Update scores for every day from *start_date* through yesterday."""
    logger.debug("Updating scores since %s", start_date)
    current = datetime.date.fromisoformat(start_date)
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    scoreboard = load_scoreboard()
    while current <= end_date:
        update_for_date(current.isoformat(), scoreboard)
        current += datetime.timedelta(days=1)
    save_scoreboard(scoreboard)
    print(f"Updated scores for {start_date} through {end_date.isoformat()}")


def main():
    logging.basicConfig(level=logging.DEBUG if os.environ.get("LOG_LEVEL") == "DEBUG" else logging.INFO)
    if len(sys.argv) > 1:
        start_date = sys.argv[1]
    else:
        start_date = OPENING_DAY
    update_since(start_date)


if __name__ == "__main__":
    main()
