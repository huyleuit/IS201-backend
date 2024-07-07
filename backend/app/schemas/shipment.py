from pydantic import Field
from datetime import datetime
from schemas.base_schema import BaseSchema
from pydantic import BaseModel
from typing import Optional


class ShipmentSchema(BaseSchema):
    shipment_id: int = Field(None, title="Shipment ID", description="Auto increment")
    shipment_name: str = Field(..., title="Shipment Name", max_length=255, examples=["Lô hàng X"])
    manufacture_date: datetime = Field(..., title="Manufacture Date")
    expiration_date: datetime = Field(None, title="Expiration Date")
    description: Optional[str] = Field(None, title="Description",examples=["Lô hàng chứa sản phẩm X"])
    quantity: int = Field(..., title="Quantity", gt=0)
    good_id: int = Field(..., title="Good ID")
    price: float = Field(..., title="Price", gt=0)


class ShipmentSchemas(BaseModel):
    data: list[ShipmentSchema] = Field(..., title="List of Shipment")
