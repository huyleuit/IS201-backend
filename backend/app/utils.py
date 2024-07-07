from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from db.tables import AccountTokenTable


def getEmpId(token: str, s: Session):
    check_account_username = s.query(AccountTokenTable).filter(AccountTokenTable.token == token).first()
    if check_account_username is not None and check_account_username.username == "admin":
        raise HTTPException(status_code=401, detail="Admin is special account with not associated with employee, Please login with cashier account")

    sql_statement = text('select "Account".EMP_ID '
                         'from "Account","AccountToken" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    return result.emp_id