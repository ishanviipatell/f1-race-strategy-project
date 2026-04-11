import serial
import serial.tools.list_ports
import time
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QHBoxLayout, QComboBox
from src.gui.pit_wall_window import PitWallWindow

class SerialWorker(QThread):
    """Background thread to handle USB Serial communication at 115200 bps."""
    data_received = Signal(list)

    def __init__(self, port, baud=115200): 
        super().__init__()
        self.port = port
        self.baud = baud
        self.ser = None
        self.running = True

    def run(self):
        try:
            # Initialize connection to match your Arduino Serial.begin(115200)
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
            self.ser.reset_input_buffer()
            print(f"✅ USB Link Active: {self.port} at {self.baud} bps")
        except Exception as e:
            print(f"❌ USB Error: {e}")
            return

        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    # Matches your Arduino code: Serial.print("SENSORS:");
                    if line.startswith("SENSORS:"):
                        parts = line.replace("SENSORS:", "").split(",")
                        if len(parts) == 3:
                            self.data_received.emit(parts)
            except Exception:
                pass
            time.sleep(0.01)

    def send(self, msg):
        """Sends 'SERVO:val' to your board."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(f"{msg}\n".encode('utf-8'))
            except:
                pass

    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()

class HardwareLinkWindow(PitWallWindow):
    def __init__(self):
        self.target_driver = None
        self.worker = None
        super().__init__()
        self.setWindowTitle("F1 Physical Hardware Link")
        self.resize(400, 350)
        
        # Auto-detect your Arduino/ESP8266 COM Port
        ports = list(serial.tools.list_ports.comports())
        target_port = ports[0].device if ports else "COM3"
        
        self.worker = SerialWorker(target_port, baud=115200)
        self.worker.data_received.connect(self.handle_hardware_input)
        self.worker.start()
        
        self.status_label.setText(f"✅ Hardware Link: {target_port} (115200 bps)")

    def setup_ui(self):
        """Builds the UI with a dynamic Driver Selector."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Searching for Hardware...")
        self.status_label.setStyleSheet("font-weight: bold; color: #2196F3; font-size: 14px;")
        layout.addWidget(self.status_label)

        # Dynamic Driver Selector
        sel_layout = QHBoxLayout()
        sel_layout.addWidget(QLabel("Track Driver:"))
        self.driver_combo = QComboBox()
        self.driver_combo.currentTextChanged.connect(self.on_driver_changed)
        sel_layout.addWidget(self.driver_combo)
        layout.addLayout(sel_layout)

        # Potentiometer Visualizer
        layout.addWidget(QLabel("Physical Potentiometer:"))
        self.pot_bar = QProgressBar()
        self.pot_bar.setRange(0, 1024)
        layout.addWidget(self.pot_bar)

        # Sensor Labels
        self.dist_label = QLabel("Hand Distance: -- cm")
        layout.addWidget(self.dist_label)
        
        self.temp_label = QLabel("Room Temp: -- °C")
        layout.addWidget(self.temp_label)

        layout.addSpacing(15)
        
        # Diagnostic Heartbeat
        self.telemetry_debug = QLabel("⚠️ Waiting for F1 Stream (Hit Play in Replay!)")
        self.telemetry_debug.setStyleSheet("color: orange; font-weight: bold;")
        layout.addWidget(self.telemetry_debug)

    def on_driver_changed(self, driver):
        self.target_driver = driver

    def handle_hardware_input(self, data):
        """Processes 'SENSORS:pot,dist,temp' from your Arduino."""
        try:
            pot, dist, temp = data
            self.pot_bar.setValue(int(pot))
            self.dist_label.setText(f"Hand Distance: {dist} cm")
            self.temp_label.setText(f"Room Temp: {temp} °C")
        except:
            pass

    def on_telemetry_data(self, data):
        """Sends data TO your Arduino's 'SERVO:' listener."""
        frame = data.get("frame", {})
        drivers = frame.get("drivers", {})
        if not drivers:
            return

        # Populates the dropdown automatically when data arrives
        if self.driver_combo.count() == 0:
            self.driver_combo.addItems(sorted(drivers.keys()))
            self.target_driver = self.driver_combo.currentText()

        self.telemetry_debug.setText("✅ Receiving Live F1 Telemetry")
        self.telemetry_debug.setStyleSheet("color: #4CAF50; font-weight: bold;")

        if self.target_driver in drivers:
            # Get Brake Pressure (0-100)
            brake = drivers[self.target_driver].get("brake", 0)
            # Sends exactly what your Arduino expects: if (input.startsWith("SERVO:"))
            if self.worker:
                self.worker.send(f"SERVO:{int(brake)}")

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
        super().closeEvent(event)