from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class StudySessionSchema(BaseModel):
    topic: str
    duration_minutes: int
    notes: Optional[str]
    date: str


# O que devolverei após usuário criar
class StudySessionPublicSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
