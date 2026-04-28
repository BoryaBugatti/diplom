from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy.orm import declarative_base
from config.dbconfig import Base

class User(Base):
    __tablename__ = "user"
    
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    user_email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    user_password: Mapped[str] = mapped_column(String(255), nullable=False)
    user_role: Mapped[str] = mapped_column(String(50), nullable=False)


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tender_name: Mapped[str] = mapped_column(String(500), nullable=True)
    tender_description: Mapped[str] = mapped_column(Text, nullable=True)
    all_requirements: Mapped[str] = mapped_column(Text, nullable=True) 
    key_requirements: Mapped[str] = mapped_column(Text, nullable=True)   
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
