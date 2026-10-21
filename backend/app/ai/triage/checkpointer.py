from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.core.config import settings


def create_checkpoint_pool() -> AsyncConnectionPool:
    """Created closed; the app opens it at startup."""
    return AsyncConnectionPool(
        conninfo=settings.checkpoint_database_url,
        min_size=1,
        max_size=3,
        kwargs={"autocommit": True, "prepare_threshold": 0, "row_factory": dict_row},
        check=AsyncConnectionPool.check_connection,   # replaces dead connections (Neon suspends idle databases)
        open=False,
    )



