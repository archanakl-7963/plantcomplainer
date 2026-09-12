from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QCheckBox, QComboBox, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt
from services.startup_manager import StartupManager

class SettingsWidget(QWidget):
    def __init__(self, plant_state, voice_engine, parent=None):
        super().__init__(parent)
        self.plant_state = plant_state
        self.voice_engine = voice_engine

        self._build_ui()
        self.load_settings()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_lbl = QLabel("⚙️ Application Settings", self)
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #10B981;")
        main_layout.addWidget(title_lbl)

        # General Options Box
        gen_box = QGroupBox("General Options", self)
        gen_box.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold; color: #34D399;
                border: 1px solid #065F46; border-radius: 10px; margin-top: 10px; padding-top: 15px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QCheckBox { color: #ECFDF5; font-size: 13px; spacing: 8px; }
        """)
        gen_layout = QVBoxLayout(gen_box)
        gen_layout.setSpacing(12)

        self.chk_startup = QCheckBox("Start Plant Complainer with Windows automatically", gen_box)
        gen_layout.addWidget(self.chk_startup)

        self.chk_complaints = QCheckBox("Enable Plant Complaints & Popups", gen_box)
        gen_layout.addWidget(self.chk_complaints)

        self.chk_voice = QCheckBox("Enable Local Voice Audio Synthesis", gen_box)
        gen_layout.addWidget(self.chk_voice)

        self.chk_context = QCheckBox("Enable Background Computer Context Detection (Coding, Video, Idle)", gen_box)
        gen_layout.addWidget(self.chk_context)

        self.chk_floating = QCheckBox("Show Floating Desktop Plant Popup", gen_box)
        gen_layout.addWidget(self.chk_floating)

        main_layout.addWidget(gen_box)

        # Behavior & Tuning Box
        tune_box = QGroupBox("Behavior & Tuning", self)
        tune_box.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold; color: #34D399;
                border: 1px solid #065F46; border-radius: 10px; margin-top: 10px; padding-top: 15px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QLabel { color: #D1D5DB; font-size: 13px; font-weight: bold; }
        """)
        tune_layout = QVBoxLayout(tune_box)
        tune_layout.setSpacing(10)

        freq_row = QHBoxLayout()
        freq_row.addWidget(QLabel("Complaint Frequency:", tune_box))
        self.freq_combo = QComboBox(tune_box)
        self.freq_combo.addItems(["Low", "Medium", "High"])
        freq_row.addWidget(self.freq_combo)
        tune_layout.addLayout(freq_row)

        irr_row = QHBoxLayout()
        irr_row.addWidget(QLabel("Irritation Behavior:", tune_box))
        self.irr_combo = QComboBox(tune_box)
        self.irr_combo.addItems(["Normal", "Always Cute", "Always Angry", "Drama Queen"])
        irr_row.addWidget(self.irr_combo)
        tune_layout.addLayout(irr_row)

        prof_row = QHBoxLayout()
        prof_row.addWidget(QLabel("Active Voice Profile:", tune_box))
        self.prof_combo = QComboBox(tune_box)
        prof_row.addWidget(self.prof_combo)
        tune_layout.addLayout(prof_row)

        main_layout.addWidget(tune_box)

        # Save Button
        save_btn = QPushButton("💾 Save Settings", self)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981; color: #064E3B; font-weight: bold;
                font-size: 14px; padding: 12px; border-radius: 8px;
            }
            QPushButton:hover { background-color: #34D399; }
        """)
        save_btn.clicked.connect(self.save_settings)
        main_layout.addWidget(save_btn)

        main_layout.addStretch()

    def load_settings(self):
        self.chk_startup.setChecked(self.plant_state.start_with_windows)
        self.chk_complaints.setChecked(self.plant_state.enable_complaints)
        self.chk_voice.setChecked(self.plant_state.enable_voice)
        self.chk_context.setChecked(self.plant_state.enable_context_detection)
        self.chk_floating.setChecked(self.plant_state.show_floating_plant)

        idx = self.freq_combo.findText(self.plant_state.frequency)
        if idx >= 0: self.freq_combo.setCurrentIndex(idx)

        idx = self.irr_combo.findText(self.plant_state.irritation_setting)
        if idx >= 0: self.irr_combo.setCurrentIndex(idx)

        # Load profiles into combo
        pdata = self.voice_engine.get_profiles()
        profiles = pdata.get("profiles", {})
        self.prof_combo.clear()
        for pname in profiles.keys():
            self.prof_combo.addItem(pname)
        idx = self.prof_combo.findText(self.plant_state.active_voice_profile)
        if idx >= 0: self.prof_combo.setCurrentIndex(idx)

    def save_settings(self):
        self.plant_state.start_with_windows = self.chk_startup.isChecked()
        self.plant_state.enable_complaints = self.chk_complaints.isChecked()
        self.plant_state.enable_voice = self.chk_voice.isChecked()
        self.plant_state.enable_context_detection = self.chk_context.isChecked()
        self.plant_state.show_floating_plant = self.chk_floating.isChecked()
        self.plant_state.frequency = self.freq_combo.currentText()
        self.plant_state.irritation_setting = self.irr_combo.currentText()
        self.plant_state.active_voice_profile = self.prof_combo.currentText()
        self.plant_state.save()

        # Update Windows Registry Startup
        StartupManager.set_startup(self.plant_state.start_with_windows)

        QMessageBox.information(self, "Settings Saved", "Application settings have been updated!")
