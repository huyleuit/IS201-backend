import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy import text
from sqlalchemy.orm import Session
from db.session import getSession
from db.tables import PromotionTable
from schemas.promotion import PromotionSchema, PromotionSchemas

promotion_router = APIRouter()


def checkWritePermission(token: str, s: Session):
    sql_statement = text('select "Role".PROMOTION_WRITE '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.promotion_write == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


def checkReadPermission(token: str, s: Session):
    sql_statement = text('select "Role".PROMOTION_READ '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.promotion_read == 0:
        raise HTTPException(status_code=403, detail="Permission Deny"

                                                    @ promotion_router.post("/", summary="Create a new promotion",
                                                                            response_model=PromotionSchema,
                                                                            status_code=201))


def create(new_promotion: PromotionSchema,
           token: str = Depends(APIKeyHeader(name='x-token', auto_error=True)),
           s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    new_promotion = PromotionTable(**new_promotion.toDict())
    try:
        new_promotion.pro_id = None
        check_name_duplicate = s.query(PromotionTable).filter(PromotionTable.pro_name == new_promotion.pro_name).first()
        if check_name_duplicate is not None:
            raise HTTPException(status_code=400, detail="pro_name already exists")
        s.add(new_promotion)
        s.commit()
        s.refresh(new_promotion)
    except sqlalchemy.exc.IntegrityError as e:
        s.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return new_promotion.toDict()


@promotion_router.get("/", summary="Get all promotions", response_model=PromotionSchemas)
def read(s: Session = Depends(getSession),
         token: str = Depends(APIKeyHeader(name='x-token', auto_error=True)),

         ):
    checkReadPermission(token, s)
    data = s.query(PromotionTable).all()
    _list = [i.toDict() for i in data]
    return PromotionSchemas(data=_list)


@promotion_router.get("/{pro_id}", summary="Get promotion by id", response_model=PromotionSchema)
def read(pro_id: int,
         token: str = Depends(APIKeyHeader(name='x-token', auto_error=True)),
         s: Session = Depends(getSession)):
    checkReadPermission(token, s)
    promotion: PromotionTable = s.query(PromotionTable).filter(PromotionTable.pro_id == pro_id).first()
    if promotion is None:
        raise HTTPException(status_code=404, detail="pro_id not found")
    return promotion.toDict()


@promotion_router.put("/", summary="Update a promotion", response_model=PromotionSchema)
def update(updated_promotion: PromotionSchema,
           token: str = Depends(APIKeyHeader(name='x-token', auto_error=True)),

           s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    updated_promotion = PromotionTable(**updated_promotion.toDict())
    old_promotion: PromotionTable = s.query(PromotionTable).filter(
        PromotionTable.pro_id == updated_promotion.pro_id).first()
    if old_promotion is None:
        raise HTTPException(status_code=404, detail="pro_id not found")
    updated_promotion.create_date = old_promotion.create_date
    updated_promotion.last_modified_date = None
    s.merge(updated_promotion)
    s.commit()
    s.refresh(old_promotion)
    return old_promotion.toDict()


@promotion_router.delete("/{pro_id}", summary="Delete a promotion", status_code=204)
def delete(pro_id: int, s: Session = Depends(getSession)):
    promotion: PromotionTable = s.query(PromotionTable).filter(PromotionTable.pro_id == pro_id).first()
    if promotion is None:
        raise HTTPException(status_code=404, detail="pro_id not found")
    s.delete(promotion)
    s.commit()
    return None
