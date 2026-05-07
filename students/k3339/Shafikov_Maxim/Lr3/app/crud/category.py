from ..models.models import Category
from ..schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from .base import BaseCrud


class CategoryCrud(BaseCrud[Category, CategoryRead, CategoryCreate, CategoryUpdate]):
    base_model = Category
    get_schema = CategoryRead
    create_schema = CategoryCreate
    update_schema = CategoryUpdate
