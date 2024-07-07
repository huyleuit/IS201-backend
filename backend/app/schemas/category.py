import datetime
from typing import Optional

from pydantic import Field
from pydantic import BaseModel
from schemas.base_schema import BaseSchema


class CategorySchema(BaseSchema):
    category_id: Optional[int] = Field(None, title="Category ID")
    category_name: str = Field(..., title="Category Name", max_length=255)
    description: Optional[str] = Field(None, title="Description", max_length=255)


class CategorySchemas(BaseModel):
    data: list[CategorySchema] = Field(..., title="List of categories")