import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.session import getSession
from db.tables import ShipmentTable, GoodsTable
from schemas.shipment import ShipmentSchema, ShipmentSchemas
from fastapi.security import APIKeyHeader
from sqlalchemy import text
from oracledb.exceptions import IntegrityError
shipment_router = APIRouter()


def checkWritePermision(token: str, s: Session):
    sql_statement = text('select "Role".SHIPMENT_WRITE '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.shipment_write == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


def checkReadPermission(token: str, s: Session):
    sql_statement = text('select "Role".SHIPMENT_READ '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.shipment_read == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


@shipment_router.post("/", summary="Create a new shipment", response_model=ShipmentSchema, status_code=201)
def create(new_shipment: ShipmentSchema, token: str = Depends(APIKeyHeader(name='x-token',auto_error=True)), s: Session = Depends(getSession)):
    checkWritePermision(token, s)
    new_shipment = ShipmentTable(**new_shipment.toDict())
    try:
        check_good_fk = s.query(GoodsTable.goods_id).filter(GoodsTable.goods_id == new_shipment.good_id).first()
        if check_good_fk is None:
            raise HTTPException(status_code=422, detail='Goods ID not found')

        new_shipment.shipment_id = None
        s.add(new_shipment)
        s.commit()
        s.refresh(new_shipment)
    except sqlalchemy.exc.IntegrityError as e:
        s.rollback()
        print(e.__cause__)
        raise HTTPException(status_code=500, detail="Some thing not right, check your server log")
    return new_shipment.toDict()


@shipment_router.get("/", summary="Get all shipments", response_model=ShipmentSchemas)
def read(token: str = Depends(APIKeyHeader(name='x-token',auto_error=True)), s: Session = Depends(getSession)):
    checkReadPermission(token, s)
    data = s.query(ShipmentTable).all()
    _list = [i.toDict() for i in data]
    return ShipmentSchemas(data=_list)


@shipment_router.put("/", summary="Update a shipment", response_model=ShipmentSchema)
def update(updated_shipment: ShipmentSchema,
           token: str = Depends(APIKeyHeader(name='x-token',auto_error=True)),
           s: Session = Depends(getSession)):
    checkWritePermision(token, s)
    updated_shipment = ShipmentTable(**updated_shipment.toDict())
    old_shipment: ShipmentTable = s.query(ShipmentTable).filter(
        ShipmentTable.shipment_id == updated_shipment.shipment_id).first()

    check_goods_fk = s.query(GoodsTable.goods_id).filter(GoodsTable.goods_id == updated_shipment.good_id).first()
    if check_goods_fk is None:
        raise HTTPException(status_code=422, detail='Goods ID not found')
    if old_shipment is None:
        raise HTTPException(status_code=404, detail="shipment_id not found")
    updated_shipment.create_date = old_shipment.create_date
    updated_shipment.last_modified_date = None
    s.merge(updated_shipment)
    s.commit()
    s.refresh(old_shipment)
    return old_shipment.toDict()

@shipment_router.delete("/{shipment_id}", summary="Delete a shipment", status_code=204)
def delete(shipment_id: int, s: Session = Depends(getSession)):
    shipment: ShipmentTable = s.query(ShipmentTable).filter(ShipmentTable.shipment_id == shipment_id).first()
    if shipment is None:
        raise HTTPException(status_code=404, detail="shipment_id not found")
    try:
        s.delete(shipment)
        s.commit()
    except sqlalchemy.exc.IntegrityError as e:
        if str(e).__contains__("child record found"):
            s.rollback()
            raise HTTPException(status_code=422, detail="Can't not delete because of child record found")
    return None