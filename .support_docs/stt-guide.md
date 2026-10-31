# Guide: Adding Speech-to-Text (STT) to Your App

## Overview

STT's real concern: **Whisper-family models can hallucinate**, mostly on silence, background noise, or very short clips. This guide shows how to reduce that with the right settings and a free stack. We start with push-to-talk (record, then transcribe). Streaming can come later.

---

## Recommended Free Stack

### Engine: `faster-whisper`
- MIT license, runs locally, no API cost.
- A faster reimplementation of OpenAI's Whisper using CTranslate2.
- Has a built-in Silero VAD filter that removes non-speech audio before transcription. It helps against hallucination, but it is not a complete fix (see the VAD note below).
- Decodes audio with PyAV, which bundles the FFmpeg libraries, so you do not need to install FFmpeg separately.

### Model: `small`
- Chosen for CPU-only use, with `compute_type="int8"`.
- The model is downloaded on the first run.
- Latency depends on your hardware, so test it on your own machine.

### Backend dependencies
```bash
uv pip install faster-whisper python-multipart
```
- Add `websockets` only if you later want live streaming.

### Frontend
- The browser's native `MediaRecorder` API records the mic. This is plain audio recording, not browser speech recognition.
- No extra npm package is required.

---

## How It Works

1. React records audio from the mic.
2. React sends the audio to the backend, with the login token.
3. faster-whisper returns text.
4. The text goes into the existing chat endpoint exactly like typed input.

---

## Backend Example

This shows the transcription core only. In a particular project, it must follow the project's specific rules.
In this project:
- the route requires a logged-in user, under `/api/v1`
- the model is loaded once in `lifespan`, not at the top of a file
- the logic lives in a service, not in the route

```python
import io
from fastapi import File, UploadFile
from faster_whisper import WhisperModel

# Load ONCE at startup, not per request
model = WhisperModel("small", device="cpu", compute_type="int8")

@router.post("/stt")
def stt(audio: UploadFile = File(...)):   # plain `def`, NOT `async def`
    data = io.BytesIO(audio.file.read())  # in memory: no temp file
    segments, info = model.transcribe(
        data,
        language="en",                     # set it, don't auto-detect
        vad_filter=True,                   # removes non-speech audio before transcribing
        condition_on_previous_text=False,  # stops repetition loops
        beam_size=5,
        initial_prompt="Helpdesk, ticket, VPN, password reset",  # domain vocabulary
    )
    return {"text": " ".join(s.text.strip() for s in segments)}
```

### Why these choices
- **Plain `def`, not `async def`:** transcription is heavy CPU work. In an `async def` route it would run on the event loop and freeze every other request (chat, tickets, login) until it finishes. A plain `def` route runs in FastAPI's thread pool.
- **`io.BytesIO`, not a temp file:** on Windows, a `NamedTemporaryFile` cannot be opened a second time by name while it is still open, so passing its name to the model fails. `transcribe` accepts a file-like object, so no file is needed. (This follows its documented signature. Confirm it in the first test.)

### Key settings explained
- **`language="en"`:** set it, don't auto-detect.
- **`vad_filter=True`:** uses the Silero VAD model to skip non-speech audio.
- **`condition_on_previous_text=False`:** stops repetition loops.
- **`beam_size=5`:** beam search width.
- **`initial_prompt`:** domain vocabulary.

### VAD note
The default VAD behavior is conservative: it only removes silence longer than 2 seconds. Short push-to-talk clips have little silence, so this alone will not prevent every hallucination. If you see made-up text on near-silent clips, tune `vad_parameters` (for example `vad_parameters=dict(min_silence_duration_ms=500)`) and test again.

---

## Frontend Example

```js
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const rec = new MediaRecorder(stream);
const chunks = [];
rec.ondataavailable = e => chunks.push(e.data);
rec.onstop = async () => {
  const fd = new FormData();
  fd.append("audio", new Blob(chunks, { type: rec.mimeType }));
  // In this project: send it through the API module, so the login token is included
  // and the path is /api/v1/stt (a bare fetch("/stt") would not).
  const { text } = await sendAudio(fd);
  // put `text` in the chat input, or send it to the existing chat endpoint
};
```

> **Note:** The mic only works on HTTPS or `localhost`.

---

## Model Choice

This project uses **`small`**, on CPU, with `compute_type="int8"`.

Other options, for reference only:

| Model | Use when |
|---|---|
| `medium` | CPU-only server, more accuracy, slower |
| `large-v3` | You have a GPU (needs CUDA libraries) |
| `distil-large-v3` | English only, faster than `large-v3` on GPU |

---

## Not Yet Verified (check in the first test)

- Download size and first-start time of the `small` model.
- Speed of `small` on your CPU.
- That the audio format your browser records (Chrome records WebM) decodes without trouble.
- That `transcribe` accepts the in-memory file as shown.

---

## Recommendation

Start with **record-then-transcribe (push-to-talk)**. It is the simplest and most accurate. Add WebSocket streaming only if you really need live text.

# The End


