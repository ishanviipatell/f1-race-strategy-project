import serial
import serial.tools.list_ports
import time
import json
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QComboBox, QPushButton
from PySide6.QtGui import QFont

try:
    from src.gui.pit_wall_window import PitWallWindow
except ImportError:
    from PySide6.QtWidgets import QMainWindow as PitWallWindow

class SerialWorker(QThread):
    data_received = Signal(dict)
    def __init__(self, port, baud=115200):
        super().__init__()
        self.port, self.baud, self.ser, self.running = port, baud, None, True
    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
            while self.running and self.ser.is_open:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("{") and line.endswith("}"):
                        try: self.data_received.emit(json.loads(line))
                        except: pass
                time.sleep(0.01)
        except Exception: pass
    def send_data(self, data):
        if self.ser and self.ser.is_open:
            msg = json.dumps(data) + "\n"
            try: self.ser.write(msg.encode())
            except: pass
    def stop(self):
        self.running = False
        if self.ser: self.ser.close()

class HardwareLinkWindow(PitWallWindow):
    request_tab_change = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1 Pro Hardware Link")
        self.resize(500, 700)
        self.worker, self.target_driver = None, None
        self.setup_ui()
        self.refresh_ports()

    def setup_ui(self):
        central = QWidget()
        # MATCHING YOUR PROJECT COLORS (Deep Black)
        central.setStyleSheet("background-color: #000000; color: #ffffff; font-family: 'Segoe UI', Arial;")
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # 1. TOP CONTROL BAR (Port & Driver)
        ctrl_frame = QFrame()
        ctrl_frame.setStyleSheet("border: 1px solid #333333; background: #0a0a0a; border-radius: 5px;")
        ctrl_layout = QHBoxLayout(ctrl_frame)
        
        self.port_combo = QComboBox()
        self.port_combo.setStyleSheet("background: #111; border: 1px solid #444; color: white; padding: 3px;")
        
        self.connect_btn = QPushButton("CONNECT")
        self.connect_btn.setStyleSheet("background: #333; font-weight: bold; border: 1px solid #555;")
        self.connect_btn.clicked.connect(self.toggle_serial)

        self.driver_combo = QComboBox()
        self.driver_combo.setStyleSheet("background: #111; border: 1px solid #444; color: #00ff00;")
        self.driver_combo.currentTextChanged.connect(self.on_driver_changed)

        ctrl_layout.addWidget(QLabel("PORT:"))
        ctrl_layout.addWidget(self.port_combo)
        ctrl_layout.addWidget(self.connect_btn)
        ctrl_layout.addWidget(QLabel("DRIVER:"))
        ctrl_layout.addWidget(self.driver_combo)
        layout.addWidget(ctrl_frame)

        # 2. STATUS BANNER
        self.status_banner = QLabel("SYSTEM NOMINAL")
        self.status_banner.setAlignment(Qt.AlignCenter)
        self.status_banner.setStyleSheet("font-size: 22px; font-weight: bold; background: #28a745; color: white; border-radius: 5px; padding: 10px;")
        layout.addWidget(self.status_banner)

        # 3. BRAKE TELEMETRY (F1 Red)
        self.brake_label = QLabel("SIM BRAKE: 0%")
        self.brake_label.setAlignment(Qt.AlignCenter)
        self.brake_label.setStyleSheet("font-size: 34px; font-weight: bold; background: #000; border: 2px solid #e10600; color: #e10600; padding: 20px; border-radius: 10px;")
        layout.addWidget(self.brake_label)

        # 4. CHASSIS DYNAMICS (MPU Text Display)
        dyn_frame = QFrame()
        dyn_frame.setStyleSheet("border: 1px solid #333; background: #050505; border-radius: 5px;")
        dyn_layout = QVBoxLayout(dyn_frame)
        self.tilt_x = QLabel("LATERAL TILT (X): 0.00 G")
        self.tilt_y = QLabel("CHASSIS PITCH (Y): 0.00 G")
        self.tilt_x.setStyleSheet("font-size: 18px; color: #00d2ff; font-weight: bold;")
        self.tilt_y.setStyleSheet("font-size: 18px; color: #00d2ff; font-weight: bold;")
        dyn_layout.addWidget(self.tilt_x)
        dyn_layout.addWidget(self.tilt_y)
        layout.addWidget(dyn_frame)

        # 5. ENVIRONMENT & RIDE (Modular Row)
        env_frame = QFrame()
        env_layout = QHBoxLayout(env_frame)
        self.ride_label = QLabel("RIDE: -- cm")
        self.temp_label = QLabel("TEMP: -- °C")
        self.hum_label = QLabel("HUMID: -- %")
        self.ride_label.setStyleSheet("font-size: 18px; color: #fff200;") # Yellow
        self.temp_label.setStyleSheet("font-size: 18px; color: #00ff00;") # Green
        self.hum_label.setStyleSheet("font-size: 18px; color: #00d2ff;") # Cyan
        env_layout.addWidget(self.ride_label)
        env_layout.addWidget(self.temp_label)
        env_layout.addWidget(self.hum_label)
        layout.addWidget(env_frame)

        # 6. ENGINE STRAT (Potentiometer)
        self.strat_label = QLabel("STRAT MODE: ---")
        self.strat_label.setAlignment(Qt.AlignCenter)
        self.strat_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff9800; border-top: 1px solid #333; padding-top: 10px;")
        layout.addWidget(self.strat_label)

    def refresh_ports(self):
        self.port_combo.clear()
        self.port_combo.addItems([p.device for p in serial.tools.list_ports.comports()])

    def toggle_serial(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop(); self.connect_btn.setText("CONNECT")
        else:
            self.worker = SerialWorker(self.port_combo.currentText())
            self.worker.data_received.connect(self.process_hardware_data)
            self.worker.start(); self.connect_btn.setText("DISCONNECT")

    def on_driver_changed(self, driver): self.target_driver = driver

    def process_hardware_data(self, data):
        # MPU Text Output
        if "tiltX" in data: self.tilt_x.setText(f"LATERAL TILT (X): {data['tiltX']/9.8:.2f} G")
        if "tiltY" in data: self.tilt_y.setText(f"CHASSIS PITCH (Y): {data['tiltY']/9.8:.2f} G")
        
        # Ride Height Alert Logic
        if "ride" in data:
            rh = data["ride"]
            self.ride_label.setText(f"RIDE: {rh:.1f} cm")
            if rh < 3.0:
                self.status_banner.setText("⚠️ WARNING: FLOOR SCRAPING!")
                self.status_banner.setStyleSheet("font-size: 22px; font-weight: bold; background: #e10600; color: white; border-radius: 5px; padding: 10px;")
            else:
                self.status_banner.setText("SYSTEM NOMINAL")
                self.status_banner.setStyleSheet("font-size: 22px; font-weight: bold; background: #28a745; color: white; border-radius: 5px; padding: 10px;")

        # Environment & Strat Restored
        if "temp" in data: self.temp_label.setText(f"TEMP: {data['temp']:.1f} °C")
        if "hum" in data: self.hum_label.setText(f"HUMID: {data['hum']:.0f}%")
        if "strat" in data: self.strat_label.setText(f"CURRENT {data['strat']}")
        
        # Gesture
        if data.get("action") == "prev_tab": self.request_tab_change.emit("prev")

    def on_telemetry_data(self, data):
        """Sim Stream Integration"""
        drivers = data.get("frame", {}).get("drivers", {})
        if not drivers: return
        if self.driver_combo.count() == 0:
            self.driver_combo.addItems(sorted(drivers.keys()))
            self.target_driver = self.driver_combo.currentText()
        if self.target_driver in drivers:
            brake = int(drivers[self.target_driver].get("brake", 0) * 100)
            if self.worker: self.worker.send_data({"brake": brake})
            self.brake_label.setText(f"SIM BRAKE: {brake}%")
            # Dynamic glow intensity
            alpha = min(255, int(brake * 2.5))
            self.brake_label.setStyleSheet(f"font-size: 34px; font-weight: bold; background: #000; border: 2px solid rgb({alpha},0,0); color: rgb({alpha},0,0); padding: 20px; border-radius: 10px;")

    def closeEvent(self, event):
        if self.worker: self.worker.stop()
        super().closeEvent(event)