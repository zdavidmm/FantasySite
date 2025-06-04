from flask import Flask, jsonify, send_from_directory
import json
import os

app = Flask(__name__, static_folder="frontend", static_url_path="")


def load_data():
    with open("participants.json") as f:
        assignments = json.load(f)
    with open("scoreboard.json") as f:
        scoreboard = json.load(f)
    return assignments, scoreboard


@app.route("/api/data")
def api_data():
    assignments, scoreboard = load_data()
    return jsonify({"assignments": assignments, "scoreboard": scoreboard})


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(debug=True)
