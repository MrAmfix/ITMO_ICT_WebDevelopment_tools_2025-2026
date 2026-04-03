from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...crud.goal import GoalCrud
from ...schemas.goal import GoalCreate, GoalRead, GoalUpdate
from ...schemas.user import UserRead
from ..dependencies import get_current_user

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.get("/", response_model=list[GoalRead])
async def get_goals(
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return await GoalCrud.get_filtered(session, user_id=current_user.id)


@router.get("/{goal_id}", response_model=GoalRead)
async def get_goal(
    goal_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    goal = await GoalCrud.get_by_id(session, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal


@router.post("/", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
async def create_goal(
    data: GoalCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return await GoalCrud.create(session, **data.model_dump(), user_id=current_user.id)


@router.patch("/{goal_id}", response_model=GoalRead)
async def update_goal(
    goal_id: int,
    data: GoalUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    goal = await GoalCrud.get_by_id(session, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return await GoalCrud.update(session, goal_id, **data.model_dump(exclude_unset=True))


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    goal = await GoalCrud.get_by_id(session, goal_id)
    if not goal or goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    await GoalCrud.delete(session, goal_id)
