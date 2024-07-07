from pydantic import Field, BaseModel
from schemas.base_schema import BaseSchema


class GoodSchema(BaseSchema):
    goods_id: int = Field(None, title="Goods ID")
    goods_name: str = Field(..., title="Goods Name")
    category_id: int = Field(..., title="Category ID")




class GoodSchemas(BaseModel):
    data: list[GoodSchema] = Field(..., title="List of Goods")
