from fastapi import APIRouter
from fastapi.security import APIKeyHeader

from db.session import getSession
from fastapi import Depends

role_router = APIRouter()
from sqlalchemy.orm import Session
from db.tables import RoleTable
from sqlalchemy import text
from schemas.role import RoleSchema
from schemas.role import RoleDetailSchema
header_schema = APIKeyHeader(name='x-token', auto_error=True)


@role_router.get('/', summary='Get all roles', status_code=200)
def read(s: Session = Depends(getSession)):
    result = s.execute(text('select ROLE_ID,ROLE_NAME from "Role"')).all()
    dict_response: list[RoleSchema] = []
    for row in result:
        dict_response.append(RoleSchema(role_id=row[0], name=row[1]))
    return dict_response


@role_router.get('/{role_id}', summary='Get detail permission by id', status_code=200)
def read(role_id: int, s: Session = Depends(getSession)):
    result: RoleTable = s.query(RoleTable).filter(RoleTable.role_id == role_id).first()

    return RoleDetailSchema(**result.toDict())

