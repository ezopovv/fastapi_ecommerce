from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship



class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer)
    image_url = Column(String)
    stock = Column(Integer)
    category_id = Column(Integer, ForeignKey('categories.id'))
    supplier_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    rating = Column(Float)
    is_active = Column(Boolean, default=True)

    category = relationship('Category', back_populates='products')
    ratings = relationship("Rating", back_populates="products", lazy="selectin")
    review = relationship("Review", back_populates="products", lazy="selectin")

#print(CreateTable(Product.__table__))