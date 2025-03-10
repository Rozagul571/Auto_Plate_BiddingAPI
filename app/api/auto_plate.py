from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app import database, models, schemas
from datetime import datetime
from .auth import get_current_user
import logging

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Router ni aniq prefiks va teglar bilan sozlash
router = APIRouter(prefix="/plates", tags=["plates"])

@router.get("/", response_model=list[schemas.AutoPlate])
def get_plates(db: Session = Depends(database.get_db), ordering: str = "deadline"):
    """
    Faol avtomobil raqamlarini ro'yxatini qaytaradi.
    """
    try:
        # `ordering` parametri xavfsizligini tekshirish
        valid_orderings = ["deadline", "-deadline", "plate_number", "-plate_number"]
        if ordering not in valid_orderings:
            logger.warning(f"Invalid ordering parameter: {ordering}")
            raise HTTPException(status_code=400, detail="Invalid ordering parameter")

        query = db.query(models.AutoPlate).filter(models.AutoPlate.is_active == True)
        plates = query.order_by(ordering).all()
        logger.info(f"Fetched {len(plates)} active plates")
        return plates
    except Exception as e:
        logger.error(f"Error fetching plates: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/", response_model=schemas.AutoPlate, status_code=status.HTTP_201_CREATED)
def create_plate(plate: schemas.AutoPlateCreate, db: Session = Depends(database.get_db),
                current_user: models.User = Depends(get_current_user)):
    """
    Yangi avtomobil raqamini yaratadi. Faqat adminlar uchun.
    """
    try:
        # Admin huquqlarini tekshirish
        if not current_user.is_staff:
            logger.warning(f"User {current_user.username} attempted to create plate without admin privileges")
            raise HTTPException(status_code=403, detail="Only admins can create plates")

        # Plate nomerining noyobligini tekshirish
        if db.query(models.AutoPlate).filter(models.AutoPlate.plate_number == plate.plate_number).first():
            logger.warning(f"Plate number {plate.plate_number} already exists")
            raise HTTPException(status_code=400, detail="Plate number already exists")

        # Deadline ni tekshirish va parse qilish
        try:
            deadline = datetime.fromisoformat(plate.deadline.replace("Z", "+00:00"))
        except ValueError as ve:
            logger.error(f"Invalid deadline format: {plate.deadline}, error: {str(ve)}")
            raise HTTPException(status_code=400, detail="Invalid deadline format")

        if deadline <= datetime.utcnow():
            logger.warning(f"Deadline {deadline} is not in the future")
            raise HTTPException(status_code=400, detail="Deadline must be in the future")

        # Yangi plate yaratish
        db_plate = models.AutoPlate(
            plate_number=plate.plate_number,
            description=plate.description,
            deadline=deadline,
            created_by_id=current_user.id,
            is_active=True
        )
        db.add(db_plate)
        db.commit()
        db.refresh(db_plate)
        logger.info(f"Plate {plate.plate_number} created successfully by user {current_user.username}")
        return db_plate

    except IntegrityError as ie:
        db.rollback()
        logger.error(f"Database integrity error while creating plate: {str(ie)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Database error: {str(ie)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating plate: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/{plate_id}", response_model=schemas.AutoPlate)
