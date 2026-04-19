from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy.orm import declarative_base
from config.dbconfig import Base

class User(Base):
    __tablename__ = "user"
    
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    user_email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    user_password: Mapped[str] = mapped_column(String(255), nullable=False)
    user_role: Mapped[str] = mapped_column(String(20), nullable=False)
