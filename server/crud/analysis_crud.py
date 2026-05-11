from sqlalchemy.orm import Session
from Models.models import AnalysisResult
import json

def save_analysis_result(
    db: Session,
    user_id: int,
    file_name: str,
    tender_name: str,
    tender_description: str,
    all_requirements: list,
    key_requirements: list
) -> AnalysisResult:
    analysis = AnalysisResult(
        user_id=user_id,
        file_name=file_name,
        tender_name=tender_name,
        tender_description=tender_description,
        all_requirements=json.dumps(all_requirements, ensure_ascii=False),
        key_requirements=json.dumps(key_requirements, ensure_ascii=False)
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis

def get_user_analyses(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(AnalysisResult).filter(AnalysisResult.user_id == user_id)\
        .order_by(AnalysisResult.created_at.desc()).offset(skip).limit(limit).all()

def get_analysis_by_id(db: Session, analysis_id: int, user_id: int):
    return db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id, AnalysisResult.user_id == user_id).first()