from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings
from app.core.exceptions import AIProviderError


@lru_cache
def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model=settings.embedding_model,
        google_api_key=settings.gemini_api_key,
        output_dimensionality=settings.embedding_dimensions,
    )


def _check_size(vectors: list[list[float]]) -> None:
    for vector in vectors:
        if len(vector) != settings.embedding_dimensions:
            raise AIProviderError(
                f"Embedding has {len(vector)} dimensions, "
                f"expected {settings.embedding_dimensions}"
            )


async def embed_documents(texts: list[str]) -> list[list[float]]:
    try:
        vectors = await _get_embeddings().aembed_documents(texts)
    except Exception as e:
        raise AIProviderError("Embedding request failed") from e
    _check_size(vectors)
    return vectors


async def embed_query(text: str) -> list[float]:
    try:
        vector = await _get_embeddings().aembed_query(text)
    except Exception as e:
        raise AIProviderError("Embedding request failed") from e
    _check_size([vector])
    return vector


