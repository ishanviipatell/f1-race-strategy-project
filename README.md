# F1 Race Strategy Replay

A Python-based Formula 1 race replay and telemetry analysis toolkit built on `fastf1`, `arcade`, and `PySide6`.

This project loads real F1 race and qualifying sessions, processes live telemetry, and renders gameplay-style race replays with an optional insights menu for additional analysis.

## Features

- Interactive GUI and command-line session selection
- Replay of race, sprint, and qualifying sessions
- Telemetry playback with driver colors, track status, and DRS awareness
- Automatic insights menu with launchable telemetry windows
- Support for sprint weekends (`Sprint Qualifying` + `Sprint` sessions)
- Local `fastf1` caching for faster repeated loads
- Example insight window architecture for custom extensions

## Requirements

- Python 3.10+ recommended
- `requirements.txt` contains the core dependencies
- Additional runtime dependencies used by the project:
  - `fastf1`
  - `scipy`

### Install dependencies

```bash
python -m pip install -r requirements.txt
python -m pip install fastf1 scipy
```

> Note: If you already have `fastf1` installed, you can skip the second command.

## Quick Start

### Run the GUI launcher

```bash
python main.py
```

This opens the graphical race selection window. From there, choose the year, event, and session to launch the replay.

### Run the interactive CLI

```bash
python main.py --cli
```

This launches a terminal-based selection flow using `questionary` and `rich`.

### Run a replay directly

```bash
python main.py --viewer --year 2024 --round 12 --qualifying
```

### Run a sprint weekend replay

```bash
python main.py --viewer --year 2024 --round 12 --sprint-qualifying
python main.py --viewer --year 2024 --round 12 --sprint
```

## Command-Line Options

`main.py` supports the following flags:

- `--cli` — launch the terminal-based session selector
- `--viewer` — run the replay viewer directly
- `--year <year>` — select the season year
- `--round <round>` — select the race weekend round number
- `--list-rounds <year>` — print all rounds for the year
- `--list-sprints <year>` — print sprint weekend rounds for the year
- `--qualifying` — load a qualifying session instead of the race
- `--sprint-qualifying` — load a sprint qualifying session
- `--sprint` — load a sprint session
- `--no-hud` — disable the on-screen HUD during replay
- `--verbose` — keep `fastf1` logging enabled for debugging
- `--ready-file <path>` — write `ready` to file after the replay window is created

## Project Structure

```text
main.py
requirements.txt
src/
  f1_data.py
  run_session.py
  cli/
    race_selection.py
  gui/
    race_selection.py
    insights_menu.py
    pit_wall_window.py
  interfaces/
    qualifying.py
    race_replay.py
  insights/
    telemetry_stream_viewer.py
  lib/
    season.py
    settings.py
    time.py
    tyres.py
```

### Key modules

- `main.py` — application entrypoint and argument parsing
- `src/f1_data.py` — session loading, telemetry processing, driver colors, circuit rotation, and caching
- `src/run_session.py` — replay launcher, insights menu startup, telemetry viewer launcher
- `src/cli/race_selection.py` — terminal session chooser
- `src/gui/race_selection.py` — PySide6 GUI selection window
- `src/gui/insights_menu.py` — insights launcher for telemetry windows
- `src/interfaces/qualifying.py` — qualifying replay renderer
- `src/interfaces/race_replay.py` — arcade-based race replay window

## How It Works

1. `main.py` loads a selected session using `fastf1`
2. Telemetry and weather data are downloaded and cached locally
3. `src/f1_data.py` converts lap telemetry into replay frames and track objects
4. `src/run_session.py` creates an `arcade` race replay window
5. For race sessions, the project launches the insights menu in parallel
6. The insights menu exposes additional analysis tools such as the telemetry stream viewer

## Insights Menu

The insights menu appears automatically during race replays and provides launch buttons for telemetry analysis windows.

See `docs/InsightsMenu.md` for details on:

- how the insights menu works
- how to add custom insight buttons
- example insight window workflows

## Extending the Project

### Add a new insight window

1. Create a new window class based on `src/gui/pit_wall_window.py`
2. Implement `setup_ui()` and telemetry callbacks
3. Add a launcher method in `src/gui/insights_menu.py`
4. Add a button for the new insight in the menu UI

### Add a new replay mode

1. Update `main.py` to recognize the new session flag
2. Add session loading logic in `src/f1_data.py` if needed
3. Add a corresponding launcher or renderer in `src/run_session.py`

## Notes

- The project currently supports race and sprint weekend sessions.
- Qualifying replay uses the `fastf1` session telemetry and loads data for driver lap comparisons.
- Local caching is enabled automatically via `src/f1_data.py` using the configured cache path.

## Troubleshooting

- If telemetry fails to load, ensure `fastf1` can access the internet and that your cache path is writable.
- If a replay window fails to appear, try running with `--verbose` to preserve logging output from `fastf1`.
- Missing package errors usually mean `fastf1` or `scipy` are not installed.

## License

This repository does not include an explicit license file. Add a `LICENSE` if you want to publish or share it publicly.
