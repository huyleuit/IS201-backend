from enum import Enum

from pydantic import Field
from typing import Optional
from datetime import datetime
from schemas.base_schema import BaseSchema
from pydantic import BaseModel


class PaymentStatusEnum(str, Enum):
    Failed = "Failed"
    Processing = "Processing"
    Success = "Success"


class PaymentSchema(BaseSchema):
    payment_id: int = Field(..., alias="payment_id")
    pro_id: Optional[int] = Field(None, alias="pro_id")
    card_id: Optional[int] = Field(None, alias="card_id")
    bill_id: Optional[int] = Field(None, alias="bill_id")
    payment_status: PaymentStatusEnum
    payment_method: Optional[str] = Field(None, alias="payment_method")
    total: float = Field(..., alias="total")
    discounts: Optional[float] = Field(None, )
    actual_payment: Optional[int] = Field(None, alias="actual_payment")
    received: Optional[float] = Field(None, alias="received")
    change: Optional[float] = Field(None, alias="change")
    payment_date: Optional[datetime] = Field(None, alias="payment_date")


class PaymentUpdateSchema(BaseModel):
    pro_id: Optional[int] = Field(None, description="Promotion id")
    card_id: Optional[int] = Field(None, description="Membership card id")
    payment_status: PaymentStatusEnum = Field(..., description="Payment status", max_length=50,examples=["Processing", "Failed", "Success"])
    payment_method: Optional[str] = Field(None, description="Payment method",examples=["Cash", "Credit card", "Debit card"])
    received: Optional[float] = Field(None, description="Received money")
    change: Optional[float] = Field(None, description="Change money")

    def toDict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and v is not None}
