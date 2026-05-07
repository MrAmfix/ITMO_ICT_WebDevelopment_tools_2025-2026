from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...crud.budget import BudgetCrud
from ...schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from ...schemas.user import UserRead
from ..dependencies import get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("/", response_model=list[BudgetRead])
async def get_budgets(
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return await BudgetCrud.get_filtered(session, user_id=current_user.id)


@router.get("/{budget_id}", response_model=BudgetRead)
async def get_budget(
    budget_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    budget = await BudgetCrud.get_by_id(session, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return budget


@router.post("/", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
async def create_budget(
    data: BudgetCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return await BudgetCrud.create(session, **data.model_dump(), user_id=current_user.id)


@router.patch("/{budget_id}", response_model=BudgetRead)
async def update_budget(
    budget_id: int,
    data: BudgetUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    budget = await BudgetCrud.get_by_id(session, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return await BudgetCrud.update(session, budget_id, **data.model_dump(exclude_unset=True))


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    budget = await BudgetCrud.get_by_id(session, budget_id)
    if not budget or budget.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    await BudgetCrud.delete(session, budget_id)
