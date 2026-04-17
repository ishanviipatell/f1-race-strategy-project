# F1 Race Strategy Replay - Troubleshooting Guide

Comprehensive guide to diagnosing and resolving common issues.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Replay & Visualization Issues](#replay--visualization-issues)
- [Data Loading Issues](#data-loading-issues)
- [Telemetry & Streaming Issues](#telemetry--streaming-issues)
- [Performance Issues](#performance-issues)
- [Multi-Window Issues](#multi-window-issues)
- [Debug Mode & Logging](#debug-mode--logging)
- [Getting Help](#getting-help)

---

## Installation Issues

### "Module not found" Errors

**Error Message**:
```
ModuleNotFoundError: No module named 'fastf1'
ModuleNotFoundError: No module named 'arcade'
ModuleNotFoundError: No module named 'PySide6'
```

**Cause**: Required packages not installed

**Solution**:

1. Verify Python version (3.10+):
```bash
python --version
```

2. Install from requirements.txt:
```bash
pip install -r requirements.txt
```

3. Install additional packages:
```bash
pip install fastf1 scipy
```

4. Verify installation:
```bash
python -c "import fastf1; import arcade; import PySide6; print('✓ All OK')"
```

**If still failing**:
```bash
# Try upgrading pip
python -m pip install --upgrade pip

# Reinstall with verbose output
pip install -r requirements.txt -v

# Check for conflicting packages
pip list | grep -E "arcade|fastf1|pyside"
```

---

### "No such file or directory" - requirements.txt

**Error**:
```
[Errno 2] No such file or directory: 'requirements.txt'
```

**Cause**: Not in project directory

**Solution**:
```bash
# Navigate to project root
cd /path/to/f1-race-strategy-project

# Verify structure
ls -la | grep requirements.txt

# Then install
pip install -r requirements.txt
```

---

### Python Version Mismatch

**Error**:
```
Python 3.9 is not supported. Requires Python 3.10+
```

**Solution**:

1. Check current version:
```bash
python --version
```

2. Install Python 3.10+ from:
   - Windows: python.org or Microsoft Store
   - macOS: brew install python@3.11
   - Linux: apt-get install python3.11

3. Create virtual environment with specific version:
```bash
python3.11 -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

---

### Virtual Environment Not Activating

**Windows**:
```powershell
# If you get ExecutionPolicy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate:
.venv\Scripts\Activate.ps1
```

**macOS/Linux**:
```bash
# Make sure you're using bash/zsh
source .venv/bin/activate

# Verify activation (should show .venv prefix)
echo $VIRTUAL_ENV
```

---

## Replay & Visualization Issues

### Replay Window Doesn't Open

**Symptoms**:
- `python main.py` runs but no window appears
- No error message in console
- Process seems to hang

**Diagnosis**:

1. Enable verbose logging:
```bash
python main.py --verbose
```

2. Check console output for errors
3. Try a specific session:
```bash
python main.py --viewer --year 2024 --round 1
```

**Solutions**:

**Graphics Driver Issue**:
- Update GPU drivers (NVIDIA, AMD, Intel)
- Try with `--no-hud` flag to minimize graphics load
- Run in windowed mode (default)

**Display Server Issue** (Linux):
```bash
# Check if display server is available
echo $DISPLAY   # Should show something like :0

# If empty, you may need Xvfb
sudo apt-get install xvfb
```

**Pygame/Arcade Initialization**:
```python
# Test arcade directly
python -c "import arcade; print(arcade.__version__)"

# Test with simple window
python -c "
import arcade
window = arcade.Window(800, 600, 'Test')
print('✓ Arcade window created successfully')
"
```

---

### Replay Crashes Immediately

**Error Message**:
```
pygame.error: No available video device
AttributeError: 'NoneType' object has no attribute ...
```

**Cause**: Graphics initialization failure or missing data

**Solutions**:

1. **Check data loading**:
```bash
python -c "
from src.f1_data import enable_cache, load_session
enable_cache()
session = load_session(2024, 12, 'R')
print(f'✓ Session loaded: {session.event[\"EventName\"]}')
"
```

2. **Check frame generation**:
```bash
python -c "
from src.f1_data import enable_cache, load_session, get_race_telemetry
enable_cache()
session = load_session(2024, 12, 'R')
telemetry = get_race_telemetry(session)
print(f'✓ Generated {len(telemetry[\"frames\"])} frames')
"
```

3. **Reduce memory usage**:
   - Close other applications
   - Increase virtual memory/swap
   - Try smaller session (Sprint race instead of GP)

---

### Window is Frozen / Not Responding

**Symptoms**:
- Window appears but doesn't respond to input
- Doesn't render animation

**Cause**: Usually threading or event loop issue

**Solutions**:

1. Check if running on secondary GPU:
```bash
# Windows: Open Device Manager → Display adapters
# macOS: System Preferences → Graphics
# Linux: glxinfo | grep "Device:"
```

2. Force single-GPU mode:
```bash
# NVIDIA (Windows)
set CUDA_VISIBLE_DEVICES=0

# AMD
set GPU_DEVICE_ORDINAL=0
```

3. Disable telemetry (reduces overhead):
```bash
# Modify main.py or use direct call
run_arcade_replay(..., enable_telemetry=False)
```

---

### Rendering Glitches / Visual Artifacts

**Symptoms**:
- Flickering, tearing, missing elements
- Track not rendering correctly
- Driver positions jump around

**Solutions**:

1. **Update GPU drivers**:
   - NVIDIA: Driver > 500 recommended
   - AMD: Driver > 21.0 recommended

2. **Check hardware acceleration**:
```bash
# Disable if causing issues
export PYGAME_FORCE_SCALE=1
export SDL_VIDEODRIVER=windowed
```

3. **Lower performance settings**:
```python
# In F1RaceReplayWindow constructor
# Reduce from 1280x720 to lower resolution
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 576
```

---

## Data Loading Issues

### "Session not found" / API Connection Failed

**Error Message**:
```
fastf1.DataNotAvailableError: Failed to load session
requests.exceptions.ConnectionError: Unable to connect to API
```

**Cause**: Invalid year/round or network connectivity issue

**Solutions**:

1. **Verify year/round combination**:
```bash
# List available rounds
python main.py --list-rounds 2024

# Check if sprint exists
python main.py --list-sprints 2024
```

2. **Check internet connection**:
```bash
python -c "import requests; r = requests.get('https://www.formula1.com'); print('✓ Connected')"
```

3. **Check fastf1 API availability**:
```bash
python -c "
import fastf1
fastf1.Cache.enable_cache('.cache')
session = fastf1.get_session(2024, 'Silverstone', 'R')
print('✓ API working')
"
```

4. **Try older sessions** (API sometimes loses historical data):
```bash
# Try 2023 or 2022 instead of 2024
python main.py --viewer --year 2023 --round 1
```

---

### Cache Corrupted

**Error Message**:
```
sqlite3.DatabaseError: database disk image is malformed
pickle.UnpicklingError: invalid load key
```

**Cause**: Cache directory corrupted

**Solution**:

1. **Clear cache completely**:
```bash
# Windows
rmdir /s /q .fastf1-cache

# macOS/Linux
rm -rf .fastf1-cache
```

2. **Clear fastf1 system cache**:
```python
# Windows
import shutil
shutil.rmtree(r'%APPDATA%\.fastf1\fastf1_cache')

# macOS/Linux
import shutil
import pathlib
shutil.rmtree(pathlib.Path.home() / '.fastf1' / 'fastf1_cache')
```

3. **Reload session** (will re-download):
```bash
python main.py --viewer --year 2024 --round 12
```

---

### "No laps available" / Empty Session

**Cause**: Session may be:
- Future session (not yet completed)
- Cancelled/red-flagged with no valid laps
- Qualifiying rain-out with no lap times

**Solution**:

1. Try different session type:
```bash
# If race failed, try qualifying
python main.py --viewer --year 2024 --round 12 --qualifying

# If qualifying failed, try sprint
python main.py --viewer --year 2024 --round 12 --sprint
```

2. Try different round:
```bash
python main.py --list-rounds 2024  # Find valid rounds
```

---

## Telemetry & Streaming Issues

### Telemetry Stream Fails to Start

**Error Message**:
```
OSError: [Errno 98] Address already in use
Failed to start telemetry server
```

**Cause**: Port 9999 already in use

**Solution**:

1. **Check what's using port 9999**:
```bash
# Windows
netstat -ano | findstr :9999

# macOS/Linux
lsof -i :9999
```

2. **Kill process using port**:
```bash
# Windows
taskkill /PID <PID> /F

# macOS/Linux
kill -9 <PID>
```

3. **Use different port** (if needed):
```python
# Modify in src/interfaces/race_replay.py
self.telemetry_stream = TelemetryStreamServer(port=8888)
```

4. **Disable telemetry if not needed**:
```bash
# Modify main.py
run_arcade_replay(..., enable_telemetry=False)
```

---

### External Tool Can't Connect to Telemetry Stream

**Error Message**:
```
WebSocket connection failed: Connection refused
localhost:9999 connection timeout
```

**Diagnosis**:

1. **Verify server is running**:
```bash
# In another terminal
python -c "
from src.services.stream import TelemetryStreamClient
client = TelemetryStreamClient()
client.start()
"
```

2. **Check if port is accessible**:
```bash
# Windows
nc -zv localhost 9999

# macOS/Linux
telnet localhost 9999
```

**Solutions**:

1. **Ensure telemetry is enabled**:
```python
# In main() function
run_arcade_replay(..., enable_telemetry=True)
```

2. **Check firewall**:
   - Windows: Allow Python through Windows Defender Firewall
   - macOS: System Preferences → Security → Firewall
   - Linux: `sudo ufw allow 9999`

3. **Use correct URL**:
   - Local: `ws://localhost:9999`
   - Remote: `ws://<machine-ip>:9999`

4. **Client connection debugging**:
```python
import websocket
try:
    ws = websocket.create_connection("ws://localhost:9999", timeout=5)
    print("✓ Connected")
except Exception as e:
    print(f"✗ Failed: {e}")
```

---

## Performance Issues

### Slow Playback / Frame Rate Drops

**Symptoms**:
- Stuttering during replay
- FPS drops below 30
- Lag when panning/zooming

**Diagnosis**:

1. **Monitor frame rate**:
```python
# Add to F1RaceReplayWindow
def on_draw(self):
    super().on_draw()
    import time
    fps = 1.0 / (time.time() - self.last_frame_time) if hasattr(self, 'last_frame_time') else 0
    print(f"FPS: {fps:.1f}")
    self.last_frame_time = time.time()
```

2. **Check resource usage**:
   - Windows: Task Manager → Performance
   - macOS: Activity Monitor
   - Linux: `top` or `htop`

**Solutions**:

1. **Reduce visual complexity**:
```bash
python main.py --viewer --year 2024 --round 12 --no-hud
```

2. **Lower resolution**:
```python
# In src/interfaces/race_replay.py
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 576
```

3. **Reduce frame rate** (modify arcade):
```python
# In __init__
self.set_update_rate(1/30)  # 30 FPS instead of 60
```

4. **Disable unnecessary features**:
```python
# Telemetry streaming uses CPU
enable_telemetry=False

# Analysis tools in background
kill insights menu
```

5. **Close other applications**:
   - Browsers
   - Video calls
   - Resource-heavy apps

---

### Memory Usage Too High

**Symptoms**:
- Replay uses >2GB RAM
- System becomes slow/unresponsive
- "Out of memory" errors

**Cause**: Large sessions store all frames in memory

**Solution**:

1. **Use smaller sessions**:
```bash
# Sprint race uses less memory
python main.py --viewer --year 2024 --round 12 --sprint

# Rather than 2-hour GP race
```

2. **Increase virtual memory** (if RAM-constrained):
   - Windows: Settings → System → Storage → Virtual memory
   - macOS: Not recommended (SSD thrashing)
   - Linux: Create swap: `fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile`

3. **Upgrade RAM** (if persistent issue)

---

## Multi-Window Issues

### Insights Menu Doesn't Open

**Symptoms**:
- Replay opens but insights menu doesn't appear
- No error message

**Cause**: Menu subprocess failed to start

**Solutions**:

1. **Check console output**:
```bash
python main.py 2>&1 | grep -i "insights\|error\|failed"
```

2. **Start insights manually**:
```bash
python -m src.gui.insights_menu
```

3. **Verify PySide6 installation**:
```bash
python -c "
from PySide6.QtWidgets import QApplication
app = QApplication([])
print('✓ PySide6 working')
"
```

---

### Multiple Windows Interfere / Cross-Talk

**Symptoms**:
- Input in one window affects another
- Windows crash when closed in wrong order
- Signal/slot errors in console

**Cause**: Thread safety or event loop issues

**Solutions**:

1. **Close windows in order**:
   - First: Close analysis windows
   - Last: Close main replay

2. **Check for blocking operations**:
   - Don't call blocking functions in Qt slots
   - Use threading for long operations

---

## Debug Mode & Logging

### Enable Verbose Logging

```bash
# FastF1 logging
python main.py --verbose

# All logging output preserved in console
# Shows API calls, cache hits/misses, data processing
```

**Output Example**:
```
2024-04-17 10:45:23 - fastf1 - INFO - Loading session...
2024-04-17 10:45:24 - fastf1 - DEBUG - Cache hit: 2024_12_R
2024-04-17 10:45:25 - INFO - Processing telemetry for 20 drivers...
```

---

### Add Debug Logging to Your Code

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in code
logger.debug(f"Frame {frame_index}: {frame['leader']}")
logger.info("Lap completed")
logger.warning("Telemetry gap detected")
logger.error("Failed to load session", exc_info=True)
```

---

### Inspect Data at Runtime

```python
# In Python REPL or debugging script
from src.f1_data import enable_cache, load_session, get_race_telemetry

enable_cache()
session = load_session(2024, 12, 'R')

# Inspect session
print(session.event)
print(session.drivers)
print(session.laps[['Driver', 'LapTime', 'Compound']])

# Inspect telemetry
telemetry = get_race_telemetry(session)
frame = telemetry['frames'][0]
print(frame)
print(frame['drivers']['VER'])
```

---

### Check System Information

```python
import sys
import platform
import pygame
import arcade

print(f"Python: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Pygame: {pygame.__version__}")
print(f"Arcade: {arcade.__version__}")

# GPU info (varies by OS)
# Windows: Direct import
# macOS: system_profiler SPDisplaysDataType
# Linux: glxinfo, nvidia-smi, lspci
```

---

## Getting Help

### Debugging Checklist

Before asking for help, verify:

- [ ] Python 3.10+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Virtual environment activated
- [ ] Running with `--verbose` flag
- [ ] Tried --list-rounds to verify API access
- [ ] Tested with 2024 Silverstone GP (round 12)
- [ ] Checked cache directory is writable
- [ ] Tried clearing cache (`.fastf1-cache`)

### Collect Debug Information

```bash
# Save system info
python -c "
import sys, platform, fastf1, arcade, PySide6
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'FastF1: {fastf1.__version__}')
print(f'Arcade: {arcade.__version__}')
" > debug_info.txt

# Save verbose output
python main.py --verbose > replay.log 2>&1

# Check error in replay
cat replay.log | grep -i error
```

### References

1. **FastF1 Documentation**: https://docs.fastf1.dev
2. **Arcade Documentation**: https://arcade.academy
3. **PySide6 Documentation**: https://doc.qt.io/qtforpython-6/
4. **Project Issues**: Check repository for similar issues
5. **Stack Overflow**: Tag with `fastf1` or `arcade-game-library`

---

**Last Updated**: April 2026
