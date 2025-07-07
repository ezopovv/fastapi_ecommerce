from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
#from sqlalchemy.schema import CreateTable

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=True)
    rating_id = Column(Integer, ForeignKey('ratings.id'))
    comment = Column(String)
    comment_date = Column(Date)
    is_active = Column(Boolean, default=True)

    products = relationship("Product", back_populates="review")


#print(CreateTable(Category.__table__))