from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from studies_api.core.database import get_connection
from studies_api.core.security import get_current_user
from studies_api.models.sessions import Session
from studies_api.models.users import User
from studies_api.schemas.stats import StudySessionsStats

router = APIRouter()


@router.get(
    path='/', status_code=status.HTTP_200_OK, response_model=StudySessionsStats, summary='Get Stats'
)
async def get_stats(
    db: AsyncSession = Depends(get_connection), current_user: User = Depends(get_current_user)
):
    # Query de total_sessions
    query = select(func.count(Session.id)).where(Session.user_id == current_user.id)

    result = await db.execute(query)
    total_sessions = result.scalar()

    # Query de total_minutes
    query = select(func.sum(Session.duration_minutes)).where(Session.user_id == current_user.id)

    result = await db.execute(query)
    total_minutes = result.scalar()

    # Query de most_studied_topic
    query = (
        select(Session.topic)
        .where(Session.user_id == current_user.id)
        .group_by(Session.topic)
        .order_by(func.count(Session.topic).desc())
    )

    result = await db.execute(query)
    most_studied_topic = result.scalars().first()

    return {
        'total_sessions': total_sessions,
        'total_minutes': total_minutes,
        'most_studied_topic': most_studied_topic,
    }
