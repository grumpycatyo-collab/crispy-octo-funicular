from sqlalchemy import Column, Integer, String, Float, LargeBinary, DateTime
from database import Base
from datetime import datetime


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    currency = Column(String)
    link = Column(String)
    screen_size = Column(String)


class FileUpload(Base):
    __tablename__ = "file_uploads"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(LargeBinary)  # For storing file content
    content_type = Column(String)
    json_content = Column(String, nullable=True)  # For storing JSON content if applicable
    upload_date = Column(DateTime, default=datetime.utcnow)
