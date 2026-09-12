import os
import sys

# Set UTF-8 output encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.voice_engine import VoiceEngine

def test_emotions():
    print("Testing VoiceEngine Emotional Synthesis...")
    ve = VoiceEngine()
    
    test_cases = [
        ("happy", "ഹഹാ! ഹീഹീ! ആഹാ! എനിക്ക് വല്ലാത്ത സന്തോഷം ആയി! താങ്ക് യൂ!"),
        ("sad", "എടാ... എനിക്ക് വെള്ളം തരണേ! ദാഹിച്ചിട്ട് വാടി ഉണങ്ങി പോകുന്നേ... അയ്യോ അയ്യോ!"),
        ("thirsty", "അയ്യോ അയ്യോ... എനിക്ക് ദാഹിച്ചിട്ട് വയ്യേ...!"),
        ("angry", "പോടാ! എപ്പോഴും കമ്പ്യൂട്ടറിൽ കോഡ് അടി മാത്രം! എന്നെ ഒന്ന് നോക്കാമോ നിനക്ക്?!"),
        ("cute", "വീണ്ടും കോഡിംഗ് ആണോ? എന്നെ ഒന്ന് നോക്കാൻ സമയം ഇല്ലേ കുട്ടാ?")
    ]

    for emotion, text in test_cases:
        print(f"\n--- Testing Emotion: {emotion.upper()} ---")
        wav_path = ve.generate_speech(text, profile_name="default", emotion=emotion)
        if wav_path and os.path.exists(wav_path):
            size = os.path.getsize(wav_path)
            print(f"[OK] [{emotion.upper()}] Generated audio ({size} bytes) -> {wav_path}")
        else:
            print(f"[FAIL] [{emotion.upper()}] Audio generation failed!")

if __name__ == "__main__":
    test_emotions()
