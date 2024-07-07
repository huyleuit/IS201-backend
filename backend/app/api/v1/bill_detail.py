from fastapi import APIRouter
from sqlalchemy import text
from db.session import getSession
from fastapi import Depends
from sqlalchemy.orm import Session
from db.tables import BillTable, BillDetailTable, GoodsTable, ShipmentTable, PaymentTable, PromotionTable
from fastapi import HTTPException
from schemas.bill_detail import *
from fastapi import Path
from typing import Annotated
from fastapi import Path, Query
from fastapi.security import APIKeyHeader

bill_detail_router = APIRouter()


def checkWritePermission(token: str, s: Session):
    sql_statement = text('select "Role".BILL_DETAILS_WRITE '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.bill_details_write == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


def checkReadPermission(token: str, s: Session):
    sql_statement = text('select "Role".BILL_DETAILS_READ '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.bill_details_read == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


def checkForeignKeys(bill: BillDetailTable, s: Session):
    check_bill_fk = s.query(BillTable.bill_id).filter(BillTable.bill_id == bill.bill_id).first()
    if check_bill_fk is None:
        s.rollback()
        raise HTTPException(status_code=422, detail='Bill ID not found')

    check_goods_fk = s.query(GoodsTable.goods_id).filter(GoodsTable.goods_id == bill.goods_id).first()
    if check_goods_fk is None:
        s.rollback()
        raise HTTPException(status_code=422, detail='Goods ID not found')

    check_shipment_fk = s.query(ShipmentTable.shipment_id).filter(ShipmentTable.shipment_id == bill.shipment_id).first()
    if check_shipment_fk is None:
        s.rollback()
        raise HTTPException(status_code=422, detail='Shipment ID not found')

    check_have_good_and_shipment = (s.query(ShipmentTable.shipment_id).
                                    filter(ShipmentTable.shipment_id == bill.shipment_id).
                                    filter(ShipmentTable.good_id == bill.goods_id).first())
    if check_have_good_and_shipment is None:
        s.rollback()
        raise HTTPException(status_code=422, detail='Goods ID not in Shipment ID')


@bill_detail_router.post('/{bill_id}', summary="", status_code=201)
def create(new_bill_detail: BillDetailRQSchemas,
           token=Depends(APIKeyHeader(name='x-token', auto_error=True)),
           bill_id: int = Path(..., description="Your bill_id "),
           s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    check_payment_status = s.query(PaymentTable.payment_status).filter(PaymentTable.bill_id == bill_id).first()[0]
    if check_payment_status is not None and check_payment_status != "Processing":
        s.rollback()
        raise HTTPException(status_code=409, detail="Payment is already done")

    bill_detail_table_list = [BillDetailTable(**i.__dict__) for i in new_bill_detail.data]
    for bill_detail in bill_detail_table_list:
        bill_detail.bill_id = bill_id
        bill_detail.unit_price = \
            s.query(ShipmentTable.price).filter(ShipmentTable.good_id == bill_detail.goods_id).first()[
                0]
        bill_detail.total = bill_detail.unit_price * bill_detail.quantity
        checkForeignKeys(bill_detail, s)
        check_duplicate_entry = s.query(BillDetailTable).filter(BillDetailTable.bill_id == bill_id).filter(
            BillDetailTable.goods_id == bill_detail.goods_id).first()
        if check_duplicate_entry:
            s.rollback()
            raise HTTPException(status_code=409, detail="Duplicate entry")
        bill_detail.bill_id = bill_id
        s.add(bill_detail)
    s.commit()

    updated_payment: PaymentTable = s.query(PaymentTable).filter(PaymentTable.bill_id == bill_id).first()
    updated_payment.total = s.execute(text('select sum(total) from "BillDetails" where bill_id = :bill_id'),
                                      {'bill_id': bill_id}).fetchone()[0]
    check_pro_id = s.query(PaymentTable.pro_id).filter(PaymentTable.bill_id == bill_id).first()[0]
    if check_pro_id is not None:
        updated_payment.discounts = \
            s.query(PromotionTable.discount).filter(PromotionTable.pro_id == check_pro_id).first()[
                0] * updated_payment.total
        updated_payment.actual_payment = updated_payment.total - updated_payment.discounts

    if updated_payment.actual_payment is None:
        updated_payment.actual_payment = updated_payment.total
    s.merge(updated_payment)
    s.commit()
    return None


@bill_detail_router.get('/{bill_id}', summary="Get your detail bill", response_model=BillDetailRPSchemas)
def read(bill_id: int, s: Session = Depends(getSession)):
    bill_detail: list[BillDetailTable] = s.query(BillDetailTable).filter(BillDetailTable.bill_id == bill_id).all()
    return BillDetailRPSchemas(data=[BillDetailRPSchema(**i.toDict()) for i in bill_detail])


@bill_detail_router.get('/', summary="Get all bill_id", response_model=list[int], status_code=200)
def read(s: Session = Depends(getSession)):
    bill_detail = s.query(BillDetailTable.bill_id).distinct().all()
    data = []
    for bill in bill_detail:
        data.append(bill.bill_id)
    return data


@bill_detail_router.put('/{bill_id}/{goods_id}', summary="Update bill detail")
def update(
        bill_id: Annotated[int, Path(..., description="Your bill_id")],
        goods_id: Annotated[int, Path(..., description="Your goods_id")],
        quantity: Annotated[int, Query(..., description="Your quantity", gt=0)],
        token=Depends(APIKeyHeader(name='x-token', auto_error=True)),
        s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    old_bill_id: BillDetailTable = s.query(BillDetailTable).filter(BillDetailTable.bill_id == bill_id).first()
    if old_bill_id is None:
        raise HTTPException(status_code=404, detail='bill_id not found')
    check_good_id = s.query(BillDetailTable.goods_id).filter(BillDetailTable.goods_id == goods_id).filter(BillDetailTable.bill_id == bill_id).first()
    if check_good_id is None:
        raise HTTPException(status_code=404, detail='goods_id not found')
    check_payment_status = s.query(PaymentTable.payment_status).filter(PaymentTable.bill_id == bill_id).first()[0]
    if check_payment_status is not None and check_payment_status != "Processing":
        s.rollback()
        raise HTTPException(status_code=409, detail="Payment is already done")
    check_quantity_shipment: ShipmentTable = \
        s.query(ShipmentTable.quantity).filter(ShipmentTable.good_id == goods_id).first()[0]
    if quantity > check_quantity_shipment:
        s.rollback()
        raise HTTPException(status_code=409, detail="quantity_shipment is is not enough")
    check_quantity_shipment += old_bill_id.quantity - quantity
    old_bill_id.quantity = quantity
    old_bill_id.total = old_bill_id.unit_price * quantity
    s.merge(old_bill_id)
    update_shipment = s.query(ShipmentTable).filter(ShipmentTable.good_id == goods_id).first()
    update_shipment.quantity = check_quantity_shipment
    s.merge(update_shipment)
    update_payment:PaymentTable = s.query(PaymentTable).filter(PaymentTable.bill_id == bill_id).first()
    update_payment.total = s.execute(text('select sum(total) from "BillDetails" where bill_id = :bill_id'),
                                     {'bill_id': bill_id}).fetchone()[0]
    if update_payment.pro_id is not None:
        update_payment.discounts = \
            s.query(PromotionTable.discount).filter(PromotionTable.pro_id == update_payment.pro_id).first()[
                0] * update_payment.total
        update_payment.actual_payment = update_payment.total - update_payment.discounts
    else:
        update_payment.actual_payment = update_payment.total
    s.merge(update_payment)
    s.commit()
    s.refresh(old_bill_id)
    return BillDetailRPSchema(**old_bill_id.toDict())


@bill_detail_router.delete('/{bill_id}/{goods_id}', summary="Delete bill detail", status_code=204)
def delete(bill_id: int, goods_id: int, s: Session = Depends(getSession)):
    bill_detail = s.query(BillDetailTable).filter(BillDetailTable.bill_id == bill_id).filter(
        BillDetailTable.goods_id == goods_id).first()
    if bill_detail is None:
        raise HTTPException(status_code=404, detail='not found')
    s.delete(bill_detail)
    update_payment: PaymentTable = s.query(PaymentTable).filter(PaymentTable.bill_id == bill_id).first()
    update_payment.total = s.execute(text('select sum(total) from "BillDetails" where bill_id = :bill_id'),
                                     {'bill_id': bill_id}).fetchone()[0]
    if update_payment.total is None:
        update_payment.total = 0
    if update_payment.pro_id is not None:
        update_payment.discounts = \
            s.query(PromotionTable.discount).filter(PromotionTable.pro_id == update_payment.pro_id).first()[
                0] * update_payment.total
        update_payment.actual_payment = update_payment.total - update_payment.discounts
    else:
        update_payment.actual_payment = update_payment.total
    update_shipment = s.query(ShipmentTable).filter(ShipmentTable.good_id == goods_id).first()
    update_shipment.quantity += bill_detail.quantity
    s.merge(update_payment)
    s.commit()
    return None
