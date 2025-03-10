from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_staff = Column(Boolean, default=False)

    plates_created = relationship("AutoPlate", back_populates="created_by")
    bids = relationship("Bid", back_populates="user")