def get_plate(plate_id: int, db: Session = Depends(database.get_db)):
    """
    Muayyan avtomobil raqami haqida ma'lumot qaytaradi.
    """
    try:
        plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == plate_id).first()
        if not plate:
            logger.warning(f"Plate with ID {plate_id} not found")
            raise HTTPException(status_code=404, detail="Plate not found")
        return plate
    except Exception as e:
        logger.error(f"Error fetching plate {plate_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.put("/{plate_id}", response_model=schemas.AutoPlate)
def update_plate(plate_id: int, plate: schemas.AutoPlateCreate, db: Session = Depends(database.get_db),
                current_user: models.User = Depends(get_current_user)):
    """
    Muayyan avtomobil raqamini yangilaydi. Faqat adminlar uchun.
    """
    try:
        if not current_user.is_staff:
            logger.warning(f"User {current_user.username} attempted to update plate without admin privileges")
            raise HTTPException(status_code=403, detail="Only admins can update plates")

        db_plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == plate_id).first()
        if not db_plate:
            logger.warning(f"Plate with ID {plate_id} not found")
            raise HTTPException(status_code=404, detail="Plate not found")

        # Plate nomerining noyobligini tekshirish
        existing_plate = db.query(models.AutoPlate).filter(models.AutoPlate.plate_number == plate.plate_number).first()
        if existing_plate and existing_plate.id != db_plate.id:
            logger.warning(f"Plate number {plate.plate_number} already exists")
            raise HTTPException(status_code=400, detail="Plate number already exists")

        # Deadline ni tekshirish va parse qilish
        try:
            deadline = datetime.fromisoformat(plate.deadline.replace("Z", "+00:00"))
        except ValueError as ve:
            logger.error(f"Invalid deadline format: {plate.deadline}, error: {str(ve)}")
            raise HTTPException(status_code=400, detail="Invalid deadline format")

        if deadline <= datetime.utcnow():
            logger.warning(f"Deadline {deadline} is not in the future")
            raise HTTPException(status_code=400, detail="Deadline must be in the future")

        # Plate ma'lumotlarini yangilash
        db_plate.plate_number = plate.plate_number
        db_plate.description = plate.description
        db_plate.deadline = deadline
        db.commit()
        db.refresh(db_plate)
        logger.info(f"Plate {plate_id} updated successfully by user {current_user.username}")
        return db_plate

    except IntegrityError as ie:
        db.rollback()
        logger.error(f"Database integrity error while updating plate: {str(ie)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Database error: {str(ie)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating plate {plate_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.delete("/{plate_id}", status_code=status.HTTP_200_OK)
def delete_plate(plate_id: int, db: Session = Depends(database.get_db),
                current_user: models.User = Depends(get_current_user)):
    """
    Muayyan avtomobil raqamini o'chiradi. Faqat adminlar uchun.
    """
    try:
        if not current_user.is_staff:
            logger.warning(f"User {current_user.username} attempted to delete plate without admin privileges")
            raise HTTPException(status_code=403, detail="Only admins can delete plates")

        db_plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == plate_id).first()
        if not db_plate:
            logger.warning(f"Plate with ID {plate_id} not found")
            raise HTTPException(status_code=404, detail="Plate not found")

        if db.query(models.Bid).filter(models.Bid.plate_id == plate_id).first():
            logger.warning(f"Plate {plate_id} has active bids and cannot be deleted")
            raise HTTPException(status_code=400, detail="Cannot delete plate with active bids")

        db.delete(db_plate)
        db.commit()
        logger.info(f"Plate {plate_id} deleted successfully by user {current_user.username}")
        return {"detail": "Plate deleted"}

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting plate {plate_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from app import database, models, schemas
# from datetime import datetime
# from .auth import get_current_user
#
# router = APIRouter()
#
#
# @router.get("/plates/", response_model=list[schemas.AutoPlate])
# def get_plates(db: Session = Depends(database.get_db), ordering: str = "deadline"):
#     plates = db.query(models.AutoPlate).filter(models.AutoPlate.is_active == True).order_by(ordering).all()
#     return plates
#
#
# from datetime import datetime
#
# @router.post("/plates/", response_model=schemas.AutoPlate)
# def create_plate(plate: schemas.AutoPlateCreate, db: Session = Depends(database.get_db),
#                  current_user: models.User = Depends(get_current_user)):
#     if not current_user.is_staff:
#         raise HTTPException(status_code=403, detail="Only admins can create plates")
#     if db.query(models.AutoPlate).filter(models.AutoPlate.plate_number == plate.plate_number).first():
#         raise HTTPException(status_code=400, detail="Plate number already exists")
#     if plate.deadline <= datetime.utcnow():
#         raise HTTPException(status_code=400, detail="Deadline must be in the future")
#
#     db_plate = models.AutoPlate(**plate.dict(), created_by_id=current_user.id, is_active=True)
#     db.add(db_plate)
#     db.commit()
#     db.refresh(db_plate)
#     return db_plate
#
#
# @router.get("/plates/{plate_id}", response_model=schemas.AutoPlate)
# def get_plate(plate_id: int, db: Session = Depends(database.get_db)):
#     plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == plate_id).first()
#     if not plate:
#         raise HTTPException(status_code=404, detail="Plate not found")
#     return plate
#
#
# @router.put("/plates/{plate_id}", response_model=schemas.AutoPlate)
# def update_plate(plate_id: int, plate: schemas.AutoPlateCreate, db: Session = Depends(database.get_db),
#                  current_user: models.User = Depends(get_current_user)):
#     if not current_user.is_staff:
#         raise HTTPException(status_code=403, detail="Only admins can update plates")
#     db_plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == plate_id).first()
#     if not db_plate:
#         raise HTTPException(status_code=404, detail="Plate not found")
#     if db.query(models.AutoPlate).filter(
#             models.AutoPlate.plate_number == plate.plate_number).first() and db_plate.plate_number != plate.plate_number:
#         raise HTTPException(status_code=400, detail="Plate number already exists")
#     if plate.deadline <= datetime.utcnow():
#         raise HTTPException(status_code=400, detail="Deadline must be in the future")
#
#     db_plate.plate_number = plate.plate_number
#     db_plate.description = plate.description
#     db_plate.deadline = plate.deadline
#     db.commit()
#     db.refresh(db_plate)
#     return db_plate
#
#
# @router.delete("/plates/{plate_id}")
# def delete_plate(plate_id: int, db: Session = Depends(database.get_db),
#                  current_user: models.User = Depends(get_current_user)):
#     if not current_user.is_staff:
#         raise HTTPException(status_code=403, detail="Only admins can delete plates")
#     db_plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == plate_id).first()
#     if not db_plate:
#         raise HTTPException(status_code=404, detail="Plate not found")
#     if db.query(models.Bid).filter(models.Bid.plate_id == plate_id).first():
#         raise HTTPException(status_code=400, detail="Cannot delete plate with active bids")
#     db.delete(db_plate)
#     db.commit()
#     return {"detail": "Plate deleted"}
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from typing import List
# from app import schemas, models, database, dependencies
#
# router = APIRouter(prefix="/plates", tags=["plates"])
#
# @router.get("/", response_model=List[schemas.AutoPlate])
# def get_plates(db: Session = Depends(database.get_db), ordering: str = None, plate_number__contains: str = None):
#     query = db.query(models.AutoPlate).filter(models.AutoPlate.is_active == True)
#     if plate_number__contains:
#         query = query.filter(models.AutoPlate.plate_number.contains(plate_number__contains))
#     if ordering:
#         query = query.order_by(ordering)
#     plates = query.all()
#     return plates
#
# @router.post("/", response_model=schemas.AutoPlate, status_code=status.HTTP_201_CREATED)
# def create_plate(plate: schemas.AutoPlateCreate, db: Session = Depends(database.get_db),
#                 current_user: models.User = Depends(dependencies.get_current_admin)):
#     if db.query(models.AutoPlate).filter(models.AutoPlate.plate_number == plate.plate_number).first():
#         raise HTTPException(status_code=400, detail="Plate number already exists")
#     if plate.deadline < datetime.utcnow():
#         raise HTTPException(status_code=400, detail="Deadline must be in the future")
#     db_plate = models.AutoPlate(**plate.dict(), created_by_id=current_user.id)
#     db.add(db_plate)
#     db.commit()
#     db.refresh(db_plate)
#     return db_plate
#
# @router.get("/{id}/", response_model=schemas.AutoPlate)
# def get_plate(id: int, db: Session = Depends(database.get_db)):
#     plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == id).first()
#     if not plate:
#         raise HTTPException(status_code=404, detail="Plate not found")
#     return plate
#
# @router.put("/{id}/", response_model=schemas.AutoPlate)
# def update_plate(id: int, plate: schemas.AutoPlateCreate, db: Session = Depends(database.get_db),
#                 current_user: models.User = Depends(dependencies.get_current_admin)):
#     db_plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == id).first()
#     if not db_plate:
#         raise HTTPException(status_code=404, detail="Plate not found")
#     for key, value in plate.dict().items():
#         setattr(db_plate, key, value)
#     db.commit()
#     db.refresh(db_plate)
#     return db_plate
#
# @router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
# def delete_plate(id: int, db: Session = Depends(database.get_db),
#                 current_user: models.User = Depends(dependencies.get_current_admin)):
#     db_plate = db.query(models.AutoPlate).filter(models.AutoPlate.id == id).first()
#     if not db_plate:
#         raise HTTPException(status_code=404, detail="Plate not found")
#     if db_plate.bids:
#         raise HTTPException(status_code=400, detail="Cannot delete plate with active bids")
#     db.delete(db_plate)
#     db.commit()