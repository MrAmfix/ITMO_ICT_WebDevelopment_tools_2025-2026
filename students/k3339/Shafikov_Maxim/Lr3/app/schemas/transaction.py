from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

from .category import CategoryRead
from .tag import TagRead


class TransactionCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    date: date
    category_id: int
    tag_ids: Optional[List[int]] = []


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[date] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class TransactionRead(BaseModel):
    id: int
    amount: float
    description: Optional[str]
    date: date
    created_at: datetime
    user_id: int
    category: CategoryRead
    tags: List[TagRead] = []

    model_config = {"from_attributes": True}
