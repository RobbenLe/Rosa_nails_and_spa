from fastapi import FastAPI

app = FastAPI()

services = [
    {"name": "Manicure", "price": 25},
    {"name": "Pedicure", "price": 35},
    {"name": "Gel Polish", "price": 30},
]

@app.get("/")
def hello_world():
    return {"message":"Hello World", "status":200}

@app.get("/services")
def list_services():
    return services