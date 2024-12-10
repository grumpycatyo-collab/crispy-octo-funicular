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
async def upload_file(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    try:
        content = await file.read()

        # Create new file upload record
        db_file = models.FileUpload(
            filename=file.filename,
            content=content,
            content_type=file.content_type
        )

        # If it's a JSON file, parse and store the JSON content
        if file.filename.endswith('.json'):
            try:
                json_data = json.loads(content)
                db_file.json_content = json.dumps(json_data)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON file")

        # Save to database
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        # Return response
        response = {
            "id": db_file.id,
            "filename": db_file.filename,
            "content_type": db_file.content_type,
            "upload_date": db_file.upload_date
        }

        if db_file.json_content:
            response["json_content"] = json.loads(db_file.json_content)

        return response

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
server = uvicorn.Server(config)

if __name__ == "__main__":
    uvicorn_thread = threading.Thread(target=server.run)
    # http_thread = threading.Thread(target=start_http_server)
    # ws_thread = threading.Thread(target=start_websocket_server)
    # tcp_thread = threading.Thread(target=start_tcp_server)

    uvicorn_thread.start()
    # http_thread.start()
    # ws_thread.start()
    # tcp_thread.start()

    uvicorn_thread.join()
    # http_thread.join()
    # ws_thread.join()
    # tcp_thread.join()

