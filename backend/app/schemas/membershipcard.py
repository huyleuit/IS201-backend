from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class MemberShipCardRPSchema(BaseModel):
    card_id: int = Field(None, example=1)
    member_name: str = Field(..., example="John Doe")
    date_of_birth: datetime = Field(None, example="1990-01-01")
    phone: str = Field(..., example="1234567890")
    email: EmailStr = Field(None, example="johndoe@example.com")
    card_point: int = Field(..., example=100)
    card_rank: str = Field(..., example="Gold")
    start_date: datetime = Field(..., example="2022-01-01")
    end_date: datetime = Field(..., example="2023-02-01")
    status: str = Field(None, example="Active")
    emp_id: int = Field(..., example=1)

    def toDict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and v is not None}


class MembershipRQSchema(BaseModel):
    member_name: str = Field(..., example="John Doe")
    date_of_birth: datetime = Field(None, example="1990-01-01")
    phone: str = Field(..., example="1234567890")
    email: EmailStr = Field(None, example="johndoe@example.com")

    def toDict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and v is not None}


class MembershipRpSchemas(BaseModel):
    data: list[MemberShipCardRPSchema] = Field(..., description="List of MembershipCard")
