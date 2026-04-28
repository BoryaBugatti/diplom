from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from PydanticSchemas.UserSchema import UserBase
from config.dbconfig import SessionLocal
from crud.user_crud import get_user_by_email, create_user
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

router = APIRouter(prefix="/reg")

@router.post("")
def register(user_data:UserBase, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_data.user_email)
    if existing_user != None:
        return{"message": "Пользователь с такой почтой уже существует"}
    else:
        new_user = create_user(db=db, user_email=user_data.user_email, user_password=user_data.user_password, user_name=user_data.user_name)
        return {"status": "OK"}