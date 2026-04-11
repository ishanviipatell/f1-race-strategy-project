import serial
from PySide6.QtCore import QThread, Signal
from src.gui.pit_wall_window import PitWallWindow

class SerialManager(QThread):
    sensor_data = Signal(list)

    def __init__(self, port="COM3"): # UPDATE THIS TO YOUR PORT
        super().__init__()
        try:
            self.ser = serial.Serial(port, 115200, timeout=0.1)
        except:
            self.ser = None
        self.running = True

    def run(self):
        while self.running and self.ser:
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode('utf-8').strip()
                if line.startswith("SENSORS:"):
                    data = line.replace("SENSORS:", "").split(",")
                    self.sensor_data.emit(data)

    def send_to_hardware(self, msg):
        if self.ser:
            self.ser.write(f"{msg}\n".encode())

class HardwareConsoleWindow(PitWallWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hardware Integration Active")
        self.resize(300, 150)
        
        # Start Serial
        self.manager = SerialManager(port="COM3") # Change COM3 to your ESP32 port
        self.manager.sensor_data.connect(self.process_hardware_inputs)
        self.manager.start()

    def process_hardware_inputs(self, data):
        # data = [pot, distance, temp]
        pot, dist, temp = data
        
        # Example: If distance < 10cm, send a 'Pause' command to your replay
        if int(dist) < 10:
            print("🖐️ Hand detected! Pause/Play Replay triggered.")
            # Trigger your stream toggle here

    def on_telemetry_data(self, data):
        frame = data.get("frame", {})
        drivers = frame.get("drivers", {})
        
        # Assuming you want to track Lando Norris (NOR)
        if "NOR" in drivers:
            brake = drivers["NOR"].get("brake", 0)
            # Send brake pressure to ESP32 to move the physical servo needle
            self.manager.send_to_hardware(f"SERVO:{brake}")