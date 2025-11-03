# app/db/session.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Replace pymysql with aiomysql for async
async_url = settings.DATABASE_URL.replace('+pymysql', '+aiomysql')
engine = create_async_engine(
    async_url,
    echo=True,
    future=True,
    # Enable pre-ping to check connection health before use, preventing "Connection reset by peer" errors
    pool_pre_ping=True,
    # Recycle connections every 5 minutes to avoid using connections closed by the server.
    # Make sure this value is lower than MySQL's wait_timeout.
    pool_recycle=300,
    pool_size=5,  # Number of connections to keep in pool
    max_overflow=10,  # Max additional connections
    pool_timeout=30,  # Timeout for getting connection from pool
    # Add retry logic for connection failures
    connect_args={'connect_timeout': 10}
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()
