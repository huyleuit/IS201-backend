import sqlalchemy.exc
from fastapi import APIRouter, Path
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from db.session import getSession
from schemas.emp import EmpSchema, EmpSchemas
from db.tables import EmpTable
from fastapi.security import APIKeyHeader
from fastapi import Depends

emp_router = APIRouter()


def checkEmpWritePermission(token: str, s: Session):
    sql_statement = text('select "Role".EMPLOYEE_WRITE '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.employee_write == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


def checkEmpReadPermission(token: str, s: Session):
    sql_statement = text('select "Role".EMPLOYEE_READ '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.employee_read == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


@emp_router.post("/", response_model=EmpSchema, status_code=201, summary="create new employee")
def created(new_employee: EmpSchema, token: str = Depends(APIKeyHeader(name='x-token', auto_error=True)),
            s: Session = Depends(getSession)):
    checkEmpWritePermission(token, s)
    new_employee = EmpTable(**new_employee.toDict())
    try:
        check_duplicate = s.query(EmpTable).filter(EmpTable.emp_id == new_employee.emp_id).first()
        if check_duplicate:
            raise HTTPException(status_code=400, detail="emp_id already exists")
        new_employee.emp_id = None
        new_employee.create_date = None
        new_employee.last_modified_date = None
        new_employee.create_by = None
        new_employee.last_modified_by = None
        s.add(new_employee)
        s.commit()
        s.refresh(new_employee)
    except sqlalchemy.exc.IntegrityError as e:
        print(e)
        s.rollback()
        raise HTTPException(status_code=500, detail="Some thing not right, check your server log")
    return EmpSchema(**new_employee.toDict())


@emp_router.get('/', response_model=EmpSchemas, summary="get all employee")
def read(token: str = Depends(APIKeyHeader(name="x-token", auto_error=True)), s: Session = Depends(getSession)):
    checkEmpReadPermission(token, s)
    data = s.query(EmpTable).all()
    return EmpSchemas(data=[EmpSchema(**i.toDict()) for i in data])


@emp_router.get('/{emp_id}', response_model=EmpSchema, summary="get employee by emp_id")
def read(emp_id: int = Path(..., description="The unique identifier of the employee"),
         token: str = Depends(APIKeyHeader(name="x-token", auto_error=True)),
         s: Session = Depends(getSession)):
    checkEmpReadPermission(token, s)
    data = s.query(EmpTable).filter(EmpTable.emp_id == emp_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="emp_id not found")
    return EmpSchema(**data.toDict())


@emp_router.put('/', response_model=EmpSchema, summary='update employee')
def put(update_emp: EmpSchema,
        token: str = Depends(APIKeyHeader(name="x-token", auto_error=True)),
        s: Session = Depends(getSession)):
    checkEmpWritePermission(token, s)
    try:
        update_emp = EmpTable(**update_emp.toDict())
        old_emp: EmpTable = s.query(EmpTable).filter(EmpTable.emp_id == update_emp.emp_id).first()
        if not old_emp:
            raise HTTPException(status_code=404, detail="emp_id not found")
        s.merge(update_emp)
        s.commit()
        s.refresh(old_emp)
    except sqlalchemy.exc.IntegrityError as e:
        print(e.__cause__)
        s.rollback()
        raise HTTPException(status_code=500, detail="Something not right, check your server log")
    return EmpSchema(**old_emp.toDict())


@emp_router.delete("/{emp_id}", summary="delete employee", status_code=204)
def delete(emp_id: int = Path(..., description="The unique identifier of the employee"),
           token: str = Depends(APIKeyHeader(name="x-token", auto_error=True)),
           s: Session = Depends(getSession)):
    checkEmpWritePermission(token, s)
    emp: EmpTable = s.query(EmpTable).filter(EmpTable.emp_id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="emp_id not found")
    try:
        s.delete(emp)
        s.commit()
    except sqlalchemy.exc.IntegrityError as e:
        if e.__str__().__contains__("child record found"):
            raise HTTPException(status_code=400, detail="Can not delete this employee because it is used in another table")
        raise HTTPException(status_code=500, detail=e.__str__())



