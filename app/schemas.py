from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    price_range: str
    brand: str
    sold: str
    rating: str
    rating_count: str
    product_option: dict
    description: str
    url: str
class ProductCreate(ProductBase):
    pass 
class Product(ProductBase):
    id: int
    class Config:
        orm_mode = True
# Schema for the request body
class ProductRequest(BaseModel):
    url: str
    reset: bool = True  # Optional: Whether to reset the database table