from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import database, models, schemas
from datetime import datetime
from .auth import get_current_user

router = APIRouter()

@router.get("/bids/", response_model=list[schemas.Bid])
def get_bids(db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    bids = db.query(models.Bid).filter(models.Bid.user_id == current_user.id).all()
    return bids

@router.post("/bids/", response_model=schemas.Bid)
def create_bid(bid: schemas.BidCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == bid.plate_id).first()
    if not plate or not plate.is_active or plate.deadline <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Bidding is closed")
    if db.query(models.Bid).filter(models.Bid.user_id == current_user.id, models.Bid.plate_id == bid.plate_id).first():
        raise HTTPException(status_code=400, detail="You already have a bid on this plate")
    if bid.amount <= 0:
        raise HTTPException(status_code=400, detail="Bid amount must be positive")
    highest_bid = db.query(models.Bid).filter(models.Bid.plate_id == bid.plate_id).order_by(models.Bid.amount.desc()).first()
    if highest_bid and bid.amount <= highest_bid.amount:
        raise HTTPException(status_code=400, detail="Bid must exceed current highest bid")

    db_bid = models.Bid(amount=bid.amount, user_id=current_user.id, plate_id=bid.plate_id)
    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)
    return db_bid

@router.get("/bids/{bid_id}", response_model=schemas.Bid)
def get_bid(bid_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    bid = db.query(models.Bid).filter(models.Bid.id == bid_id, models.Bid.user_id == current_user.id).first()
    if not bid:
        raise HTTPException(status_code=403, detail="Not authorized to view this bid")
    return bid

@router.put("/bids/{bid_id}", response_model=schemas.Bid)
def update_bid(bid_id: int, bid: schemas.BidCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    db_bid = db.query(models.Bid).filter(models.Bid.id == bid_id, models.Bid.user_id == current_user.id).first()
    if not db_bid:
        raise HTTPException(status_code=403, detail="Not authorized to update this bid")
    plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == db_bid.plate_id).first()
    if not plate.is_active or plate.deadline <= datetime.utcnow():
        raise HTTPException(status_code=403, detail="Bidding period has ended")
    if bid.amount <= 0:
        raise HTTPException(status_code=400, detail="Bid amount must be positive")
    highest_bid = db.query(models.Bid).filter(models.Bid.plate_id == db_bid.plate_id).order_by(models.Bid.amount.desc()).first()
    if highest_bid and bid.amount <= highest_bid.amount and db_bid.id != highest_bid.id:
        raise HTTPException(status_code=400, detail="Bid must exceed current highest bid")

    db_bid.amount = bid.amount
    db.commit()
    db.refresh(db_bid)
    return db_bid

@router.delete("/bids/{bid_id}")
def delete_bid(bid_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    db_bid = db.query(models.Bid).filter(models.Bid.id == bid_id, models.Bid.user_id == current_user.id).first()
    if not db_bid:
        raise HTTPException(status_code=403, detail="Not authorized to delete this bid")
    plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == db_bid.plate_id).first()
    if not plate.is_active or plate.deadline <= datetime.utcnow():
        raise HTTPException(status_code=403, detail="Bidding period has ended")
    db.delete(db_bid)
    db.commit()
    return {"detail": "Bid deleted"}
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from app import schemas, models, database, dependencies
# from datetime import datetime
#
# router = APIRouter(prefix="/bids", tags=["bids"])
#
# @router.get("/", response_model=List[schemas.Bid])
# def get_bids(db: Session = Depends(database.get_db), current_user: models.User = Depends(dependencies.get_current_user)):
#     bids = db.query(models.Bid).filter(models.Bid.user_id == current_user.id).all()
#     return bids
#
# @router.post("/", response_model=schemas.Bid, status_code=status.HTTP_201_CREATED)
# def create_bid(bid: schemas.BidCreate, db: Session = Depends(database.get_db),
#               current_user: models.User = Depends(dependencies.get_current_user)):
#     plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == bid.plate_id).first()
#     if not plate or not plate.is_active or plate.deadline < datetime.utcnow():
#         raise HTTPException(status_code=400, detail="Bidding is closed")
#     if db.query(models.Bid).filter(models.Bid.user_id == current_user.id, models.Bid.plate_id == bid.plate_id).first():
#         raise HTTPException(status_code=400, detail="You already have a bid on this plate")
#     highest_bid = db.query(models.Bid).filter(models.Bid.plate_id == bid.plate_id).order_by(models.Bid.amount.desc()).first()
#     if highest_bid and bid.amount <= highest_bid.amount:
#         raise HTTPException(status_code=400, detail="Bid must exceed current highest bid")
#     if bid.amount <= 0:
#         raise HTTPException(status_code=400, detail="Bid amount must be positive")
#     db_bid = models.Bid(amount=bid.amount, user_id=current_user.id, plate_id=bid.plate_id)
#     db.add(db_bid)
#     db.commit()
#     db.refresh(db_bid)
#     return db_bid
#
# @router.get("/{id}/", response_model=schemas.Bid)
# def get_bid(id: int, db: Session = Depends(database.get_db),
#             current_user: models.User = Depends(dependencies.get_current_user)):
#     bid = db.query(models.Bid).filter(models.Bid.id == id).first()
#     if not bid or bid.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Bid not found or not authorized")
#     return bid
#
# @router.put("/{id}/", response_model=schemas.Bid)
# def update_bid(id: int, bid_update: schemas.BidCreate, db: Session = Depends(database.get_db),
#               current_user: models.User = Depends(dependencies.get_current_user)):
#     bid = db.query(models.Bid).filter(models.Bid.id == id).first()
#     if not bid or bid.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Bid not found or not authorized")
#     plate = bid.plate
#     if plate.deadline < datetime.utcnow():
#         raise HTTPException(status_code=403, detail="Bidding period has ended")
#     bid.amount = bid_update.amount
#     db.commit()
#     db.refresh(bid)
#     return bid
#
# @router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
# def delete_bid(id: int, db: Session = Depends(database.get_db),
#               current_user: models.User = Depends(dependencies.get_current_user)):
#     bid = db.query(models.Bid).filter(models.Bid.id == id).first()
#     if not bid or bid.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Bid not found or not authorized")
#     if bid.plate.deadline < datetime.utcnow():
#         raise HTTPException(status_code=403, detail="Bidding period has ended")
#     db.delete(bid)
#     db.commit()