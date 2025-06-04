from flask import Flask, render_template_string
import json

app = Flask(__name__)

INDEX_TMPL = """
<!doctype html>
<title>Fantasy Runs Challenge</title>
<h1>Fantasy Runs Challenge</h1>
<table border="1" cellpadding="5">
<tr><th>Participant</th><th>Team</th><th>Runs 0-13</th></tr>
{% for participant, team in assignments.items() %}
  <tr>
    <td>{{ participant }}</td>
    <td>{{ team }}</td>
    <td>{{ scoreboard.get(team, []) }}</td>
  </tr>
{% endfor %}
</table>
"""


def load_data():
    with open("participants.json") as f:
        assignments = json.load(f)
    with open("scoreboard.json") as f:
        scoreboard = json.load(f)
    return assignments, scoreboard


@app.route("/")
def index():
    assignments, scoreboard = load_data()
    return render_template_string(INDEX_TMPL, assignments=assignments, scoreboard=scoreboard)


if __name__ == "__main__":
    app.run(debug=True)
