from pydantic import BaseModel
from typing import Optional, List


class StudySessionsStats(BaseModel):
    total_sessions: int
    total_minutes: int
    most_studied_topic: str | None
