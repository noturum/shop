# todo: check errors
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, select
from sqlalchemy.orm import Session, DeclarativeBase, relationship
from sqlalchemy.orm import mapped_column
import settings


class Base(DeclarativeBase):
    ...


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    coutn = Column(Integer)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer)
    name = Column(String)
    type = Column(String)



class Cart(Base):
    __tablename__ = 'cart'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, ForeignKey("user.id"))
    cartforuser = relationship("User",backref="carts")

class CartItems(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    item = Column(ForeignKey('item.id', ondelete='CASCADE'), nullable=False, index=True)
    cart = Column(ForeignKey('cart.id', ondelete='CASCADE'), nullable=False, index=True)
    items = relationship("Item", backref="items")
    carts = relationship("Cart", backref="cart")


class Database():
    def __init__(self):
        self.__engine = create_engine(settings.String.sqlite, echo=True)
        self.session = Session(self.__engine)
        Base.metadata.create_all(self.__engine)

    def update(self, table, filter: list, values: dict):
        self.session.query(table).filter(*filter).update(values)
        self.session.commit()

    def select(self, table, filter=True, count=False, one=False):
        if count:
            return self.session.query(table).filter(filter).count()
        else:
            return self.session.query(table).filter(*filter).one() if one else self.session.query(table).filter(
                filter).all()

    def delete(self, table, filter: list, values: dict):
        self.session.query(table).filter(*filter).delete()
        self.session.commit()

da=Database()
a=da.session.query(User).all()[0]
print(da.session.query(User).all()[0])



