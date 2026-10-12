from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import embed_documents, embed_query
from app.models import Article
from app.repositories.chunk_repository import ChunkHit, ChunkRepository

_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)


class IndexingService:
    """Chunks, embeds and stores article text. Never commits: the caller does."""

    def __init__(self, session: AsyncSession):
        self.chunks = ChunkRepository(session)

    async def index_article(self, article: Article) -> None:
        pieces = _splitter.split_text(article.body)
        texts = [f"{article.title}\n\n{piece}" for piece in pieces]
        # Embed BEFORE touching the database: a provider failure leaves old chunks intact.
        vectors = await embed_documents(texts) if texts else []
        await self.chunks.replace_for_article(article.id, texts, vectors)

    async def remove_article(self, article_id: int) -> None:
        await self.chunks.delete_by_article(article_id)

    async def search(self, question: str, k: int = 4) -> list[ChunkHit]:
        return await self.chunks.search(await embed_query(question), k)

