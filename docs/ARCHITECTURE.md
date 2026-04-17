# F1 Race Strategy Replay - Architecture & Design

This document provides a detailed technical overview of the system architecture, component relationships, data flow, and guidelines for extending the project.

## Table of Contents

- [System Architecture](#system-architecture)
- [Component Overview](#component-overview)
- [Data Flow Pipeline](#data-flow-pipeline)
- [Core Subsystems](#core-subsystems)
- [Extension Guide](#extension-guide)
- [Design Patterns](#design-patterns)

---

## System Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        F1 RACE STRATEGY REPLAY                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────┐         ┌─────────────────────┐        │
│  │   SESSION SELECTION  │         │   DATA LOADING      │        │
│  │  ┌─────────────────┐ │         │  ┌─────────────────┐│        │
│  │  │  GUI Launcher   │ │         │  │ FastF1 API      ││        │
│  │  │  (PySide6)      │ │         │  │ Cache Manager   ││        │
│  │  │  CLI Selector   │ │         │  │ Session Loading ││        │
│  │  └─────────────────┘ │         │  └─────────────────┘│        │
│  └─────────────────────┘         └─────────────────────┘        │
│           │                              │                        │
│           └──────────────┬───────────────┘                        │
│                          ▼                                        │
│           ┌────────────────────────────┐                         │
│           │  TELEMETRY PROCESSING      │                         │
│           │  ┌──────────────────────┐  │                         │
│           │  │ Data Transformation  │  │                         │
│           │  │ (25 FPS Frames)      │  │                         │
│           │  │ Driver Positioning   │  │                         │
│           │  │ Weather Data         │  │                         │
│           │  │ Track Status         │  │                         │
│           │  │ DRS Detection        │  │                         │
│           │  └──────────────────────┘  │                         │
│           └────────────────────────────┘                         │
│                          │                                        │
│        ┌─────────────────┼─────────────────┐                     │
│        ▼                 ▼                 ▼                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   REPLAY     │  │  TELEMETRY   │  │   INSIGHTS   │            │
│  │   ENGINE     │  │   STREAM     │  │   MENU       │            │
│  │ (Arcade)    │  │ (WebSocket)  │  │ (PySide6)    │            │
│  │              │  │              │  │              │            │
│  │ - Track Geo  │  │ - Server     │  │ - Launcher   │            │
│  │ - Drivers    │  │ - Broadcast  │  │ - Tools      │            │
│  │ - Overlays   │  │ - Clients    │  │ - Windows    │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│        │                 │                 │                     │
│        └─────────────────┼─────────────────┘                     │
│                          ▼                                        │
│           ┌────────────────────────────┐                         │
│           │   ANALYSIS SUBSYSTEMS      │                         │
│           │  ┌──────────────────────┐  │                         │
│           │  │ Strategy Engine      │  │                         │
│           │  │ Tyre Degradation     │  │                         │
│           │  │ Qualifying Analysis  │  │                         │
│           │  │ Custom Windows       │  │                         │
│           │  └──────────────────────┘  │                         │
│           └────────────────────────────┘                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Component Overview

### 1. Session Selection Layer

**Purpose**: Get user input for which F1 session to replay

**Components**:

#### `main.py`
- Application entrypoint
- Command-line argument parsing
- Route to GUI or CLI based on flags
- Integration point for all systems

#### `src/gui/race_selection.py`
- PySide6-based GUI window
- Year/Round/Session selection dropdowns
- Event name display
- Launch button

#### `src/cli/race_selection.py`
- Terminal-based selection using `questionary`
- Rich formatted output
- Interactive prompts

**Data Output**:
```python
{
    "year": 2024,
    "round": 12,
    "session_type": "R"  # R/Q/S/SQ
}
```

---

### 2. Data Loading & Caching Layer

**Purpose**: Load F1 data from fastf1 API and manage local cache

**Components**:

#### `src/f1_data.py` - Core Data Module

**Key Functions**:

- `load_session(year, round, session_type)` → fastf1.Session
  - Handles API connection
  - Checks cache
  - Downloads if missing
  - Returns hydrated session object

- `enable_cache()` → None
  - Initializes cache directory
  - Configures fastf1 caching

- `get_driver_colors(session)` → Dict[str, str]
  - Extract driver-to-color mapping from fastf1
  - Returns hex colors

- `get_circuit_rotation(session)` → float
  - Calculate circuit rotation angle
  - Used for correct track orientation in replay

- `get_race_telemetry(session, session_type)` → Dict
  - Transform session to 25 FPS frames
  - Extract track statuses
  - Compile driver colors
  - Return replay-ready data structure

#### `src/lib/settings.py` - Settings Manager

- Singleton pattern for app-wide settings
- Persistent JSON storage in user home
- Default cache location management
- Configuration accessors

#### `src/lib/tyres.py` - Tyre Utilities

- Tyre compound mapping
- Tyre code translation
- Life tracking

#### `src/lib/season.py` - Season Utilities

- Current season detection
- Season override capability

**Data Output**:
```python
{
    "frames": [
        {
            "lap": int,
            "t": float,
            "drivers": {...},
            "leader": str,
            "safety_car": {...},
            "weather": {...}
        },
        # ... more frames at 25fps
    ],
    "track_statuses": [...],
    "driver_colors": {"VER": "#0082FA", ...},
    "total_laps": int
}
```

---

### 3. Telemetry Processing Layer

**Purpose**: Convert raw lap telemetry into visualization-ready frame data

**Processing Pipeline**:

```
FastF1 Session Data
        │
        ▼
    Per-Driver Lap Processing
        ├─ Extract lap telemetry
        ├─ Resample to 25 FPS
        ├─ Extract coordinates
        ├─ Extract telemetry channels
        └─ Build driver frame objects
        │
        ▼
    Frame Assembly (every 40ms)
        ├─ Compile all drivers
        ├─ Calculate leader
        ├─ Add track status
        ├─ Add weather
        └─ Add safety car position
        │
        ▼
    Replay-Ready Frames
```

**Key Transformations**:

1. **Temporal Resampling**: Raw lap telemetry (variable rate) → 25 FPS frames
2. **Positional Calculation**: (X, Y) coordinates projected to track relative distance
3. **Status Aggregation**: Combine track flags, weather, SC position
4. **Driver Ordering**: Calculate race positions and gaps

---

### 4. Replay Engine Layer

**Purpose**: Render interactive race replay with keyboard controls

**Components**:

#### `src/interfaces/race_replay.py` - Main Replay Window

**Class**: `F1RaceReplayWindow(arcade.Window)`

**Responsibilities**:
- Render track, drivers, overlays at 60 FPS
- Handle keyboard input (play/pause, speed, DRS toggle, etc)
- Update frame index based on playback speed
- Stream telemetry data via WebSocket

**Key Methods**:
```python
on_draw()          # Render current frame
on_key_press()     # Handle keyboard
on_key_release()   # Handle key release
update(delta_time) # Update state, advance frame
```

**Key Properties**:
```python
frame_index      # Current frame (float, 0-n_frames)
paused           # Playback paused?
playback_speed   # Speed multiplier (0.1-256x)
telemetry_stream # TelemetryStreamServer instance
```

#### `src/interfaces/qualifying.py` - Qualifying Replay

- Specialized replay for qualifying sessions
- Lap-by-lap comparison instead of race progress
- Different UI focus (lap times, sectors)

#### `src/ui_components.py` - UI Overlay Components

Modular components for HUD overlays:

- `LeaderboardComponent`: Live race standings
- `WeatherComponent`: Weather conditions
- `LegendComponent`: Track legend
- `DriverInfoComponent`: Selected driver telemetry
- `RaceProgressBarComponent`: Lap progress
- `RaceControlsComponent`: Playback controls
- `SessionInfoComponent`: Event metadata
- `ControlsPopupComponent`: Help overlay

**Design Pattern**: Composite pattern with position/visibility control

---

### 5. Telemetry Streaming Layer

**Purpose**: Broadcast live replay data to external consumers via WebSocket

**Components**:

#### `src/services/stream.py`

**Classes**:

- `TelemetryStreamServer`
  - WebSocket server (localhost:9999)
  - Broadcasts frame data at 25 FPS
  - Integrates with replay window
  - Handles client connections

- `TelemetryStreamClient`
  - Qt-based WebSocket client
  - Connection status signals
  - Data received signals
  - Error handling

**Protocol**:
```
Connection: ws://localhost:9999
Frame Rate: 25 FPS (40ms intervals)
Data Format: JSON (frame structure)
Encoding: UTF-8
```

**Sample Broadcast**:
```json
{
  "frame": {
    "drivers": {
      "VER": {...},
      "LEC": {...}
    },
    "leader": "VER",
    "safety_car": null,
    "weather": {...},
    "lap": 5,
    "t": 234.56
  },
  "frame_index": 5850,
  "total_frames": 148500,
  "playback_speed": 1.0,
  "is_paused": false,
  "session_data": {
    "lap": 5,
    "leader": "VER",
    "time": "00:03:54",
    "total_laps": 57
  },
  "track_status": "1"
}
```

---

### 6. Insights & Analysis Layer

**Purpose**: Extensible system for analysis tools and visualizations

**Components**:

#### `src/gui/insights_menu.py` - Main Insights Window

**Class**: `InsightsMenu(QMainWindow)`

**Features**:
- Categorized tool buttons
- Launch buttons for each insight
- Connection status indicator
- Gesture-based window switching (future)

**Built-in Tools**:
- Driver Telemetry Window
- Pit Wall Example Window
- Tyre Strategy Analyzer
- Hardware Link (Serial Communication)
- Telemetry Stream Viewer

#### `src/gui/pit_wall_window.py` - Extensible Base Class

**Class**: `PitWallWindow(QMainWindow)`

**Purpose**: Base class for custom analysis windows

**Key Features**:
- Integrated telemetry stream client
- Signal/slot architecture for data updates
- Status bar with connection indicator
- Abstract methods for subclasses:
  - `setup_ui()` - Create custom UI
  - `on_telemetry_data(data)` - Process frame data
  - `on_connection_status_changed(status)` - Handle connection
  - `on_stream_error(error)` - Handle errors

**Lifecycle**:
```
__init__
├─ Create telemetry client
├─ Setup status bar
├─ Call setup_ui()  (subclass)
└─ Start client

on_telemetry_data (continuous)
├─ Update message counter
└─ Call on_telemetry_data()  (subclass)

closeEvent
├─ Stop client
└─ Cleanup
```

#### `src/strategy_engine.py` - Strategy Analysis

**Class**: `StrategyEngine`

**Methods**:
- `find_optimum_strategy(curr_lap, current_compound)`
  - Returns recommended stints and score
  - Built-in tyre degradation curves

#### `src/bayesian_tyre_model.py` - Tyre Degradation

**Class**: `BayesianTyreDegradationModel`

**Capabilities**:
- Fit model to historical lap data
- Predict next lap times
- Calculate tyre health metrics
- Account for fuel, weather, track evolution

**Model**:
```
State: α_t (latent pace)
Observation: y_t (lap time)
Inputs: fuel, track_condition, lap_on_tyre, compound
```

---

## Data Flow Pipeline

### Complete User Journey

```
1. User Launch
   ├─ python main.py (or with flags)
   └─ → main()

2. Session Selection
   ├─ GUI Path: show race_selection.py window
   ├─ CLI Path: cli_load() → interactive prompts
   └─ → (year, round, session_type)

3. Data Loading
   ├─ load_session(year, round, session_type)
   ├─ Check cache → use if exists
   ├─ Otherwise download from fastf1
   ├─ Get driver colors → get_driver_colors()
   ├─ Get circuit rotation → get_circuit_rotation()
   └─ → Session object

4. Telemetry Processing
   ├─ get_race_telemetry(session, session_type)
   ├─ Per-driver lap processing (_process_single_driver)
   ├─ Multiprocessing (one worker per core)
   ├─ Frame assembly (25fps resampling)
   ├─ Extract track statuses
   └─ → {frames, driver_colors, track_statuses, total_laps}

5. Analysis System Initialization
   ├─ launch_insights_menu() → subprocess
   ├─ Setup TyreDegradationIntegrator (if session provided)
   ├─ Initialize StrategyEngine
   └─ Parallel to replay

6. Replay Launch
   ├─ run_arcade_replay()
   ├─ Create F1RaceReplayWindow
   ├─ Start TelemetryStreamServer (if enabled)
   ├─ Call arcade.run() → blocking
   └─ → Interactive replay window

7. Replay Interaction
   ├─ User keyboard input → on_key_press()
   ├─ Update frame_index / playback_speed
   ├─ Every 40ms:
   │  ├─ Render current frame → on_draw()
   │  ├─ Broadcast telemetry (if streaming)
   │  └─ Update UI components
   └─ Until window closed

8. Insights Tools
   ├─ Connect to telemetry stream
   ├─ Receive frame data every 40ms
   ├─ Update visualizations
   ├─ Custom analysis per tool
   └─ Until closed
```

---

## Core Subsystems

### Subsystem: Track Geometry & Positioning

**Purpose**: Convert (X, Y) world coordinates to race progress metrics

**Implementation**: `src/f1_data.py`

**Key Functions**:

```python
def _build_track_from_example_lap(example_lap):
    """Extract track geometry from reference lap"""
    # Returns: coordinates list for track outline

def _compute_relative_distance(x, y, track_coords):
    """Project point onto track, return distance 0-1"""
    # Uses cKDTree for fast spatial lookup
    # Returns: normalized distance around circuit

def _compute_circuit_rotation(example_lap):
    """Determine rotation angle of circuit"""
    # Extracts first/last point on track
    # Calculates angle relative to north
    # Returns: degrees for display rotation
```

**Why It Matters**:
- Accurate driver positioning on track
- Correct visual rendering of race
- Relative distance for overtaking metrics

---

### Subsystem: Safety Car Management

**Purpose**: Simulate realistic safety car behavior

**Implementation**: `src/f1_data.py` → `_compute_safety_car_positions()`

**Logic**:

1. Detect safety car deployment from track status
2. Position SC ~500m ahead of race leader
3. Manage field bunching (all drivers slow down)
4. Track phases: deploying → on_track → returning
5. Provide position data to replay for rendering

**Data Structure**:
```python
{
    "x": float,           # World X
    "y": float,           # World Y
    "phase": "on_track",  # deploying/on_track/returning
    "alpha": 1.0          # 0-1 opacity for fade
}
```

---

### Subsystem: DRS Detection

**Purpose**: Identify DRS zones and detect activation

**Implementation**: 
- Raw data from fastf1 telemetry
- DRS field in frame["drivers"][driver]["drs"]
- Blue zone overlays on track in replay

**Data**:
```python
frame["drivers"]["VER"]["drs"] = 1  # 0=off, 1=on
```

---

### Subsystem: Weather Integration

**Purpose**: Display and track weather conditions

**Data From**: fastf1 API (usually from first-lap telemetry)

**Stored In**: frame["weather"]
```python
{
    "air_temp": 18.5,        # Celsius
    "track_temp": 25.0,      # Celsius
    "humidity": 72.0,        # 0-100%
    "wind_speed": 1.5,       # m/s
    "wind_direction": 120,   # degrees
    "rain_state": "DRY"      # DRY/DAMP/WET
}
```

**Display**: WeatherComponent in replay HUD

---

## Extension Guide

### Adding a Custom Insight Window

**Step 1**: Create window class

```python
# src/insights/my_custom_analysis.py
from src.gui.pit_wall_window import PitWallWindow
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget
from PySide6.QtCore import Qt

class MyCustomAnalysis(PitWallWindow):
    def setup_ui(self):
        """Create custom UI"""
        layout = QVBoxLayout()
        
        # Your widgets here
        title = QLabel("Custom Analysis")
        layout.addWidget(title)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        layout.addWidget(self.table)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def on_telemetry_data(self, data):
        """Handle incoming frame data"""
        frame = data["frame"]
        
        # Clear old data
        self.table.setRowCount(0)
        
        # Populate with current driver positions
        row = 0
        for driver_code, driver_data in frame["drivers"].items():
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(driver_code))
            self.table.setItem(row, 1, QTableWidgetItem(f"{driver_data['position']}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{driver_data['speed']}"))
            row += 1
```

**Step 2**: Add launcher method to InsightsMenu

```python
# src/gui/insights_menu.py
def launch_my_custom_analysis(self):
    try:
        from src.insights.my_custom_analysis import MyCustomAnalysis
        window = MyCustomAnalysis()
        window.show()
    except Exception as e:
        self.show_placeholder_message(f"Error: {e}")
```

**Step 3**: Add button to insights menu

```python
# In create_category_section()
insights_dict = {
    "Analysis": [
        ("My Analysis", "Custom data analysis", 
         self.launch_my_custom_analysis),
    ]
}
```

### Modifying Replay Visualization

**Option 1**: Subclass F1RaceReplayWindow

```python
from src.interfaces.race_replay import F1RaceReplayWindow
import arcade

class CustomReplayWindow(F1RaceReplayWindow):
    def on_draw(self):
        """Add custom overlays"""
        super().on_draw()
        
        # Draw after main replay
        arcade.draw_rectangle_outline(
            100, 100, 200, 100,
            arcade.color.RED, 2
        )
```

**Option 2**: Add custom UI component

```python
from src.ui_components import UIComponent

class MyCustomComponent(UIComponent):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.data = None
    
    def draw(self):
        # Your drawing code
        pass
    
    def update(self, frame):
        self.data = frame
```

### Adding Telemetry Stream Consumers

**Example**: Log telemetry to file

```python
from src.services.stream import TelemetryStreamClient
import json

class TelemetryLogger:
    def __init__(self, log_file):
        self.log_file = open(log_file, 'w')
        self.client = TelemetryStreamClient()
        self.client.data_received.connect(self.on_data)
        self.client.start()
    
    def on_data(self, data):
        json.dump(data, self.log_file)
        self.log_file.write('\n')
        self.log_file.flush()
    
    def close(self):
        self.client.stop()
        self.log_file.close()

# Usage
logger = TelemetryLogger("replay.jsonl")
# ... run replay ...
logger.close()
```

---

## Design Patterns

### 1. Composite Pattern (UI Components)

Multiple small components combine to form complex HUD:

```
F1RaceReplayWindow
├─ LeaderboardComponent
├─ WeatherComponent
├─ DriverInfoComponent
├─ RaceProgressBarComponent
└─ RaceControlsComponent

Each component:
├─ Knows its position/size
├─ Draws itself
├─ Updates from frame data
└─ Can toggle visibility
```

### 2. Observer Pattern (Telemetry Stream)

```
TelemetryStreamServer (Observable)
    │
    ├─ Frame generated
    ├─ Broadcast to all connected clients
    │
    └─ TelemetryStreamClient (Observer)
        ├─ Receive frame
        ├─ Emit signal
        └─ Notify listeners (Qt slots)
```

### 3. Strategy Pattern (Session Types)

Different handling for Race vs Qualifying vs Sprint:

```
run_session(session_type)
    ├─ if session_type == 'R': run_race()
    ├─ if session_type == 'Q': run_qualifying_replay()
    └─ if session_type == 'S': run_sprint()

Each uses appropriate:
    ├─ Telemetry function
    ├─ UI layout
    └─ Analysis tools
```

### 4. Singleton Pattern (Settings Manager)

```python
class SettingsManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Usage: Always same instance
settings = SettingsManager()
cache_location = settings.get("cache_location")
```

### 5. Factory Pattern (Window Creation)

```python
class InsightsMenu:
    def launch_driver_telemetry(self):
        window = DriverTelemetryWindow()  # Factory
        window.show()
    
    def launch_tyre_strategy(self):
        window = TyreStrategyWindow()     # Factory
        window.show()
```

---

## Performance Considerations

### Frame Rendering (25 FPS)

- **Target**: 40ms per frame
- **Arcade Performance**: GPU-accelerated rendering
- **Optimization**: Only redraw changed elements

### Telemetry Processing

- **Multiprocessing**: Per-driver processing uses CPU cores
- **Temporal Resampling**: Vectorized numpy operations
- **Memory**: Frames stored in memory (typically 100-200MB for full race)

### WebSocket Streaming

- **Bandwidth**: ~500KB/s at 25 FPS + metadata
- **Latency**: <50ms typical
- **Connections**: Supports multiple simultaneous clients

---

**Last Updated**: April 2026
