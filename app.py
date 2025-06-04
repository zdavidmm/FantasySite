from flask import Flask, jsonify, send_from_directory
import json
import logging
import os

app = Flask(__name__, static_folder="frontend", static_url_path="")

PARTICIPANTS_FILE = os.environ.get("PARTICIPANTS_FILE", "participants.json")
SCOREBOARD_FILE = os.environ.get("SCOREBOARD_FILE", "scoreboard.json")

logger = logging.getLogger(__name__)


def load_data():
    logger.debug("Loading participants from %s", PARTICIPANTS_FILE)
    with open(PARTICIPANTS_FILE) as f:
        assignments = json.load(f)
    logger.debug("Loading scoreboard from %s", SCOREBOARD_FILE)
    with open(SCOREBOARD_FILE) as f:
        scoreboard = json.load(f)
    return assignments, scoreboard


@app.route("/api/data")
def api_data():
    logger.debug("/api/data requested")
    assignments, scoreboard = load_data()
    return jsonify({"assignments": assignments, "scoreboard": scoreboard})


@app.route("/")
def index():
    logger.debug("Serving index page")
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    logger.debug("Serving static file: %s", path)
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG if os.environ.get("LOG_LEVEL") == "DEBUG" else logging.INFO)
    app.run(debug=True)
