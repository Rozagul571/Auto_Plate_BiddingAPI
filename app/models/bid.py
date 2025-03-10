from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Bid(Base):
    __tablename__ = "bids"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    plate_id = Column(Integer, ForeignKey("auto_plates.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bids")
    plate = relationship("AutoPlate", back_populates="bids")
# from datetime import datetime
#
# from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
# from sqlalchemy.orm import relationship
# from app.database import Base
#
# class Bid(Base):
#     __tablename__ = "bids"
#     id = Column(Integer, primary_key=True, index=True)
#     amount = Column(Float)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     plate_id = Column(Integer, ForeignKey("auto_plates.id"))
#     created_at = Column(DateTime, default=datetime.utcnow)
#
#     user = relationship("User", back_populates="bids")
#     plate = relationship("AutoPlate", back_populates="bids")
#
