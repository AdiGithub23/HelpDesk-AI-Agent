from typing import BinaryIO

from app.ai.stt import transcribe
from app.core.exceptions import AIProviderError, InvalidInputError

MAX_AUDIO_BYTES = 5 * 1024 * 1024   # starting value, tune after testing


class SpeechService:
    """Takes the model (not a session): there is no database in this feature."""

    def __init__(self, model):
        self.model = model

    def transcribe(self, audio_file: BinaryIO) -> str:
        if self.model is None:
            raise AIProviderError("Speech recognition is not available")
        data = audio_file.read(MAX_AUDIO_BYTES + 1)
        if not data:
            raise InvalidInputError("The audio is empty")
        if len(data) > MAX_AUDIO_BYTES:
            raise InvalidInputError("The audio is too large (5 MB maximum)")
        try:
            return transcribe(self.model, data)
        except Exception as e:
            raise AIProviderError("Speech recognition failed") from e



