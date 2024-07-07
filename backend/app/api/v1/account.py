import bcrypt
from fastapi import APIRouter, HTTPException, Depends, Path
from fastapi.security import HTTPBasic, HTTPBasicCredentials, APIKeyHeader
import secrets
from sqlalchemy.orm import Session
from db.session import getSession
from schemas.account import AccountTokenRPSchema
import base64
from typing import Annotated, Union
from fastapi import Header
from db.tables import AccountTable, AccountTokenTable

header_schema = APIKeyHeader(name='x-token', auto_error=True)
from sqlalchemy import text

account_router = APIRouter()
basic_security = HTTPBasic(description="Please enter your username and password here")


def checkWritePermission(token: str, s: Session):
    sql_statement = text('select "Role".ACCOUNT_WRITE from "AccountToken","Account","Role"'
                         ' where "AccountToken".username = "Account".username and "Account".ROLE_ID = "Role".role_id'
                         ' and token = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.account_write == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


def checkReadPermission(token: str, s: Session):
    sql_statement = text('select "Role".ACCOUNT_READ from "AccountToken","Account","Role"'
                         ' where "AccountToken".username = "Account".username and "Account".ROLE_ID = "Role".role_id'
                         ' and token = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.account_read == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


@account_router.get('/set-password/{emp_id}', summary='set password for employee account ', status_code=200, )
def set_password(emp_id: Annotated[int, Path(description="Your emp_id")],
                 new_password: Annotated[str, Header(description="Your new password")],
                 current_password: Annotated[Union[str, None], Header(description="Your old password")] = None,
                 token: str = Depends(header_schema),
                 s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    account_info: AccountTable = s.query(AccountTable).filter(AccountTable.emp_id == emp_id).first()

    def store_new_password():
        salt = bcrypt.gensalt()
        hashed_pw_bytes = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        account_info.salt = base64.b64encode(salt).decode('utf-8')
        account_info.password = base64.b64encode(hashed_pw_bytes).decode('utf-8')

    if account_info.password is None:
        store_new_password()
    else:
        salt_bytes: bytes = base64.b64decode(account_info.salt.encode('utf-8'))
        hashed_password = bcrypt.hashpw(current_password.encode('utf-8'), salt_bytes)
        if hashed_password != base64.b64decode(account_info.password.encode('utf-8')):
            raise HTTPException(status_code=401, detail="old password incorrect")
        store_new_password()

    account_info.status = 'Active'
    s.merge(account_info)
    s.commit()
    return {"message": "password changed"}


@account_router.get('/login', summary='login ', status_code=200, response_model=AccountTokenRPSchema)
def login(credential: HTTPBasicCredentials = Depends(basic_security), s: Session = Depends(getSession)):
    account: AccountTable = s.query(AccountTable.username, AccountTable.password, AccountTable.salt).filter(
        AccountTable.username == credential.username).first()
    if account is None:
        raise HTTPException(status_code=404, detail="username not found")

    salt_bytes: bytes = base64.b64decode(account.salt)
    hashed_password = bcrypt.hashpw(credential.password.encode('utf-8'), salt_bytes)
    if hashed_password != base64.b64decode(account.password):
        raise HTTPException(status_code=401, detail="incorrect password")
    token = secrets.token_urlsafe(32)
    account_token = AccountTokenTable(username=credential.username, token=token)
    s.add(account_token)
    s.commit()
    s.refresh(account_token)
    return account_token.toDict()
