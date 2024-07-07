import os
from datetime import timedelta, datetime
from fastapi import FastAPI, HTTPException
from fastapi.security import APIKeyHeader
from api.v1.emp import emp_router
from api.v1.goods import goods_router
from api.v1.shipment import shipment_router
from api.v1.isolation_demo import isolation_router
# from api.v1.goods import goods_router
from api.v1.payment import payment_router
from api.v1.import_note import import_note_router
from api.v1.category import category_router
from api.v1.account import account_router
from api.v1.promotion import promotion_router
from api.v1.bill import bill_router
from api.v1.membership_card import membership_router
from api.v1.bill_detail import bill_detail_router
from api.v1.role import role_router
from fastapi import Depends
from db.session import getSession
from sqlalchemy.orm import Session
import uvicorn
from db.tables import AccountTokenTable

COMMIT_HASH = os.getenv('COMMIT_HASH', 'unknown')
app = FastAPI(
    title="API list for frontend application",
    version=f'pre-alpha-{COMMIT_HASH}',
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    description="A list of api for Front-end application", )
header_schema = APIKeyHeader(name='x-token', auto_error=True)


def isTokenValid(token: str = Depends(header_schema), s: Session = Depends(getSession)):
    # admin_token = 'MWQ+S348U1B6SHVYeTgzYQ=='
    #
    # if token != admin_token:
    #     raise HTTPException(status_code=401, detail='Invalid token')
    check_token: AccountTokenTable = s.query(AccountTokenTable).filter(AccountTokenTable.token == token).first()
    if check_token is None:
        raise HTTPException(status_code=401, detail='Invalid token')
    if check_token.expire + timedelta(hours=7) < datetime.now():
        raise HTTPException(status_code=401, detail='Token expired')


app.include_router(role_router, prefix='/api/v1/role', tags=['Role'])
app.include_router(account_router, prefix='/api/v1/account', tags=['Account'])
app.include_router(emp_router, prefix='/api/v1/emp', tags=['Employee'], dependencies=[Depends(isTokenValid)])
app.include_router(category_router, prefix='/api/v1/category', tags=['Category'], dependencies=[Depends(isTokenValid)])
app.include_router(goods_router, prefix='/api/v1/goods', tags=['Goods'], dependencies=[Depends(isTokenValid)])
app.include_router(import_note_router, prefix='/api/v1/import_note', tags=['Import Note'],
                   dependencies=[Depends(isTokenValid)])
app.include_router(promotion_router, prefix='/api/v1/promotion', tags=['Promotion'],
                   dependencies=[Depends(isTokenValid)])
app.include_router(membership_router, prefix='/api/v1/membership', tags=['Membership'],
                   dependencies=[Depends(isTokenValid)])
app.include_router(shipment_router, prefix='/api/v1/shipment', tags=['Shipment'], dependencies=[Depends(isTokenValid)])
app.include_router(bill_router, prefix='/api/v1/bill', tags=['Bill'], dependencies=[Depends(isTokenValid)])
app.include_router(bill_detail_router, prefix='/api/v1/bill_detail', tags=['Bill Detail'],
                   dependencies=[Depends(isTokenValid)])
app.include_router(payment_router, prefix='/api/v1/payment', tags=['Payment'], dependencies=[Depends(isTokenValid)])
app.include_router(isolation_router, prefix='/api/v1/isolation', tags=['Isolation'],
                   dependencies=[Depends(isTokenValid)], deprecated=True)
if __name__ == "__main__":
    uvicorn.run(app=app, port=8009, host="0.0.0.0")
