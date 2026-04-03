from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...crud.tag import TagCrud
from ...schemas.tag import TagCreate, TagRead
from ...schemas.user import UserRead
from ..dependencies import get_current_user

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("/", response_model=list[TagRead])
async def get_tags(
    session: AsyncSession = Depends(get_session),
    _: UserRead = Depends(get_current_user),
):
    return await TagCrud.get_all(session)


@router.get("/{tag_id}", response_model=TagRead)
async def get_tag(
    tag_id: int,
    session: AsyncSession = Depends(get_session),
    _: UserRead = Depends(get_current_user),
):
    tag = await TagCrud.get_by_id(session, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(
    data: TagCreate,
    session: AsyncSession = Depends(get_session),
    _: UserRead = Depends(get_current_user),
):
    return await TagCrud.create(session, **data.model_dump())


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    session: AsyncSession = Depends(get_session),
    _: UserRead = Depends(get_current_user),
):
    await TagCrud.delete(session, tag_id)
