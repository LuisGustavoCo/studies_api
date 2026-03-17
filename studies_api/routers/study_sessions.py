from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from studies_api.schemas.study_sessions import (
    StudySessionListPublicSchema,
    StudySessionSchema,
    StudySessionPublicSchema,
    StudySessionUpdateSchema
)
from studies_api.models.sessions import Session
from studies_api.models.users import User
from studies_api.core.database import get_connection
from studies_api.core.security import get_current_user, verify_study_session_ownership


router = APIRouter()


@router.post(
    path='/session',
    status_code=status.HTTP_201_CREATED,
    response_model=StudySessionPublicSchema,
    summary='Create new Study Session',
)
async def create_session(
    session: StudySessionSchema,
    db: AsyncSession = Depends(get_connection),
    current_user: User = Depends(get_current_user),
    ):
    db_session = Session(
        topic=session.topic,
        duration_minutes=session.duration_minutes,
        notes=session.notes,
        date=session.date,
        user_id=current_user.id,
    )

    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)

    return db_session


@router.get(
    path='/sessions',
    status_code=status.HTTP_200_OK,
    response_model=StudySessionListPublicSchema,
    summary='List all Study Sessions'
)
async def list_sessions(
    offset: int = Query(0, ge=0, description='Number of registers to skip'),
    limit: int = Query(100, ge=1, le=100, description='Limit of registers'),
    search: Optional[str] = Query(None, description='Search by Topic'),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_connection)
    ):
    
    query = select(Session).where(Session.user_id == current_user.id)

    if search:
        search_filter = f'%{search}%'
        query = query.where(
            (Session.topic.ilike(search_filter))
        )

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)

    study_sessions = result.scalars().all()

    return {
        'sessions': study_sessions,
        'offset': offset,
        'limit': limit,
    }


@router.get(
    path="/sessions/{session_id}", 
    status_code=status.HTTP_200_OK,
    response_model=StudySessionPublicSchema,
    summary="Search Study Session by ID",
    )
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_connection),
    current_user: User = Depends(get_current_user),
    ):
    query = select(Session).where(Session.id == session_id)
    result = await db.execute(query)

    study_session = result.scalar_one_or_none()

    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Study Session Not Found",
            )
    
    verify_study_session_ownership(study_session=study_session, current_user=current_user)

    return study_session


@router.put(
    path='/sessions/{session_id}',
    status_code=status.HTTP_200_OK,
    response_model=StudySessionPublicSchema,
    summary='Update Study Session'
)
async def update_session(
    session_id: int,
    session_update: StudySessionUpdateSchema, 
    db: AsyncSession = Depends(get_connection),
    current_user: User = Depends(get_current_user),
    ):
    study_session = await db.get(Session, session_id)

    if not study_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Study Session Not Found'
        )
    
    verify_study_session_ownership(study_session=study_session, current_user=current_user)
    
    update_data = session_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(study_session, field, value)
    
    await db.commit()
    await db.refresh(study_session)
    
    return study_session
    
    

@router.delete(path='/sessions/{session_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int, 
    db: AsyncSession = Depends(get_connection),
    current_user: User = Depends(get_current_user),
    ):
    study_session = await db.get(Session, session_id)

    if not study_session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Study Session Not Found')
    
    verify_study_session_ownership(study_session=study_session, current_user=current_user)

    await db.delete(study_session)
    await db.commit()

    return
