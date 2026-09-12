import os
import shutil
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QComboBox, QFileDialog,
    QGroupBox, QMessageBox, QFrame, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal

class VoiceLibraryWidget(QWidget):
    def __init__(self, voice_engine, audio_manager, plant_state, parent=None):
        super().__init__(parent)
        self.voice_engine = voice_engine
        self.audio_manager = audio_manager
        self.plant_state = plant_state
        self.last_generated_wav = None

        self._build_ui()
        self.refresh_profiles()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header Title & Voice Model Status
        title_box = QHBoxLayout()
        title_lbl = QLabel("🎙️ Voice Library & Reference Samples", self)
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #10B981;")
        title_box.addWidget(title_lbl)
        title_box.addStretch()

        status_text, is_ready = self.voice_engine.get_status()
        self.status_badge = QLabel(f"Voice Model: {status_text}", self)
        self.status_badge.setStyleSheet(f"""
            font-size: 12px;
            font-weight: bold;
            padding: 6px 12px;
            border-radius: 12px;
            background-color: {"#065F46" if is_ready else "#7F1D1D"};
            color: {"#34D399" if is_ready else "#FCA5A5"};
        """)
        title_box.addWidget(self.status_badge)

        main_layout.addLayout(title_box)

        # Content Row
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Left Column: Profiles & Sample Management
        left_box = QGroupBox("Plant Voice Profiles", self)
        left_box.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold; color: #34D399;
                border: 1px solid #065F46; border-radius: 10px; margin-top: 10px; padding-top: 15px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        left_layout = QVBoxLayout(left_box)

        profile_row = QHBoxLayout()
        profile_row.addWidget(QLabel("Active Profile:", left_box))
        self.profile_combo = QComboBox(left_box)
        self.profile_combo.currentIndexChanged.connect(self._on_profile_changed)
        profile_row.addWidget(self.profile_combo)

        self.new_profile_btn = QPushButton("+ New Profile", left_box)
        self.new_profile_btn.clicked.connect(self._create_new_profile)
        profile_row.addWidget(self.new_profile_btn)

        left_layout.addLayout(profile_row)

        # Voice Tone & Childishness Customizer
        style_row = QHBoxLayout()
        style_row.addWidget(QLabel("Voice Tone Style:", left_box))
        self.style_combo = QComboBox(left_box)
        self.style_combo.addItems([
            "Cute & Childish (Clear Medium Speed)",
            "Whiny & Irritating (Cute Childish)",
            "Drama Queen (High Irritation)",
            "Natural Tone"
        ])
        self.style_combo.currentIndexChanged.connect(self._on_style_changed)
        style_row.addWidget(self.style_combo)
        left_layout.addLayout(style_row)

        # Samples List
        left_layout.addWidget(QLabel("Uploaded Reference Samples (WAV / MP3 / OGG / M4A):", left_box))
        self.samples_list = QListWidget(left_box)
        self.samples_list.setStyleSheet("""
            QListWidget {
                background-color: #064E3B; border: 1px solid #047857;
                border-radius: 8px; color: #ECFDF5; font-size: 13px; padding: 5px;
            }
            QListWidget::item:selected { background-color: #10B981; color: #064E3B; font-weight: bold; }
        """)
        left_layout.addWidget(self.samples_list)

        # Action Buttons Row
        btn_row = QHBoxLayout()
        self.add_sample_btn = QPushButton("📁 Add Voice Sample", left_box)
        self.add_sample_btn.setStyleSheet("background-color: #059669; color: white; font-weight: bold; padding: 8px;")
        self.add_sample_btn.clicked.connect(self._add_voice_sample)
        btn_row.addWidget(self.add_sample_btn)

        self.preview_btn = QPushButton("▶ Preview Sample", left_box)
        self.preview_btn.clicked.connect(self._preview_selected_sample)
        btn_row.addWidget(self.preview_btn)

        self.delete_sample_btn = QPushButton("🗑️ Remove", left_box)
        self.delete_sample_btn.setStyleSheet("background-color: #991B1B; color: white;")
        self.delete_sample_btn.clicked.connect(self._delete_selected_sample)
        btn_row.addWidget(self.delete_sample_btn)

        left_layout.addLayout(btn_row)

        # Acoustic Tone Calibration Badge
        self.tone_info_lbl = QLabel("Acoustic Tone: Cute Childish (~340Hz) | Clear Medium Speed", left_box)
        self.tone_info_lbl.setWordWrap(True)
        self.tone_info_lbl.setStyleSheet("color: #6EE7B7; font-size: 11px; padding: 4px;")
        left_layout.addWidget(self.tone_info_lbl)

        content_layout.addWidget(left_box, 1)

        # Right Column: Voice Test & Verification Panel
        right_box = QGroupBox("Voice Test & Tone Verification Panel", self)
        right_box.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold; color: #34D399;
                border: 1px solid #065F46; border-radius: 10px; margin-top: 10px; padding-top: 15px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        right_layout = QVBoxLayout(right_box)
        right_layout.setSpacing(12)

        right_layout.addWidget(QLabel("Enter test sentence to verify cute childish voice tone & legibility:", right_box))
        
        self.test_text_input = QLineEdit(right_box)
        self.test_text_input.setText("Edaa... njan vishakkunnu! Enikku vellam tharoo!")
        self.test_text_input.setStyleSheet("""
            QLineEdit {
                background-color: #022C22; border: 1px solid #10B981; border-radius: 6px;
                color: #FFFFFF; font-size: 14px; padding: 8px;
            }
        """)
        right_layout.addWidget(self.test_text_input)

        # Quick preset sentence chips
        chip_row = QHBoxLayout()
        chip1 = QPushButton("Malayalam Test", right_box)
        chip1.clicked.connect(lambda: self.test_text_input.setText("എടാ... എനിക്ക് വിശക്കുന്നു! വെള്ളം താ!"))
        chip_row.addWidget(chip1)

        chip2 = QPushButton("Manglish Test", right_box)
        chip2.clicked.connect(lambda: self.test_text_input.setText("Edaa... njan oru cactus alla ketto!"))
        chip_row.addWidget(chip2)

        chip3 = QPushButton("Cute Plant Test", right_box)
        chip3.clicked.connect(lambda: self.test_text_input.setText("Hello? Njan ivide oru plant aanu!"))
        chip_row.addWidget(chip3)
        right_layout.addLayout(chip_row)

        self.gen_voice_btn = QPushButton("✨ Generate & Synthesize Cute Childish Voice", right_box)
        self.gen_voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981; color: #064E3B; font-weight: bold;
                font-size: 14px; padding: 12px; border-radius: 8px;
            }
            QPushButton:hover { background-color: #34D399; }
        """)
        self.gen_voice_btn.clicked.connect(self._generate_and_test_voice)
        right_layout.addWidget(self.gen_voice_btn)

        self.play_result_btn = QPushButton("▶ Play Generated Audio", right_box)
        self.play_result_btn.setEnabled(False)
        self.play_result_btn.setStyleSheet("background-color: #047857; color: white; padding: 10px; border-radius: 6px;")
        self.play_result_btn.clicked.connect(self._play_generated_test)
        right_layout.addWidget(self.play_result_btn)

        self.test_status_lbl = QLabel("Status: Idle", right_box)
        self.test_status_lbl.setWordWrap(True)
        self.test_status_lbl.setStyleSheet("color: #6EE7B7; font-size: 12px;")
        right_layout.addWidget(self.test_status_lbl)

        right_layout.addStretch()
        content_layout.addWidget(right_box, 1)

        main_layout.addLayout(content_layout)

    def refresh_profiles(self):
        pdata = self.voice_engine.get_profiles()
        profiles = pdata.get("profiles", {})
        active = pdata.get("active_profile", "default")

        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for pname in profiles.keys():
            self.profile_combo.addItem(pname)

        idx = self.profile_combo.findText(active)
        if idx >= 0:
            self.profile_combo.setCurrentIndex(idx)
        self.profile_combo.blockSignals(False)

        self._load_samples_for_active_profile()

    def _on_profile_changed(self):
        active = self.profile_combo.currentText()
        if not active:
            return
        pdata = self.voice_engine.get_profiles()
        pdata["active_profile"] = active
        self.voice_engine.save_profiles(pdata)
        self.plant_state.active_voice_profile = active
        self.plant_state.save()
        self._load_samples_for_active_profile()

    def _on_style_changed(self):
        active = self.profile_combo.currentText()
        if not active:
            return
        style_text = self.style_combo.currentText()
        pdata = self.voice_engine.get_profiles()
        pinfo = pdata.setdefault("profiles", {}).setdefault(active, {})
        pinfo["style"] = style_text
        self.voice_engine.save_profiles(pdata)
        self._load_samples_for_active_profile()

    def _load_samples_for_active_profile(self):
        self.samples_list.clear()
        active = self.profile_combo.currentText()
        if not active:
            return

        profile_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "voices", active))
        os.makedirs(profile_dir, exist_ok=True)

        samples = []
        if os.path.exists(profile_dir):
            for f in os.listdir(profile_dir):
                if f.endswith((".wav", ".mp3", ".ogg", ".m4a")):
                    self.samples_list.addItem(f)
                    samples.append(f)

        tone = self.voice_engine.analyze_and_calibrate_tone(active)
        f0 = tone.get("pitch_hz", 340.0)
        self.tone_info_lbl.setText(f"Acoustic Calibrated Tone: ~{int(f0)}Hz Cute Childish Pitch | Clear Medium Speed | {len(samples)} sample(s)")

    def _create_new_profile(self):
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "New Profile", "Enter Voice Profile Name:")
        if ok and name.strip():
            pname = name.strip()
            pdir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "voices", pname))
            os.makedirs(pdir, exist_ok=True)

            pdata = self.voice_engine.get_profiles()
            pdata.setdefault("profiles", {})[pname] = {
                "name": pname,
                "language": "Malayalam / English",
                "style": "Cute & Childish",
                "samples": [],
                "pitch_hz": 340.0,
                "pitch_shift": 1.35,
                "speed_shift": 1.0
            }
            pdata["active_profile"] = pname
            self.voice_engine.save_profiles(pdata)
            self.refresh_profiles()

    def _add_voice_sample(self):
        active = self.profile_combo.currentText()
        if not active:
            QMessageBox.warning(self, "No Profile", "Please select or create a voice profile first.")
            return

        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Reference Audio Sample Files", "", "Audio Files (*.wav *.mp3 *.ogg *.m4a *.aac)"
        )
        if not file_paths:
            return

        profile_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "voices", active))
        os.makedirs(profile_dir, exist_ok=True)

        added_count = 0
        for src_path in file_paths:
            if not os.path.exists(src_path):
                continue
            fname = os.path.basename(src_path)
            dest_path = os.path.join(profile_dir, fname)

            converted = self.voice_engine.convert_audio_to_wav(src_path, dest_path)
            if converted:
                added_count += 1

        pdata = self.voice_engine.get_profiles()
        current_samples = [f for f in os.listdir(profile_dir) if f.endswith((".wav", ".mp3", ".ogg", ".m4a"))]
        pdata.setdefault("profiles", {}).setdefault(active, {})["samples"] = current_samples
        self.voice_engine.save_profiles(pdata)

        self._load_samples_for_active_profile()
        QMessageBox.information(self, "Samples Added", f"Successfully loaded and calibrated {added_count} reference voice sample(s) for '{active}'!")

    def _preview_selected_sample(self):
        item = self.samples_list.currentItem()
        if not item:
            QMessageBox.information(self, "Select Sample", "Please select a sample from the list to preview.")
            return
        active = self.profile_combo.currentText()
        sample_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "voices", active, item.text()))
        self.audio_manager.play_audio(sample_path)

    def _delete_selected_sample(self):
        item = self.samples_list.currentItem()
        if not item:
            return
        active = self.profile_combo.currentText()
        sample_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "voices", active, item.text()))
        if os.path.exists(sample_path):
            os.remove(sample_path)
            self._load_samples_for_active_profile()

    def _generate_and_test_voice(self):
        text = self.test_text_input.text().strip()
        if not text:
            return

        active = self.profile_combo.currentText()
        self.test_status_lbl.setText("Status: Synthesizing cute childish speech at clear medium speed...")
        self.gen_voice_btn.setEnabled(False)
        QApplication.processEvents()

        try:
            wav_path = self.voice_engine.generate_speech(text, profile_name=active)
            if wav_path and os.path.exists(wav_path):
                self.last_generated_wav = wav_path
                self.play_result_btn.setEnabled(True)
                self.test_status_lbl.setText(f"Status: Cute childish speech synthesized! Playback ready.")
                self._play_generated_test()
            else:
                self.test_status_lbl.setText("Status: Speech generation failed.")
        except Exception as e:
            self.test_status_lbl.setText(f"Status: Error - {e}")
        finally:
            self.gen_voice_btn.setEnabled(True)

    def _play_generated_test(self):
        if self.last_generated_wav and os.path.exists(self.last_generated_wav):
            self.audio_manager.play_audio(self.last_generated_wav)
