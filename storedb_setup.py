import sys
from sqlalchemy import Column, Integer, String, ForeignKey,NUMERIC,LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine



Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    username = Column(
        String(100), nullable = False        
    )
    id = Column(
        Integer, primary_key = True
    )
    email = Column(
        String(250), nullable = False
    )
    password = Column(
        LargeBinary, nullable = False
    )
    forgouttoken = Column(
        LargeBinary, nullable = True
    )

class ProductType(Base):
    __tablename__ = 'product_type'
    name = Column(
        String(80), nullable = False        
    )
    id = Column(
        Integer, primary_key = True
    )


class Product(Base):
    __tablename__ = 'product'
    name = Column(
        String(100), nullable = False        
    )
    id = Column(
        Integer, primary_key = True
    )
    typeId = Column(
        Integer,ForeignKey('product_type.id')
    )
    userId = Column(
        Integer,ForeignKey('user.id')
    )
    desc = Column(
        String(250), nullable = False
    )
    price = Column(
        NUMERIC, nullable = False
    )
    ProductType = relationship(ProductType)
    User = relationship(User)

#######insert at end of file #######

engine = create_engine(
'sqlite:///nasserzon.db'
)

Base.metadata.create_all(engine)

