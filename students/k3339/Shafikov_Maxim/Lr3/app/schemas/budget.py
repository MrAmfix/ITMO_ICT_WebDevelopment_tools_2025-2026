from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from ..models.models import PeriodType
from .category import CategoryRead


class BudgetCreate(BaseModel):
    limit_amount: float
    period: PeriodType
    category_id: int


class BudgetUpdate(BaseModel):
    limit_amount: Optional[float] = None
    period: Optional[PeriodType] = None
    category_id: Optional[int] = None


class BudgetRead(BaseModel):
    id: int
    limit_amount: float
    period: PeriodType
    created_at: datetime
    user_id: int
    category: CategoryRead

    model_config = {"from_attributes": True}
