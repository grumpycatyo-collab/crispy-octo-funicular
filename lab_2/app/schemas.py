from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    price: float
    currency: str
    link: str
    screen_size: str

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True