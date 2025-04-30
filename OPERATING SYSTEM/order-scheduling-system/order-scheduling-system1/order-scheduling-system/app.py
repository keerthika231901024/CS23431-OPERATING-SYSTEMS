from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from scheduler import read_orders, schedule_orders
from datetime import datetime
import csv
import os

app = FastAPI()

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data.csv")


# Serve index.html directly from root
@app.get("/")
async def root():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

# Serve additional static files (like CSS/JS in same folder)
@app.get("/{file_name}")
async def serve_file(file_name: str):
    file_path = os.path.join(BASE_DIR, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(content={"error": "File not found"}, status_code=404)

# API endpoint to get scheduled orders
@app.get("/api/orders")
async def get_orders(algorithm: str = "Priority", quantum: int = 5):
    orders = read_orders(DATA_PATH)
    scheduled = schedule_orders(orders, algorithm, quantum)
    return {"algorithm": algorithm, "orders": scheduled}

# API endpoint to add a new order
@app.post("/api/orders")
async def add_order(request: Request):
    data = await request.json()
    with open(DATA_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            data["customer_name"],
            data["dish_name"],
            data["prep_time"],
            data["category"],
            data["priority"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
    return {"message": "Order added"}