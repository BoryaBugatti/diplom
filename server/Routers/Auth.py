from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from PydanticSchemas.UserSchema import UserAuth
from config.dbconfig import SessionLocal
from crud.user_crud import get_user_by_email, create_user, pwd_context
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
@router.post("")
def auth(user_data:UserAuth, request:Request, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_data.user_email)
    if not existing_user:
        return {"message": "Неверный логин или пароль"}
    if not pwd_context.verify(user_data.user_password, existing_user.user_password):
        return {"message": "Неверный логин или пароль"}
    
    request.session['user_id'] = existing_user.user_id
    request.session['user_name'] = existing_user.user_name
    request.session['user_role'] = existing_user.user_role

    return {
        "status": "OK",
        "message": "Authentication successful",
        "user_name": existing_user.user_name,
        "user_role": existing_user.user_role,
        "user_email": existing_user.user_email
    }