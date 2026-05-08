from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...core.security import verify_password
from ...crud.user import UserCrud
from ...schemas.user import UserPasswordChange, UserRead, UserUpdate
from ..dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def get_me(current_user: UserRead = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=list[UserRead])
async def get_all_users(
    session: AsyncSession = Depends(get_session),
    _: UserRead = Depends(get_current_user),
):
    """
    В задании на 15 баллов есть требование:
    Дополнительные АПИ-методы для получения информации о пользователе, списка пользователей и смене пароля

    Сама по себе эта ручка - огромная дыра в безопасности и я бы ее не оставлял если что :)
    """
    return await UserCrud.get_all(session)


@router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return await UserCrud.update(session, current_user.id, **data.model_dump(exclude_unset=True))


@router.post("/me/change-password", response_model=UserRead)
async def change_password(
    data: UserPasswordChange,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    user_orm = await UserCrud.get_by_id_orm(session, current_user.id)
    if not verify_password(data.old_password, user_orm.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong current password"
        )
    return await UserCrud.change_password(session, current_user.id, data.new_password)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    await UserCrud.delete(session, current_user.id)
