from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime


class UserSchema(BaseModel):
    username: str
    password: str
    email: EmailStr

    @field_validator('username')
    def username_min_length(cls, v):
        if len(v) < 6:
            raise ValueError('Username must be greather than 6 characters.')
        return v
        
    @field_validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must have more than 7 characters.')
        return v


class UserPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    @field_validator('username')
    def username_min_length(cls, v):
        if len(v) < 6:
            raise ValueError('Username must be greather than 6 characters.')
        return v
        
    @field_validator('password')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must have more than 7 characters.')
        return v


class UserListPublicSchema(BaseModel):
    users: List[UserPublicSchema]
    offset: int
    limit: int
