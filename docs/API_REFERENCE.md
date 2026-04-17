# F1 Race Strategy Replay - API Reference

Complete reference for classes, functions, and data structures in the F1 Race Strategy Replay project.

## Table of Contents

- [Data Loading API](#data-loading-api)
- [Replay & Visualization API](#replay--visualization-api)
- [Analysis & Strategy API](#analysis--strategy-api)
- [Telemetry Streaming API](#telemetry-streaming-api)
- [UI Components API](#ui-components-api)
- [Settings & Configuration API](#settings--configuration-api)
- [Data Structures](#data-structures)
- [Exception Handling](#exception-handling)

---

## Data Loading API

### Module: `src.f1_data`

#### `enable_cache()`

Initialize the fastf1 caching system.

**Signature**:
```python
def enable_cache() -> None
```

**Returns**: None

**Raises**: 
- `OSError` if cache directory cannot be created

**Example**:
```python
from src.f1_data import enable_cache
enable_cache()
```

**Note**: Must be called before any `load_session()` calls for caching to work.

---

#### `load_session(year: int, round_number: int, session_type: str = "R") -> fastf1.Session`

Load an F1 session from the fastf1 API with local caching.

**Parameters**:
- `year` (int): Season year (e.g., 2024)
- `round_number` (int): Round number (1-24 typically)
- `session_type` (str): Session type code
  - `"R"`: Race (default)
  - `"Q"`: Qualifying
  - `"S"`: Sprint
  - `"SQ"`: Sprint Qualifying

**Returns**: `fastf1.Session` object

**Raises**:
- `ValueError`: If year/round/session_type invalid
- `ConnectionError`: If API unreachable and not in cache
- `IOError`: If cache corrupted

**Example**:
```python
from src.f1_data import enable_cache, load_session

enable_cache()

# Load Silverstone 2024 race
session = load_session(2024, 12, 'R')

print(f"Event: {session.event['EventName']}")
print(f"Drivers: {list(session.drivers)}")
print(f"Laps: {len(session.laps)}")
```

**Session Object Structure**:
```python
session.event          # Event metadata
session.drivers        # List of driver codes
session.laps           # DataFrame of all laps
session.telemetry      # Available on some sessions
```

---

#### `get_driver_colors(session: fastf1.Session) -> Dict[str, str]`

Extract driver-to-color mapping from session.

**Parameters**:
- `session` (fastf1.Session): Session object from `load_session()`

**Returns**: Dict[str, str] - Mapping of driver code to hex color
- Keys: Driver codes (e.g., "VER", "HAM")
- Values: Hex color strings (e.g., "#FF0000")

**Example**:
```python
colors = get_driver_colors(session)
print(colors["VER"])    # "#0082FA" (Red Bull blue)
print(colors["LEC"])    # "#DC0000" (Ferrari red)
```

---

#### `get_circuit_rotation(session: fastf1.Session) -> float`

Calculate the rotation angle of the circuit for correct display orientation.

**Parameters**:
- `session` (fastf1.Session): Session object

**Returns**: float - Rotation angle in degrees

**Example**:
```python
rotation = get_circuit_rotation(session)
# Use in arcade window: transform track coordinates
```

---

#### `get_race_telemetry(session: fastf1.Session, session_type: str = "R") -> Dict`

Transform session data into replay-ready telemetry frames.

**Parameters**:
- `session` (fastf1.Session): Session from `load_session()`
- `session_type` (str): Session type ('R', 'S', 'Q', 'SQ')

**Returns**: Dictionary with structure:
```python
{
    "frames": List[Dict],           # 25 FPS frame data
    "driver_colors": Dict[str, str], # Driver hex colors
    "track_statuses": List[Dict],   # Track flag history
    "total_laps": int               # Race distance
}
```

**Example**:
```python
from src.f1_data import load_session, get_race_telemetry, enable_cache

enable_cache()
session = load_session(2024, 12, 'R')
telemetry = get_race_telemetry(session)

print(f"Total frames: {len(telemetry['frames'])}")
print(f"Total laps: {telemetry['total_laps']}")
print(f"Drivers: {list(telemetry['driver_colors'].keys())}")

# Access individual frame
frame = telemetry['frames'][750]  # Frame at 30 seconds (750/25fps)
print(f"Leader: {frame['leader']}")
print(f"Lap: {frame['lap']}")
```

**Frame Dictionary** (see Data Structures section)

---

#### `get_quali_telemetry(session: fastf1.Session, session_type: str = "Q") -> Dict`

Extract qualifying session telemetry.

**Parameters**:
- `session` (fastf1.Session): Qualifying session
- `session_type` (str): 'Q' or 'SQ'

**Returns**: Dictionary with qualifying lap data

**Example**:
```python
from src.f1_data import load_session, get_quali_telemetry, enable_cache

session = load_session(2024, 5, 'Q')  # Monaco qualifying
quali_data = get_quali_telemetry(session)
```

---

#### `list_rounds(year: int) -> None`

Print all rounds for a given season.

**Parameters**:
- `year` (int): Season year

**Returns**: None (prints to stdout)

**Example**:
```bash
python main.py --list-rounds 2024
```

---

#### `list_sprints(year: int) -> None`

Print all sprint weekends for a given season.

**Parameters**:
- `year` (int): Season year

**Returns**: None (prints to stdout)

**Example**:
```bash
python main.py --list-sprints 2024
```

---

## Replay & Visualization API

### Module: `src.run_session`

#### `run_arcade_replay(...) -> None`

Launch the main arcade-based race replay window.

**Signature**:
```python
def run_arcade_replay(
    frames: List[Dict],
    track_statuses: List[Dict],
    example_lap: pd.Series,
    drivers: List[str],
    title: str = "F1 Replay",
    playback_speed: float = 1.0,
    driver_colors: Optional[Dict] = None,
    circuit_rotation: float = 0.0,
    total_laps: Optional[int] = None,
    visible_hud: bool = True,
    session_info: Optional[Dict] = None,
    session: Optional[fastf1.Session] = None,
    enable_telemetry: bool = False
) -> None
```

**Parameters**:
- `frames` (List[Dict]): Frame data from `get_race_telemetry()`
- `track_statuses` (List[Dict]): Track status history
- `example_lap` (pd.Series): Reference lap for track geometry
- `drivers` (List[str]): Driver codes
- `title` (str): Window title (default: "F1 Replay")
- `playback_speed` (float): Initial speed multiplier (default: 1.0)
- `driver_colors` (Dict): Driver code → hex color mapping
- `circuit_rotation` (float): Track rotation in degrees
- `total_laps` (int): Race distance in laps
- `visible_hud` (bool): Show UI overlays (default: True)
- `session_info` (Dict): Event metadata for display
- `session` (fastf1.Session): Session object for analysis tools
- `enable_telemetry` (bool): Start WebSocket streaming (default: False)

**Returns**: None (blocking - runs until window closed)

**Raises**:
- `pygame.error` if display cannot be created
- `OSError` if WebSocket port unavailable (if enable_telemetry=True)

**Example**:
```python
from src.f1_data import load_session, get_race_telemetry, enable_cache
from src.run_session import run_arcade_replay

enable_cache()
session = load_session(2024, 12, 'R')
telemetry = get_race_telemetry(session)

# Get example lap for track layout
fastest_lap = session.laps.pick_fastest()
example_lap = fastest_lap.get_telemetry()

run_arcade_replay(
    frames=telemetry['frames'],
    track_statuses=telemetry['track_statuses'],
    example_lap=example_lap,
    drivers=session.drivers,
    title="Silverstone 2024 - Race",
    playback_speed=1.0,
    driver_colors=telemetry['driver_colors'],
    circuit_rotation=get_circuit_rotation(session),
    total_laps=telemetry['total_laps'],
    visible_hud=True,
    enable_telemetry=True
)
```

---

#### `launch_insights_menu() -> None`

Open the insights analysis menu in a separate subprocess.

**Signature**:
```python
def launch_insights_menu() -> None
```

**Returns**: None (spawns subprocess)

**Example**:
```python
from src.run_session import launch_insights_menu

launch_insights_menu()
# Menu appears in ~1 second
```

**Note**: Opens asynchronously in separate process. Safe to call from main replay.

---

### Module: `src.interfaces.race_replay`

#### `class F1RaceReplayWindow(arcade.Window)`

Main arcade window for race replay visualization and interaction.

**Constructor**:
```python
def __init__(
    self,
    frames: List[Dict],
    track_statuses: List[Dict],
    example_lap: pd.Series,
    drivers: List[str],
    title: str,
    playback_speed: float = 1.0,
    driver_colors: Optional[Dict] = None,
    circuit_rotation: float = 0.0,
    total_laps: Optional[int] = None,
    visible_hud: bool = True,
    session_info: Optional[Dict] = None,
    session: Optional[fastf1.Session] = None,
    enable_telemetry: bool = False
)
```

**Key Properties**:
```python
frame_index: float           # Current frame (0-n_frames)
paused: bool                 # Playback paused?
playback_speed: float        # Speed multiplier
n_frames: int                # Total frames
drivers: List[str]           # Driver codes
visible_hud: bool            # HUD visible?
telemetry_stream: Optional   # WebSocket server
```

**Key Methods**:

**`on_draw() -> None`**
- Render current frame (called every arcade frame ~60 FPS)
- Draws track, drivers, overlays

**`on_key_press(key: int, modifiers: int) -> None`**
- Handle keyboard input
- Supports: SPACE (play/pause), arrows (seek), D (DRS), L (labels), H (HUD), etc.

**`on_key_release(key: int, modifiers: int) -> None`**
- Handle key release

**`update(delta_time: float) -> None`**
- Update frame index based on playback speed
- Update telemetry stream
- Update UI components

**Example Subclass**:
```python
from src.interfaces.race_replay import F1RaceReplayWindow
import arcade

class CustomReplayWindow(F1RaceReplayWindow):
    def on_draw(self):
        super().on_draw()
        # Add custom overlays
        arcade.draw_text(
            f"Custom: {self.frame_index:.0f}/{self.n_frames}",
            50, 50,
            arcade.color.WHITE,
            14
        )
    
    def on_key_press(self, key, modifiers):
        super().on_key_press(key, modifiers)
        if key == arcade.key.C:
            print("Custom key pressed!")
```

---

### Module: `src.interfaces.qualifying`

#### `run_qualifying_replay(session: fastf1.Session, data: Dict, title: str, ready_file: Optional[str] = None) -> None`

Launch qualifying-specific replay window.

**Parameters**:
- `session` (fastf1.Session): Qualifying session
- `data` (Dict): Output from `get_quali_telemetry()`
- `title` (str): Window title
- `ready_file` (str): Optional file path to write "ready" when window created

**Returns**: None (blocking)

**Example**:
```python
from src.f1_data import load_session, get_quali_telemetry, enable_cache
from src.interfaces.qualifying import run_qualifying_replay

session = load_session(2024, 5, 'Q')
quali_data = get_quali_telemetry(session)

run_qualifying_replay(
    session=session,
    data=quali_data,
    title="Monaco 2024 Qualifying",
    ready_file="/tmp/quali_ready.txt"
)
```

---

## Analysis & Strategy API

### Module: `src.strategy_engine`

#### `class StrategyEngine`

Pit stop strategy optimization engine.

**Constructor**:
```python
def __init__(self, total_laps: int = 57)
```

**Parameters**:
- `total_laps` (int): Race distance in laps

**Key Methods**:

**`find_optimum_strategy(curr_lap: int, current_compound: str) -> Tuple[List[Tuple[str, int]], float]`**

Calculate optimal pit strategy.

**Parameters**:
- `curr_lap` (int): Current lap number
- `current_compound` (str): Current tyre compound
  - "SOFT", "MEDIUM", "HARD", "INTER", "WET", "UNKNOWN"

**Returns**: Tuple of:
1. `List[Tuple[str, int]]` - Stints: [(compound, laps_in_stint), ...]
2. `float` - Strategy score (0-1, higher is better)

**Example**:
```python
from src.strategy_engine import StrategyEngine

engine = StrategyEngine(total_laps=57)

# At lap 15 on soft tyres
stints, score = engine.find_optimum_strategy(15, "SOFT")

print(f"Strategy: {stints}")
# Output: [('SOFT', 8), ('HARD', 34)]

print(f"Confidence: {score:.2f}")
# Output: 1.00
```

**Tyre Data** (built-in):
```python
{
    "SOFT":   {"max_life": 20,  "optimum_range": (12, 18)},
    "MEDIUM": {"max_life": 32,  "optimum_range": (20, 28)},
    "HARD":   {"max_life": 50,  "optimum_range": (35, 45)},
    "INTER":  {"max_life": 25,  "optimum_range": (15, 22)},
    "WET":    {"max_life": 20,  "optimum_range": (12, 18)},
}
```

---

### Module: `src.bayesian_tyre_model`

#### `class BayesianTyreDegradationModel`

Statistical tyre degradation analysis using Bayesian state-space model.

**Constructor**:
```python
def __init__(self, config: Optional[StateSpaceConfig] = None)
```

**Parameters**:
- `config` (StateSpaceConfig): Model configuration (optional)

**Key Methods**:

**`fit(laps_df: pd.DataFrame, driver: Optional[str] = None) -> None`**

Fit model to lap data.

**Parameters**:
- `laps_df` (pd.DataFrame): Lap data from fastf1 session
- `driver` (str): Driver code filter (optional)

**Returns**: None

**Example**:
```python
from src.bayesian_tyre_model import BayesianTyreDegradationModel

model = BayesianTyreDegradationModel()
model.fit(session.laps, driver='VER')
```

---

**`predict_next_lap(fuel: float, track_condition: str, lap_on_tyre: int, compound: str) -> Tuple[float, float]`**

Predict next lap time given current conditions.

**Parameters**:
- `fuel` (float): Fuel remaining in kg
- `track_condition` (str): 'DRY', 'DAMP', or 'WET'
- `lap_on_tyre` (int): Laps completed on current tyre set
- `compound` (str): Tyre compound ('SOFT', 'MEDIUM', 'HARD', etc.)

**Returns**: Tuple of (predicted_time, confidence_interval)

**Example**:
```python
# Predict lap 45 in dry conditions with 35kg fuel on medium tyre (lap 8 on set)
lap_time, confidence = model.predict_next_lap(
    fuel=35.0,
    track_condition='DRY',
    lap_on_tyre=8,
    compound='MEDIUM'
)

print(f"Predicted: {lap_time:.3f}s ±{confidence:.3f}s")
```

---

**`get_health(compound: str) -> Dict[str, Any]`**

Get current health metrics for tyre compound.

**Parameters**:
- `compound` (str): Tyre compound

**Returns**: Dictionary with metrics:
```python
{
    "degradation_rate": float,  # seconds per lap
    "remaining_life": int,      # estimated laps
    "temperature": float,       # operating temp
    "max_life": int,            # maximum life
}
```

**Example**:
```python
health = model.get_health("MEDIUM")
print(f"Degradation: {health['degradation_rate']:.3f}s/lap")
print(f"Remaining: {health['remaining_life']} laps")
```

---

**`get_degradation_rate(compound: str) -> float`**

Get degradation rate for compound.

**Parameters**:
- `compound` (str): Tyre compound

**Returns**: float - Seconds per lap of degradation

**Example**:
```python
rate = model.get_degradation_rate("SOFT")
print(f"Soft tyre: {rate:.3f}s/lap degradation")
```

---

## Telemetry Streaming API

### Module: `src.services.stream`

#### `class TelemetryStreamServer`

WebSocket server broadcasting replay telemetry.

**Constructor**:
```python
def __init__(self, host: str = "localhost", port: int = 9999)
```

**Parameters**:
- `host` (str): Bind address (default: "localhost")
- `port` (int): Bind port (default: 9999)

**Key Methods**:

**`start() -> None`**

Start the WebSocket server.

**Raises**: `OSError` if port already in use

**`stop() -> None`**

Stop the server and close all connections.

**`broadcast(data: Dict) -> None`**

Send data to all connected clients.

**Parameters**:
- `data` (Dict): Frame data to broadcast

**Example**:
```python
from src.services.stream import TelemetryStreamServer

server = TelemetryStreamServer()
server.start()
print("Server started on ws://localhost:9999")

# Broadcast frame (called automatically by replay)
server.broadcast({
    "frame": {...},
    "frame_index": 123,
    ...
})

server.stop()
```

---

#### `class TelemetryStreamClient`

Qt-based WebSocket client for receiving telemetry.

**Constructor**:
```python
def __init__(self, url: str = "ws://localhost:9999")
```

**Parameters**:
- `url` (str): WebSocket URL to connect to

**Key Methods**:

**`start() -> None`**

Start client and connect to server.

**`stop() -> None`**

Disconnect and stop client.

**Key Signals** (Qt):
- `data_received(data: Dict)` - Emitted when frame received
- `connection_status(status: str)` - Emitted on connection change ("Connected", "Disconnected", etc.)
- `error_occurred(error: str)` - Emitted on error

**Example**:
```python
from src.services.stream import TelemetryStreamClient
from PySide6.QtCore import QObject, Slot

class MyAnalysisTool(QObject):
    def __init__(self):
        super().__init__()
        self.client = TelemetryStreamClient()
        self.client.data_received.connect(self.on_data_received)
        self.client.start()
    
    @Slot(dict)
    def on_data_received(self, data):
        frame = data["frame"]
        print(f"Frame {data['frame_index']}: Leader is {frame['leader']}")
```

---

## UI Components API

### Module: `src.ui_components`

#### Base Component

All UI components inherit from or follow this pattern:

```python
class UIComponent:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
    
    def draw(self) -> None:
        """Render component"""
        pass
    
    def update(self, frame: Dict) -> None:
        """Update from frame data"""
        pass
```

#### `class LeaderboardComponent`

Display live race standings.

**Constructor**:
```python
def __init__(self, x: float, width: float = 240, visible: bool = True)
```

**Methods**:
- `draw()` - Render leaderboard
- `update(frame)` - Update from frame data

---

#### `class WeatherComponent`

Display weather conditions.

**Constructor**:
```python
def __init__(self, left: float, top_offset: float = 170, visible: bool = True)
```

---

#### `class DriverInfoComponent`

Display detailed telemetry for selected driver.

**Constructor**:
```python
def __init__(self, left: float, width: float = 300)
```

**Key Attributes**:
- `degradation_integrator` - Optional tyre degradation model

---

## Settings & Configuration API

### Module: `src.lib.settings`

#### `class SettingsManager` (Singleton)

Manage application settings with JSON persistence.

**Methods**:

**`get(key: str, default: Any = None) -> Any`**

Get setting value.

**Parameters**:
- `key` (str): Setting key
- `default`: Default value if not found

**Returns**: Setting value or default

**Example**:
```python
from src.lib.settings import get_settings

settings = get_settings()
cache_location = settings.cache_location
computed_data_location = settings.computed_data_location
```

---

### Module: `src.lib.season`

#### `get_season() -> int`

Get current F1 season year.

**Returns**: int - Current season year

**Example**:
```python
from src.lib.season import get_season

year = get_season()
print(f"Current season: {year}")
```

---

## Data Structures

### Frame Dictionary

Each frame in `telemetry['frames']`:

```python
{
    "lap": int,                       # Current lap number
    "t": float,                       # Time in seconds from session start
    
    "drivers": {
        "VER": {                      # Driver code
            "position": int,          # Race position (1-20)
            "speed": float,           # km/h
            "lap": int,               # Lap number
            "rel_dist": float,        # 0-1 around circuit (0=start/finish)
            "x": float,               # World X coordinate
            "y": float,               # World Y coordinate
            "throttle": float,        # 0-100% pedal input
            "brake": float,           # 0-100% pedal input
            "gear": int,              # 1-8, 0=neutral
            "drs": int,               # 0=off, 1=on
            "tyre": int,              # 1=soft, 2=medium, 3=hard, 4=inter, 5=wet
        },
        # ... more drivers
    },
    
    "leader": "VER",                  # Leading driver code
    
    "safety_car": {                   # null if not deployed
        "x": float,                   # World X
        "y": float,                   # World Y
        "phase": "on_track",          # deploying/on_track/returning
        "alpha": float,               # 0-1 opacity
    },
    
    "weather": {
        "air_temp": float,            # Celsius
        "track_temp": float,          # Celsius
        "humidity": float,            # 0-100%
        "wind_speed": float,          # m/s
        "wind_direction": int,        # 0-360 degrees
        "rain_state": "DRY"           # DRY/DAMP/WET
    }
}
```

### Broadcast Data Structure

Data sent by `TelemetryStreamServer`:

```python
{
    "frame": {...},                   # Frame dictionary (see above)
    "frame_index": int,               # Frame number (0-total_frames)
    "total_frames": int,              # Total frames in session
    "playback_speed": float,          # Current speed multiplier
    "is_paused": bool,                # Paused?
    "session_data": {
        "lap": int,                   # Current lap
        "leader": "VER",              # Leading driver
        "time": "00:34:12",           # Formatted time
        "total_laps": 57              # Race distance
    },
    "track_status": "1"               # Current track status code
}
```

### Session Info Dictionary

Event metadata for display:

```python
{
    "event_name": "Silverstone",
    "circuit_name": "Silverstone Circuit",
    "country": "United Kingdom",
    "year": 2024,
    "round": 12,
    "date": "July 7, 2024",
    "total_laps": 52,
    "circuit_length_m": 5891.0
}
```

---

## Exception Handling

### Common Exceptions

**`fastf1.DataNotAvailableError`**
Raised when session data cannot be loaded from API.

```python
try:
    session = load_session(2024, 99, 'R')  # Invalid round
except ValueError:
    print("Invalid round number")
```

**`OSError`**
File or network I/O errors.

```python
try:
    enable_cache()
except OSError as e:
    print(f"Cache initialization failed: {e}")
```

**`pygame.error` / `RuntimeError`** (Arcade)
Display or rendering errors.

```python
try:
    run_arcade_replay(...)
except RuntimeError as e:
    print(f"Replay failed: {e}")
```

---

**Last Updated**: April 2026 | API v1.0
