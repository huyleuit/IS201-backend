from sqlalchemy import Column, INTEGER, ForeignKey, DateTime, Integer, Identity, String, CheckConstraint, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects import oracle

Base = declarative_base()


class BaseTable(Base):
    __abstract__ = True
    create_date = Column(DateTime, nullable=False)
    create_by = Column(String(50), nullable=False)
    last_modified_date = Column(DateTime, nullable=False)
    last_modified_by = Column(String(50), nullable=False)

    def toDict(self):
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }


class EmpTable(BaseTable):
    __tablename__ = 'Employee'
    emp_id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    emp_name = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('Role.role_id'), nullable=False)
    gender = Column(String(10), CheckConstraint("gender in('Nam', 'Nu', 'Khac')"), nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    salary = Column(Float(precision=10).with_variant(oracle.FLOAT(10), 'oracle'))
    kpi = Column(Integer)


class AccountTable(BaseTable):
    __tablename__ = 'Account'
    username: str = Column(String(50), nullable=False, primary_key=True)
    role_id = Column(Integer, nullable=True)
    emp_id = Column(Integer, ForeignKey('Employee.emp_id'), nullable=False)
    status = Column(String(50), CheckConstraint("status in ('Active', 'Inactive',pw_not_set)"), nullable=False)
    password = Column(String(255), nullable=False)
    salt = Column(String(50), nullable=False)
    create_by = Column(String(50), nullable=False)
    create_date = Column(DateTime, nullable=False)
    last_modified_by = Column(String(50), nullable=False)
    last_modified_date = Column(DateTime, nullable=False)

    def toDict(self):
        return {
            "username": self.username,
            "role_id": self.role_id,
            "create_date": self.create_date,
            "last_modified_date": self.last_modified_date
        }


class AccountTokenTable(BaseTable):
    __tablename__ = 'AccountToken'
    no = Column(Integer, Identity(start=1), primary_key=True)
    username = Column(String(50), ForeignKey('Account.username', ondelete='CASCADE'))
    token = Column(String(255), nullable=False)
    expire = Column(DateTime, nullable=False)


class GoodsTable(BaseTable):
    __tablename__ = 'Goods'
    goods_id = Column(Integer, primary_key=True)
    goods_name = Column(String(255), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey('Category.category_id'))
    create_by = Column(String(20), nullable=False)
    last_modified_by = Column(String(20), nullable=False)


class CategoryTable(BaseTable):
    __tablename__ = 'Category'
    category_id = Column(Integer, primary_key=True, nullable=False)
    category_name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=True)


class PromotionTable(BaseTable):
    __tablename__ = 'Promotion'
    pro_id = Column(Integer, primary_key=True, autoincrement=True)
    pro_name = Column(String(255), nullable=False)
    discount = Column(Float(10), nullable=False)
    content = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)


class MembershipCardTable(Base):
    __tablename__ = 'MembershipCard'
    card_id = Column(Integer, primary_key=True, autoincrement=True)
    member_name = Column(String(255), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255))
    card_point = Column(Integer, nullable=False)
    card_rank = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False)
    emp_id = Column(Integer, ForeignKey('Employee.emp_id'), nullable=False)

    def toDict(self):
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }

    __table_args__ = (
        CheckConstraint("status in ('Active', 'Inactive', 'expired')", name='status_check'),
    )


class BillTable(BaseTable):
    __tablename__ = 'Bill'
    bill_id = Column(Integer, primary_key=True, nullable=False)
    emp_id = Column(Integer, ForeignKey('Employee.emp_id'), nullable=False)


