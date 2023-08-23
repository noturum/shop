# todo: check errors
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, insert, select, delete
from sqlalchemy.orm import Session, DeclarativeBase, relationship
from sqlalchemy.orm import mapped_column

from settings import String as string

class Base(DeclarativeBase):
    ...


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    count = Column(Integer)
    def __repr__(self):
        return f'{self.name}\n{self.description}'

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer)
    name = Column(String)
    type = Column(String)
    items = relationship("UserCart")





class UserCart(Base):
    __tablename__ = 'user_cart'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    item = Column(ForeignKey('item.id', ondelete='CASCADE'), nullable=False, index=True)
    count =Column(Integer)





class Database():
    def __init__(self):
        self.__engine = create_engine(string.sqlite, echo=True)
        self.session = Session(self.__engine)
        Base.metadata.create_all(self.__engine)
    def insert(self,table,returning=None,**values):
        if returning:
            returns=self.session.execute(insert(table).values(**values).returning(returning)).fetchone()
            self.session.commit()
            return returns
        else:
            self.session.execute(insert(table).values(**values))
            self.session.commit()

    def is_available_items(self,id_item,count):
        return True if count<=self.select(Item.count,(Item.id==id_item,),one=True)[0] else False
    def update(self, table, filter: list, values: dict):
        self.session.query(table).filter(*filter).update(values)
        self.session.commit()

    def select(self, table, filter=(True,), count=False, one=False):
        if count:
            return self.session.query(table).filter(*filter).count()
        else:
            return self.session.query(table).filter(*filter).one() if one else self.session.query(table).filter(
                *filter).all()

    def delete(self, table, filter: list,returning=None ):
        if returning:
            returns=self.session.execute(delete(table).returning(returning)).fetchone()
            self.session.commit()
            return returns
        else:
            self.session.query(table).filter(*filter).delete()
            self.session.commit()





