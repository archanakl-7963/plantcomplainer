from PySide6.QtCore import QObject, QTimer

class DemoModeRunner(QObject):
    """
    Polished Automated Presentation / Hackathon Demo Runner.
    Executes a step-by-step interactive demo sequence showcasing
    dynamic activity detection, plant need changes, natural Malayalam speech synthesis, and care reactions.
    """
    def __init__(self, activity_detector, plant_state, complaint_engine, tts_manager, popup_widget, parent=None):
        super().__init__(parent)
        self.activity_detector = activity_detector
        self.plant_state = plant_state
        self.complaint_engine = complaint_engine
        self.tts_manager = tts_manager
        self.popup_widget = popup_widget
        self.step = 0

        self.demo_timer = QTimer(self)
        self.demo_timer.timeout.connect(self._next_step)

    def start_demo(self):
        self.step = 0
        self.demo_timer.start(3500) # 3.5 sec per step

    def stop_demo(self):
        self.demo_timer.stop()
        self.activity_detector.clear_manual_override()

    def _next_step(self):
        self.step += 1

        if self.step == 1:
            # 1. Healthy Plant
            self.plant_state.water_level = 80
            self.plant_state.sunlight_level = 80
            self.activity_detector.set_manual_override("coding")
            complaint = {"text": "അയ്യോ system start ചെയ്തല്ലോ… ഇന്ന് എന്നെ നോക്കുമോ എന്ന് നോക്കാം 😌🌱", "irritation": "happy", "context": "System"}
            self.popup_widget.show_complaint(complaint, context_name="System Start")
            self.tts_manager.speak(complaint["text"], emotion="happy")

        elif self.step == 2:
            # 2. User Gaming & Thirsty
            self.activity_detector.set_manual_override("game")
            self.plant_state.water_level = 10
            complaint = self.complaint_engine.select_complaint(self.plant_state, self.activity_detector, force=True)
            if complaint:
                self.popup_widget.show_complaint(complaint, context_name="Gaming Detected")
                self.tts_manager.speak(complaint["text"], emotion="dramatic")

        elif self.step == 3:
            # 3. User Waters Plant
            self.plant_state.water()
            reaction_text = "അഹാ! Finally! വെള്ളം കിട്ടി. ഇനി ഞാൻ നിങ്ങളെ കുറിച്ച് നല്ലത് പറയാം 😌🌱"
            complaint = {"text": reaction_text, "irritation": "happy", "context": "Watered"}
            self.popup_widget.show_complaint(complaint, context_name="Watered")
            self.tts_manager.speak(reaction_text, emotion="happy")

        elif self.step == 4:
            # 4. User Gives Sunlight
            self.plant_state.give_sunlight()
            reaction_text = "ഇതാണ് പറയുന്നത് ജീവിതത്തിൽ ചെറിയ കാര്യങ്ങൾ മതി സന്തോഷിക്കാൻ ☀️🌱"
            complaint = {"text": reaction_text, "irritation": "happy", "context": "Sunlight"}
            self.popup_widget.show_complaint(complaint, context_name="Sunlight")
            self.tts_manager.speak(reaction_text, emotion="happy")

        elif self.step == 5:
            # 5. YouTube Activity
            self.activity_detector.set_manual_override("youtube")
            complaint = self.complaint_engine.select_complaint(self.plant_state, self.activity_detector, force=True)
            if complaint:
                self.popup_widget.show_complaint(complaint, context_name="YouTube Activity")
                self.tts_manager.speak(complaint["text"], emotion="cute")

        elif self.step >= 6:
            self.stop_demo()
