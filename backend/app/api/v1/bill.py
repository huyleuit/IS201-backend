import sqlalchemy.exc
from fastapi import APIRouter
from db.session import getSession
from utils import getEmpId
from sqlalchemy.orm import Session
from db.tables import BillTable
from schemas.bill import BillSchema
from fastapi import HTTPException
from schemas.bill import BillSchemas
from sqlalchemy import text
from fastapi import Depends
from fastapi.security import APIKeyHeader


def checkWritePermission(token: str, s: Session):
    sql_statement = text('select "Role".BILL_WRITE '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.bill_write == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


def checkReadPermission(token: str, s: Session):
    sql_statement = text('select "Role".BILL_READ '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.bill_read == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")




bill_router = APIRouter()


@bill_router.post("/", description="Create a new bill", response_model=BillSchema, status_code=201)
def create(token=Depends(APIKeyHeader(name='x-token', auto_error=True)), db: Session = Depends(getSession)):
    checkWritePermission(token, db)

    new_bill = BillTable(emp_id=getEmpId(token, db))
    new_bill.create_date = None
    new_bill.last_modified_date = None
    new_bill.bill_id = None
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)
    return new_bill.toDict()


@bill_router.get("/", description="Get all bills", response_model=BillSchemas)
def read_all(token=Depends(APIKeyHeader(name='x-token', auto_error=True)), db: Session = Depends(getSession)):
    checkReadPermission(token, db)
    data = db.query(BillTable).all()
    return BillSchemas(data=[bill.toDict() for bill in data])


@bill_router.delete("/{bill_id}", description="Delete a bill", status_code=204)
def delete(bill_id: int, db: Session = Depends(getSession)):
    bill = db.query(BillTable).filter(BillTable.bill_id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill ID not found")
    try:
        db.delete(bill)
        db.commit()
    except sqlalchemy.exc.IntegrityError as e:
        if str(e).__contains__("child record found"):
            raise HTTPException(status_code=422,
                                detail="This bill has child record, can't not delete, please delete child record first")
    return None
