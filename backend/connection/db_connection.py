
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from backend.config.settings import settings
from contextlib import contextmanager

_pool: pool.SimpleConnectionPool | None = None

def init_pool():
    global _pool
    _pool = pool.SimpleConnectionPool(
        minconn=settings.DB_MIN_CONN,
        maxconn=settings.DB_MAX_CONN,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )

def get_connection():
    if _pool is None:
        raise RuntimeError("DB pool not initialised. Call init_pool() first.")
    return _pool.getconn()

def release_connection(conn):
    if _pool:
        _pool.putconn(conn)

@contextmanager
def get_cursor(commit: bool = False):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
            if commit:
                conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)