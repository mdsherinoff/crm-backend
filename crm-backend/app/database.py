import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

# Connection pool — reuses connections instead of
# opening a new one for every request
pool = None

async def init_pool():
    global pool
    pool = oracledb.create_pool(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN"),
        min=2,
        max=10,
        increment=1
    )

async def close_pool():
    if pool:
        pool.close()

def get_connection():
    """Get a connection from the pool."""
    return pool.acquire()