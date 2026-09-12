import os
import sys
from PySide6.QtCore import QObject, QTimer, QUrl

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

try:
    from PySide6.QtMultimedia import QSoundEffect
    HAS_QSOUND = True
except ImportError:
    HAS_QSOUND = False

class AudioManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.muted = False
        self._current_callback = None
        if HAS_QSOUND:
            self.effect = QSoundEffect(self)
            self.effect.playingChanged.connect(self._on_playing_changed)
        else:
            self.effect = None

    def stop_audio(self):
        """Stops any currently playing audio."""
        if HAS_WINSOUND:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass
        if self.effect and self.effect.isPlaying():
            self.effect.stop()

    def play_audio(self, wav_path, callback=None):
        if not wav_path or not os.path.exists(wav_path):
            print(f"[AudioManager] Missing audio file: {wav_path}")
            if callback:
                callback()
            return

        if self.muted:
            print("[AudioManager] Muted, skipping audio play.")
            if callback:
                callback()
            return

        self.stop_audio()
        self._current_callback = callback

        played_success = False

        # 1. Primary method on Windows: winsound
        if HAS_WINSOUND and wav_path.lower().endswith(".wav"):
            try:
                winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                played_success = True
                print(f"[AudioManager] Playing via winsound: {os.path.basename(wav_path)}")
            except Exception as e:
                print(f"[AudioManager] winsound error: {e}")

        # 2. Fallback: QSoundEffect
        if not played_success and self.effect:
            try:
                url = QUrl.fromLocalFile(wav_path)
                self.effect.setSource(url)
                self.effect.setVolume(1.0)
                QTimer.singleShot(100, lambda: self.effect.play())
                played_success = True
            except Exception as e:
                print(f"[AudioManager] QSoundEffect error: {e}")

        if not played_success and callback:
            callback()

    def _on_playing_changed(self):
        if self.effect and not self.effect.isPlaying():
            if self._current_callback:
                cb = self._current_callback
                self._current_callback = None
                try:
                    cb()
                except Exception as e:
                    print(f"[AudioManager] Callback error: {e}")

    def set_muted(self, muted_bool):
        self.muted = muted_bool
        if muted_bool:
            self.stop_audio()
