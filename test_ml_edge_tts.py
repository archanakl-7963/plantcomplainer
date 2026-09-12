import asyncio
import edge_tts
import os

async def main():
    texts = [
        ("happy", "+75Hz", "ഹഹാ! ഹീഹീ! ആഹാ! എനിക്ക് വല്ലാത്ത സന്തോഷം ആയി! താങ്ക് യൂ!"),
        ("sad", "+40Hz", "എടാ... എനിക്ക് വെള്ളം തരണേ! ദാഹിച്ചിട്ട് വാടി ഉണങ്ങി പോകുന്നേ... അയ്യോ അയ്യോ!")
    ]
    for emotion, pitch, text in texts:
        print(f"Testing {emotion} with {pitch}")
        try:
            comm = edge_tts.Communicate(text, "ml-IN-SobhanaNeural", pitch=pitch, rate="+10%")
            out_file = f"test_{emotion}.mp3"
            await comm.save(out_file)
            size = os.path.getsize(out_file) if os.path.exists(out_file) else 0
            print(f"Success {emotion}, size: {size} bytes")
        except Exception as e:
            print(f"Error {emotion}: {e}")

asyncio.run(main())
