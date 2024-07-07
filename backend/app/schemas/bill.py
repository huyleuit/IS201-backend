from schemas.base_schema import BaseSchema
from typing import Optional
from datetime import datetime
from pydantic import Field
from pydantic import BaseModel


class BillSchema(BaseSchema):
    bill_id: int = Field(None, title="Bill ID")
    emp_id: int = Field(..., title="Employee ID", examples=[1])


class BillSchemas(BaseModel):
    data: list[BillSchema]
