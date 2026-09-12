from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QListWidget, QLineEdit, QComboBox, QTextEdit, QSpinBox,
    QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt

class DatasetEditorWidget(QWidget):
    def __init__(self, complaint_engine, voice_engine, audio_manager, plant_state, parent=None):
        super().__init__(parent)
        self.complaint_engine = complaint_engine
        self.voice_engine = voice_engine
        self.audio_manager = audio_manager
        self.plant_state = plant_state
        self.current_complaint_id = None

        self._build_ui()
        self.refresh_list()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_lbl = QLabel("📝 Complaint Dataset Editor (Malayalam & English)", self)
        title_lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #10B981;")
        main_layout.addWidget(title_lbl)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Left Column: Complaint List
        left_box = QGroupBox("Existing Malayalam Complaints", self)
        left_box.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold; color: #34D399;
                border: 1px solid #065F46; border-radius: 10px; margin-top: 10px; padding-top: 15px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        left_layout = QVBoxLayout(left_box)

        self.complaints_list = QListWidget(left_box)
        self.complaints_list.setStyleSheet("""
            QListWidget {
                background-color: #064E3B; border: 1px solid #047857;
                border-radius: 8px; color: #ECFDF5; font-size: 13px; padding: 5px;
            }
            QListWidget::item:selected { background-color: #10B981; color: #064E3B; font-weight: bold; }
        """)
        self.complaints_list.currentRowChanged.connect(self._on_complaint_selected)
        left_layout.addWidget(self.complaints_list)

        new_btn = QPushButton("+ Add New Malayalam Complaint", left_box)
        new_btn.setStyleSheet("background-color: #059669; color: white; font-weight: bold; padding: 8px;")
        new_btn.clicked.connect(self._new_complaint)
        left_layout.addWidget(new_btn)

        content_layout.addWidget(left_box, 1)

        # Right Column: Edit Form
        right_box = QGroupBox("Edit Complaint Details", self)
        right_box.setStyleSheet("""
            QGroupBox {
                font-size: 14px; font-weight: bold; color: #34D399;
                border: 1px solid #065F46; border-radius: 10px; margin-top: 10px; padding-top: 15px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
            QLabel { color: #D1D5DB; font-size: 12px; font-weight: bold; }
        """)
        form_layout = QVBoxLayout(right_box)
        form_layout.setSpacing(10)

        # ID Row
        id_row = QHBoxLayout()
        id_row.addWidget(QLabel("Complaint ID:", right_box))
        self.id_input = QLineEdit(right_box)
        self.id_input.setStyleSheet("background: #022C22; color: white; border: 1px solid #059669; padding: 5px;")
        id_row.addWidget(self.id_input)
        form_layout.addLayout(id_row)

        # Condition Row
        cond_row = QHBoxLayout()
        cond_row.addWidget(QLabel("Condition:", right_box))
        self.cond_combo = QComboBox(right_box)
        self.cond_combo.addItems([
            "thirsty", "sunlight", "ignored", "coding", "youtube",
            "too_much_water", "poke", "happy", "angry", "any", "random"
        ])
        cond_row.addWidget(self.cond_combo)

        cond_row.addWidget(QLabel("Context:", right_box))
        self.context_combo = QComboBox(right_box)
        self.context_combo.addItems([
            "any", "coding", "youtube", "browser", "presentation",
            "document", "idle", "game", "other"
        ])
        cond_row.addWidget(self.context_combo)
        form_layout.addLayout(cond_row)

        # Irritation & Priority Row
        irr_row = QHBoxLayout()
        irr_row.addWidget(QLabel("Irritation Level:", right_box))
        self.irr_combo = QComboBox(right_box)
        self.irr_combo.addItems(["cute", "annoyed", "angry", "drama_queen"])
        irr_row.addWidget(self.irr_combo)

        irr_row.addWidget(QLabel("Priority (1-10):", right_box))
        self.priority_spin = QSpinBox(right_box)
        self.priority_spin.setRange(1, 10)
        self.priority_spin.setValue(5)
        irr_row.addWidget(self.priority_spin)

        irr_row.addWidget(QLabel("Cooldown (sec):", right_box))
        self.cooldown_spin = QSpinBox(right_box)
        self.cooldown_spin.setRange(5, 600)
        self.cooldown_spin.setValue(45)
        irr_row.addWidget(self.cooldown_spin)

        form_layout.addLayout(irr_row)

        # Complaint Text Area
        form_layout.addWidget(QLabel("Complaint Text (Malayalam Unicode / English):", right_box))
        self.text_input = QTextEdit(right_box)
        self.text_input.setPlaceholderText("Enter Malayalam complaint text here (e.g. എടാ... എനിക്ക് വെള്ളം വേണം!)...")
        self.text_input.setStyleSheet("""
            QTextEdit {
                background-color: #022C22; border: 1px solid #10B981;
                border-radius: 6px; color: #FFFFFF; font-size: 14px; padding: 8px;
            }
        """)
        form_layout.addWidget(self.text_input)

        # Translate Row
        trans_row = QHBoxLayout()
        self.translate_btn = QPushButton("🌐 Translate English to Malayalam", right_box)
        self.translate_btn.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold; padding: 6px;")
        self.translate_btn.clicked.connect(self._translate_english_to_malayalam)
        trans_row.addWidget(self.translate_btn)
        form_layout.addLayout(trans_row)

        # Form Buttons Row
        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("💾 Save Complaint", right_box)
        self.save_btn.setStyleSheet("background-color: #10B981; color: #064E3B; font-weight: bold; padding: 10px;")
        self.save_btn.clicked.connect(self._save_complaint)
        btn_row.addWidget(self.save_btn)

        self.test_btn = QPushButton("🔊 Test Voice", right_box)
        self.test_btn.setStyleSheet("background-color: #047857; color: white; padding: 10px;")
        self.test_btn.clicked.connect(self._test_voice)
        btn_row.addWidget(self.test_btn)

        self.delete_btn = QPushButton("🗑️ Delete", right_box)
        self.delete_btn.setStyleSheet("background-color: #991B1B; color: white; padding: 10px;")
        self.delete_btn.clicked.connect(self._delete_complaint)
        btn_row.addWidget(self.delete_btn)

        form_layout.addLayout(btn_row)
        content_layout.addWidget(right_box, 1)

        main_layout.addLayout(content_layout)

    def refresh_list(self):
        self.complaint_engine.load_dataset()
        self.complaints_list.clear()
        for c in self.complaint_engine.complaints:
            cid = c.get("id", "")
            txt = c.get("text", "")
            cond = c.get("condition", "any")
            self.complaints_list.addItem(f"[{cond}] {cid}: {txt[:28]}")

    def _on_complaint_selected(self, row):
        if row < 0 or row >= len(self.complaint_engine.complaints):
            return
        c = self.complaint_engine.complaints[row]
        self.current_complaint_id = c.get("id")
        self.id_input.setText(c.get("id", ""))
        
        idx = self.cond_combo.findText(c.get("condition", "any"))
        if idx >= 0: self.cond_combo.setCurrentIndex(idx)
        
        idx = self.context_combo.findText(c.get("context", "any"))
        if idx >= 0: self.context_combo.setCurrentIndex(idx)

        idx = self.irr_combo.findText(c.get("irritation", "cute"))
        if idx >= 0: self.irr_combo.setCurrentIndex(idx)

        self.priority_spin.setValue(c.get("priority", 5))
        self.cooldown_spin.setValue(c.get("cooldown", 45))
        self.text_input.setText(c.get("text", ""))

    def _new_complaint(self):
        self.current_complaint_id = f"complaint_{len(self.complaint_engine.complaints)+1:03d}"
        self.id_input.setText(self.current_complaint_id)
        self.cond_combo.setCurrentIndex(0)
        self.context_combo.setCurrentIndex(0)
        self.irr_combo.setCurrentIndex(0)
        self.priority_spin.setValue(5)
        self.cooldown_spin.setValue(45)
        self.text_input.clear()

    def _translate_english_to_malayalam(self):
        txt = self.text_input.toPlainText().strip()
        if not txt:
            return

        # Built-in English to Malayalam Dictionary Map
        translation_map = {
            "i need water": "എനിക്ക് വെള്ളം വേണം!",
            "give me water": "എനിക്ക് കുറച്ചു വെള്ളം തരൂ!",
            "i am thirsty": "എനിക്ക് നല്ല ദാഹം എടുക്കുന്നു!",
            "i need sunlight": "എനിക്ക് കുറച്ചു വെയിൽ തരൂ!",
            "stop coding": "കോഡ് ചെയ്തത് മതി... എന്നെ ശ്രദ്ധിക്കൂ!",
            "are you coding again": "വീണ്ടും കോഡിംഗ് ആണോ? എന്നെ നോക്കാൻ സമയം ഇല്ലേ?",
            "don't watch video": "വീഡിയോ കണ്ടുകൊണ്ടിരിക്കല്ലേ... ഞാനും ഇവിടെ ഉണ്ടേ!",
            "hello": "ഹലോ... ഞാൻ ഇവിടെ ഉണ്ടേ!",
            "stop ignoring me": "എന്നെ ഇഗ്നോർ ചെയ്യല്ലേ!",
            "i am hungry": "എനിക്ക് വിശക്കുന്നു!",
            "don't touch me": "എന്നെ തൊടല്ലേ!",
            "too much water": "മതി വെള്ളം! ഞാൻ മീൻ അല്ല!",
            "thank you": "താങ്ക് യൂ താങ്ക് യൂ!"
        }

        txt_lower = txt.lower()
        translated = translation_map.get(txt_lower)

        if not translated:
            # Keyphrase matching
            if "water" in txt_lower:
                translated = "എനിക്ക് കുറച്ചു വെള്ളം വേണം!"
            elif "sun" in txt_lower or "light" in txt_lower:
                translated = "എനിക്ക് കുറച്ചു വെളിച്ചം തരൂ!"
            elif "code" in txt_lower or "coding" in txt_lower:
                translated = "കമ്പ്യൂട്ടറിൽ കോഡ് അടിച്ചു കൊണ്ടിരുന്നാൽ എനിക്ക് വെള്ളം കിട്ടുമോ?"
            elif "video" in txt_lower or "youtube" in txt_lower:
                translated = "വീഡിയോ കണ്ടുകൊണ്ടിരിക്കല്ലേ... എന്നെ നോക്കൂ!"
            elif "touch" in txt_lower or "poke" in txt_lower:
                translated = "എയ്യ്! എന്നെ തൊടല്ലേ!"
            else:
                translated = f"എടാ... {txt}!"

        self.text_input.setText(translated)
        QMessageBox.information(self, "Translated", f"Translated to Malayalam: {translated}")

    def _save_complaint(self):
        cid = self.id_input.text().strip()
        txt = self.text_input.toPlainText().strip()
        if not cid or not txt:
            QMessageBox.warning(self, "Validation Error", "ID and Text cannot be empty.")
            return

        item_data = {
            "id": cid,
            "condition": self.cond_combo.currentText(),
            "context": self.context_combo.currentText(),
            "irritation": self.irr_combo.currentText(),
            "priority": self.priority_spin.value(),
            "text": txt,
            "cooldown": self.cooldown_spin.value()
        }

        updated = False
        for i, c in enumerate(self.complaint_engine.complaints):
            if c.get("id") == cid:
                self.complaint_engine.complaints[i] = item_data
                updated = True
                break

        if not updated:
            self.complaint_engine.complaints.append(item_data)

        self.complaint_engine.save_dataset()
        self.refresh_list()
        QMessageBox.information(self, "Saved", f"Saved Malayalam complaint '{cid}' to dataset!")

    def _delete_complaint(self):
        cid = self.id_input.text().strip()
        if not cid:
            return
        self.complaint_engine.complaints = [c for c in self.complaint_engine.complaints if c.get("id") != cid]
        self.complaint_engine.save_dataset()
        self.refresh_list()
        self._new_complaint()

    def _test_voice(self):
        txt = self.text_input.toPlainText().strip()
        if not txt:
            return
        active_prof = self.plant_state.active_voice_profile
        wav_path = self.voice_engine.generate_speech(txt, profile_name=active_prof)
        if wav_path:
            self.audio_manager.play_audio(wav_path)
