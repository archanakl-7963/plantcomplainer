import os
import sys
import hashlib
import wave
import subprocess
import numpy as np

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = None

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

CACHE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "audio_cache"))

class TTSManager:
    """
    Modular Malayalam TTS Subsystem.
    Provides standard interfaces:
    - speak(text)
    - stopSpeaking()
    - setVoice(voice_id)
    - setVolume(volume_level)
    Synthesizes Malayalam TTS with high-pitched Talking Tom cartoon audio filters.
    """
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        self.muted = False
        self.volume = 100
        self.voice_id = "default"
        self.pyttsx3_engine = None
        self._init_pyttsx3()

    def _init_pyttsx3(self):
        if HAS_PYTTSX3:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                self.pyttsx3_engine.setProperty('rate', 145)
            except Exception as e:
                print(f"[TTSManager] pyttsx3 init error: {e}")

    def setVoice(self, voice_id):
        self.voice_id = voice_id

    def setVolume(self, volume_level):
        self.volume = max(0, min(100, volume_level))

    def setMuted(self, is_muted):
        self.muted = is_muted
        if is_muted:
            self.stopSpeaking()

    def stopSpeaking(self):
        """Stops any currently playing audio."""
        if HAS_WINSOUND:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass

    def convert_to_wav(self, src_path, dest_wav):
        if FFMPEG_EXE and os.path.exists(FFMPEG_EXE):
            try:
                cmd = [FFMPEG_EXE, "-y", "-i", src_path, "-ar", "22050", "-ac", "1", dest_wav]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                return os.path.exists(dest_wav) and os.path.getsize(dest_wav) > 100
            except Exception:
                pass
        return False

    def synthesize(self, text, emotion="cute"):
        """Synthesizes Malayalam text to High-Pitched Talking Tom WAV audio."""
        clean_text = text.strip()
        if not clean_text:
            return None

        text_hash = hashlib.md5(f"v100_tom_{self.voice_id}_{emotion}_{clean_text}".encode("utf-8")).hexdigest()
        output_wav = os.path.join(CACHE_DIR, f"tom_v100_{text_hash}.wav")

        if os.path.exists(output_wav) and os.path.getsize(output_wav) > 1024:
            return output_wav

        raw_wav = os.path.join(CACHE_DIR, f"raw_{text_hash}.wav")
        synth_success = False

        # 1. Edge-TTS Synthesis
        if HAS_EDGE_TTS:
            try:
                import asyncio
                has_malayalam_unicode = any(ord(c) >= 0x0D00 and ord(c) <= 0x0D7F for c in clean_text)
                voice_model = "ml-IN-SobhanaNeural" if has_malayalam_unicode else "en-US-AnaNeural"

                async def _async_synth():
                    communicate = edge_tts.Communicate(clean_text, voice_model, pitch="+65Hz", rate="+2%")
                    temp_mp3 = os.path.join(CACHE_DIR, f"edge_{text_hash}.mp3")
                    await communicate.save(temp_mp3)
                    return temp_mp3

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                mp3_file = loop.run_until_complete(_async_synth())
                loop.close()

                if mp3_file and os.path.exists(mp3_file):
                    synth_success = self.convert_to_wav(mp3_file, raw_wav)
                    if os.path.exists(mp3_file):
                        os.remove(mp3_file)
            except Exception as e:
                print(f"[TTSManager] Edge-TTS synth error: {e}")

        # 2. Local pyttsx3 fallback
        if not synth_success and self.pyttsx3_engine:
            try:
                self.pyttsx3_engine.save_to_file(clean_text, raw_wav)
                self.pyttsx3_engine.runAndWait()
                synth_success = os.path.exists(raw_wav)
            except Exception as e:
                print(f"[TTSManager] pyttsx3 synth error: {e}")

        if not synth_success or not os.path.exists(raw_wav):
            return None

        # 3. High-Pitched Talking Tom Resynthesis via ffmpeg asetrate filter
        pitch_multiplier = 1.52
        if emotion in ["angry", "dramatic"]:
            pitch_multiplier = 1.62
        elif emotion in ["sad", "thirsty"]:
            pitch_multiplier = 1.45

        if FFMPEG_EXE and os.path.exists(FFMPEG_EXE):
            try:
                temp_tom = os.path.join(CACHE_DIR, f"temp_{text_hash}.wav")
                rate_val = int(22050 * pitch_multiplier)
                cmd = [
                    FFMPEG_EXE, "-y", "-i", raw_wav,
                    "-af", f"asetrate={rate_val},aresample=22050",
                    "-ar", "22050", "-ac", "1", temp_tom
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                if os.path.exists(temp_tom) and os.path.getsize(temp_tom) > 100:
                    if os.path.exists(output_wav):
                        os.remove(output_wav)
                    os.rename(temp_tom, output_wav)
                    if os.path.exists(raw_wav):
                        os.remove(raw_wav)
                    return output_wav
            except Exception as e:
                print(f"[TTSManager] Talking Tom pitch shift error: {e}")

        return raw_wav

    def speak(self, text, emotion="cute"):
        """Plays synthesized speech text."""
        if self.muted or self.volume == 0:
            return

        audio_wav = self.synthesize(text, emotion=emotion)
        if audio_wav and os.path.exists(audio_wav) and HAS_WINSOUND:
            try:
                self.stopSpeaking()
                winsound.PlaySound(audio_wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"[TTSManager] PlaySound error: {e}")
