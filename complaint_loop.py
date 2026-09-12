import os
import time
from PySide6.QtCore import QObject, QTimer

CACHE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "audio_cache"))

class ComplaintLoop(QObject):
    def __init__(self, plant_state, complaint_engine, context_detector, voice_engine, audio_manager, popup_widget, tray=None, parent=None):
        super().__init__(parent)
        self.plant_state = plant_state
        self.complaint_engine = complaint_engine
        self.context_detector = context_detector
        self.voice_engine = voice_engine
        self.audio_manager = audio_manager
        self.popup_widget = popup_widget
        self.tray = tray
        self.audio_index = 0
        
        self.sim_timer = QTimer(self)
        self.sim_timer.timeout.connect(self._on_tick)
        self.sim_timer.start(15000) # Every 15 seconds
        
        # Trigger immediately on startup
        QTimer.singleShot(1000, self._trigger)
        
    def _on_tick(self):
        self.plant_state.update_decay(seconds_elapsed=15.0)
        self._trigger()

    def _get_audio_cache_files(self):
        """Scans audio_cache for valid audio files (>1KB). Excludes procedural bg tracks."""
        if not os.path.exists(CACHE_DIR):
            return []
        
        valid_exts = (".wav", ".mp3", ".mpeg", ".m4a", ".ogg", ".flac", ".aac")
        bg_files = {"crying_bg.wav", "happy_giggle.wav"}
        
        audio_files = []
        for fname in os.listdir(CACHE_DIR):
            if fname in bg_files:
                continue
            if fname.startswith("temp_conv_") or fname.startswith("raw_"):
                continue
            
            fpath = os.path.join(CACHE_DIR, fname)
            if os.path.isfile(fpath) and fname.lower().endswith(valid_exts):
                try:
                    if os.path.getsize(fpath) > 1024:
                        audio_files.append(fpath)
                except Exception:
                    pass
                    
        # Sort files to ensure deterministic one-by-one playback
        audio_files.sort()
        return audio_files
        
    def _trigger(self):
        try:
            if self.tray and not self.tray.is_active:
                return
                
            active_context = "other"
            if self.plant_state.enable_context_detection:
                active_context, _ = self.context_detector.detect_context()
                
            complaint = self.complaint_engine.select_complaint(self.plant_state, active_context)
            if not complaint:
                complaint = {"text": "YouTube and all, you need to care about me!", "irritation": "cute"}
                
            text = complaint.get("text", "")
            irr = complaint.get("irritation", "cute")
            
            self.plant_state.last_complaint_time = time.time()
            self.plant_state.save()
            
            profile_name = self.plant_state.active_voice_profile
            audio_path = None
            if self.plant_state.enable_voice and text:
                try:
                    audio_path = self.voice_engine.generate_speech(text, profile_name=profile_name, emotion=irr)
                except Exception as ve_err:
                    print(f"[ComplaintLoop] Voice synth error: {ve_err}")
                
            self.popup_widget.show_complaint(complaint, audio_path=audio_path, context_name=active_context.capitalize())
        except Exception as err:
            print(f"[ComplaintLoop] Error in _trigger: {err}")

    def sing_song(self):
        try:
            songs = [
                {"id": "song_001", "text": "ഒന്നാം പക്കം... ബൗ~ ബൗ~... രണ്ടാം പക്കം... ബൗ~... മൂന്നാം പക്കം... ബൗ~ ബൗ~ ബൗ~! 🐶🎵🌱", "irritation": "song"},
                {"id": "song_002", "text": "പാടം പൂത്ത~ കാലം... പാടാൻ വന്നു~ നീയും~! 🌾🎶🌸", "irritation": "song"},
                {"id": "song_003", "text": "പ്രേമമെന്നാൽ എന്താണ് പെണ്ണേ~... അത് കരളിനുള്ളില്ലേ~ തീയാണ് കണ്ണേ~! 🔥❤️🎵", "irritation": "song"},
                {"id": "song_004", "text": "കിളിയേ~ കിളിയേ~ നാളെ വരാം... എനിക്ക് വെള്ളം തന്നാൽ ഇനിയും പാടാം~! 🎵🌱", "irritation": "song"},
                {"id": "song_005", "text": "കുട്ടാ കുട്ടാ മാടത്തക്കുട്ടാ~... ഞാനൊരു പാവം സുന്ദരി ചെടിയല്ലേ മോളേ~! 🎶✨", "irritation": "song"},
                {"id": "song_006", "text": "ജിമിക്കി കമ്മൽ പോലെ ഞാനും ആടുന്നുണ്ട്~... കുറച്ച് വെയിൽ കിട്ടിയാൽ പൊളിക്കും~! 💃✨🎶", "irritation": "song"}
            ]


            import random
            complaint = random.choice(songs)
            text = complaint.get("text", "")
            irr = complaint.get("irritation", "happy")

            profile_name = getattr(self.plant_state, 'active_voice_profile', 'default')
            audio_path = None
            if self.plant_state.enable_voice and text:
                try:
                    audio_path = self.voice_engine.generate_speech(text, profile_name=profile_name, emotion="song")
                except Exception as ve_err:
                    print(f"[ComplaintLoop] Voice synth error: {ve_err}")

                
            self.popup_widget.show_complaint(complaint, audio_path=audio_path, context_name="Music")
        except Exception as err:
            print(f"[ComplaintLoop] Error in sing_song: {err}")

