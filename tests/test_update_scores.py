import json
from types import SimpleNamespace
import sys
from pathlib import Path
import datetime

sys.path.append(str(Path(__file__).resolve().parents[1]))

import update_scores


def test_update_for_date(monkeypatch, tmp_path):
    scoreboard_file = tmp_path / "scoreboard.json"
    scoreboard_file.write_text(json.dumps({"Test Team": {}}))
    monkeypatch.setenv("SCOREBOARD_FILE", str(scoreboard_file))
    update_scores.SCOREBOARD_FILE = str(scoreboard_file)

    sample_games = [{
        "gamePk": 1,
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
    assert data["Test Team"]["5"]["date"] == "2022-01-01"
    assert data["Test Team"]["5"]["game_pk"] == 1


def test_update_since(monkeypatch, tmp_path):
    scoreboard_file = tmp_path / "scoreboard.json"
    scoreboard_file.write_text(json.dumps({"Test Team": {}}))
    monkeypatch.setenv("SCOREBOARD_FILE", str(scoreboard_file))
    update_scores.SCOREBOARD_FILE = str(scoreboard_file)

    day1 = [{
        "gamePk": 1,
        "teams": {
            "home": {"team": {"name": "Test Team"}, "score": 5},
            "away": {"team": {"name": "Other"}, "score": 3}
        }
    }]
    day2 = [{
        "gamePk": 2,
        "teams": {
            "home": {"team": {"name": "Test Team"}, "score": 7},
            "away": {"team": {"name": "Other"}, "score": 2}
        }
    }]

    games_iter = iter([day1, day2])

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"dates": [{"games": next(games_iter)}]}

    def fake_get(url, timeout):
        return FakeResponse()

    monkeypatch.setattr(update_scores, "requests", SimpleNamespace(get=fake_get))

    class FakeDate(datetime.date):
        @classmethod
        def today(cls):
            return cls(2022, 1, 3)

    monkeypatch.setattr(update_scores, "datetime", SimpleNamespace(date=FakeDate, timedelta=datetime.timedelta))

    update_scores.update_since("2022-01-01")

    data = json.loads(scoreboard_file.read_text())
    assert set(data["Test Team"].keys()) == {"5", "7"}
    assert data["Test Team"]["5"]["date"] == "2022-01-01"
    assert data["Test Team"]["7"]["game_pk"] == 2


def test_main_uses_opening_day(monkeypatch):
    called = {}

    def fake_update_since(start_date):
        called["start"] = start_date

    monkeypatch.setattr(update_scores, "update_since", fake_update_since)
    monkeypatch.setattr(update_scores, "OPENING_DAY", "2022-03-31", raising=False)
    monkeypatch.setattr(sys, "argv", ["update_scores.py"])

    class FakeDate(datetime.date):
        @classmethod
        def today(cls):
            return cls(2022, 4, 1)

    monkeypatch.setattr(update_scores, "datetime", SimpleNamespace(date=FakeDate, timedelta=datetime.timedelta))

    update_scores.main()

    assert called["start"] == "2022-03-31"
