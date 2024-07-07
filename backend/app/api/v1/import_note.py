from fastapi import APIRouter, Depends
from fastapi.security import APIKeyHeader
from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from db.session import getSession
from schemas.import_note import ImportNoteSchema, ImportNoteSchemas
from db.tables import GoodsTable, ShipmentTable
from db.tables import ImportNoteTable
from fastapi import HTTPException

import_note_router = APIRouter()


def isHaveForeignKey(shipment_id: int, goods_id: int, s: Session):
    good_table = s.query(GoodsTable.goods_id).filter(GoodsTable.goods_id == goods_id).first()
    shipment_table = s.query(ShipmentTable.shipment_id).filter(ShipmentTable.shipment_id == shipment_id).first()
    if good_table is None:
        raise HTTPException(status_code=422, detail="Goods ID not found")
    if shipment_table is None:
        raise HTTPException(status_code=422, detail="Shipment ID not found")


def isHaveImportId(import_id: int, s: Session):
    import_note = s.query(ImportNoteTable.import_id).filter(ImportNoteTable.import_id == import_id).first()
    if import_note is None:
        raise HTTPException(status_code=404, detail="Import ID not found")


def checkWritePermission(token: str, s: Session):
    sql_statement = text('select "Role".IMPORT_NOTE_WRITE '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.import_note_write == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


def checkReadPermission(token: str, s: Session):
    sql_statement = text('select "Role".IMPORT_NOTE_READ '
                         'from "Account","AccountToken","Role" '
                         'where "Account".USERNAME = "AccountToken".USERNAME '
                         'and "Account".ROLE_ID = "Role".role_id '
                         'and "AccountToken".TOKEN = :token')

    result = s.execute(sql_statement, {'token': token}).fetchone()
    if result is None or result.import_note_read == 0:
        raise HTTPException(status_code=403, detail="Permission Deny")


@import_note_router.post("/", response_model=ImportNoteSchema, status_code=201, summary="create new import note")
def create(new_import_note: ImportNoteSchema,
           token: str = Depends(APIKeyHeader(name='x-token', auto_error=True)),
           s: Session = Depends(getSession)):
    checkWritePermission(token, s)
    new_import_note = ImportNoteTable(**new_import_note.toDict())
    isHaveForeignKey(new_import_note.shipment_id, new_import_note.goods_id, s)
    new_import_note.create_date = None
    new_import_note.import_id = None
    new_import_note.last_modified_date = None
    s.add(new_import_note)
    s.commit()
    s.refresh(new_import_note)
    return new_import_note.toDict()


@import_note_router.get("/", response_model=ImportNoteSchemas, status_code=200, summary="get all import note")
def read(s: Session = Depends(getSession), token: str = Depends(APIKeyHeader(name="x-token", auto_error=True))):
    checkReadPermission(token, s)
    import_note = s.query(ImportNoteTable).all()
    return {"data": import_note}


@import_note_router.put("/", response_model=ImportNoteSchema, status_code=200, summary="update import note")
def update(update_import_note: ImportNoteSchema, s: Session = Depends(getSession), token: str = Depends(APIKeyHeader(name="x-token", auto_error=True))):
    checkWritePermission(token, s)
    update_table = ImportNoteTable(**update_import_note.toDict())
    isHaveImportId(update_table.import_id, s)
    isHaveForeignKey(update_table.shipment_id, update_table.goods_id, s)
    old_import_note = s.query(ImportNoteTable).filter(ImportNoteTable.import_id == update_table.import_id).first()
    update_table.create_date = old_import_note.create_date
    update_table.last_modified_date = None
    s.merge(update_table)
    s.commit()
    s.refresh(old_import_note)
    return old_import_note.toDict()


@import_note_router.delete("/{import_id}", status_code=204, summary="delete import note")
def delete(import_id: int, s: Session = Depends(getSession), token: str = Depends(APIKeyHeader(name="x-token", auto_error=True))):
    checkWritePermission(token, s)
    isHaveImportId(import_id, s)
    import_note = s.query(ImportNoteTable).filter(ImportNoteTable.import_id == import_id).first()
    s.delete(import_note)
    s.commit()
    return None
