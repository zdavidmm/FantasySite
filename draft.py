import json
import logging
import os
import random
import sys

import db

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


PARTICIPANTS_FILE = os.environ.get("PARTICIPANTS_FILE", "participants.json")
SCOREBOARD_FILE = os.environ.get("SCOREBOARD_FILE", "scoreboard.json")
DB_FILE = os.environ.get("DB_FILE", db.DB_FILE)

logger = logging.getLogger(__name__)


def main(participants_file: str):
    logger.debug("Reading participants from %s", participants_file)
    with open(participants_file) as f:
        participants = [line.strip() for line in f if line.strip()]

    if len(participants) != 30:
        logger.error("Expected 30 participants but got %d", len(participants))
        raise SystemExit("Exactly 30 participants are required")

    random.shuffle(TEAMS)
    logger.debug("Teams after shuffle: %s", TEAMS)

    assignments = dict(zip(participants, TEAMS))

    # Save participant assignments
    logger.debug("Writing assignments to %s", PARTICIPANTS_FILE)
    with open(PARTICIPANTS_FILE, "w") as f:
        json.dump(assignments, f, indent=2)

    # Initialize scoreboard with an empty dict for each team. Each run total
    # will map to a metadata dictionary (date and game_pk) when achieved.
    scoreboard = {team: {} for team in TEAMS}
    logger.debug("Initializing scoreboard in %s", SCOREBOARD_FILE)
    with open(SCOREBOARD_FILE, "w") as f:
        json.dump(scoreboard, f, indent=2)

    # Initialize database
    conn = db.connect(DB_FILE)
    db.init_db(conn)
    db.save_assignments(assignments, conn)
    conn.execute("DELETE FROM scoreboard")
    conn.commit()
    conn.close()

    logger.info("Draft complete. Assignments written to %s", PARTICIPANTS_FILE)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python draft.py PARTICIPANTS_FILE")
        sys.exit(1)
    logging.basicConfig(level=logging.DEBUG if os.environ.get("LOG_LEVEL") == "DEBUG" else logging.INFO)
    main(sys.argv[1])
