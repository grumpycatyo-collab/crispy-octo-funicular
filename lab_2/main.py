import threading
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import json
from app import models, schemas, database
from app.database import Base, engine
from app.websocket_handler import start_websocket_server, start_http_server
from app.tcp_server import start_tcp_server
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@app.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products


@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product.dict().items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    if file.filename.endswith('.json'):
        data = json.loads(content)
        return {"filename": file.filename, "content": data}
    return {"filename": file.filename}


config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
server = uvicorn.Server(config)

if __name__ == "__main__":
    uvicorn_thread = threading.Thread(target=server.run)
    http_thread = threading.Thread(target=start_http_server)
    ws_thread = threading.Thread(target=start_websocket_server)
    tcp_thread = threading.Thread(target=start_tcp_server)

    uvicorn_thread.start()
    http_thread.start()
    ws_thread.start()
    tcp_thread.start()

    uvicorn_thread.join()
    http_thread.join()
    ws_thread.join()
    tcp_thread.join()

