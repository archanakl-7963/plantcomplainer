from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, QSlider, QLabel, QPushButton, QGroupBox
from PySide6.QtCore import Qt
from startup.startup_manager import StartupManager
from storage.state_manager import StateManager

class SettingsWindow(QDialog):
    """
    Full Settings Configuration Window for Plant Companion.
    """
    def __init__(self, plant_state, parent=None):
        super().__init__(parent)
        self.plant_state = plant_state

        self.setWindowTitle("⚙️ Plant Companion Settings")
        self.setFixedSize(500, 520)
        self.setStyleSheet("""
            QDialog { background-color: #064E3B; color: white; font-family: 'Segoe UI', sans-serif; }
            QGroupBox { font-weight: bold; border: 2px solid #059669; border-radius: 8px; margin-top: 10px; padding: 10px; color: #A7F3D0; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QCheckBox { font-size: 13px; color: #ECFDF5; spacing: 8px; }
            QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 1px solid #10B981; }
            QCheckBox::indicator:checked { background-color: #10B981; }
            QLabel { font-size: 13px; color: #ECFDF5; }
            QPushButton { background-color: #059669; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #10B981; }
        """)

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)

        # 1. Behavior Toggles
        grp_toggles = QGroupBox("Behavior & Notifications", self)
        lay_toggles = QVBoxLayout(grp_toggles)

        self.chk_auto = QCheckBox("Enable Automatic Complaints & Interruption", self)
        self.chk_auto.setChecked(self.plant_state.auto_complaints)
        
        self.chk_voice = QCheckBox("Enable High-Pitched Malayalam Voice Output", self)
        self.chk_voice.setChecked(self.plant_state.enable_voice)

        self.chk_gossip = QCheckBox("Enable Random Gossip & Observations", self)
        self.chk_gossip.setChecked(self.plant_state.enable_random_gossip)

        self.chk_activity = QCheckBox("Enable Real-Time Activity Monitoring", self)
        self.chk_activity.setChecked(self.plant_state.enable_context_detection)

        self.chk_startup = QCheckBox("Start Plant Companion with Windows", self)
        self.chk_startup.setChecked(StartupManager.is_startup_enabled())

        lay_toggles.addWidget(self.chk_auto)
        lay_toggles.addWidget(self.chk_voice)
        lay_toggles.addWidget(self.chk_gossip)
        lay_toggles.addWidget(self.chk_activity)
        lay_toggles.addWidget(self.chk_startup)

        main_layout.addWidget(grp_toggles)

        # 2. Sliders
        grp_sliders = QGroupBox("Personality & Timing Controls", self)
        lay_sliders = QVBoxLayout(grp_sliders)

        # Dramatic Level
        lay_dramatic = QHBoxLayout()
        lay_dramatic.addWidget(QLabel("Dramatic Level:", self))
        self.sld_dramatic = QSlider(Qt.Horizontal, self)
        self.sld_dramatic.setRange(1, 10)
        self.sld_dramatic.setValue(self.plant_state.dramatic_level)
        lay_dramatic.addWidget(self.sld_dramatic)
        lay_sliders.addLayout(lay_dramatic)

        # Sarcasm Level
        lay_sarcasm = QHBoxLayout()
        lay_sarcasm.addWidget(QLabel("Sarcasm Level:", self))
        self.sld_sarcasm = QSlider(Qt.Horizontal, self)
        self.sld_sarcasm.setRange(1, 10)
        self.sld_sarcasm.setValue(self.plant_state.sarcasm_level)
        lay_sarcasm.addWidget(self.sld_sarcasm)
        lay_sliders.addLayout(lay_sarcasm)

        # Interval
        lay_freq = QHBoxLayout()
        self.lbl_freq = QLabel(f"Complaint Frequency: {self.plant_state.complaint_interval_sec}s", self)
        lay_freq.addWidget(self.lbl_freq)
        self.sld_freq = QSlider(Qt.Horizontal, self)
        self.sld_freq.setRange(5, 120)
        self.sld_freq.setValue(self.plant_state.complaint_interval_sec)
        self.sld_freq.valueChanged.connect(lambda v: self.lbl_freq.setText(f"Complaint Frequency: {v}s"))
        lay_freq.addWidget(self.sld_freq)
        lay_sliders.addLayout(lay_freq)

        main_layout.addWidget(grp_sliders)

        # Buttons
        lay_btns = QHBoxLayout()
        btn_save = QPushButton("Save Settings", self)
        btn_save.clicked.connect(self._save)
        btn_cancel = QPushButton("Cancel", self)
        btn_cancel.clicked.connect(self.reject)

        lay_btns.addWidget(btn_save)
        lay_btns.addWidget(btn_cancel)
        main_layout.addLayout(lay_btns)

    def _save(self):
        self.plant_state.auto_complaints = self.chk_auto.isChecked()
        self.plant_state.enable_voice = self.chk_voice.isChecked()
        self.plant_state.enable_random_gossip = self.chk_gossip.isChecked()
        self.plant_state.enable_context_detection = self.chk_activity.isChecked()
        self.plant_state.dramatic_level = self.sld_dramatic.value()
        self.plant_state.sarcasm_level = self.sld_sarcasm.value()
        self.plant_state.complaint_interval_sec = self.sld_freq.value()

        # Update Windows startup
        StartupManager.set_startup_enabled(self.chk_startup.isChecked())

        # Save to local storage
        StateManager.save_state(self.plant_state)
        self.accept()
