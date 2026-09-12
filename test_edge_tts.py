import asyncio
import edge_tts
import os

async def main():
    try:
        comm = edge_tts.Communicate("Hello", "en-US-AnaNeural", pitch="+75Hz")
        await comm.save("test.mp3")
        size = os.path.getsize("test.mp3") if os.path.exists("test.mp3") else 0
        print(f"Success with +75Hz, size: {size} bytes")
        if os.path.exists("test.mp3"):
            os.remove("test.mp3")
    except Exception as e:
        print(f"Error with +75Hz: {e}")

asyncio.run(main())
