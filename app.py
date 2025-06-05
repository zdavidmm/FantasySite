from flask import Flask, jsonify, send_from_directory
import json
import logging
import os
import db

app = Flask(__name__, static_folder="frontend", static_url_path="")

PARTICIPANTS_FILE = os.environ.get("PARTICIPANTS_FILE", "participants.json")
SCOREBOARD_FILE = os.environ.get("SCOREBOARD_FILE", "scoreboard.json")
DB_FILE = os.environ.get("DB_FILE", db.DB_FILE)

logger = logging.getLogger(__name__)


def load_data():
    logger.debug("Loading data from database %s", DB_FILE)
    conn = db.connect(DB_FILE)
    db.init_db(conn)
    assignments = db.get_assignments(conn)
    scoreboard = db.load_scoreboard(conn)
    conn.close()
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
