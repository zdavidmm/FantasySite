import json
import os
import sys
from pathlib import Path
import sqlite3

sys.path.append(str(Path(__file__).resolve().parents[1]))

import draft


def test_draft_creates_files(monkeypatch, tmp_path):
    participants = [f"P{i}" for i in range(30)]
    participants_file = tmp_path / "participants.txt"
    participants_file.write_text("\n".join(participants))

    participants_json = tmp_path / "participants.json"
    scoreboard_file = tmp_path / "scoreboard.json"
    db_file = tmp_path / "scores.db"
    monkeypatch.setenv("PARTICIPANTS_FILE", str(participants_json))
    monkeypatch.setenv("SCOREBOARD_FILE", str(scoreboard_file))
    monkeypatch.setenv("DB_FILE", str(db_file))
    draft.DB_FILE = str(db_file)

    monkeypatch.chdir(tmp_path)
    draft.main(str(participants_file))

    assert participants_json.exists()
    assert scoreboard_file.exists()
    assert db_file.exists()

    data = json.loads(scoreboard_file.read_text())
    assert len(data) == len(draft.TEAMS)
    for scores in data.values():
        assert scores == {}

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    rows = cur.execute("SELECT COUNT(*) FROM participants").fetchone()[0]
    assert rows == 30
    score_rows = cur.execute("SELECT COUNT(*) FROM scoreboard").fetchone()[0]
    assert score_rows == 0
