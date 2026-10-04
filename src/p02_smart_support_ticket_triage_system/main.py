from fastapi import FastAPI, Request

from .api import tickets
from .api.dependencies import get_db_pool
from .db.database import lifespan

app = FastAPI(lifespan=lifespan)

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
