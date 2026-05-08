from typing import Optional

from pydantic import BaseModel

from ..models.models import TransactionType


class CategoryCreate(BaseModel):
    name: str
    type: TransactionType


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[TransactionType] = None


class CategoryRead(BaseModel):
    id: int
    name: str
    type: TransactionType

    model_config = {"from_attributes": True}
