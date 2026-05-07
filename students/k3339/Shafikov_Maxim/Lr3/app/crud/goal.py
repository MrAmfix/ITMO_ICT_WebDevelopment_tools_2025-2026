from ..models.models import Goal
from ..schemas.goal import GoalCreate, GoalRead, GoalUpdate
from .base import BaseCrud


class GoalCrud(BaseCrud[Goal, GoalRead, GoalCreate, GoalUpdate]):
    base_model = Goal
    get_schema = GoalRead
    create_schema = GoalCreate
    update_schema = GoalUpdate
