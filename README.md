# F1 Race Strategy Replay

A comprehensive Formula 1 race replay and telemetry analysis toolkit that brings F1 sessions to life. Built on `fastf1`, `arcade`, and `PySide6`, this project loads real F1 race and qualifying sessions, processes live telemetry, and renders gameplay-style race replays with an integrated insights ecosystem for detailed analysis.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation & Setup](#installation--setup)
- [Quick Start](#quick-start)
- [User Guide](#-user-guide)
- [Core Functions Explained](#-core-functions-explained)
- [Features Deep Dive](#features-deep-dive)
- [Architecture Overview](#architecture-overview)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Extending the Project](#extending-the-project)
- [Resources & Links](#resources--links)

---

## Overview

**F1 Race Strategy Replay** is a full-featured toolkit for replaying, analyzing, and strategizing F1 sessions. Whether you're a casual fan wanting to relive a race, a data analyst exploring telemetry patterns, or a developer building custom tools, this project provides the infrastructure to work with real F1 data.

### What You Can Do

- 🏁 **Replay races, sprints, and qualifying sessions** with full telemetry visualization
- 📊 **Access real-time telemetry data** via streaming WebSocket for custom tools
- 🎯 **Analyze pit stop strategies** with automatic tyre degradation modeling
- 🔧 **Create custom analysis windows** with the extensible insights menu system
- ⚙️ **Choose your interface**: GUI launcher, CLI, or direct Python API

### Perfect For

- F1 enthusiasts wanting interactive race replays
- Data scientists analyzing tyre and fuel behavior
- Strategy analysts exploring pit stop optimization
- Developers building custom F1 analysis tools
- Teams building pit wall dashboards

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Interactive GUI Launcher** | Point-and-click race selection with year/round/session filters |
| **Full Race & Sprint Replays** | Replay with 25 FPS telemetry-driven visualization |
| **Qualifying Replays** | Sprint Qualifying, Qualifying, and Q1/Q2/Q3 lap analysis |
| **Real-time Telemetry Stream** | WebSocket server broadcasting live telemetry data (25fps) |
| **DRS Visualization** | Visual indicators for DRS zones and activation |
| **Safety Car Simulation** | Realistic Safety Car deployment with gap management |
| **Tyre Degradation Model** | Bayesian state-space analysis of tyre performance |
| **Pit Stop Strategy Engine** | Automated optimal strategy suggestions |
| **Insights Menu** | Extensible dashboard for custom analysis windows |
| **Multi-mode CLI** | Terminal-based session selection and batch operations |
| **Track Status Overlays** | Yellow/red flags, virtual safety cars, weather conditions |
| **Weather Visualization** | Real-time air temp, track temp, wind, humidity, precipitation |
| **Driver Telemetry** | Speed, throttle, brake, DRS, gear, fuel consumption |
| **Local Cache** | Automatic fastf1 caching for faster repeated loads |

---

## Installation & Setup

### System Requirements

- **Python**: 3.10 or higher
- **OS**: Windows, macOS, or Linux
- **GPU**: Optional (arcade benefits from discrete GPU)
- **RAM**: 4GB minimum (8GB recommended for analysis tools)

### Step 1: Clone the Repository

```bash
git clone https://github.com/ishanviipatell/f1-race-strategy-project.git
cd f1-race-strategy-project
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Install additional optional packages for advanced features
pip install fastf1 scipy
```

### Step 4: Verify Installation

```bash
# Test import of core modules
python -c "import fastf1; import arcade; import PySide6; print('✓ All dependencies installed')"
```

### Step 5: Cache Configuration (Optional)

By default, fastf1 cache is stored in `.fastf1-cache/` in the project directory. To use a different location:

```bash
# Edit cache location in settings (created on first run)
# On Windows: %APPDATA%\F1RaceReplay\settings.json
# On macOS/Linux: ~/.config/f1-race-replay/settings.json

# Or set via environment variable
export F1_CACHE_LOCATION="/path/to/cache"  # macOS/Linux
set F1_CACHE_LOCATION=C:\path\to\cache     # Windows
```

### First-Time Setup Validation

```bash
# Launch the GUI to validate setup
python main.py

# If you see the Race Selection window, you're ready to go!
# Select any past season/round to verify replay works
```

---

## Quick Start

### 1. Launch GUI (Easiest)

```bash
python main.py
```

A window opens. Select:
1. **Year**: 2024
2. **Round**: 12 (Silverstone)
3. **Session**: Race
4. Click "Launch Replay"

You'll see the race replay with live telemetry, leaderboard, and controls.

### 2. Launch CLI (Interactive)

```bash
python main.py --cli
```

Terminal prompts guide you through:
- Season year selection
- Round selection with event name hints
- Session type (Race/Sprint/Qualifying)

### 3. Direct Command (Power Users)

```bash
# Replay Silverstone 2024 race
python main.py --viewer --year 2024 --round 12

# Replay Monaco 2024 qualifying
python main.py --viewer --year 2024 --round 5 --qualifying

# Replay Hungarian GP 2024 sprint
python main.py --viewer --year 2024 --round 12 --sprint
```

### 4. List Available Sessions

```bash
# Show all rounds for 2024
python main.py --list-rounds 2024

# Show sprint weekends for 2024
python main.py --list-sprints 2024
```

---

## User Guide

### Launching the Replay

#### Via GUI

1. Run `python main.py`
2. Select **Year** (defaults to current season)
3. Select **Round** (1-24, shows event name)
4. Select **Session Type**:
   - `Race` - Main Grand Prix race (default)
   - `Sprint` - Sprint race (if available)
   - `Qualifying` - Qualifying session
   - `Sprint Qualifying` - Sprint qualifying session
5. Click **"Launch Replay"**

**What Happens Next:**
- Insights menu opens (separate window)
- FastF1 loads and caches session data
- Replay window launches with full telemetry visualization
- You're in control!

#### Via CLI

```bash
python main.py --cli
```

Navigate using arrow keys, type selections, press Enter.

#### Via Command Line

```bash
python main.py --viewer --year 2024 --round 5 --qualifying
```

### Understanding the Replay Window

```
┌─────────────────────────────────────────────────────┐
│   REPLAY CONTROLS (top-left corner)                 │
│   [◀ Prev]  [▶ Play/Pause]  [Next ▶]               │
│   Speed: [1.0x ▼]  Frame: 123/50000                 │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│   RACE TRACK WITH DRIVERS                           │
│   (Center - 80% of screen)                          │
│                                                      │
│   • Driver positions updated 25x per second         │
│   • Driver names and lap numbers visible            │
│   • DRS zones shown in blue                         │
│   • Track status overlay (yellow/red flags)         │
│   • Safety Car path if deployed                     │
└─────────────────────────────────────────────────────┘

┌──────────────────┐  ┌────────────────────┐
│  LEADERBOARD     │  │  WEATHER           │
│  (right side)    │  │  (top-left)        │
│                  │  │                    │
│  1. VER  +0.000  │  │  Air: 18°C         │
│  2. LEC  +1.234  │  │  Track: 25°C       │
│  3. SAI  +2.456  │  │  Wind: 1.5 m/s    │
│  ...             │  │  Humidity: 72%    │
└──────────────────┘  └────────────────────┘

┌──────────────────┐
│  DRIVER INFO     │
│  (left side)     │
│                  │
│  Driver: VER     │
│  Position: 1st   │
│  Lap: 45/57      │
│  Tyre: Soft (12) │
│  Gap: Leader     │
└──────────────────┘
```

### Replay Controls

#### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `SPACE` | Play/Pause |
| `←` / `→` | Rewind/Forward 5 frames |
| `D` | Toggle DRS zones (blue highlighting) |
| `L` | Toggle driver labels (names on track) |
| `H` | Toggle HUD (all overlays) |
| `1-9` | Set playback speed (1x to 9x) |
| `+` / `-` | Increase/Decrease playback speed |
| `ESC` | Exit replay |

#### Playback Speeds

Preset speeds: **0.1x, 0.2x, 0.5x, 1.0x, 2.0x, 4.0x, 8.0x, 16.0x, 32.0x, 64.0x, 128.0x, 256.0x**

Use speed to:
- **0.5x-1.0x**: Analyze critical moments in detail
- **2.0x-4.0x**: Quick race overview
- **8.0x-64.0x**: Jump through race phases
- **128.0x-256.0x**: Skip to end instantly

### Understanding the Display Elements

#### Leaderboard (Right Side)
Shows live race standings with gaps to leader in seconds. Updates every frame.

```
Position  Driver  Gap      Pit Stops  Tyre
1         VER     -        1          Hard(42)
2         LEC     +1.234   1          Medium(35)
3         SAI     +2.456   2          Hard(12)
```

#### Weather Overlay (Top-Left)
Real-time conditions affecting driver performance:
- **Air Temp**: Ambient temperature (affects tyre warmup)
- **Track Temp**: Surface temperature (directly affects grip)
- **Wind**: Speed and direction (minimal visible effect in replay)
- **Humidity**: Environmental moisture (affects grip)
- **Rain State**: DRY / DAMP / WET

#### Driver Info (Left Side)
Detailed telemetry for the selected driver:
- **Position**: Current race position
- **Lap**: Current lap number
- **Tyre**: Compound and laps completed on current set
- **Speed**: Current speed in km/h
- **Throttle/Brake**: Pedal inputs (0-100%)
- **Gear**: Current gear (1-8)
- **DRS**: Enabled (✓) or disabled
- **Fuel**: Estimated remaining fuel

#### Track Status Overlay
Yellow/Red flag indicators:
- 🟡 **Yellow Flag**: Caution (one sector affected)
- 🔴 **Red Flag**: Session stopped
- 🟠 **Virtual Safety Car**: Deployed, pace controlled by leader
- 🟠 **Safety Car**: Deployed, bunched field

### Working with the Insights Menu

The Insights Menu opens automatically with each replay and provides:

```
┌─────────────────────────────────────┐
│   F1 RACE INSIGHTS                  │
├─────────────────────────────────────┤
│                                      │
│  📊 ANALYSIS TOOLS                   │
│   • Driver Telemetry Window          │
│   • Pit Stop Analysis                │
│   • Gap Evolution Chart              │
│                                      │
│  🎯 STRATEGY TOOLS                   │
│   • Tyre Strategy Analyzer           │
│   • Fuel Consumption Model           │
│                                      │
│  🔗 INTEGRATIONS                     │
│   • Hardware Link (Serial Comms)     │
│   • Telemetry Stream Viewer          │
│                                      │
└─────────────────────────────────────┘
```

**Available Tools:**
- **Driver Telemetry**: Real-time driver data inspection
- **Pit Wall Window**: Example extensible analysis interface
- **Tyre Strategy**: Bayesian degradation model predictions
- **Hardware Link**: Serial communication for simulator rigs
- **Telemetry Viewer**: Raw WebSocket data inspection

### CLI Advanced Usage

#### Show Detailed Round Info

```bash
python main.py --list-rounds 2024 --verbose
```

Output:
```
2024 F1 Season Rounds:
1  - Bahrain GP          2024-03-02
2  - Saudi Arabian GP    2024-03-09
3  - Australian GP       2024-03-24
...
12 - Silverstone GP      2024-07-07
```

#### Batch Mode with Direct Parameters

```bash
# Load and replay without any GUI prompts
python main.py --viewer --year 2024 --round 12

# Disable HUD for cleaner recording
python main.py --viewer --year 2024 --round 12 --no-hud

# Enable verbose logging for debugging
python main.py --viewer --year 2024 --round 12 --verbose

# Write "ready" file when window is loaded (for automation)
python main.py --viewer --year 2024 --round 12 --ready-file /tmp/ready.txt
```

#### Command-Line Flag Reference

```
LAUNCHER OPTIONS:
  --cli                    Use terminal-based session selector (interactive)
  --viewer                 Run replay viewer directly (requires --year, --round)

SESSION SELECTION:
  --year <YEAR>           Season year (e.g., 2024)
  --round <ROUND>         Round number (1-24)
  --list-rounds <YEAR>    Print all rounds for year
  --list-sprints <YEAR>   Print sprint weekends for year

SESSION TYPE:
  --qualifying            Load qualifying session (default: race)
  --sprint-qualifying     Load sprint qualifying session
  --sprint                Load sprint race session
  (omit all for main race)

REPLAY OPTIONS:
  --no-hud               Disable on-screen HUD (controls, leaderboard, etc)
  --playback-speed <N>   Set initial speed (0.1 to 256.0)

DIAGNOSTICS:
  --verbose              Keep fastf1 logging enabled (debug info)
  --ready-file <PATH>    Write "ready" to file when window created

EXAMPLES:
  python main.py                                    # GUI launcher
  python main.py --cli                             # CLI selector
  python main.py --list-rounds 2024               # Show rounds
  python main.py --viewer --year 2024 --round 5   # Direct replay
  python main.py --viewer --year 2023 --round 1 --qualifying --no-hud
```

---

## Core Functions Explained

### Data Loading Functions

#### `load_session(year, round_number, session_type)`

**Purpose**: Load a Formula 1 session from the fastf1 API with caching.

**Parameters**:
- `year` (int): Season year (e.g., 2024)
- `round_number` (int): Round number (1-24)
- `session_type` (str): 'R' (race), 'Q' (qualifying), 'S' (sprint), 'SQ' (sprint qual)

**Returns**: `fastf1.Session` object with all session data

**Example**:
```python
from src.f1_data import load_session

# Load Silverstone 2024 race
session = load_session(2024, 12, 'R')
print(f"Loaded: {session.event['EventName']}")
print(f"Drivers: {len(session.drivers)}")
```

**What It Does**:
1. Connects to fastf1 API
2. Checks local cache for existing data
3. Downloads session data if not cached
4. Returns Session object with:
   - Laps data for all drivers
   - Track geometry
   - Event metadata (name, location, date)
   - Driver information
   - Weather data

---

#### `enable_cache()`

**Purpose**: Initialize fastf1 local caching system.

**Parameters**: None

**Returns**: None

**Example**:
```python
from src.f1_data import enable_cache

enable_cache()
# Now subsequent load_session() calls will use/populate cache
```

**What It Does**:
1. Reads cache location from settings
2. Creates cache directory if missing
3. Tells fastf1 to store/use cache

---

#### `get_race_telemetry(session, session_type='R')`

**Purpose**: Transform raw session data into 25 FPS replay-ready telemetry frames.

**Parameters**:
- `session`: fastf1.Session object (from `load_session()`)
- `session_type` (str): Session type ('R', 'S', 'Q', 'SQ')

**Returns**: Dictionary with keys:
- `frames` (list): Frame data for each of 25 FPS timestamps
- `driver_colors` (dict): Hex colors for each driver (#RRGGBB)
- `track_statuses` (list): Track flag data per frame
- `total_laps` (int): Race distance in laps

**Example**:
```python
from src.f1_data import load_session, get_race_telemetry, enable_cache

enable_cache()
session = load_session(2024, 12, 'R')
telemetry = get_race_telemetry(session)

print(f"Total frames: {len(telemetry['frames'])}")
print(f"Total laps: {telemetry['total_laps']}")
print(f"Drivers: {list(telemetry['driver_colors'].keys())}")

# Access frame at 30 seconds into race
frame_at_30s = telemetry['frames'][750]  # 30s * 25fps
print(f"Leader at 30s: {frame_at_30s['leader']}")
```

**Frame Structure** (each element in `frames`):
```python
{
    "lap": 5,                    # Current lap number
    "t": 234.56,                 # Time in seconds
    "drivers": {
        "VER": {
            "position": 1,       # Race position
            "speed": 285.5,      # km/h
            "lap": 5,            # Lap number
            "rel_dist": 0.456,   # 0-1 around circuit
            "x": 1234.5,         # World X coordinate
            "y": 5678.9,         # World Y coordinate
            "throttle": 100.0,   # 0-100%
            "brake": 0.0,        # 0-100%
            "gear": 6,           # 1-8
            "drs": 1,            # 0=off, 1=on
            "tyre": 1,           # Tyre compound (1=soft, 2=medium, 3=hard)
        },
        # ... other drivers
    },
    "leader": "VER",             # Position leader code
    "safety_car": {              # null if not deployed
        "x": 1234.5,
        "y": 5678.9,
        "phase": "on_track",     # deploying/on_track/returning
        "alpha": 1.0             # 0-1 for fade animation
    },
    "weather": {
        "air_temp": 18.5,        # Celsius
        "track_temp": 25.0,      # Celsius
        "humidity": 72.0,        # 0-100%
        "wind_speed": 1.5,       # m/s
        "wind_direction": 120,   # degrees
        "rain_state": "DRY"      # DRY/DAMP/WET
    }
}
```

---

#### `get_quali_telemetry(session, session_type='Q')`

**Purpose**: Extract qualifying session telemetry for qualifying replay.

**Parameters**:
- `session`: fastf1.Session (qualifying or sprint qualifying)
- `session_type` (str): 'Q' or 'SQ'

**Returns**: Dictionary with qualifying lap data

**Example**:
```python
from src.f1_data import load_session, get_quali_telemetry, enable_cache

session = load_session(2024, 5, 'Q')  # Monaco qualifying
quali_data = get_quali_telemetry(session)
```

---

### Replay & Visualization Functions

#### `run_arcade_replay(frames, track_statuses, example_lap, drivers, ...)`

**Purpose**: Launch the main race replay window with full telemetry visualization.

**Parameters** (key ones):
- `frames` (list): Frame data from `get_race_telemetry()`
- `track_statuses` (list): Track flag data
- `example_lap`: Sample telemetry for track geometry
- `drivers` (list): Driver codes
- `title` (str): Window title
- `playback_speed` (float): Initial speed (0.1-256.0)
- `driver_colors` (dict): Color mapping
- `visible_hud` (bool): Show overlays?
- `session_info` (dict): Event metadata for display
- `enable_telemetry` (bool): Start WebSocket server?

**Returns**: None (blocking - runs until window closed)

**Example**:
```python
from src.f1_data import load_session, get_race_telemetry, enable_cache
from src.run_session import run_arcade_replay

enable_cache()
session = load_session(2024, 12, 'R')
telemetry = get_race_telemetry(session)

run_arcade_replay(
    frames=telemetry['frames'],
    track_statuses=telemetry['track_statuses'],
    example_lap=example_lap,
    drivers=session.drivers,
    title="Silverstone 2024 Race",
    playback_speed=1.0,
    driver_colors=telemetry['driver_colors'],
    enable_telemetry=True  # Start WebSocket for other tools
)
```

---

#### `F1RaceReplayWindow`

**Purpose**: Core arcade.Window subclass handling all replay rendering and controls.

**Key Methods**:
- `on_draw()`: Renders frame, track, drivers, overlays
- `on_key_press(key)`: Handles keyboard input
- `update(delta_time)`: Updates frame, physics, telemetry

**Key Properties**:
- `frame_index`: Current frame number
- `paused`: Playback paused?
- `playback_speed`: Current speed multiplier
- `telemetry_stream`: TelemetryStreamServer instance

**Example** (custom subclass):
```python
from src.interfaces.race_replay import F1RaceReplayWindow

class CustomReplayWindow(F1RaceReplayWindow):
    def on_draw(self):
        super().on_draw()
        # Add custom overlays here
        
    def on_key_press(self, key, _):
        super().on_key_press(key, _)
        if key == arcade.key.C:
            print("Custom key handler!")
```

---

### Strategy & Analysis Functions

#### `StrategyEngine.find_optimum_strategy(curr_lap, current_compound)`

**Purpose**: Calculate optimal pit stop strategy based on current tyre compound.

**Parameters**:
- `curr_lap` (int): Current lap number
- `current_compound` (str): Current tyre compound ('SOFT', 'MEDIUM', 'HARD', etc)

**Returns**: Tuple of `(best_stints, score)`
- `best_stints`: List of tuples `[(compound, laps_in_stint), ...]`
- `score`: Quality score (0-1, higher is better)

**Example**:
```python
from src.strategy_engine import StrategyEngine

engine = StrategyEngine(total_laps=57)

# Driver on soft tyres at lap 12
stints, score = engine.find_optimum_strategy(curr_lap=12, current_compound='SOFT')
print(f"Strategy: {stints}")  # [('SOFT', 8), ('HARD', 37)]
print(f"Score: {score}")       # 1.0
```

**How It Works**:
1. Determines remaining laps to race end
2. Analyzes current tyre degradation curve
3. Predicts optimal pit window
4. Recommends compound sequence
5. Returns strategy confidence score

---

#### `BayesianTyreDegradationModel`

**Purpose**: Statistically model tyre degradation across a race using Bayesian inference.

**Key Methods**:

**`fit(laps_df, driver=None)`**
- Analyzes driver's lap times to estimate degradation
- Accounts for fuel, track evolution, weather

**`predict_next_lap(fuel, track_condition, lap_on_tyre, compound)`**
- Predicts next lap time given current conditions
- Returns: (predicted_time, confidence_interval)

**`get_health(compound)`**
- Returns: `{"degradation_rate": 0.01, "remaining_life": 15, ...}`

**`get_degradation_rate(compound)`**
- Returns float: Seconds per lap of degradation

**Example**:
```python
from src.bayesian_tyre_model import BayesianTyreDegradationModel
import pandas as pd

# Load lap data
laps_df = pd.read_csv('race_laps.csv')

# Create and fit model
model = BayesianTyreDegradationModel()
model.fit(laps_df, driver='VER')

# Predict next lap
next_time, ci = model.predict_next_lap(
    fuel=50.0,  # kg
    track_condition='DRY',
    lap_on_tyre=5,
    compound='MEDIUM'
)
print(f"Predicted lap time: {next_time:.2f}s ±{ci:.2f}s")

# Check current health
health = model.get_health('MEDIUM')
print(f"Degradation: {health['degradation_rate']:.3f}s/lap")
```

---

#### `run_qualifying_replay(session, data, title, ready_file=None)`

**Purpose**: Launch qualifying-specific replay window (lap times, not race progress).

**Parameters**:
- `session`: fastf1.Session (qualifying)
- `data`: Output from `get_quali_telemetry()`
- `title` (str): Window title
- `ready_file` (str): Optional file to signal readiness

**Returns**: None (blocking)

**Example**:
```python
from src.f1_data import load_session, get_quali_telemetry, enable_cache
from src.interfaces.qualifying import run_qualifying_replay

session = load_session(2024, 5, 'Q')  # Monaco qualifying
quali_data = get_quali_telemetry(session)

run_qualifying_replay(
    session=session,
    data=quali_data,
    title="Monaco 2024 Qualifying"
)
```

---

### Insights & Dashboard Functions

#### `launch_insights_menu()`

**Purpose**: Open the insights analysis menu in a separate window.

**Parameters**: None

**Returns**: None (spawns subprocess)

**Example**:
```python
from src.run_session import launch_insights_menu

launch_insights_menu()
# Menu opens in ~1 second in separate window
```

**What Opens**:
- Categorized analysis tools
- Launcher buttons for each insight window
- Connection status for telemetry stream

---

#### `InsightsMenu`

**Purpose**: Qt-based main window containing insight launcher buttons.

**Key Methods**:
- `launch_driver_telemetry()`: Open driver telemetry window
- `launch_tyre_strategy()`: Show tyre analysis
- `launch_hardware_link()`: Serial communication interface

---

### Telemetry Streaming Functions

#### `TelemetryStreamServer`

**Purpose**: WebSocket server broadcasting replay telemetry at 25 FPS.

**Parameters**:
- `host` (str): Default "localhost"
- `port` (int): Default 9999

**Example**:
```python
from src.services.stream import TelemetryStreamServer
import json

# Start server
server = TelemetryStreamServer()
server.start()

# Connect client to ws://localhost:9999
# Receive frame data as JSON every 40ms (25fps)
```

**Emitted Data Format** (every frame):
```json
{
  "frame": { /* frame data */ },
  "frame_index": 1234,
  "total_frames": 50000,
  "playback_speed": 1.0,
  "is_paused": false,
  "session_data": {
    "lap": 5,
    "leader": "VER",
    "time": "02:34:56",
    "total_laps": 57
  }
}
```

---

## Features Deep Dive

### Race Replay Features

#### DRS (Drag Reduction System) Visualization

**What You See**:
- Blue highlighted sections on track = DRS zones
- Driver lights up when DRS is active
- Real DRS detection from telemetry

**Toggle With**: Press `D` key

#### Safety Car System

**Simulated Behavior**:
- Deploys when virtual/actual SC triggered
- Positions ~500m ahead of race leader
- Manages field bunching
- Returns when SC period ends
- Visual animation (fade in/out)

**Data Available**:
```python
frame["safety_car"] = {
    "x": float,           # Position X
    "y": float,           # Position Y
    "phase": "on_track",  # deploying/on_track/returning
    "alpha": 1.0          # 0-1 opacity for animation
}
```

#### Track Status Indicators

Real-time flag overlay shows:
- Yellow flags (specific sectors)
- Red flags (session stopped)
- Virtual Safety Car/Safety car deployed
- Green flag (normal racing)

#### Weather Visualization

Live weather data displayed:
- **Air Temperature**: Affects tyre warmup rate
- **Track Temperature**: Primary grip factor
- **Wind**: Direction and speed (cosmetic)
- **Humidity**: Secondary grip factor
- **Rain**: DRY/DAMP/WET states

---

### Telemetry Streaming

The telemetry stream broadcasts live race data to connected clients every frame (40ms).

#### Why It's Powerful

Instead of everything in one window, you can:
- Build custom dashboards in separate tools
- Create pit wall style interfaces
- Feed data to hardware (steering wheels, displays)
- Build machine learning models in real-time
- Log data for post-race analysis

#### Connecting a Client

```python
from src.services.stream import TelemetryStreamClient
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    frame = data["frame"]
    print(f"Frame {data['frame_index']}: Leader is {frame['leader']}")

ws = websocket.WebSocketApp("ws://localhost:9999",
    on_message=on_message)
ws.run_forever()
```

#### Data You Get

Each frame contains:
- All driver telemetry (position, speed, throttle, brake, gear, DRS, tyre)
- Safety car status and position
- Weather conditions (temp, wind, humidity, rain)
- Track status (flags, yellow/red)
- Lap information (current lap, lap times)
- Race leader and gaps

---

### Strategy Tools

#### Tyre Degradation Modeling

The **Bayesian model** analyzes:

**State-Space Model**:
```
α_{t+1} = (1 - I_pit) * (α_t + ν * A_track) + I_pit * α_reset + η_t
y_t = α_t + γ * fuel_t + δ_mismatch + ε_t
```

Where:
- `α_t` = latent tire pace (true capability)
- `ν` = degradation rate (compound-specific)
- `A_track` = track abrasion factor
- `γ` = fuel effect
- `δ_mismatch` = condition-tyre mismatch penalty

**Tyre Data** (built-in):
```
SOFT:   max_life=20  laps,  optimum_range=(12-18)
MEDIUM: max_life=32  laps,  optimum_range=(20-28)
HARD:   max_life=50  laps,  optimum_range=(35-45)
INTER:  max_life=25  laps,  optimum_range=(15-22)
WET:    max_life=20  laps,  optimum_range=(12-18)
```

#### Pit Stop Strategy Engine

```python
engine = StrategyEngine(total_laps=57)
stints, score = engine.find_optimum_strategy(12, 'SOFT')
```

**Produces**:
- Optimal pit lap number
- Tyre compound recommendations
- Strategy quality score

---

## Architecture Overview

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed component diagrams, data flow, and system design.

**High-Level Flow**:

```
┌──────────────────────────────────────────────────────┐
│ 1. User Launches Application                         │
│    (python main.py)                                  │
└──────────────┬───────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ 2. Session Selection (GUI or CLI)                    │
│    Choose: Year, Round, Session Type                 │
└──────────────┬───────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ 3. Data Loading (fastf1)                            │
│    load_session() → API/Cache                        │
└──────────────┬───────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ 4. Telemetry Processing                             │
│    get_race_telemetry() → 25 FPS frames             │
└──────────────┬───────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ 5. Launch Replay Window                             │
│    run_arcade_replay() → F1RaceReplayWindow         │
└──────────────┬───────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│ 6. Render Frames (25 FPS)                           │
│    on_draw() → Track + Drivers + Overlays           │
│                                                      │
│    Optionally:                                       │
│    - Stream telemetry via WebSocket (TelemetryStream)
│    - Show Insights menu (separate window)           │
│    - Run analysis tools (custom windows)            │
└──────────────────────────────────────────────────────┘
```

---

## Configuration

### Default Settings

```json
{
  "cache_location": ".fastf1-cache",
  "computed_data_location": "computed_data"
}
```

### Customizing Cache Location

Edit your settings file:
```json
{
  "cache_location": "/fast_storage/f1-cache",
  "computed_data_location": "/storage/f1-data"
}
```

Or set environment variable:
```bash
export F1_CACHE_LOCATION="/path/to/cache"  # macOS/Linux
set F1_CACHE_LOCATION=C:\path\to\cache     # Windows
```

### Other Configurations

**Season Configuration**:
Defaults to current year. Override in code:
```python
from src.lib.season import get_season, set_season
set_season(2023)
```

**Driver Colors**:
Automatically loaded from fastf1. Hex colors per driver in `get_race_telemetry()`.

---

## Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for detailed solutions to common issues.

### Quick Fixes

**"Module not found" error**:
```bash
pip install -r requirements.txt
pip install fastf1 scipy
```

**Replay window doesn't appear**:
```bash
# Run with verbose logging
python main.py --verbose
# Check console for errors
```

**Cache errors**:
```bash
# Clear cache and retry
rm -rf .fastf1-cache  # macOS/Linux
rmdir /s .fastf1-cache  # Windows

# Or set custom location in settings.json
```

**Telemetry stream not connecting**:
- Make sure `--enable-telemetry` or `enable_telemetry=True`
- Check port 9999 is available
- Check firewall settings

### Getting Help

1. Check [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Enable verbose logging: `python main.py --verbose`
3. Check console output for specific error messages
4. Review fastf1 documentation: https://docs.fastf1.dev

---

## Extending the Project

### Creating Custom Insight Windows

See [docs/ARCHITECTURE.md - Extension Guide](docs/ARCHITECTURE.md#extension-guide).

**Example**: Building a custom pit wall dashboard

```python
from src.gui.pit_wall_window import PitWallWindow
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class MyCustomDashboard(PitWallWindow):
    def setup_ui(self):
        """Override to create custom UI"""
        layout = QVBoxLayout()
        label = QLabel("My Custom Analysis")
        layout.addWidget(label)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def on_telemetry_data(self, data):
        """Called when telemetry frame arrives"""
        frame = data["frame"]
        leader = frame["leader"]
        print(f"Leader: {leader}")
```

### Adding Telemetry Consumers

Create a WebSocket client to receive telemetry:

```python
from src.services.stream import TelemetryStreamClient
import json

class MyAnalysisTool:
    def __init__(self):
        self.client = TelemetryStreamClient()
        self.client.data_received.connect(self.analyze_frame)
        self.client.start()
    
    def analyze_frame(self, data):
        frame = data["frame"]
        # Your analysis code here
        for driver_code, driver_data in frame["drivers"].items():
            speed = driver_data["speed"]
            # Do something with speed...
```

### Modifying Replay Visualization

Subclass `F1RaceReplayWindow`:

```python
from src.interfaces.race_replay import F1RaceReplayWindow
import arcade

class CustomReplayWindow(F1RaceReplayWindow):
    def on_draw(self):
        """Override to add custom drawing"""
        super().on_draw()  # Draw base replay
        
        # Add custom overlays
        arcade.draw_text(
            "My Custom Overlay",
            50, 50,
            arcade.color.WHITE, 14
        )
```

---

## Resources & Links

- **FastF1 Documentation**: https://docs.fastf1.dev
- **Arcade (Game Engine)**: https://arcade.academy
- **PySide6 Documentation**: https://doc.qt.io/qtforpython-6/
- **F1 Data Availability**: Check fastf1 docs for supported seasons/rounds
- **Contributing**: Follow project code style and add tests

---

## License

This project is provided as-is for educational and personal use.

---

## Support & Community

- Check the troubleshooting guide
- Review example code in `src/insights/`
- Explore the insights menu architecture for extension patterns