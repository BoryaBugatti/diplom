from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from PydanticSchemas.UserSchema import UserAuth
from config.dbconfig import SessionLocal
from crud.user_crud import get_user_by_email, create_user, pwd_context


router = APIRouter(prefix="/me")
@router.get("")
def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"user_id": user_id, "user_name": request.session.get("user_name")}