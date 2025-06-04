# Fantasy Site

This repository contains a simple fantasy baseball challenge site that helps run
a "runs 0–13" competition. Participants are randomly assigned MLB teams and the
site tracks which run totals each team achieves throughout the season.
The user interface is built with React and styled with a dark theme reminiscent
of DraftKings.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Prepare a `participants.txt` file with one participant name per line. There
   must be exactly 30 participants.

3. Run the draft to assign each participant a random team and initialize the
   scoreboard:
   ```bash
   python draft.py participants.txt
   ```

4. Each day, update the scoreboard with the previous day's results (or pass a
   date in `YYYY-MM-DD` format to fetch another day):
   ```bash
   python update_scores.py            # uses yesterday's date
   python update_scores.py 2025-04-01 # specific date
   ```
   The script pulls scores from the official MLB schedule API and updates
   `scoreboard.json` accordingly.

5. Launch the local web site:
   ```bash
   python app.py
   ```
   Visit `http://localhost:5000` to view the React interface. The app fetches
   the assignment and scoreboard data from `/api/data` and displays a table in
   a dark theme inspired by DraftKings.

The ultimate goal is for a team to record every run total from 0 through 13.
The sample rules in the project description award prizes for milestones such as
first team to 13 runs, first team to complete all totals, and so on.

## Testing

Automated tests are provided using `pytest`.

1. Install the dependencies (including `pytest`):
   ```bash
   pip install -r requirements.txt
   ```

2. Run the test suite:
   ```bash
   pytest -v
   ```

To see detailed debug output while running any of the scripts, set the
`LOG_LEVEL` environment variable to `DEBUG`:

```bash
LOG_LEVEL=DEBUG python update_scores.py
```

`draft.py`, `update_scores.py` and `app.py` also respect the optional
`SCOREBOARD_FILE` and `PARTICIPANTS_FILE` environment variables which can be
used to override the default file locations when troubleshooting.
