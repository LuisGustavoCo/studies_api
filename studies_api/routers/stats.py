from fastapi import APIRouter, status, Depends
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from studies_api.db import SESSIONS
from studies_api.core.database import get_connection
from studies_api.schemas.stats import StudySessionsStats


router = APIRouter()


@router.get(path='/stats', status_code=status.HTTP_200_OK, response_model=StudySessionsStats, summary='Get Stats')
async def get_stats(user_id: int, db: AsyncSession = Depends(get_connection)):
    total_sessions = db.query(func.count(StudySessionsStats.id))
    total_minutes = 0
    topics_count = {}
    for session in SESSIONS:
        total_minutes += session.duration_minutes
        topic = session.topic

        if topic not in topics_count:
            topics_count[topic] = 1
        else:
            topics_count[topic] += 1

    most_studied_topic = None
    max_count = 0

    for topic, count in topics_count.items():
        if count > max_count:
            max_count = count
            most_studied_topic = topic

    return {
        'total_sessions': total_sessions,
        'total_minutes': total_minutes,
        'most_studied_topic': most_studied_topic,
    }
