from sqlalchemy import Column, Integer, String, JSON
from app.database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price_range = Column(String)
    brand = Column(String)
    sold = Column(String)
    rating = Column(String)
    rating_count = Column(String)
    product_option = Column(JSON)
    description = Column(String)
    url = Column(String)