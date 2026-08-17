from fastapi import FastAPI

app = FastAPI()

services = [
    {"name": "Manicure", "price": 25},
    {"name": "Pedicure", "price": 35},
    {"name": "Gel Polish", "price": 30},
]

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
open_days = []
for day in days:
    open_days.append({"day": day, "from": "10:00", "to": "18:00"})

salon_info = {
    "name": "Rosa Nails & Spa",
    "phone": "0633426798",
    "open_days" : open_days,
}

@app.get("/")
def hello_world():
    return {"message":"Hello World", "status":200}

@app.get("/services")
def list_services():
    return services

@app.get("/salon")
def get_salon():
    return salon_info