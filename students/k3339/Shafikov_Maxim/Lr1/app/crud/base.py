from __future__ import annotations

from typing import ClassVar, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete as sa_delete
from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelT = TypeVar("ModelT", bound=DeclarativeBase)
GetSchemaT = TypeVar("GetSchemaT", bound=BaseModel)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class CrudIntegrityError(Exception):
    pass


class BaseCrud(Generic[ModelT, GetSchemaT, CreateSchemaT, UpdateSchemaT]):
    base_model: ClassVar[Type[ModelT]]
    get_schema: ClassVar[Type[GetSchemaT]]
    create_schema: ClassVar[Type[CreateSchemaT]]
    update_schema: ClassVar[Type[UpdateSchemaT]]

    @classmethod
    async def get_by_id(cls, session: AsyncSession, record_id: int) -> Optional[GetSchemaT]:
        result = await session.execute(select(cls.base_model).where(cls.base_model.id == record_id))
        obj = result.scalar_one_or_none()
        return cls.get_schema.model_validate(obj) if obj else None

    @classmethod
    async def get_by_id_orm(cls, session: AsyncSession, record_id: int) -> Optional[ModelT]:
        result = await session.execute(select(cls.base_model).where(cls.base_model.id == record_id))
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(
        cls, session: AsyncSession, offset: int = 0, limit: int = 100
    ) -> List[GetSchemaT]:
        result = await session.execute(select(cls.base_model).offset(offset).limit(limit))
        return [cls.get_schema.model_validate(x) for x in result.scalars().all()]

    @classmethod
    async def get_filtered(cls, session: AsyncSession, **kwargs) -> List[GetSchemaT]:
        result = await session.execute(select(cls.base_model).filter_by(**kwargs))
        return [cls.get_schema.model_validate(x) for x in result.scalars().all()]

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> GetSchemaT:
        instance = cls.base_model(**kwargs)
        session.add(instance)
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise CrudIntegrityError("Invalid or conflicting data") from exc
        await session.refresh(instance)
        return cls.get_schema.model_validate(instance)

    @classmethod
    async def update(cls, session: AsyncSession, record_id: int, **kwargs) -> Optional[GetSchemaT]:
        clean = {k: v for k, v in kwargs.items() if v is not None}
        if not clean:
            return await cls.get_by_id(session, record_id)
        try:
            await session.execute(
                sa_update(cls.base_model).where(cls.base_model.id == record_id).values(**clean)
            )
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise CrudIntegrityError("Invalid or conflicting data") from exc
        return await cls.get_by_id(session, record_id)

    @classmethod
    async def delete(cls, session: AsyncSession, record_id: int) -> None:
        try:
            await session.execute(sa_delete(cls.base_model).where(cls.base_model.id == record_id))
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise CrudIntegrityError("Invalid or conflicting data") from exc
