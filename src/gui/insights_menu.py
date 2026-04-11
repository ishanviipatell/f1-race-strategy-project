import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class InsightsMenu(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("F1 Insights")
        self.setGeometry(50, 50, 350, 650)
        
        # Keep references to opened windows
        self.opened_windows = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(2)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add insight categories

        content_layout.addWidget(self.create_category_section(
            "Example Insights",
            [
                ("Example Insight Window", "Launch an example insight window", self.launch_example_window),
            ]
        ))

        content_layout.addWidget(self.create_category_section(
            "Live Telemetry",
            [
                ("Telemetry Stream Viewer", "View raw telemetry data", self.launch_telemetry_viewer),
                ("Driver Live Telemetry", "Speed, gear, throttle & braking for a selected driver", self.launch_driver_telemetry),
            ]
        ))

        content_layout.addWidget(self.create_category_section(
            "Track",
            [
                ("Track Position Map", "Live driver positions plotted on a circular track map", self.launch_track_position),
            ]
        ))

        content_layout.addWidget(self.create_category_section(
         "Hardware",
         [("Physical Pit Wall", "Link ESP32, Servo & Sensors", self.launch_hardware_console)]
        ))

        # --- DYNAMIC STRATEGY SECTION ---
        content_layout.addWidget(self.create_category_section(
            "Strategy",
            [
                ("Tyre Strategy Dashboard", "Dynamic pit windows & tyre predictions", self.launch_tyre_strategy),
            ]
        ))
        
        content_layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)
    
    def create_header(self):
        header = QFrame()
        header.setFrameShape(QFrame.NoFrame)
        layout = QVBoxLayout(header)
        title = QLabel("🏎️ F1 Insights")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        layout.addWidget(title)
        subtitle = QLabel("Launch telemetry insights and analysis tools")
        subtitle.setFont(QFont("Arial", 11))
        layout.addWidget(subtitle)
        return header
    
    def create_footer(self):
        footer = QFrame()
        footer.setFrameShape(QFrame.NoFrame)
        layout = QHBoxLayout(footer)
        info_label = QLabel("Requires telemetry stream enabled")
        info_label.setFont(QFont("Arial", 10))
        layout.addWidget(info_label)
        layout.addStretch()
        close_btn = QPushButton("Close Menu")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        return footer
    
    def create_category_section(self, category_name, insights):
        section = QFrame()
        section.setFrameShape(QFrame.NoFrame)
        layout = QVBoxLayout(section)
        layout.setSpacing(4)
        category_label = QLabel(category_name.upper())
        category_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(category_label)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        layout.addWidget(separator)
        for name, description, callback in insights:
            btn = self.create_insight_button(name, description, callback)
            layout.addWidget(btn)
        return section
    
    def create_insight_button(self, name, description, callback):
        button = QPushButton()
        button.setCursor(Qt.PointingHandCursor)
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(2)
        btn_layout.setContentsMargins(4, 4, 4, 4)
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 10))
        btn_layout.addWidget(name_label)
        btn_layout.addWidget(desc_label)
        button.setLayout(btn_layout)
        button.setMinimumHeight(50)
        button.clicked.connect(callback)
        return button
    
    # Insight launch methods 
    def launch_example_window(self):
        from src.insights.example_pit_wall_window import ExamplePitWallWindow
        example_window = ExamplePitWallWindow()
        example_window.show()
        self.opened_windows.append(example_window)

    def launch_driver_telemetry(self):
        from src.insights.driver_telemetry_window import DriverTelemetryWindow
        window = DriverTelemetryWindow()
        window.show()
        self.opened_windows.append(window)

    def launch_track_position(self):
        from src.insights.track_position_window import TrackPositionWindow
        window = TrackPositionWindow()
        window.show()
        self.opened_windows.append(window)

    def launch_telemetry_viewer(self):
        try:
            import subprocess
            import sys
            subprocess.Popen([sys.executable, "-m", "src.insights.telemetry_stream_viewer"])
        except Exception as e:
            self.show_placeholder_message("Telemetry Stream Viewer")
            
    # --- LAUNCHES DYNAMIC DASHBOARD ---
    def launch_tyre_strategy(self):
        from src.gui.strategy_dashboard import StrategyDashboardWindow
        # We no longer pass a hardcoded driver! The window handles it dynamically.
        window = StrategyDashboardWindow() 
        window.show()
        self.opened_windows.append(window)

    def launch_hardware_console(self):
        print("🚀 Launching: Physical Hardware Console")
        from src.insights.hardware_console import HardwareConsoleWindow
        window = HardwareConsoleWindow()
        window.show()
        self.opened_windows.append(window)
    
    def launch_speed_monitor(self): self.show_placeholder_message("Speed Monitor")
    def launch_position_tracker(self): self.show_placeholder_message("Position Tracker")
    def launch_pit_analysis(self): self.show_placeholder_message("Pit Stop Analysis")
    def launch_gap_analysis(self): self.show_placeholder_message("Gap Analysis")
    def launch_sector_times(self): self.show_placeholder_message("Sector Times")
    def launch_lap_evolution(self): self.show_placeholder_message("Lap Time Evolution")
    def launch_top_speed(self): self.show_placeholder_message("Top Speed Tracker")
    def launch_flag_tracker(self): self.show_placeholder_message("Flag Tracker")
    def launch_overtake_counter(self): self.show_placeholder_message("Overtake Counter")
    def launch_drs_usage(self): self.show_placeholder_message("DRS Usage")
    
    def show_placeholder_message(self, insight_name):
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Coming Soon")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"{insight_name} will be available soon!")
        msg.exec()


def launch_insights_menu():
    app = QApplication.instance()
    if app is None: app = QApplication(sys.argv)
    menu = InsightsMenu()
    menu.show()
    return menu

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("F1 Insights Menu")
    menu = InsightsMenu()
    menu.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()