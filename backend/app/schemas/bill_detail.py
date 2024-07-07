from pydantic import BaseModel, Field, validator


class BillDetailRPSchema(BaseModel):
    goods_id: int = Field(..., title="Goods ID", examples=[1])
    shipment_id: int = Field(..., title="Shipment ID", examples=[1])
    unit_price: float = Field(..., title="Unit Price", examples=[1])
    quantity: int = Field(..., title="Quantity", examples=[5])
    total: float = Field(..., title="Price", examples=[7000])


class BillDetailRQSchema(BaseModel):
    goods_id: int = Field(..., title="Goods ID", examples=[1])
    quantity: int = Field(..., title="Quantity", examples=[1])
    shipment_id: int = Field(..., title="Shipment ID", examples=[1])


class BillDetailRQSchemas(BaseModel):
    data: list[BillDetailRQSchema]


class BillDetailRPSchemas(BaseModel):
    data: list[BillDetailRPSchema]
