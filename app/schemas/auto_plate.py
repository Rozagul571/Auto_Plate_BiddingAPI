from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AutoPlateBase(BaseModel):
    plate_number: str
    description: str
    deadline: datetime

class AutoPlateCreate(AutoPlateBase):
    pass

class AutoPlate(AutoPlateBase):
    id: int
    created_by_id: int
    is_active: bool

    class Config:
        orm_mode = True
# from pydantic import BaseModel
# from datetime import datetime
# from typing import Optional, List
# from app.schemas.bid import Bid
#
# class AutoPlateBase(BaseModel):
#     plate_number: str
#     description: str
#     deadline: datetime
#
# class AutoPlateCreate(AutoPlateBase):
#     pass
#
# class AutoPlate(AutoPlateBase):
#     id: int
#     is_active: bool
#     highest_bid: Optional[float] = None
#     bids: List[Bid] = []
#
#     class Config:
#         orm_mode = True