class BillDetailTable(Base):
    __tablename__ = 'BillDetails'
    goods_id = Column(Integer, ForeignKey('Goods.goods_id'), primary_key=True, nullable=False)
    shipment_id = Column(Integer, ForeignKey('Shipment.shipment_id'), nullable=False)
    bill_id = Column(Integer, ForeignKey('Bill.bill_id'), primary_key=True, nullable=False)
    unit_price = Column(Float(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    total = Column(Float(10), nullable=False)

    def toDict(self):
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }


class RoleTable(Base):
    __tablename__ = 'Role'
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(50), unique=True, nullable=False)
    account_read = Column(Integer, CheckConstraint("account_read in (0, 1)"), nullable=False)
    account_write = Column(Integer, CheckConstraint("account_write in (0, 1)"), nullable=False)
    account_token_read = Column(Integer, CheckConstraint("account_token_read in (0, 1)"), nullable=False)
    account_token_write = Column(Integer, CheckConstraint("account_token_write in (0, 1)"), nullable=False)
    employee_read = Column(Integer, CheckConstraint("employee_read in (0, 1)"), nullable=False)
    employee_write = Column(Integer, CheckConstraint("employee_write in (0, 1)"), nullable=False)
    category_read = Column(Integer, CheckConstraint("category_read in (0, 1)"), nullable=False)
    category_write = Column(Integer, CheckConstraint("category_write in (0, 1)"), nullable=False)
    goods_read = Column(Integer, CheckConstraint("goods_read in (0, 1)"), nullable=False)
    goods_write = Column(Integer, CheckConstraint("goods_write in (0, 1)"), nullable=False)
    shipment_read = Column(Integer, CheckConstraint("shipment_read in (0, 1)"), nullable=False)
    shipment_write = Column(Integer, CheckConstraint("shipment_write in (0, 1)"), nullable=False)
    membership_card_read = Column(Integer, CheckConstraint("membership_card_read in (0, 1)"), nullable=False)
    membership_card_write = Column(Integer, CheckConstraint("membership_card_write in (0, 1)"), nullable=False)
    promotion_read = Column(Integer, CheckConstraint("promotion_read in (0, 1)"), nullable=False)
    promotion_write = Column(Integer, CheckConstraint("promotion_write in (0, 1)"), nullable=False)
    bill_read = Column(Integer, CheckConstraint("bill_read in (0, 1)"), nullable=False)
    bill_write = Column(Integer, CheckConstraint("bill_write in (0, 1)"), nullable=False)
    payment_read = Column(Integer, CheckConstraint("payment_read in (0, 1)"), nullable=False)
    payment_write = Column(Integer, CheckConstraint("payment_write in (0, 1)"), nullable=False)
    bill_details_read = Column(Integer, CheckConstraint("bill_details_read in (0, 1)"), nullable=False)
    bill_details_write = Column(Integer, CheckConstraint("bill_details_write in (0, 1)"), nullable=False)
    export_note_read = Column(Integer, CheckConstraint("export_note_read in (0, 1)"), nullable=False)
    export_note_write = Column(Integer, CheckConstraint("export_note_write in (0, 1)"), nullable=False)
    import_note_read = Column(Integer, CheckConstraint("import_note_read in (0, 1)"), nullable=False)
    import_note_write = Column(Integer, CheckConstraint("import_note_write in (0, 1)"), nullable=False)

    def toDict(self):
        return {
            k: v for k, v in self.__dict__.items() if not k.startswith("_")
        }


class ImportNoteTable(BaseTable):
    __tablename__ = 'ImportNote'
    import_id = Column(Integer, primary_key=True, autoincrement=True)
    import_date = Column(DateTime, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float(10), nullable=False)
    goods_id = Column(Integer, ForeignKey('Goods.goods_id'), nullable=False)
    shipment_id = Column(Integer, ForeignKey('Shipment.shipment_id'), nullable=False)


class ShipmentTable(BaseTable):
    __tablename__ = 'Shipment'
    shipment_id = Column(Integer, primary_key=True, autoincrement=True)
    shipment_name = Column(String(255), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    manufacture_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    quantity = Column(Integer, nullable=False)
    good_id = Column(Integer, ForeignKey('Goods.goods_id'), nullable=False)
    price = Column(Float(10), nullable=False)


from sqlalchemy import text


class PaymentTable(BaseTable):
    __tablename__ = 'Payment'
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    pro_id = Column(Integer, ForeignKey('Promotion.pro_id'))
    card_id = Column(Integer, ForeignKey('MembershipCard.card_id'))
    bill_id = Column(Integer, ForeignKey('Bill.bill_id'), nullable=False)
    payment_status = Column(String(50), nullable=False)
    payment_method = Column(String(50))
    discounts = Column(Float(10))
    total = Column(Float(10), nullable=False)
    actual_payment = Column(Float(10), nullable=False)
    received = Column(Float(10))
    change = Column(Float(10))
    payment_date = Column(DateTime)
    __table_args__ = (
        CheckConstraint(text("payment_status in ('Success', 'Processing', 'Failed')"), name='payment_status_check'),
    )
