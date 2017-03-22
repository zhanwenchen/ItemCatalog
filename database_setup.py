from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    items = relationship("Item", cascade="all, delete", backref="parent")

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    description = Column(String(250))
    # category_id = Column(Integer, ForeignKey('category.id'))
    category_id = Column(Integer, ForeignKey(Category.id))
    creator = Column(String(80), nullable = False)
    # category = relationship("Category",
    #     backref=backref("items", cascade="all, delete-orphan")
    # )


    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'description'  : self.description,
           'id'           : self.id,
           'creator'      : self.creator
       }



engine = create_engine('sqlite:///itemcatalog.db')


Base.metadata.create_all(engine)
