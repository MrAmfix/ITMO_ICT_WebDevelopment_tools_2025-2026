from ..models.models import Budget
from ..schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate
from .base import BaseCrud


class BudgetCrud(BaseCrud[Budget, BudgetRead, BudgetCreate, BudgetUpdate]):
    base_model = Budget
    get_schema = BudgetRead
    create_schema = BudgetCreate
    update_schema = BudgetUpdate
