import sys
import time

from app.ai.stt import load_stt_model, transcribe

start = time.time()
model = load_stt_model()
if model is None:
    raise SystemExit("The model failed to load (see the error above)")
print(f"model loaded in {time.time() - start:.1f}s")

if len(sys.argv) > 1:
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    start = time.time()
    print("text:", repr(transcribe(model, data)))
    print(f"transcribed in {time.time() - start:.1f}s")

# RUN: python -m scripts.try_stt
# The first run downloads the small model

# python -m scripts.try_stt ..\.support_docs\sound-recordings\myself-speech.m4a
# python -m scripts.try_stt ..\.support_docs\sound-recordings\silent-speech.m4a

