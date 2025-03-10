from pydantic import BaseModel
from datetime import datetime

class BidBase(BaseModel):
    amount: float
    plate_id: int

class BidCreate(BidBase):
    pass

class Bid(BidBase):
    id: int
    created_at: datetime
    user_id: int

    class Config:
        orm_mode = True