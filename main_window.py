import os
import sys
from PySide6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, 
    QProgressBar, QMenu, QApplication, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal, QPoint
from PySide6.QtGui import QColor, QFont, QIcon, QAction

from .plant_view import PlantView
from .test_panel import TestPanel
from .demo_mode import DemoModeRunner
from .settings_view import SettingsWindow
from .history_view import HistoryWindow

class SpeechBubbleWidget(QFrame):
    """Custom comic-style speech bubble for Malayalam gossips."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #047857;
                border: 2px solid #10B981;
                border-radius: 14px;
                padding: 10px;
            }
            QLabel {
                color: #F0FDF4;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        self.label = QLabel("«ഹലോ! ഞാൻ നിങ്ങളുടെ സ്വന്തം ചെടിയാണ് 🌱»", self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

    def set_content(self, text, mood="NORMAL"):
        self.label.setText(f"«{text}»")


class MainWindow(QWidget):
    """
    Main Plant Companion Desktop Interface.
    Combines Plant View Avatar, Stats (Water, Sunlight, Health, Mood),
    Dynamic Malayalam Speech Bubble, and Quick Care & Simulation Controls.
    """
    def __init__(self, plant_state, complaint_engine, activity_detector, tts_manager, parent=None):
        super().__init__(parent)
        self.plant_state = plant_state
        self.complaint_engine = complaint_engine
        self.activity_detector = activity_detector
        self.tts_manager = tts_manager
        
        self.drag_position = QPoint()

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.WindowSystemMenuHint |
            Qt.Tool
        )
        self.setWindowTitle("🌱 Plant Companion")
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(580, 480)

        self._build_ui()
        self._setup_timers()
        self.update_display()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # Background Container Card
        card = QFrame(self)
        card.setStyleSheet("""
            QFrame#card {
                background-color: #064E3B;
                border: 3px solid #059669;
                border-radius: 20px;
            }
            QLabel { color: #ECFDF5; font-family: 'Segoe UI', sans-serif; }
            QPushButton {
                background-color: #059669;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 12px;
                border: none;
            }
            QPushButton:hover { background-color: #10B981; }
            QPushButton:pressed { background-color: #047857; }
        """)
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)

        # Top Header Bar (Title + Drag Handle + System Buttons)
        header = QHBoxLayout()
        lbl_title = QLabel("🌱 PLANT COMPANION", self)
        lbl_title.setStyleSheet("font-size: 15px; font-weight: bold; color: #FEF08A; letter-spacing: 1px;")
        header.addWidget(lbl_title)
        header.addStretch()

        btn_min = QPushButton("—", self)
        btn_min.setFixedSize(28, 24)
        btn_min.clicked.connect(self.showMinimized)
        
        btn_close = QPushButton("✕", self)
        btn_close.setFixedSize(28, 24)
        btn_close.setStyleSheet("background-color: #991B1B;")
        btn_close.clicked.connect(QApplication.quit)

        header.addWidget(btn_min)
        header.addWidget(btn_close)
        card_layout.addLayout(header)

        # Middle Content Row (Plant Avatar + Stats Column + Speech Bubble)
        mid_layout = QHBoxLayout()

        # Left Column: Plant Avatar
        self.plant_view = PlantView(self)
        mid_layout.addWidget(self.plant_view, 0, Qt.AlignCenter)

        # Right Column: Stats & Mood
        right_col = QVBoxLayout()
        
        self.lbl_mood = QLabel("Mood: 😌 NORMAL", self)
        self.lbl_mood.setStyleSheet("font-size: 14px; font-weight: bold; color: #A7F3D0;")
        right_col.addWidget(self.lbl_mood)

        # Stat Bars
        self.bar_water = self._create_bar("Water:", "#0284C7")
        self.bar_sun = self._create_bar("Sunlight:", "#EAB308")
        self.bar_health = self._create_bar("Health:", "#16A34A")

        right_col.addLayout(self.bar_water["layout"])
        right_col.addLayout(self.bar_sun["layout"])
        right_col.addLayout(self.bar_health["layout"])

        mid_layout.addLayout(right_col, 1)
        card_layout.addLayout(mid_layout)

        # Speech Bubble / Thought Area
        self.speech_bubble = SpeechBubbleWidget(self)
        card_layout.addWidget(self.speech_bubble)

        # Care Actions Row ([💧 Water] [☀️ Sunlight] [💬 Talk] [🔊 Speak] [🔇 Mute])
        care_row = QHBoxLayout()
        
        btn_water = QPushButton("💧 Water", self)
        btn_water.clicked.connect(self._action_water)
        
        btn_sun = QPushButton("☀️ Sunlight", self)
        btn_sun.clicked.connect(self._action_sunlight)
        
        btn_talk = QPushButton("💬 Talk", self)
        btn_talk.clicked.connect(self._action_talk)
        
        btn_sing = QPushButton("🎵 Sing", self)
        btn_sing.clicked.connect(self._action_sing)

        self.btn_mute = QPushButton("🔊 Voice ON", self)
        self.btn_mute.clicked.connect(self._toggle_mute)

        care_row.addWidget(btn_water)
        care_row.addWidget(btn_sun)
        care_row.addWidget(btn_talk)
        care_row.addWidget(btn_sing)
        care_row.addWidget(self.btn_mute)
        card_layout.addLayout(care_row)


        # Bottom Tools Row ([⚙️ Settings] [🧪 Test Panel] [🎬 Demo Mode] [📜 History])
        tools_row = QHBoxLayout()
        
        btn_test = QPushButton("🧪 Test Panel", self)
        btn_test.clicked.connect(self._open_test_panel)
        
        btn_demo = QPushButton("🎬 Demo Mode", self)
        btn_demo.clicked.connect(self._start_demo_mode)

        btn_settings = QPushButton("⚙️ Settings", self)
        btn_settings.clicked.connect(self._open_settings)

        btn_history = QPushButton("📜 History", self)
        btn_history.clicked.connect(self._open_history)

        tools_row.addWidget(btn_test)
        tools_row.addWidget(btn_demo)
        tools_row.addWidget(btn_settings)
        tools_row.addWidget(btn_history)
        card_layout.addLayout(tools_row)

        main_layout.addWidget(card)

    def _create_bar(self, label_text, color_hex):
        layout = QHBoxLayout()
        lbl = QLabel(label_text, self)
        lbl.setFixedWidth(65)
        bar = QProgressBar(self)
        bar.setRange(0, 100)
        bar.setFixedHeight(12)
        bar.setTextVisible(False)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #047857;
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                background-color: {color_hex};
                border-radius: 6px;
            }}
        """)
        layout.addWidget(lbl)
        layout.addWidget(bar)
        return {"layout": layout, "bar": bar}

    def _setup_timers(self):
        # 1. Decay & Complaint Loop Timer
        self.loop_timer = QTimer(self)
        self.loop_timer.timeout.connect(self._on_loop_tick)
        self.loop_timer.start(15000) # Every 15 seconds

        # 2. Position Center On First Launch
        QTimer.singleShot(100, self._center_on_screen)

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def update_display(self):
        if hasattr(self.plant_state, 'mood'):
            mood = self.plant_state.mood
        elif hasattr(self.plant_state, 'get_irritation_level'):
            _, mood = self.plant_state.get_irritation_level()
        else:
            mood = "NORMAL"

        self.lbl_mood.setText(f"Mood: {str(mood).upper()}")

        water_val = getattr(self.plant_state, 'water', getattr(self.plant_state, 'water_level', 80))
        sun_val = getattr(self.plant_state, 'sunlight', getattr(self.plant_state, 'sunlight_level', 70))
        health_val = getattr(self.plant_state, 'happiness', getattr(self.plant_state, 'health', 75))

        self.bar_water["bar"].setValue(int(water_val))
        self.bar_sun["bar"].setValue(int(sun_val))
        self.bar_health["bar"].setValue(int(health_val))

        self.plant_view.set_expression(str(mood))

        enable_v = getattr(self.plant_state, 'enable_voice', True)
        if enable_v:
            self.btn_mute.setText("🔊 Voice ON")
        else:
            self.btn_mute.setText("🔇 Muted")

    def _on_loop_tick(self):
        if hasattr(self.plant_state, 'update_decay'):
            self.plant_state.update_decay(seconds_elapsed=15.0)
        self.update_display()

    def trigger_complaint(self, complaint):
        text = complaint.get("text", "")
        mood = complaint.get("mood", "NORMAL")
        irr = complaint.get("irritation", mood)
        context_name = complaint.get("context", "System")

        self.speech_bubble.set_content(text, mood=str(mood))
        self.plant_view.set_expression(str(mood))
        self.plant_view.set_talking(True)
        QTimer.singleShot(2500, lambda: self.plant_view.set_talking(False))

        if getattr(self.plant_state, 'enable_voice', True) and text:
            if hasattr(QApplication.instance(), 'complaint_loop') and QApplication.instance().complaint_loop:
                loop = QApplication.instance().complaint_loop
                profile = getattr(self.plant_state, 'active_voice_profile', 'default')
                try:
                    audio_path = loop.voice_engine.generate_speech(text, profile_name=profile, emotion=str(irr))
                    loop.popup_widget.show_complaint(complaint, audio_path=audio_path, context_name=context_name)
                except Exception as err:
                    print(f"[MainWindow] Voice synth error: {err}")
            elif hasattr(self, 'tts_manager') and self.tts_manager and hasattr(self.tts_manager, 'speak'):
                try:
                    self.tts_manager.speak(text, emotion=str(mood).lower())
                except Exception as err:
                    print(f"[MainWindow] TTSManager error: {err}")

    def _action_water(self):
        if hasattr(self.plant_state, 'do_action'):
            self.plant_state.do_action("water")
        elif hasattr(self.plant_state, 'water'):
            self.plant_state.water()
        self.update_display()
        reaction = "അഹാ! വെള്ളം കിട്ടി. ഇനി കുറച്ച് നേരത്തേക്ക് നിന്നെ ഞാൻ forgive ചെയ്തു 😌🌱"
        complaint = {"text": reaction, "mood": "happy", "irritation": "happy", "context": "Care"}
        self.trigger_complaint(complaint)

    def _action_sunlight(self):
        if hasattr(self.plant_state, 'do_action'):
            self.plant_state.do_action("sunlight")
        elif hasattr(self.plant_state, 'give_sunlight'):
            self.plant_state.give_sunlight()
        self.update_display()
        reaction = "ഇതാണ് പറയുന്നത് ജീവിതത്തിൽ ചെറിയ കാര്യങ്ങൾ മതി സന്തോഷിക്കാൻ ☀️🌱"
        complaint = {"text": reaction, "mood": "happy", "irritation": "happy", "context": "Care"}
        self.trigger_complaint(complaint)

    def _action_talk(self):
        if hasattr(self.plant_state, 'do_action'):
            self.plant_state.do_action("care")
        elif hasattr(self.plant_state, 'interact'):
            self.plant_state.interact()
        self.update_display()
        if hasattr(QApplication.instance(), 'complaint_loop') and QApplication.instance().complaint_loop:
            QApplication.instance().complaint_loop._trigger()


    def _action_sing(self):
        if hasattr(self.plant_state, 'do_action'):
            self.plant_state.do_action("sing")
        else:
            self.plant_state.interact()
        self.update_display()
        
        # Pick a song complaint or force song condition
        complaint = None
        if hasattr(self.complaint_engine, 'select_complaint'):
            try:
                complaint = self.complaint_engine.select_complaint(self.plant_state, "any", force_condition="song")
            except Exception:
                pass
        
        if not complaint:
            songs = [
                "കിളിയേ കിളിയേ നാളെ വരാം... എനിക്ക് വെള്ളം തന്നാൽ ഇനിയും പാടാം! 🎵🌱",
                "കുട്ടാ കുട്ടാ മാടത്തക്കുട്ടാ... ഞാനൊരു പാവം സുന്ദരി ചെടിയല്ലേ മോളേ! 🎶✨",
                "പൂപറിക്കാൻ പോരുമോ... എന്റെ പൂവ് വാടിപ്പോകാതെ വെള്ളം തരുമോ! 🌸🎶",
                "ജിമിക്കി കമ്മൽ പോലെ ഞാനും ആടുന്നുണ്ട്... കുറച്ച് വെയിൽ കിട്ടിയാൽ പൊളിക്കും! 💃✨🎶",
                "പൂവണിഞ്ഞു കാടുകൾ... ഞാൻ പച്ചപ്പണിഞ്ഞു നിങ്ങളുടെ laptop-ന് അരികിൽ പാടുന്നു! 🌿🎤🎵"
            ]
            import random
            complaint = {"text": random.choice(songs), "mood": "HAPPY", "context": "Music"}
            
        self.trigger_complaint(complaint)


    def _toggle_mute(self):
        self.plant_state.enable_voice = not self.plant_state.enable_voice
        self.tts_manager.setMuted(not self.plant_state.enable_voice)
        self.update_display()

    def _open_test_panel(self):
        panel = TestPanel(self.activity_detector, self.plant_state, self.complaint_engine, self.tts_manager, self, self)
        panel.exec()

    def _start_demo_mode(self):
        demo = DemoModeRunner(self.activity_detector, self.plant_state, self.complaint_engine, self.tts_manager, self, self)
        demo.start_demo()

    def _open_settings(self):
        win = SettingsWindow(self.plant_state, self)
        if win.exec():
            self.update_display()

    def _open_history(self):
        win = HistoryWindow(self)
        win.exec()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
