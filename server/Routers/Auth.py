from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from PydanticSchemas.UserSchema import UserAuth
from config.dbconfig import SessionLocal
from crud.user_crud import get_user_by_email, pwd_context
from auth.jwt import create_access_token

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

router = APIRouter(prefix="/auth")

@router.post("/login")
def login(user_data: UserAuth, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_data.user_email)
    if not existing_user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    if not pwd_context.verify(user_data.user_password, existing_user.user_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    access_token = create_access_token(data={"sub": str(existing_user.user_id), "role": existing_user.user_role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": existing_user.user_name,
        "user_role": existing_user.user_role,
        "user_email": existing_user.user_email
    }