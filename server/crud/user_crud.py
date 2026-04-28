from sqlalchemy.orm import Session
from passlib.context import CryptContext
from Models.models import User

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_user_by_id(db:Session, user_id:int)->User|None:
    return db.query(User).filter(User.user_id == user_id).first()
def get_user_by_email(db:Session, user_email:str)->User|None:
    return db.query(User).filter(User.user_email == user_email).first()

def create_user(db:Session, user_email:str, user_password:str, user_name:str)->User|None:
    hashed_password = pwd_context.hash(user_password)
    db_user = User(user_name=user_name, user_email=user_email, user_password=hashed_password, user_role="Пользователь")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user