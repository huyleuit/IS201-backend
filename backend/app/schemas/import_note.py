from datetime import datetime

from schemas.base_schema import BaseSchema, Field
from pydantic import BaseModel


class ImportNoteSchema(BaseSchema):
    import_id: int = Field(None, title="Import ID")
    import_date: datetime = Field(None, title="Import date", examples=['2021-10-10T00:00:00'])
    quantity: int = Field(..., title="Quantity of goods", gt=-1, lt=100000, examples=[10])
    price: float = Field(..., title="Price of goods", gt=-1, lt=100000, examples=[354.5])
    goods_id: int = Field(..., title="Goods ID", examples=[1])
    shipment_id: int = Field(None, title="Shipment ID", examples=[1])


class ImportNoteSchemas(BaseModel):
    data: list[ImportNoteSchema]
