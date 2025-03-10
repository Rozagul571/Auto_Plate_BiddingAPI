# app/api/auth.py
# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # Add this import
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app import database, models, schemas, config
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/login/", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register/", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_staff=user.is_staff
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
# # app/api/auth.py
# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from sqlalchemy.orm import Session
# from jose import jwt
# from datetime import datetime, timedelta
# from app import schemas, models, database, config
# from passlib.context import CryptContext
#
# router = APIRouter()
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
#
# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM)
#
#
# # Foydalanuvchi qo‘shish endpointi
# @router.post("/register/", response_model=schemas.User)
# def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
#     # Username yoki email allaqachon mavjudligini tekshirish
#     if db.query(models.User).filter(models.User.username == user.username).first():
#         raise HTTPException(status_code=400, detail="Username already exists")
#     if db.query(models.User).filter(models.User.email == user.email).first():
#         raise HTTPException(status_code=400, detail="Email already exists")
#
#     # Parolni hash qilish
#     hashed_password = pwd_context.hash(user.password)
#
#     # Foydalanuvchi yaratish
#     db_user = models.User(
#         username=user.username,
#         email=user.email,
#         hashed_password=hashed_password,
#         is_staff=user.is_staff  # is_staff ni UserCreate dan olamiz
#     )
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
#
#
# @router.post("/login/", response_model=schemas.Token)
# def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
#     user = db.query(models.User).filter(models.User.username == form_data.username).first()
#     if not user or not pwd_context.verify(form_data.password, user.hashed_password):
#         raise HTTPException(status_code=401, detail="Incorrect username or password")
#     token = create_access_token(data={"sub": user.username})
#     return {"access_token": token, "token_type": "bearer"}
# # # app/api/auth.py
# # from fastapi import APIRouter, Depends, HTTPException, status
# # from fastapi.security import OAuth2PasswordRequestForm
# # from sqlalchemy.orm import Session
# # from jose import jwt
# # from datetime import datetime, timedelta
# # from app import schemas, models, database, config
# # from passlib.context import CryptContext
# #
# # router = APIRouter()
# # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# #
# #
# # def create_access_token(data: dict):
# #     to_encode = data.copy()
# #     expire = datetime.utcnow() + timedelta(minutes=config.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
# #     to_encode.update({"exp": expire})
# #     return jwt.encode(to_encode, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM)
# #
# #
# # # Foydalanuvchi qo‘shish endpointi
# # @router.post("/register/", response_model=schemas.User)
# # def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
# #     # Username yoki email allaqachon mavjudligini tekshirish
# #     if db.query(models.User).filter(models.User.username == user.username).first():
# #         raise HTTPException(status_code=400, detail="Username already exists")
# #     if db.query(models.User).filter(models.User.email == user.email).first():
# #         raise HTTPException(status_code=400, detail="Email already exists")
# #
# #     # Parolni hash qilish
# #     hashed_password = pwd_context.hash(user.password)
# #
# #     # Foydalanuvchi yaratish
# #     db_user = models.User(
# #         username=user.username,
# #         email=user.email,
# #         hashed_password=hashed_password,
# #         is_staff=user.is_staff  # is_staff ni UserCreate dan olamiz
# #     )
# #     db.add(db_user)
# #     db.commit()
# #     db.refresh(db_user)
# #     return db_user
# #
# #
# # @router.post("/login/", response_model=schemas.Token)
# # def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
# #     user = db.query(models.User).filter(models.User.username == form_data.username).first()
# #     if not user or not pwd_context.verify(form_data.password, user.hashed_password):
# #         raise HTTPException(status_code=401, detail="Incorrect username or password")
# #     token = create_access_token(data={"sub": user.username})
# #     return {"access_token": token, "token_type": "bearer"}