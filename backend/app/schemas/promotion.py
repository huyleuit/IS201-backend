from schemas.base_schema import BaseSchema
from pydantic import Field
from datetime import datetime
from pydantic import BaseModel


class PromotionSchema(BaseSchema):
    pro_id: int = Field(None, title="Promotion ID")
    pro_name: str = Field(..., title="Name of promotion", max_length=255)
    discount: float = Field(..., title="Discount", gt=0, lt=1)
    content: str = Field(..., title="Content of promotion", max_length=255)
    start_date: datetime = Field(..., title="Start date of promotion")
    end_date: datetime = Field(..., title="End date of promotion")


class PromotionSchemas(BaseModel):
    data: list[PromotionSchema] = Field(..., title="List of promotions")
