from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.database import get_session
from ...crud.transaction import TransactionCrud
from ...schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate
from ...schemas.user import UserRead
from ..dependencies import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=list[TransactionRead])
async def get_transactions(
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return await TransactionCrud.get_filtered(session, user_id=current_user.id)


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(
    transaction_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    transaction = await TransactionCrud.get_by_id(session, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return transaction


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    return await TransactionCrud.create_transaction(session, data, current_user.id)


@router.patch("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: int,
    data: TransactionUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    transaction = await TransactionCrud.get_by_id(session, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return await TransactionCrud.update_transaction(session, transaction_id, data)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: UserRead = Depends(get_current_user),
):
    transaction = await TransactionCrud.get_by_id(session, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    await TransactionCrud.delete(session, transaction_id)
