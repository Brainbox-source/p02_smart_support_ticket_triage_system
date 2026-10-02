from fastapi import FastAPI, Request

from .api.dependencies import get_db_pool
from .db.database import lifespan

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def test_databae_connection(request: Request):
    """tests the database connection"""

    pool = get_db_pool(request)

    query = """
        SELECT version();
    """

    async with pool.acquire() as connection:
        version = await connection.fetchval(query)

        return {"msg": "Connection Successful! ✅", "postgres_version": version}
