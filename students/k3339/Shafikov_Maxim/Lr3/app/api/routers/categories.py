from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...crud.category import CategoryCrud
from ...schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from ...schemas.user import UserRead
from ..dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryRead])
async def get_categories(
    session: AsyncSession = Depends(get_session),
    _: UserRead = Depends(get_current_user),
):
    return await CategoryCrud.get_all(session)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: int,
    session: AsyncSession = Depends(get_session),
    _: UserRead = Depends(get_current_user),
):
    category = await CategoryCrud.get_by_id(session, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_session),
    _: UserRead = Depends(get_current_user),
):
    return await CategoryCrud.create(session, **data.model_dump())


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    session: AsyncSession = Depends(get_session),
    _: UserRead = Depends(get_current_user),
):
    category = await CategoryCrud.update(
        session, category_id, **data.model_dump(exclude_unset=True)
    )
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_session),
    _: UserRead = Depends(get_current_user),
):
    await CategoryCrud.delete(session, category_id)
