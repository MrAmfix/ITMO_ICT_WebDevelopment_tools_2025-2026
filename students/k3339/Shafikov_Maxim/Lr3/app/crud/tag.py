from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import Tag
from ..schemas.tag import TagCreate, TagRead
from .base import BaseCrud


class TagCrud(BaseCrud[Tag, TagRead, TagCreate, TagRead]):
    base_model = Tag
    get_schema = TagRead
    create_schema = TagCreate
    update_schema = TagRead

    @classmethod
    async def get_by_ids_orm(cls, session: AsyncSession, tag_ids: List[int]) -> List[Tag]:
        result = await session.execute(select(Tag).where(Tag.id.in_(tag_ids)))
        return result.scalars().all()
