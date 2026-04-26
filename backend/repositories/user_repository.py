from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.models import User
from backend.schemas.schemas import UserCreate
from backend.core.logging import logger

class UserRepository:
    def __init__(self, db: AsyncSession): self.db = db

    async def create_user(self, user: UserCreate) -> User:
        try:
            db_user = User(username=user.username)
            self.db.add(db_user)
            await self.db.flush()
            await self.db.refresh(db_user)
            return db_user
        except Exception as e:
            logger.error(f"Repo Error creating user: {e}")
            raise

    async def get_user(self, user_id: int) -> User:
        try:
            result = await self.db.execute(select(User).where(User.id == user_id))
            return result.scalars().first()
        except Exception as e:
            logger.error(f"Repo Error fetching user {user_id}: {e}")
            raise