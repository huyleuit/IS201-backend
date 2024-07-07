import sqlalchemy
from fastapi import APIRouter, HTTPException

from db.tables import GoodsTable
from schemas.goods import GoodSchema, GoodSchemas
from db.session import getSession
from fastapi import Depends
from sqlalchemy.orm import Session

goods_router = APIRouter()


@goods_router.post('/', summary='create new Good', response_model=GoodSchema, status_code=201)
def create(new_goods: GoodSchema, s: Session = Depends(getSession)):
    new_goods = GoodsTable(**new_goods.toDict())
    try:
        check_duplicate = s.query(GoodsTable).filter(GoodsTable.goods_name == new_goods.goods_name).first()
        if check_duplicate is not None:
            raise HTTPException(status_code=400, detail="goods_name already exists")
        new_goods.goods_id = None
        s.add(new_goods)
        s.commit()
        s.refresh(new_goods)
    except sqlalchemy.exc.IntegrityError as e:
        s.rollback()
        print(e.__cause__)
        raise HTTPException(status_code=500, detail="Some thing not right, check your server log")
    return GoodSchema(**new_goods.toDict())


@goods_router.get('/', summary='get all Goods', response_model=GoodSchemas)
def read(s: Session = Depends(getSession)):
    data = s.query(GoodsTable).all()
    return GoodSchemas(data=[GoodSchema(**i.toDict()) for i in data])


@goods_router.get("/{goods_id}", summary="get good by id", response_model=GoodSchema)
def read(goods_id: int, s: Session = Depends(getSession)):
    good: GoodsTable = s.query(GoodsTable).filter(GoodsTable.goods_id == goods_id).first()
    if not good:
        raise HTTPException(status_code=404, detail="goods_id not found")
    return GoodSchema(**good.toDict())


@goods_router.put("/", summary="update good", response_model=GoodSchema)
def update(updated_good: GoodSchema, s: Session = Depends(getSession)):
    try:
        updated_good = GoodsTable(**updated_good.toDict())
        old_good: GoodsTable = s.query(GoodsTable).filter(GoodsTable.goods_id == updated_good.goods_id).first()
        if not old_good:
            raise HTTPException(status_code=404, detail="goods_id not found")
        updated_good.create_date = old_good.create_date
        updated_good.last_modified_date = None
        s.merge(updated_good)
        s.commit()
        s.refresh(old_good)
    except sqlalchemy.exc.IntegrityError as e:
        s.rollback()
        print(e.__cause__)
        raise HTTPException(status_code=500, detail="Some thing not right, check your server log")
    return old_good.toDict()


@goods_router.delete("/{goods_id}", summary="delete good", status_code=204)
def delete(goods_id: int, s: Session = Depends(getSession)):
    good: GoodsTable = s.query(GoodsTable).filter(GoodsTable.goods_id == goods_id).first()
    if not good:
        raise HTTPException(status_code=404, detail="goods_id not found")
    try:
        s.delete(good)
        s.commit()
    except sqlalchemy.exc.IntegrityError as e:
        if str(e).__contains__("child record found"):
            raise HTTPException(status_code=422,
                                detail="This bill has child record, can't not delete, please delete child record first")
