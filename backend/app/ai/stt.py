import io
import logging
import threading

from faster_whisper import WhisperModel

logger = logging.getLogger("uvicorn.error")

# one transcription at a time: I have not verified that one model object is safe to share
_lock = threading.Lock()


def load_stt_model() -> WhisperModel | None:
    """Returns None if the model cannot be loaded, so the rest of the app still starts."""
    try:
        return WhisperModel("small", device="cpu", compute_type="int8")
    except Exception:
        logger.exception("Speech model could not be loaded. Voice input is disabled.")
        return None


def transcribe(model: WhisperModel, audio_bytes: bytes) -> str:
    with _lock:
        segments, _ = model.transcribe(
            io.BytesIO(audio_bytes),
            language="en",
            vad_filter=True,
            condition_on_previous_text=False,
            beam_size=5,
            initial_prompt="Helpdesk, ticket, VPN, password reset",
        )
        # `segments` is lazy: the real work happens while we join, so it stays inside the lock
        return " ".join(s.text.strip() for s in segments).strip()

