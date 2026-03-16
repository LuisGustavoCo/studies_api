from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from studies_api.schemas.study_sessions import (
    StudySessionListPublicSchema,
    StudySessionSchema,
    StudySessionPublicSchema,
)
from studies_api.db import SESSIONS
from studies_api.models.sessions import Session
from studies_api.core.database import get_connection

router = APIRouter()


@router.post(
    path='/study-session',
    status_code=status.HTTP_201_CREATED,
    response_model=StudySessionPublicSchema,
    summary='Create new Study Session',
)
async def create_session(session: StudySessionSchema, db: AsyncSession = Depends(get_connection)):
    db_session = Session(
        topic=session.topic,
        duration_minutes=session.duration_minutes,
        notes=session.notes,
        date=session.date,
        user_id=session.user_id,
    )

    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)

    return db_session


@router.get(
    path='/study-session',
    status_code=status.HTTP_200_OK,
    response_model=StudySessionListPublicSchema,
    summary='List all Study Sessions'
)
async def list_sessions(
    offset: int = Query(0, ge=0, description='Number of registers to skip'),
    limit: int = Query(100, ge=1, le=100, description='Limit of registers'),
    search: Optional[str] = Query(None, description='Search by Topic'),
    db: AsyncSession = Depends(get_connection)):
    query = select(Session)

    if search:
        search_filter = '%{search}%'
        query = query.where(
            (Session.topic.ilike(search_filter))
        )

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)

    sessions = result.scalars().all()

    return {
        'sessions': sessions,
        'offset': offset,
        'limit': limit,
    }


@router.put(
    path='/study-session/{session_id}',
    status_code=status.HTTP_201_CREATED,
    response_model=StudySessionPublicSchema,
    summary='Update Study Session'
)
async def update_session(session_id: int, session: StudySessionSchema):
    session_with_id = StudySessionPublicSchema(**session.model_dump(), id=session_id)
    SESSIONS[session_id - 1] = session_with_id
    return session_with_id


@router.delete(path='/study-session/{session_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: int, db: AsyncSession = Depends(get_connection)):
    study_session = await db.get(Session, session_id)
    if not study_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Study Session Not Found')

    await db.delete(study_session)
    await db.commit()

    return
