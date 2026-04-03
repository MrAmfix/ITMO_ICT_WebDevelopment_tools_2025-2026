from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import hash_password
from ..models.models import User
from ..schemas.user import UserCreate, UserRead, UserUpdate
from .base import BaseCrud


class UserCrud(BaseCrud[User, UserRead, UserCreate, UserUpdate]):
    base_model = User
    get_schema = UserRead
    create_schema = UserCreate
    update_schema = UserUpdate

    @classmethod
    async def get_by_username(cls, session: AsyncSession, username: str) -> Optional[UserRead]:
        result = await session.execute(select(User).where(User.username == username))
        obj = result.scalar_one_or_none()
        return UserRead.model_validate(obj) if obj else None

    @classmethod
    async def get_by_username_orm(cls, session: AsyncSession, username: str) -> Optional[User]:
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Optional[UserRead]:
        result = await session.execute(select(User).where(User.email == email))
        obj = result.scalar_one_or_none()
        return UserRead.model_validate(obj) if obj else None

    @classmethod
    async def create_user(cls, session: AsyncSession, data: UserCreate) -> UserRead:
        return await cls.create(
            session,
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
        )

    @classmethod
    async def change_password(
        cls, session: AsyncSession, user_id: int, new_password: str
    ) -> Optional[UserRead]:
        return await cls.update(session, user_id, hashed_password=hash_password(new_password))
