from PySide6.QtWidgets import (
    QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QWidget, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

class FirstRunWizardDialog(QDialog):
    def __init__(self, voice_engine, audio_manager, plant_state, parent=None):
        super().__init__(parent)
        self.voice_engine = voice_engine
        self.audio_manager = audio_manager
        self.plant_state = plant_state

        self.setWindowTitle("🌱 Welcome to Plant Complainer Setup Wizard")
        self.setFixedSize(500, 380)
        self.setStyleSheet("""
            QDialog {
                background-color: #064E3B; color: #ECFDF5;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel { color: #ECFDF5; }
            QPushButton {
                background-color: #10B981; color: #064E3B; font-weight: bold;
                font-size: 14px; padding: 10px; border-radius: 8px;
            }
            QPushButton:hover { background-color: #34D399; }
        """)

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)

        self.stack = QStackedWidget(self)

        # Page 1: Welcome & Add Samples
        p1 = QWidget()
        l1 = QVBoxLayout(p1)
        lbl1 = QLabel("🌱 Welcome to Plant Complainer!", p1)
        lbl1.setStyleSheet("font-size: 22px; font-weight: bold; color: #34D399;")
        l1.addWidget(lbl1)

        desc1 = QLabel("Your irritating virtual plant is ready to complain!\n\nStep 1: Upload reference audio samples in your preferred voice style.", p1)
        desc1.setWordWrap(True)
        desc1.setStyleSheet("font-size: 14px; color: #D1D5DB;")
        l1.addWidget(desc1)
        l1.addStretch()

        btn1 = QPushButton("📁 Add Voice Samples (Step 1)", p1)
        btn1.clicked.connect(self._step1_add_samples)
        l1.addWidget(btn1)

        btn1_next = QPushButton("Next ➔", p1)
        btn1_next.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        l1.addWidget(btn1_next)

        self.stack.addWidget(p1)

        # Page 2: Select/Create Voice Profile
        p2 = QWidget()
        l2 = QVBoxLayout(p2)
        lbl2 = QLabel("🎙️ Step 2: Set Plant Voice Profile", p2)
        lbl2.setStyleSheet("font-size: 20px; font-weight: bold; color: #34D399;")
        l2.addWidget(lbl2)

        desc2 = QLabel("Select or create a voice profile for your plant companion.", p2)
        desc2.setWordWrap(True)
        l2.addWidget(desc2)
        l2.addStretch()

        btn2_next = QPushButton("Next ➔", p2)
        btn2_next.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        l2.addWidget(btn2_next)

        self.stack.addWidget(p2)

        # Page 3: Test & Start
        p3 = QWidget()
        l3 = QVBoxLayout(p3)
        lbl3 = QLabel("✨ Step 3 & 4: Test & Start!", p3)
        lbl3.setStyleSheet("font-size: 20px; font-weight: bold; color: #34D399;")
        l3.addWidget(lbl3)

        desc3 = QLabel("Everything is ready! Click 'Start Plant' to let your plant live on your desktop.", p3)
        desc3.setWordWrap(True)
        l3.addWidget(desc3)
        l3.addStretch()

        btn3_test = QPushButton("🔊 Try Voice Sample", p3)
        btn3_test.clicked.connect(self._step3_test_voice)
        l3.addWidget(btn3_test)

        btn3_finish = QPushButton("🌱 Start Plant Complainer!", p3)
        btn3_finish.setStyleSheet("background-color: #34D399; font-size: 16px; padding: 12px;")
        btn3_finish.clicked.connect(self.accept)
        l3.addWidget(btn3_finish)

        self.stack.addWidget(p3)

        main_layout.addWidget(self.stack)

    def _step1_add_samples(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Reference Audio Sample", "", "Audio Files (*.wav *.mp3 *.ogg *.m4a)"
        )
        if file_path:
            import shutil
            profile_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "voices", "default"))
            os.makedirs(profile_dir, exist_ok=True)
            fname = os.path.basename(file_path)
            shutil.copy(file_path, os.path.join(profile_dir, fname))
            QMessageBox.information(self, "Sample Added", f"Added voice sample: {fname}")

    def _step3_test_voice(self):
        txt = "Edaa... enikku vellam venam!"
        wav_path = self.voice_engine.generate_speech(txt, profile_name="default")
        if wav_path:
            self.audio_manager.play_audio(wav_path)
