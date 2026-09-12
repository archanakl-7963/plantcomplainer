import os
import sys
import hashlib
import json
import wave
import struct
import math
import shutil
import asyncio
import subprocess
import numpy as np

try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_EXE = None

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False

try:
    import pydub
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

VOICES_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "voices"))
CACHE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "audio_cache"))
PROFILES_FILE = os.path.join(VOICES_DIR, "profiles.json")

class VoiceEngine:
    """
    Emotional Voice Engine.
    Expresses distinct emotions (Angry, Sad with Crying Background, Happy with Smile, Cute)
    using Talking Tom cartoon resynthesis & procedural crying soundscape layering.
    """
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        os.makedirs(VOICES_DIR, exist_ok=True)
        self.tts_engine = None
        self._init_engine()
        self._ensure_crying_bg_sample()
        self._ensure_happy_giggle_sample()

    def _init_engine(self):
        if HAS_PYTTSX3:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty('rate', 145)
                self.tts_engine.setProperty('volume', 1.0)
                voices = self.tts_engine.getProperty('voices')
                for v in voices:
                    if "zira" in v.name.lower() or "female" in v.name.lower() or "child" in v.name.lower():
                        self.tts_engine.setProperty('voice', v.id)
                        break
            except Exception as e:
                print(f"[VoiceEngine] pyttsx3 init error: {e}")

    def _ensure_crying_bg_sample(self):
        """Generates procedural cute crying/sobbing background audio track."""
        crying_wav = os.path.join(CACHE_DIR, "crying_bg.wav")
        if not os.path.exists(crying_wav):
            try:
                framerate = 22050
                duration = 6.0
                n_samples = int(framerate * duration)
                t = np.linspace(0, duration, n_samples, False)

                # Crying sobbing pitch variation (weeping sine + tremolo)
                sobbing = 0.12 * np.sin(2 * np.pi * (320 + 45 * np.sin(2 * np.pi * 1.5 * t)) * t)
                # Sniffing pauses
                env = 0.5 + 0.5 * np.sin(2 * np.pi * 0.8 * t)
                crying_audio = (sobbing * env * 32767).astype(np.int16)

                with wave.open(crying_wav, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(framerate)
                    wf.writeframes(crying_audio.tobytes())
            except Exception as e:
                print(f"[VoiceEngine] Error creating crying bg track: {e}")

    def _ensure_happy_giggle_sample(self):
        """Generates procedural cute Talking Tom cartoon laugh/giggle audio track."""
        giggle_wav = os.path.join(CACHE_DIR, "happy_giggle.wav")
        if not os.path.exists(giggle_wav):
            try:
                framerate = 22050
                duration = 0.9
                n_samples = int(framerate * duration)
                t = np.linspace(0, duration, n_samples, False)

                # Cute childish chirp laughter (540Hz - 680Hz fast chirp pulses)
                chirp = np.sin(2 * np.pi * (560 + 100 * np.sin(2 * np.pi * 8.0 * t)) * t)
                env = (np.maximum(0, np.sin(2 * np.pi * 8.0 * t)) ** 2) * (1.0 - t/duration)
                giggle_audio = (chirp * env * 0.45 * 32767).astype(np.int16)

                with wave.open(giggle_wav, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(framerate)
                    wf.writeframes(giggle_audio.tobytes())
            except Exception as e:
                print(f"[VoiceEngine] Error creating happy giggle track: {e}")

    def get_status(self):
        if HAS_EDGE_TTS:
            return "Ready (Emotional Talking Tom Voice + Crying Audio Layer)", True
        elif HAS_PYTTSX3:
            return "Ready (Local Emotional Voice Engine)", True
        else:
            return "Not Installed", False

    def get_profiles(self):
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "active_profile": "default",
            "profiles": {
                "default": {
                    "name": "Cute Plant",
                    "language": "Malayalam / Manglish",
                    "style": "Talking Tom Emotional",
                    "samples": ["sample_01.wav"],
                    "pitch_hz": 380.0,
                    "pitch_shift": 1.48,
                    "speed_shift": 0.96
                }
            }
        }

    def save_profiles(self, data):
        try:
            with open(PROFILES_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[VoiceEngine] Save profiles error: {e}")

    def convert_audio_to_wav(self, src_path, dest_wav_path):
        """Converts ANY audio format (WAV, MP3, OGG, M4A, AAC) to 22050Hz 16-bit Mono WAV."""
        try:
            if os.path.abspath(src_path) == os.path.abspath(dest_wav_path):
                return True

            if FFMPEG_EXE and os.path.exists(FFMPEG_EXE):
                try:
                    cmd = [FFMPEG_EXE, "-y", "-i", src_path, "-ar", "22050", "-ac", "1", dest_wav_path]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                    if os.path.exists(dest_wav_path) and os.path.getsize(dest_wav_path) > 100:
                        return True
                except Exception as ff_err:
                    print(f"[VoiceEngine] ffmpeg convert error: {ff_err}")

            if HAS_SOUNDFILE:
                try:
                    data, samplerate = sf.read(src_path)
                    if len(data.shape) > 1:
                        data = np.mean(data, axis=1)
                    sf.write(dest_wav_path, data, 22050, subtype='PCM_16')
                    return True
                except Exception:
                    pass

            if HAS_PYDUB:
                try:
                    sound = pydub.AudioSegment.from_file(src_path)
                    sound = sound.set_frame_rate(22050).set_channels(1).set_sample_width(2)
                    sound.export(dest_wav_path, format="wav")
                    return True
                except Exception:
                    pass

            if src_path.lower().endswith(".wav"):
                shutil.copy(src_path, dest_wav_path)
                return True

            return False
        except Exception as e:
            print(f"[VoiceEngine] Audio conversion failed for {src_path}: {e}")
            return False

    def analyze_and_calibrate_tone(self, profile_name):
        """
        Analyzes uploaded user voice sample files in the profile directory.
        Calibrates fundamental pitch (F0) to Talking Tom cartoon pitch spectrum (~380Hz).
        """
        profile_dir = os.path.normpath(os.path.join(VOICES_DIR, profile_name))
        if not os.path.exists(profile_dir):
            return {"pitch_hz": 380.0, "ref_samples": [], "timbre": "talking tom cute cartoon"}

        samples = [f for f in os.listdir(profile_dir) if f.endswith((".wav", ".mp3", ".ogg", ".m4a", ".aac"))]
        if not samples:
            return {"pitch_hz": 380.0, "ref_samples": [], "timbre": "talking tom cute cartoon"}

        all_pitches = []
        valid_wav_samples = []

        for fname in samples:
            spath = os.path.join(profile_dir, fname)
            try:
                if not spath.endswith(".wav"):
                    temp_conv = os.path.join(CACHE_DIR, f"conv_{fname}.wav")
                    if self.convert_audio_to_wav(spath, temp_conv):
                        spath = temp_conv

                if os.path.exists(spath) and spath.endswith(".wav"):
                    valid_wav_samples.append(spath)
                    with wave.open(spath, 'rb') as wf:
                        framerate = wf.getframerate()
                        nframes = wf.getnframes()
                        raw = wf.readframes(nframes)
                        samples_data = np.frombuffer(raw, dtype=np.int16).astype(np.float32)

                        if len(samples_data) > 1000:
                            corr = np.correlate(samples_data[:4000], samples_data[:4000], mode='full')
                            corr = corr[len(corr)//2:]
                            min_lag = int(framerate / 550)
                            max_lag = int(framerate / 80)
                            if max_lag < len(corr):
                                peak_lag = min_lag + np.argmax(corr[min_lag:max_lag])
                                f0 = framerate / float(peak_lag)
                                if 80 <= f0 <= 550:
                                    all_pitches.append(f0)
            except Exception as e:
                print(f"[VoiceEngine] Sample pitch error: {e}")

        measured_f0 = float(np.mean(all_pitches)) if all_pitches else 280.0
        target_f0 = max(360.0, min(440.0, measured_f0 * 1.35))
        pitch_shift_ratio = target_f0 / 160.0

        tone_result = {
            "pitch_hz": target_f0,
            "measured_f0": measured_f0,
            "pitch_shift": pitch_shift_ratio,
            "ref_samples": valid_wav_samples,
            "timbre": "talking tom cute cartoon"
        }

        pdata = self.get_profiles()
        pinfo = pdata.setdefault("profiles", {}).setdefault(profile_name, {})
        pinfo["pitch_hz"] = target_f0
        pinfo["pitch_shift"] = pitch_shift_ratio
        pinfo["timbre"] = "talking tom cute cartoon"
        self.save_profiles(pdata)

        return tone_result

    def generate_speech(self, text, profile_name="default", emotion="cute"):
        """
        Generates NEW speech audio with emotional expression (Angry, Sad + Crying BG, Happy, Cute).
        Returns absolute path to synthesized WAV file.
        """
        clean_text = text.strip()
        if not clean_text:
            return None

        text_hash = hashlib.md5(f"{profile_name}_{emotion}_v99_high_talking_tom_{clean_text}".encode("utf-8")).hexdigest()
        output_wav = os.path.join(CACHE_DIR, f"tom_v99_{text_hash}.wav")

        if os.path.exists(output_wav):
            if os.path.getsize(output_wav) > 1024:
                return output_wav
            else:
                try:
                    os.remove(output_wav)
                except Exception:
                    pass

        raw_synth_wav = os.path.join(CACHE_DIR, f"raw_{text_hash}.wav")
        synth_success = False

        # Configure pitch & rate based on emotion (Talking Tom cute cartoon voice)
        emotion_str = emotion.lower() if emotion else "cute"
        if emotion_str in ["song", "happy_song"]:
            pitch_str = "+90Hz"   # High musical singing pitch
            rate_str = "+0%"     # Musical singing tempo
        elif emotion_str in ["angry"]:
            pitch_str = "+95Hz"   # High screeching furious Talking Tom pitch
            rate_str = "+15%"    # Fast tantrum speed
        elif emotion_str in ["sad", "drama_queen", "thirsty"]:
            pitch_str = "+40Hz"   # Soft weeping high Talking Tom pitch
            rate_str = "-8%"     # Slow tearful weeping rate
        elif emotion_str in ["happy"]:
            pitch_str = "+75Hz"   # Upbeat joyful high Talking Tom pitch
            rate_str = "+10%"    # Upbeat cheerful rate
        else: # cute / annoyed
            pitch_str = "+65Hz"   # Classic cute childish Talking Tom pitch
            rate_str = "+2%"

        if HAS_EDGE_TTS:
            try:
                has_malayalam_unicode = any(ord(c) >= 0x0D00 and ord(c) <= 0x0D7F for c in clean_text)
                voice_model = "ml-IN-SobhanaNeural" if has_malayalam_unicode else "en-US-AnaNeural"

                async def _async_synth():
                    communicate = edge_tts.Communicate(clean_text, voice_model, pitch=pitch_str, rate=rate_str)
                    temp_mp3 = os.path.join(CACHE_DIR, f"edge_{text_hash}.mp3")
                    await communicate.save(temp_mp3)
                    return temp_mp3

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                mp3_file = loop.run_until_complete(_async_synth())
                loop.close()

                if mp3_file and os.path.exists(mp3_file):
                    synth_success = self.convert_audio_to_wav(mp3_file, raw_synth_wav)
                    if os.path.exists(mp3_file):
                        os.remove(mp3_file)
            except Exception as e:
                print(f"[VoiceEngine] Edge-TTS synth error: {e}")
                synth_success = False

        if not synth_success and HAS_PYTTSX3 and self.tts_engine:
            try:
                self.tts_engine.setProperty('rate', 145)
                self.tts_engine.save_to_file(clean_text, raw_synth_wav)
                self.tts_engine.runAndWait()
                synth_success = os.path.exists(raw_synth_wav)
            except Exception as e:
                print(f"[VoiceEngine] pyttsx3 synth error: {e}")

        if not synth_success or not os.path.exists(raw_synth_wav):
            raw_synth_wav = self._generate_procedural_fallback(clean_text, raw_synth_wav)

        # Apply Emotional Talking Tom Vocoder Resynthesis & Crying/Laughing Audio Layer
        try:
            self._apply_emotional_resynthesis(raw_synth_wav, output_wav, emotion=emotion_str)
            if os.path.exists(raw_synth_wav):
                os.remove(raw_synth_wav)
            return output_wav
        except Exception as e:
            print(f"[VoiceEngine] Emotional resynthesis error: {e}")
            if os.path.exists(raw_synth_wav):
                return raw_synth_wav
            return None

    def _apply_emotional_resynthesis(self, input_wav, output_wav, emotion="cute"):
        """
        Applies authentic high-pitched Talking Tom cartoon voice effect.
        """
        pitch_multiplier = 1.52
        if emotion in ["song", "happy_song"]:
            pitch_multiplier = 1.58
        elif emotion in ["angry"]:
            pitch_multiplier = 1.62
        elif emotion in ["sad", "drama_queen", "thirsty"]:
            pitch_multiplier = 1.45
        elif emotion in ["happy"]:
            pitch_multiplier = 1.55

        if FFMPEG_EXE and os.path.exists(FFMPEG_EXE):
            try:
                temp_tom = os.path.join(CACHE_DIR, f"tom_{os.path.basename(output_wav)}")
                rate_val = int(22050 * pitch_multiplier)
                
                # Apply studio vocal vibrato + equalizer + chorus echo tuning for songs
                if emotion in ["song", "happy_song"]:
                    filter_str = f"asetrate={rate_val},aresample=22050,vibrato=f=5.8:d=0.36,equalizer=f=3000:t=q:w=1.2:g=4,aecho=0.8:0.85:40:0.25"
                else:
                    filter_str = f"asetrate={rate_val},aresample=22050"


                cmd = [
                    FFMPEG_EXE, "-y", "-i", input_wav,
                    "-af", filter_str,
                    "-ar", "22050", "-ac", "1", temp_tom
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                if os.path.exists(temp_tom) and os.path.getsize(temp_tom) > 100:
                    input_wav = temp_tom
            except Exception as ff_err:
                print(f"[VoiceEngine] ffmpeg Talking Tom pitch shift error: {ff_err}")


        with wave.open(input_wav, 'rb') as in_wf:
            n_channels = in_wf.getnchannels()
            sampwidth = in_wf.getsampwidth()
            framerate = in_wf.getframerate()
            n_frames = in_wf.getnframes()
            audio_raw = in_wf.readframes(n_frames)

        samples = np.frombuffer(audio_raw, dtype=np.int16).astype(np.float32)

        if len(samples) == 0:
            shutil.copy(input_wav, output_wav)
            return

        m_samples = samples
        filter_kernel = np.array([-0.08, 1.16, -0.08])
        m_samples = np.convolve(m_samples, filter_kernel, mode='same')

        # 1. HAPPY EMOTION: Prepend Cute Cartoon Giggle Laughter Track
        if emotion in ["happy"]:
            giggle_file = os.path.join(CACHE_DIR, "happy_giggle.wav")
            if os.path.exists(giggle_file):
                try:
                    with wave.open(giggle_file, 'rb') as g_wf:
                        g_raw = g_wf.readframes(g_wf.getnframes())
                        g_samples = np.frombuffer(g_raw, dtype=np.int16).astype(np.float32)

                    if len(g_samples) > 0:
                        m_samples = np.concatenate([g_samples * 0.75, m_samples])
                except Exception as g_err:
                    print(f"[VoiceEngine] Giggle audio mix error: {g_err}")

        # 2. SAD / THIRSTY EMOTION: Layer Crying Soundscape Audio
        elif emotion in ["sad", "drama_queen", "thirsty"]:
            crying_bg_file = os.path.join(CACHE_DIR, "crying_bg.wav")
            if os.path.exists(crying_bg_file):
                try:
                    with wave.open(crying_bg_file, 'rb') as cry_wf:
                        cry_raw = cry_wf.readframes(min(len(m_samples), cry_wf.getnframes()))
                        cry_samples = np.frombuffer(cry_raw, dtype=np.int16).astype(np.float32)

                    if len(cry_samples) > 0:
                        min_len = min(len(m_samples), len(cry_samples))
                        # Mix 80% speech dialogue + 22% crying background soundscape
                        m_samples[:min_len] = m_samples[:min_len] * 0.80 + cry_samples[:min_len] * 0.22
                except Exception as cry_err:
                    print(f"[VoiceEngine] Crying audio mix error: {cry_err}")

        # Peak normalization
        max_val = np.max(np.abs(m_samples))
        if max_val > 0:
            m_samples = (m_samples / max_val) * 28500.0

        m_int16 = np.clip(m_samples, -32768, 32767).astype(np.int16)

        with wave.open(output_wav, 'wb') as out_wf:
            out_wf.setnchannels(n_channels)
            out_wf.setsampwidth(sampwidth)
            out_wf.setframerate(framerate)
            out_wf.writeframes(m_int16.tobytes())

    def _generate_procedural_fallback(self, text, output_wav):
        framerate = 22050
        duration = max(1.5, len(text) * 0.07)
        n_samples = int(framerate * duration)
        t = np.linspace(0, duration, n_samples, False)

        freq = 360.0 + 45.0 * np.sin(2 * np.pi * 3.2 * t)
        audio = 0.35 * np.sin(2 * np.pi * freq * t)
        audio_int16 = (audio * 32767).astype(np.int16)

        with wave.open(output_wav, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(framerate)
            wf.writeframes(audio_int16.tobytes())

        return output_wav
