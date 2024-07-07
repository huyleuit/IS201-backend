import datetime
import time

from fastapi import APIRouter, HTTPException
from db.session import getSession
from db.tables import MembershipCardTable
from schemas.membershipcard import MembershipRQSchema, MembershipRpSchemas, MemberShipCardRPSchema
from sqlalchemy.orm import Session
from fastapi import Depends
import sqlalchemy
from utils import getEmpId
from fastapi.security import APIKeyHeader
from sqlalchemy import text

membership_router = APIRouter()


def checkWritePermission(token: str, s: Session):
    sql_statement = text('select "Role".MEMBERSHIP_CARD_WRITE '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.membership_card_write == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


def checkReadPermission(token: str, s: Session):
    sql_statement = text('select "Role".MEMBERSHIP_CARD_READ '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.membership_card_read == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


@membership_router.post('/', status_code=201, response_model=MemberShipCardRPSchema, summary='Create Membership Card')
def create(new_card: MembershipRQSchema,
           token: str = Depends(APIKeyHeader(name='x-token', auto_error=True)),
           s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    check_email_duplicate = s.query(MembershipCardTable).filter(MembershipCardTable.email == new_card.email).first()
    if check_email_duplicate:
        raise HTTPException(status_code=400, detail="Email already exists")
    new_card = MembershipCardTable(**new_card.toDict())
    try:
        new_card.emp_id = getEmpId(token, s)
        new_card.start_date = datetime.datetime.now(tz=datetime.timezone.utc)
        new_card.end_date = new_card.start_date + datetime.timedelta(days=365)
        new_card.card_point = 0
        new_card.card_rank = "Normal"
        new_card.status = "Active"
        s.add(new_card)
        s.commit()
        s.refresh(new_card)
        return new_card.toDict()
    except sqlalchemy.exc.IntegrityError as e:
        s.rollback()
        cause = e.__cause__.__str__()
        print(cause)
        raise HTTPException(status_code=500, detail=cause)


@membership_router.get('/', response_model=MembershipRpSchemas, summary='Get Membership Cards')
def read(s: Session = Depends(getSession),
         token: str = Depends(APIKeyHeader(name='x-token', auto_error=True)),
         ):
    checkReadPermission(token, s)
    data = s.query(MembershipCardTable).all()
    return MembershipRpSchemas(data=[i.toDict() for i in data])


@membership_router.get("/{card_id}", response_model=MemberShipCardRPSchema, summary='Get Membership Card')
def read(card_id: int, s: Session = Depends(getSession),
         token: str = Depends(APIKeyHeader(name='x-token', auto_error=True)),
         ):
    checkReadPermission(token, s)
    card = s.query(MembershipCardTable).filter(MembershipCardTable.card_id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="card_id not found")
    return card.toDict()


@membership_router.put("/", response_model=MemberShipCardRPSchema, summary='Update Membership Card')
def update(update_card: MemberShipCardRPSchema, s: Session = Depends(getSession)):
    try:
        update_card = MembershipCardTable(**update_card.toDict())
        old_card: MembershipCardTable = s.query(MembershipCardTable).filter(
            MembershipCardTable.card_id == update_card.card_id).first()
        if not old_card:
            raise HTTPException(status_code=404, detail="card_id not found")
        s.merge(update_card)
        s.commit()
        return update_card.toDict()
    except sqlalchemy.exc.IntegrityError as e:
        s.rollback()
        cause = e.__cause__.__str__()
        print(cause)
        raise HTTPException(status_code=500, detail=cause)


@membership_router.delete("/{card_id}", status_code=204, summary='Delete Membership Card')
def delete(card_id: int, s: Session = Depends(getSession)):
    card = s.query(MembershipCardTable).filter(MembershipCardTable.card_id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="card_id not found")
    s.delete(card)
    s.commit()
    return None
