from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGroupBox
from PySide6.QtCore import Qt

class TestPanel(QDialog):
    """
    Developer / Simulation Test Panel.
    Allows manual simulation of:
    - Gaming
    - Coding
    - Studying / Document Reading
    - YouTube
    - Idle
    - Thirst
    - No Sunlight
    - Neglect
    - Happy
    """
    def __init__(self, activity_detector, plant_state, complaint_engine, tts_manager, popup_widget, parent=None):
        super().__init__(parent)
        self.activity_detector = activity_detector
        self.plant_state = plant_state
        self.complaint_engine = complaint_engine
        self.tts_manager = tts_manager
        self.popup_widget = popup_widget

        self.setWindowTitle("🧪 Plant Companion - Simulation & Developer Panel")
        self.setFixedSize(520, 420)
        self.setStyleSheet("""
            QDialog { background-color: #064E3B; color: white; font-family: 'Segoe UI', sans-serif; }
            QGroupBox { font-weight: bold; border: 2px solid #059669; border-radius: 8px; margin-top: 10px; padding: 10px; color: #A7F3D0; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QPushButton { background-color: #059669; color: white; font-weight: bold; padding: 8px 12px; border-radius: 6px; border: none; }
            QPushButton:hover { background-color: #10B981; }
            QPushButton:pressed { background-color: #047857; }
            QLabel { font-size: 13px; color: #ECFDF5; }
        """)

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel("🧪 Developer & Presentation Simulation Panel", self)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FEF08A;")
        main_layout.addWidget(title)

        # 1. Activity Simulation Group
        act_group = QGroupBox("Simulate User Activity", self)
        act_layout = QVBoxLayout(act_group)
        
        row1 = QHBoxLayout()
        btn_gaming = QPushButton("🎮 Simulate Gaming (2 hrs)", self)
        btn_gaming.clicked.connect(lambda: self._sim_activity("game"))
        btn_coding = QPushButton("💻 Simulate Coding (3 hrs)", self)
        btn_coding.clicked.connect(lambda: self._sim_activity("coding"))
        row1.addWidget(btn_gaming)
        row1.addWidget(btn_coding)
        act_layout.addLayout(row1)

        row2 = QHBoxLayout()
        btn_doc = QPushButton("📄 Simulate Studying/Doc", self)
        btn_doc.clicked.connect(lambda: self._sim_activity("document"))
        btn_yt = QPushButton("▶️ Simulate YouTube", self)
        btn_yt.clicked.connect(lambda: self._sim_activity("youtube"))
        row2.addWidget(btn_doc)
        row2.addWidget(btn_yt)
        act_layout.addLayout(row2)

        row3 = QHBoxLayout()
        btn_idle = QPushButton("💤 Simulate Idle (1 hr)", self)
        btn_idle.clicked.connect(lambda: self._sim_activity("idle"))
        btn_clear = QPushButton("🔄 Reset Activity Detection", self)
        btn_clear.clicked.connect(self._clear_activity)
        row3.addWidget(btn_idle)
        row3.addWidget(btn_clear)
        act_layout.addLayout(row3)

        main_layout.addWidget(act_group)

        # 2. Plant State Simulation Group
        state_group = QGroupBox("Simulate Plant Needs & Moods", self)
        state_layout = QHBoxLayout(state_group)

        btn_thirst = QPushButton("💧 Simulate Thirst (Water 10%)", self)
        btn_thirst.clicked.connect(self._sim_thirst)
        btn_sun = QPushButton("☀️ Simulate No Sunlight", self)
        btn_sun.clicked.connect(self._sim_no_sunlight)
        btn_happy = QPushButton("🌱 Simulate Happy State", self)
        btn_happy.clicked.connect(self._sim_happy)

        state_layout.addWidget(btn_thirst)
        state_layout.addWidget(btn_sun)
        state_layout.addWidget(btn_happy)

        main_layout.addWidget(state_group)

        # Output Status
        self.lbl_status = QLabel("Click any button above to trigger instant Malayalam complaint synthesis.", self)
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setStyleSheet("color: #FDE68A; font-style: italic;")
        main_layout.addWidget(self.lbl_status)

        # Close
        btn_close = QPushButton("Close Panel", self)
        btn_close.clicked.connect(self.accept)
        main_layout.addWidget(btn_close)

    def _sim_activity(self, act_name):
        self.activity_detector.set_manual_override(act_name)
        complaint = self.complaint_engine.select_complaint(self.plant_state, self.activity_detector, force=True)
        if complaint:
            self._trigger_complaint_ui(complaint)

    def _clear_activity(self):
        self.activity_detector.clear_manual_override()
        self.lbl_status.setText("Activity override cleared. Live system monitoring active.")

    def _sim_thirst(self):
        self.plant_state.water_level = 10.0
        complaint = self.complaint_engine.select_complaint(self.plant_state, self.activity_detector, force=True)
        if complaint:
            self._trigger_complaint_ui(complaint)

    def _sim_no_sunlight(self):
        self.plant_state.sunlight_level = 15.0
        complaint = self.complaint_engine.select_complaint(self.plant_state, self.activity_detector, force=True)
        if complaint:
            self._trigger_complaint_ui(complaint)

    def _sim_happy(self):
        self.plant_state.water_level = 90.0
        self.plant_state.sunlight_level = 90.0
        self.plant_state.happiness = 100.0
        complaint = self.complaint_engine.select_complaint(self.plant_state, self.activity_detector, force=True)
        if complaint:
            self._trigger_complaint_ui(complaint)

    def _trigger_complaint_ui(self, complaint):
        text = complaint.get("text", "")
        context_desc = complaint.get("context", "System")
        mood = complaint.get("mood", "NORMAL")

        self.lbl_status.setText(f"Generated: «{text}» [{context_desc} | Mood: {mood}]")
        self.popup_widget.show_complaint(complaint, context_name=context_desc)
        if self.plant_state.enable_voice:
            self.tts_manager.speak(text, emotion=mood.lower())
