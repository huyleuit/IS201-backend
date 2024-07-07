from schemas.base_schema import BaseSchema
from pydantic import Field
from typing import Optional
from pydantic.main import BaseModel


class EmpSchema(BaseSchema):
    emp_id: int = Field(None, description="The unique identifier of the employee", examples=[1])
    username: Optional[str] = Field(None, description="The username of the employee", examples=['nguyenvana'])
    emp_name: str = Field(..., description="The name of the employee", examples=['NguyenVanA'])
    role_id: int = Field(..., description="The role_id of the employee", examples=[1])
    gender: str = Field(..., description="The gender of the employee", examples=['Nam'])
    address: str = Field(..., description="The address of the employee", examples=['123 Nguyen Van Linh'])
    phone: str = Field(..., description="The phone number of the employee", examples=['0123456789'])
    salary: Optional[float] = Field(None, description="The salary of the employee")
    kpi: Optional[int] = Field(None, description="The KPI of the employee")


class EmpSchemas(BaseModel):
    data: list[EmpSchema]
