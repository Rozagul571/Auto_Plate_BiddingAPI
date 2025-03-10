from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class AutoPlate(Base):
    __tablename__ = "auto_plates"
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(10), unique=True, index=True)
    description = Column(Text)
    deadline = Column(DateTime)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)

    created_by = relationship("User", back_populates="plates_created")
    bids = relationship("Bid", back_populates="plate")
# from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
# from sqlalchemy.orm import relationship
# from app.database import Base
#
# class AutoPlate(Base):
#     __tablename__ = "auto_plates"
#     id = Column(Integer, primary_key=True, index=True)
#     plate_number = Column(String(10), unique=True, index=True)
#     description = Column(Text)
#     deadline = Column(DateTime)
#     created_by_id = Column(Integer, ForeignKey("users.id"))
#     is_active = Column(Boolean, default=True)
#
#     created_by = relationship("User", back_populates="plates_created")
#     bids = relationship("Bid", back_populates="plate")