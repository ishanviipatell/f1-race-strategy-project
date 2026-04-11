from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QHBoxLayout, QComboBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.gui.pit_wall_window import PitWallWindow
from src.strategy_engine import StrategyEngine
from src.lib.tyres import get_tyre_compound_str

class StrategyDashboardWindow(PitWallWindow):
    def __init__(self):
        self.target_driver = None
        
        # Engine initializes at 57, but updates automatically if stream provides total_laps
        self.engine = StrategyEngine(total_laps=57) 
        self.last_calc_lap = -1
        
        super().__init__()
        self.setWindowTitle("Live Strategy Wall")

    def setup_ui(self):
        """Build the dashboard UI elements."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. Dynamic Driver Selector
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Track Driver:")
        selector_label.setFont(QFont("Arial", 14, QFont.Bold))
        
        self.driver_combo = QComboBox()
        self.driver_combo.setFont(QFont("Arial", 14, QFont.Bold))
        self.driver_combo.setMinimumWidth(100)
        self.driver_combo.currentTextChanged.connect(self.on_driver_changed)
        
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.driver_combo)
        selector_layout.addStretch()
        main_layout.addLayout(selector_layout)

        # 2. Driver Header
        self.header_label = QLabel("Strategy: Waiting for stream...")
        self.header_label.setFont(QFont("Arial", 26, QFont.Bold))
        self.header_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.header_label)

        # 3. Tyre Status Group
        tyre_group = QGroupBox("Current Tyre Status")
        tyre_group.setFont(QFont("Arial", 12, QFont.Bold))
        tyre_layout = QVBoxLayout()
        
        self.compound_label = QLabel("Compound: WAITING...")
        self.compound_label.setFont(QFont("Arial", 16))
        self.age_label = QLabel("Tyre Age: 0 Laps")
        self.age_label.setFont(QFont("Arial", 16))
        
        tyre_layout.addWidget(self.compound_label)
        tyre_layout.addWidget(self.age_label)
        tyre_group.setLayout(tyre_layout)
        main_layout.addWidget(tyre_group)

        # 4. Strategy & Pit Window Group
        strat_group = QGroupBox("Predictive Strategy")
        strat_group.setFont(QFont("Arial", 12, QFont.Bold))
        strat_layout = QVBoxLayout()
        
        self.plan_label = QLabel("Plan: CALCULATING...")
        self.plan_label.setFont(QFont("Arial", 16))
        self.plan_label.setStyleSheet("color: #4CAF50;") # Green text
        
        self.box_window_label = QLabel("Box Window: --")
        self.box_window_label.setFont(QFont("Arial", 16))
        
        strat_layout.addWidget(self.plan_label)
        strat_layout.addWidget(self.box_window_label)
        strat_group.setLayout(strat_layout)
        main_layout.addWidget(strat_group)

        # 5. SC / VSC Alert Banner
        self.alert_label = QLabel("TRACK CLEAR")
        self.alert_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.alert_label.setStyleSheet("color: white; background-color: #4CAF50; padding: 15px; border-radius: 5px;")
        main_layout.addWidget(self.alert_label)
        
        main_layout.addStretch()

    def on_driver_changed(self, driver_code):
        """Triggered when the user picks a new driver from the dropdown."""
        if not driver_code: return
        self.target_driver = driver_code
        self.header_label.setText(f"Strategy: {self.target_driver}")
        
        # Reset labels instantly while waiting for next telemetry tick
        self.compound_label.setText("Compound: WAITING...")
        self.plan_label.setText("Plan: CALCULATING...")
        self.box_window_label.setText("Box Window: --")
        
        # Force the engine to recalculate immediately on the next data frame
        self.last_calc_lap = -1 

    def on_telemetry_data(self, data):
        """Processes live telemetry frames for strategy updates and tracks scrubbing."""
        frame = data.get("frame", {})
        drivers = frame.get("drivers", {})
        
        # --- DYNAMIC SETUP: Auto-populate dropdown if new drivers appear ---
        if drivers:
            current_items = set([self.driver_combo.itemText(i) for i in range(self.driver_combo.count())])
            new_drivers = [d for d in drivers.keys() if d not in current_items]
            if new_drivers:
                self.driver_combo.addItems(sorted(new_drivers))
                # Auto-select the first driver if none is selected
                if not self.target_driver and self.driver_combo.count() > 0:
                    self.driver_combo.setCurrentIndex(0)

        # --- DYNAMIC SETUP: Update total laps if stream provides it ---
        if "total_laps" in frame:
            self.engine.total_laps = int(frame["total_laps"])

        # Track Status
        track_status = str(data.get("track_status", "1")) 

        # --- 1. CHEAP PIT STOP ALERTS ---
        if track_status in ["4", "6"]:
            self.alert_label.setText("⚠️ CHEAP PIT STOP OPPORTUNITY (SC/VSC) ⚠️")
            self.alert_label.setStyleSheet("color: black; background-color: #FFEB3B; padding: 15px; border-radius: 5px;")
        else:
            self.alert_label.setText("TRACK CLEAR")
            self.alert_label.setStyleSheet("color: white; background-color: #4CAF50; padding: 15px; border-radius: 5px;")

        # --- 2. DRIVER SPECIFIC DATA & SCRUBBING ---
        if self.target_driver and self.target_driver in drivers:
            d_data = drivers[self.target_driver]
            
            tyre_code = int(d_data.get("tyre", -1))
            compound = get_tyre_compound_str(tyre_code)
            tyre_age = int(d_data.get("tyre_life", 0))
            curr_lap = int(d_data.get("lap", 1))

            self.compound_label.setText(f"Compound: {compound}")
            self.age_label.setText(f"Tyre Age: {tyre_age} Laps")
            
            # --- 3. DYNAMIC STRATEGY PREDICTIONS ---
            # The '!=' catches normal progression AND rewind/fast-forward scrubbing perfectly
            if curr_lap != self.last_calc_lap:
                best_stints, _ = self.engine.find_optimum_strategy(curr_lap, compound)
                
                if best_stints and len(best_stints) > 1:
                    pit_in = curr_lap + best_stints[0][1]
                    next_tyre = best_stints[1][0]
                    
                    self.plan_label.setText(f"Plan: {compound} ➔ {next_tyre}")
                    
                    if curr_lap >= pit_in - 2:
                        self.box_window_label.setText(f"BOX WINDOW: Lap {pit_in} [ACTIVE]")
                        self.box_window_label.setStyleSheet("color: #FF9800; font-weight: bold;")
                    else:
                        self.box_window_label.setText(f"Target Pit Lap: {pit_in}")
                        self.box_window_label.setStyleSheet("")
                        
                # Update tracker so we don't recalculate unless lap changes (or user scrubs)
                self.last_calc_lap = curr_lap