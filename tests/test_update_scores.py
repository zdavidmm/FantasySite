import json
from types import SimpleNamespace
import sys
from pathlib import Path
import datetime
import sqlite3

sys.path.append(str(Path(__file__).resolve().parents[1]))

import update_scores


def test_update_for_date(monkeypatch, tmp_path):
    db_file = tmp_path / "scores.db"
    monkeypatch.setenv("DB_FILE", str(db_file))
    update_scores.DB_FILE = str(db_file)
    conn = sqlite3.connect(db_file)
    update_scores.db.init_db(conn)
    conn.execute("INSERT INTO participants (participant, team) VALUES ('P1', 'Test Team')")
    conn.commit()
    conn.close()

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

    conn = sqlite3.connect(db_file)
    row = conn.execute("SELECT date, game_pk FROM scoreboard WHERE team='Test Team' AND run_total=5").fetchone()
    assert row[0] == "2022-01-01"
    assert row[1] == 1


def test_update_since(monkeypatch, tmp_path):
    db_file = tmp_path / "scores.db"
    monkeypatch.setenv("DB_FILE", str(db_file))
    update_scores.DB_FILE = str(db_file)
    conn = sqlite3.connect(db_file)
    update_scores.db.init_db(conn)
    conn.execute("INSERT INTO participants (participant, team) VALUES ('P1', 'Test Team')")
    conn.commit()
    conn.close()

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

    conn = sqlite3.connect(db_file)
    rows = conn.execute("SELECT run_total, date, game_pk FROM scoreboard WHERE team='Test Team'").fetchall()
    totals = {r[0]: r[1:] for r in rows}
    assert set(totals.keys()) == {5, 7}
    assert totals[5][0] == "2022-01-01"
    assert totals[7][1] == 2


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
