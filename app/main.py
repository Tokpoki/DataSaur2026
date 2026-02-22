from fastapi import FastAPI
from .database import engine, Base
from .routers import tickets

app = FastAPI(title="FIRE Engine")

Base.metadata.create_all(bind=engine)

app.include_router(tickets.router)


@app.get("/")
def root():
    return {"message": "FIRE backend is running 🔥"}