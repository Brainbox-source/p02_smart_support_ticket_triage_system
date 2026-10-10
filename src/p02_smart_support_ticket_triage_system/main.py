from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api import tickets
from .api.dependencies import get_db_pool
from .core.config import settings
from .db.database import lifespan

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Content-Type"],
)

app.include_router(tickets.router)


@app.get("/")
async def test_database_connection(request: Request):
    """tests the database connection"""

    pool = get_db_pool(request)

    query = """
        SELECT version();
    """

    async with pool.acquire() as connection:
        version = await connection.fetchval(query)

        return {"msg": "Connection Successful! ✅", "postgres_version": version}
