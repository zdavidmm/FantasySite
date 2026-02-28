# Fantasy Site

This repository contains a fantasy baseball challenge site that helps run
a "runs 0–13" competition. Participants are randomly assigned MLB teams and the
site tracks which run totals each team achieves throughout the season.
The user interface is built with React and a responsive dark product-style
layout.

## Setup

1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Prepare a `participants.txt` file with one participant name per line. There
   must be exactly 30 participants.

3. Run the draft to assign each participant a random team and initialize the
   scoreboard database. The database stores the participant assignments and will
   track the first date and MLB game id for every run total achieved by each
   team:
   ```bash
   python3 draft.py participants.txt
   ```

4. At the start of a new season, choose one reset mode:
   - Keep existing participant/team assignments and clear progress only:
     ```bash
     python3 - <<'PY'
     import os
     import sqlite3

     db_file = os.environ.get("DB_FILE", "fantasy.db")
     conn = sqlite3.connect(db_file)
     conn.execute("DELETE FROM scoreboard")
     conn.commit()
     conn.close()
     print(f"scoreboard reset in {db_file}")
     PY
     ```
   - Re-run a full draft (new team assignments + fresh scoreboard):
     ```bash
     python3 draft.py participants.txt
     ```

5. Update scores daily. `update_scores.py` defaults to the 2026 Opening Day
   (`2026-03-26`) unless overridden by `OPENING_DAY`:
   ```bash
   python3 update_scores.py             # uses default OPENING_DAY through yesterday
   python3 update_scores.py 2026-03-26  # specific start date
   OPENING_DAY=2027-04-01 python3 update_scores.py
   ```
   The script pulls scores from the official MLB schedule API and updates the
   SQLite database accordingly.

6. Launch the local web site:
   ```bash
   python3 app.py
   ```
   Visit `http://localhost:5000` to view the React interface. The app fetches
   the assignment and scoreboard data from `/api/data` and includes:
   - responsive dark-themed leaderboard layout
   - participant search
   - sort controls (default: progress descending, then name ascending)
   - optional "Only Missing Totals" filter toggle
   - sticky table header with horizontal scroll on smaller screens
   - progress shown as both text (`X/14`) and a compact progress bar
   - run-total cells with metadata tooltips and links to MLB gameday when
     `game_pk` exists

## GitHub Pages

This repo deploys the frontend to GitHub Pages with GitHub Actions.

- Triggered on:
  - push to `main`
  - daily schedule at `6:00 AM UTC`
  - manual `workflow_dispatch`
- The workflow updates score data, exports static JSON for the frontend, and
  deploys the `frontend/` artifact.
- The site header includes a \"Last updated\" note and the daily refresh time.

The ultimate goal is for a team to record every run total from 0 through 13.
The sample rules in the project description award prizes for milestones such as
first team to 13 runs, first team to complete all totals, and so on.

## Testing

Automated tests are provided for both Python and frontend logic.

1. Install the dependencies (including `pytest`):
   ```bash
   pip3 install -r requirements.txt
   ```

2. Run the Python test suite:
   ```bash
   python3 -m pytest -v
   ```

3. Run frontend unit/component tests:
   ```bash
   npm install
   npm run test:frontend
   ```

To see detailed debug output while running any of the scripts, set the
`LOG_LEVEL` environment variable to `DEBUG`:

```bash
LOG_LEVEL=DEBUG python3 update_scores.py
```

`draft.py`, `update_scores.py` and `app.py` also respect the optional
`DB_FILE`, `SCOREBOARD_FILE`, `PARTICIPANTS_FILE`, and `OPENING_DAY`
environment variables which can be used to override defaults when
troubleshooting or rolling into a new season.
