from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

class UserBase(BaseModel):
    user_email: EmailStr
    user_name: str = Field(..., min_length=3, max_length=50)
    user_password: str=Field(..., min_length=6, max_length=72)

    
    @field_validator('user_password')
    @classmethod
    def validate_password_bytes(cls, v: str) -> str:
        if len(v.encode('utf-8')) > 72:
            raise ValueError('Password must be at most 72 bytes (e.g., up to 72 ASCII chars or fewer Unicode chars)')
        return v
    
class UserAuth(BaseModel):
    user_email: EmailStr
    user_password: str