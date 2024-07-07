from fastapi import APIRouter, Path, Query
from db.session import getSession
from fastapi import Depends
from sqlalchemy.orm import Session
from db.tables import PaymentTable, ShipmentTable, PromotionTable
from schemas.payment import PaymentSchema
from db.tables import BillDetailTable
from fastapi import HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy import text
from schemas.payment import PaymentStatusEnum
from typing import Annotated


def checkWritePermission(token: str, s: Session):
    sql_statement = text('select "Role".PAYMENT_WRITE '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.payment_write == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


def checkReadPermission(token: str, s: Session):
    sql_statement = text('select "Role".PAYMENT_READ '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.payment_read == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


payment_router = APIRouter()


@payment_router.get("/{bill_id}", description="Get payment info", response_model=PaymentSchema)
def get(bill_id: int, token=Depends(APIKeyHeader(name='x-token', auto_error=True)), s: Session = Depends(getSession)):
    checkReadPermission(token, s)
    payment = s.query(PaymentTable).filter(PaymentTable.bill_id == bill_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@payment_router.put("/{bill_id}/update-promotion", description="update payment", response_model=PaymentSchema)
def update(bill_id: Annotated[int, Path(..., title="The ID of the payment to update")],
           pro_id: Annotated[int, Query(..., title="Promotion ID")],
           force: Annotated[bool, Query(..., title="Force update promotion")]= False,
           token=Depends(APIKeyHeader(name='x-token', auto_error=True, )),
           s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    old_payment: PaymentTable = s.query(PaymentTable).filter(PaymentTable.bill_id == bill_id).first()
    if not old_payment:
        raise HTTPException(status_code=404, detail="payment_id not found")

    if old_payment.payment_status == "Processing":
        check_pro_id_fk = s.query(PromotionTable).filter(PromotionTable.pro_id == pro_id).first()
        if check_pro_id_fk is None:
            raise HTTPException(status_code=422, detail='Promotion ID not found')
        if old_payment.pro_id is not None and force is False:
            raise HTTPException(status_code=422, detail='Payment already have promotion, consider use Force option')
        old_payment.pro_id = pro_id
        s.merge(old_payment)
        old_payment.discounts = check_pro_id_fk.discount * old_payment.total
        old_payment.actual_payment = old_payment.total - old_payment.discounts
    elif old_payment.payment_status == "Success":
        raise HTTPException(status_code=422, detail="Can't update promotion after payment success")
    else:
        raise HTTPException(status_code=422, detail="Can't update promotion after payment cancel")
    s.commit()
    s.refresh(old_payment)
    return old_payment


@payment_router.put("/{bill_id}/update-status", description="update payment status", response_model=PaymentSchema)
def update(bill_id: Annotated[int, Path(..., title="The ID of the payment to update")],
           payment_status: Annotated[PaymentStatusEnum, Query(..., title="Payment Status")],
           token: str = Depends(APIKeyHeader(name='x-token', auto_error=True)),
           s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    old_payment: PaymentTable = s.query(PaymentTable).filter(PaymentTable.bill_id == bill_id).first()
    if not old_payment:
        raise HTTPException(status_code=404, detail="payment_id not found")
    if old_payment.payment_status == "Failed":
        raise HTTPException(status_code=422, detail="Can't update status after payment failed")
    elif old_payment.payment_status == "Success":
        raise HTTPException(status_code=422, detail="Can't update status after payment success")
    else:
        old_payment.payment_status = payment_status
        if payment_status == "Failed":
            bill_details_list = s.query(BillDetailTable).filter(BillDetailTable.bill_id == old_payment.bill_id).all()
            for bill_detail in bill_details_list:
                rollback_shipment: ShipmentTable = s.query(ShipmentTable).filter(
                    ShipmentTable.shipment_id == bill_detail.shipment_id).first()
                rollback_shipment.quantity += bill_detail.quantity
                s.merge(rollback_shipment)
        elif payment_status == "Success":
            if old_payment.received is None:
                raise HTTPException(status_code=422, detail="Received is required")
            if old_payment.payment_method is None:
                raise HTTPException(status_code=422, detail="Payment Method is required")
            if old_payment.received < old_payment.actual_payment:
                raise HTTPException(status_code=422, detail="Received less than actual payment")
            if old_payment.received is None:
                raise HTTPException(status_code=422, detail="Received is required")
            old_payment.payment_date = text("current_timestamp")
        s.merge(old_payment)
        s.commit()
        s.refresh(old_payment)
    return old_payment


@payment_router.put("/{bill_id}/update-payment-method", description="update payment", response_model=PaymentSchema)
def update(bill_id: Annotated[int, Path(..., title="The ID of the payment to update")],
           payment_method: Annotated[str, Query(..., title="Payment Method")],
           token=Depends(APIKeyHeader(name='x-token', auto_error=True, )),
           s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    old_payment: PaymentTable = s.query(PaymentTable).filter(PaymentTable.bill_id == bill_id).first()
    if not old_payment:
        raise HTTPException(status_code=404, detail="payment_id not found")
    if old_payment.payment_status == "Processing":
        old_payment.payment_method = payment_method
        s.merge(old_payment)
    s.commit()
    s.refresh(old_payment)
    return PaymentSchema(**old_payment.toDict())


@payment_router.put("/{bill_id}/update-received", description="update payment receive", response_model=PaymentSchema)
def update(bill_id: Annotated[int, Path(..., title="The ID of the payment to update")],
           payment_receive: Annotated[float, Query(..., title="Payment Received")],
           token: str = Depends(APIKeyHeader(name='x-token', auto_error=True)),
           s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    old_payment: PaymentTable = s.query(PaymentTable).filter(PaymentTable.bill_id == bill_id).first()
    if not old_payment:
        raise HTTPException(status_code=404, detail="payment_id not found")
    if old_payment.payment_status == "Processing":
        old_payment.received = payment_receive

        if old_payment.received < old_payment.actual_payment:
            raise HTTPException(status_code=422, detail="Received less than actual payment")
        if old_payment.received >= old_payment.actual_payment:
            old_payment.change = old_payment.received - old_payment.actual_payment
        s.merge(old_payment)
        s.commit()
        s.refresh(old_payment)
    elif old_payment.payment_status == "Success":
        raise HTTPException(status_code=422, detail="Can't update received after payment success")
    else:
        raise HTTPException(status_code=422, detail="Can't update received after payment cancel")

    return old_payment
