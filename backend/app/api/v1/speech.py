from fastapi import APIRouter, File, UploadFile

from app.api.deps import CurrentUser, SttModelDep
from app.schemas.speech import TranscriptionRead
from app.services.speech_service import SpeechService

router = APIRouter(prefix="/speech", tags=["speech"])


# plain `def`, not `async def`: transcription is heavy CPU work, and FastAPI
# runs plain `def` routes in a thread pool, so the server is never blocked.
@router.post("/transcribe", response_model=TranscriptionRead)
def transcribe_speech(user: CurrentUser, model: SttModelDep, audio: UploadFile = File(...)):
    return TranscriptionRead(text=SpeechService(model).transcribe(audio.file))
