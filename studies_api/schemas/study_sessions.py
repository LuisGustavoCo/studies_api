from pydantic import BaseModel
from typing import Optional, List


class StudySessionSchema(BaseModel):
    topic: str
    duration_minutes: int
    notes: Optional[str]
    date: str
    user_id: int


# O que devolverei após usuário criar
class StudySessionPublicSchema(BaseModel):
    id: int
    topic: str
    duration_minutes: int
    notes: Optional[str]
    date: str
    user_id: int


class StudySessionUpdateSchema(BaseModel):
    topic: Optional[str] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    date: Optional[str] = None


class StudySessionListPublicSchema(BaseModel):
    sessions: List[StudySessionPublicSchema]
    offset: int
    limit: int
