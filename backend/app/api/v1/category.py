from fastapi import APIRouter
from fastapi.security import APIKeyHeader
from db.tables import CategoryTable
from schemas.category import *
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi import HTTPException
from db.session import getSession
import sqlalchemy
from typing import Annotated
from fastapi import Depends
from fastapi import Path
from sqlalchemy import text

category_router = APIRouter()
header_schema = APIKeyHeader(name='x-token', auto_error=True)


def checkWritePermission(token: str, s: Session):
    sql_statement = text('select "Role".CATEGORY_WRITE from "AccountToken","Account","Role"'
                         ' where "AccountToken".username = "Account".username and "Account".ROLE_ID = "Role".role_id'
                         ' and token = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.category_write == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


def checkReadPermission(token: str, s: Session):
    sql_statement = text('select "Role".CATEGORY_READ from "AccountToken","Account","Role"'
                         ' where "AccountToken".username = "Account".username and "Account".ROLE_ID = "Role".role_id'
                         ' and token = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.category_read == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


@category_router.post("/", summary="Create a new category", response_model=CategorySchema, status_code=201)
def create(new_category: CategorySchema, token: str = Depends(header_schema), s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    new_category = CategoryTable(**new_category.toDict())
    try:
        check_duplicate = s.query(CategoryTable).filter(
            CategoryTable.category_name == new_category.category_name).first()
        if check_duplicate:
            raise HTTPException(status_code=400, detail="category_name already exists")
        new_category.create_by = None
        new_category.last_modified_by = None
        new_category.create_date = None
        new_category.last_modified_date = None
        new_category.category_id = None
        s.add(new_category)
        s.commit()
        s.refresh(new_category)
    except sqlalchemy.exc.IntegrityError as e:
        print(e.__cause__)
        s.rollback()
        raise HTTPException(status_code=500, detail="Some thing not right, check your server log")

    return new_category.toDict()


@category_router.get("/", summary="Get all categories", response_model=CategorySchemas)
def read(s: Session = Depends(getSession), token: str = Depends(header_schema)):
    checkReadPermission(token, s)
    data = s.query(CategoryTable).all()
    return CategorySchemas(data=[CategorySchema(**i.toDict()) for i in data])


@category_router.get("/{category_id}", summary="Get a category by ID", response_model=CategorySchema)
def read_by_id(category_id: Annotated[int, Path(description="your category id")],
               token: str = Depends(header_schema),
               s: Session = Depends(getSession)):
    checkReadPermission(token, s)
    result: CategoryTable = s.query(CategoryTable).filter(CategoryTable.category_id == category_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="category_id not found")
    return result.toDict()


@category_router.put("/", summary="Update a category by ID", response_model=CategorySchema)
def update(update_category: CategorySchema,
           token: str = Depends(header_schema),
           s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    update_category = CategoryTable(**update_category.toDict())
    old_category: CategoryTable = s.query(CategoryTable).filter(
        CategoryTable.category_id == update_category.category_id).first()
    if not old_category:
        raise HTTPException(status_code=404, detail="category_id not found")

    update_category.create_by = old_category.create_by
    update_category.last_modified_date = None
    s.merge(update_category)
    s.commit()
    s.refresh(old_category)
    return old_category.toDict()


@category_router.delete("/{category_id}", summary="Delete a category by ID", status_code=204)
def delete(category_id: Annotated[int, Path(description="your category id")],
           token: str = Depends(header_schema),
           s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    check_exist = s.query(CategoryTable).filter(CategoryTable.category_id == category_id).first()
    if check_exist is None:
        raise HTTPException(status_code=404, detail="category_id not found")
    try:
        s.delete(check_exist)
        s.commit()
    except sqlalchemy.exc.IntegrityError as e:
        if str(e).__contains__("child record found"):
            raise HTTPException(status_code=422,
                                detail="This bill has child record, can't not delete, please delete child record first")

