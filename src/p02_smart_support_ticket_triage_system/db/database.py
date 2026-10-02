from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI

from ..core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("creating database connection pool...")

    app.state.db_pool = await asyncpg.create_pool(settings.database_url)

    yield

    print("closing database connection pool...")

    await app.state.db_pool.close()
