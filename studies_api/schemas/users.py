from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserSchema(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserPublicSchema(BaseModel):
    id: int
    username: str
    email: EmailStr


class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserListPublicSchema(BaseModel):
    users: List[UserPublicSchema]
    offset: int
    limit: int
