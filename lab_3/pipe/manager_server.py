# enhanced_manager.py
from fastapi import FastAPI
import uvicorn
from typing import Dict
import threading
from manager import ProductManager

app = FastAPI()
current_leader = None
product_manager = None

@app.on_event("startup")
async def startup_event():
    global product_manager
    product_manager = ProductManager()
    threading.Thread(target=product_manager.start, daemon=True).start()

@app.post("/update_leader")
async def update_leader(leader_info: Dict):
    global current_leader
    current_leader = leader_info["leader_port"]
    return {"status": "success", "current_leader": current_leader}

@app.get("/current_leader")
async def get_current_leader():
    return {"current_leader": current_leader}

if __name__ == "__main__":
    uvicorn.run(app, host="8080", port=8080)