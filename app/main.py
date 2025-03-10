# app/main.py
from fastapi import FastAPI
from app.database import Base, engine
from app.api import auth, auto_plate, bid

app = FastAPI(title="Auto Plate Bidding API")
Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(auto_plate.router, prefix="/plates", tags=["plates"])
app.include_router(bid.router, prefix="/bids", tags=["bids"])