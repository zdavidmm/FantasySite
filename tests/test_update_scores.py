import json
from types import SimpleNamespace
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import update_scores


def test_update_for_date(monkeypatch, tmp_path):
    scoreboard_file = tmp_path / "scoreboard.json"
    scoreboard_file.write_text(json.dumps({"Test Team": []}))
    monkeypatch.setenv("SCOREBOARD_FILE", str(scoreboard_file))
    update_scores.SCOREBOARD_FILE = str(scoreboard_file)

    sample_games = [{
        "teams": {
            "home": {"team": {"name": "Test Team"}, "score": 5},
            "away": {"team": {"name": "Other"}, "score": 3}
        }
    }]

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"dates": [{"games": sample_games}]}

    def fake_get(url, timeout):
        return FakeResponse()

    monkeypatch.setattr(update_scores, "requests", SimpleNamespace(get=fake_get))

    update_scores.update_for_date("2022-01-01")

    data = json.loads(scoreboard_file.read_text())
    assert data["Test Team"] == [5]
