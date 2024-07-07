from pydantic import BaseModel, Field


class RoleSchema(BaseModel):
    role_id: int = Field(description="Role id")
    name: str = Field(description="Role name", examples=['manager'])


class RoleSchemas(BaseModel):
    data: list[RoleSchema] = Field(description="List of roles")


class RoleDetailSchema(BaseModel):
    role_id: int = Field(description="Role id")
    role_name: str = Field(description="Role name", examples=['manager'])
    account_read: bool = Field(..., description="Account read permission")
    account_write: bool = Field(..., description="Account write permission")
    account_token_read: bool = Field(..., description="Account token read permission")
    account_token_write: bool = Field(..., description="Account token write permission")
    employee_read: bool = Field(..., description="Employee read permission")
    employee_write: bool = Field(..., description="Employee write permission")
    category_read: bool = Field(..., description="Category read permission")
    category_write: bool = Field(..., description="Category write permission")
    goods_read: bool = Field(..., description="Goods read permission")
    goods_write: bool = Field(..., description="Goods write permission")
    shipment_read: bool = Field(..., description="Shipment read permission")
    shipment_write: bool = Field(..., description="Shipment write permission")
    membership_card_read: bool = Field(..., description="Membership card read permission")
    membership_card_write: bool = Field(..., description="Membership card write permission")
    promotion_read: bool = Field(..., description="Promotion read permission")
    promotion_write: bool = Field(..., description="Promotion write permission")
    bill_read: bool = Field(..., description="Bill read permission")
    bill_write: bool = Field(..., description="Bill write permission")
    payment_read: bool = Field(..., description="Payment read permission")
    payment_write: bool = Field(..., description="Payment write permission")
    bill_details_read: bool = Field(..., description="Bill details read permission")
    bill_details_write: bool = Field(..., description="Bill details write permission")
    import_note_read: bool = Field(..., description="Import read permission")
    import_note_write: bool = Field(..., description="Import write permission")
    export_note_read: bool = Field(..., description="Export read permission")
    export_note_write: bool = Field(..., description="Export write permission")
