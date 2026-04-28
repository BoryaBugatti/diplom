from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from config.dbconfig import SessionLocal
from crud.analysis_crud import get_user_analyses, get_analysis_by_id
from auth.dependencies import get_current_user
from Models.models import User
import json

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



router = APIRouter(prefix="/user/documents", tags=["User Documents"])

class RequirementItem(BaseModel):
    text: str

class AnalysisOut(BaseModel):
    id: int
    file_name: str
    tender_name: str
    tender_description: str
    all_requirements: List[str]
    key_requirements: List[str]
    created_at: str

@router.get("", response_model=List[AnalysisOut])
async def list_user_analyses(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    analyses = get_user_analyses(db, current_user.user_id)
    result = []
    for a in analyses:
        result.append({
            "id": a.id,
            "file_name": a.file_name,
            "tender_name": a.tender_name or "",
            "tender_description": a.tender_description or "",
            "all_requirements": json.loads(a.all_requirements) if a.all_requirements else [],
            "key_requirements": json.loads(a.key_requirements) if a.key_requirements else [],
            "created_at": a.created_at.strftime("%d.%m.%Y")
        })
    return result

@router.get("/{analysis_id}", response_model=AnalysisOut)
async def get_analysis_detail(analysis_id: int, request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не авторизован")
    analysis = get_analysis_by_id(db, analysis_id, user_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Анализ не найден")
    return {
        "id": analysis.id,
        "file_name": analysis.file_name,
        "tender_name": analysis.tender_name or "",
        "tender_description": analysis.tender_description or "",
        "all_requirements": json.loads(analysis.all_requirements) if analysis.all_requirements else [],
        "key_requirements": json.loads(analysis.key_requirements) if analysis.key_requirements else [],
        "created_at": analysis.created_at.strftime("%d.%m.%Y")
    }