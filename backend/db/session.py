from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.core.config import get_settings
from backend.db.base import Base
from backend.core.logging import logger

settings = get_settings()

# ENTERPRISE POSTGRES POOLING
# Prevents connection leaks and idle timeouts in production
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=10,          # Persistent connections
    max_overflow=20,       # Spike capacity
    pool_recycle=3600,     # Recycle connections every hour before Postgres kills them
    pool_pre_ping=True     # Test connection before using it
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("PostgreSQL tables created/verified successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize PostgreSQL database: {e}")
        raise

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"PostgreSQL transaction failed, rolled back: {e}")
            raise
        finally:
            await session.close()