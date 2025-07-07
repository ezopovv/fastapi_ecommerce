from app.backend.db import Base
from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
#from sqlalchemy.schema import CreateTable

class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, index=True)
    grade = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    is_active = Column(Boolean, default=True)

    products = relationship("Product", back_populates="ratings")


#print(CreateTable(Category.__table__))