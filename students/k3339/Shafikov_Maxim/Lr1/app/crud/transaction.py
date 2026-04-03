from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.models import Transaction
from ..schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from .base import BaseCrud, CrudIntegrityError
from .tag import TagCrud


class TransactionCrud(BaseCrud[Transaction, TransactionRead, TransactionCreate, TransactionUpdate]):
    base_model = Transaction
    get_schema = TransactionRead
    create_schema = TransactionCreate
    update_schema = TransactionUpdate

    @classmethod
    async def _get_validated_tags(cls, session: AsyncSession, tag_ids: List[int]) -> List:
        tags = await TagCrud.get_by_ids_orm(session, tag_ids)
        missing_tag_ids = sorted(set(tag_ids) - {tag.id for tag in tags})
        if missing_tag_ids:
            raise CrudIntegrityError(f"Unknown tag ids: {missing_tag_ids}")
        return tags

    @classmethod
    async def create_transaction(
        cls, session: AsyncSession, data: TransactionCreate, user_id: int
    ) -> TransactionRead:
        tags = await cls._get_validated_tags(session, data.tag_ids or [])
        instance = Transaction(
            amount=data.amount,
            description=data.description,
            date=data.date,
            category_id=data.category_id,
            user_id=user_id,
            tags=tags,
        )
        session.add(instance)
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise CrudIntegrityError("Invalid or conflicting data") from exc
        await session.refresh(instance)
        return TransactionRead.model_validate(instance)

    @classmethod
    async def update_transaction(
        cls, session: AsyncSession, transaction_id: int, data: TransactionUpdate
    ) -> Optional[TransactionRead]:
        update_data = data.model_dump(exclude_unset=True)
        instance = await cls.get_by_id_orm(session, transaction_id)
        if not instance:
            return None

        if "tag_ids" in update_data:
            instance.tags = await cls._get_validated_tags(session, update_data.pop("tag_ids") or [])

        for key, value in update_data.items():
            setattr(instance, key, value)

        session.add(instance)
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise CrudIntegrityError("Invalid or conflicting data") from exc
        await session.refresh(instance)
        return TransactionRead.model_validate(instance)
