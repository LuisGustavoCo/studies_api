from pydantic import BaseModel


class StudySessionsStats(BaseModel):
    total_sessions: int
    total_minutes: int
    most_studied_topic: str | None
