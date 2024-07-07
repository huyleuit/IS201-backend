from sqlalchemy import (create_engine)
from sqlalchemy.orm import Session

USER = 'C##is210'
PASS = 'is210'
HOSTNAME = 'is210-db'
SERVICE_NAME = "XE"
PORT = 1521
from sqlalchemy import text
DATABASE_URL = f"oracle+oracledb://{USER}:{PASS}@{HOSTNAME}:{PORT}/?service_name={SERVICE_NAME}"
engine = create_engine(DATABASE_URL)


def getSession() -> Session:
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


def getSessionSerializableMode() -> Session:
    db = Session(bind=engine)
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))
        yield db
    finally:
        db.close()
#Base.metadata.create_all(engine)
