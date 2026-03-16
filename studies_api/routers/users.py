from fastapi import APIRouter, status, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

from studies_api.schemas.users import UserSchema, UserPublicSchema, UserListPublicSchema, UserUpdateSchema
from studies_api.core.security import verify_password, get_password_hash
from studies_api.models.users import User
from studies_api.core.database import get_connection


router = APIRouter()


@router.post(
    path='/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublicSchema,
    summary='Create New User',
)
async def create_user(user: UserSchema, db: AsyncSession = Depends(get_connection)):
    username_exists = await db.scalar(select(exists().where(User.username == user.username)))
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Username already exists.'
        )

    email_exists = await db.scalar(select(exists().where(User.email == user.email)))

    if email_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already exists.')

    db_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


@router.get(
    path='/',
    status_code=status.HTTP_200_OK,
    response_model=UserListPublicSchema,
    summary='Search Users',
)
async def list_users(
    offset: int = Query(0, ge=0, description="Number of registers to skip"),
    limit: int = Query(100, ge=1, le=100, description="Limit of registers"),
    search: Optional[str] = Query(None, description='Search by username or email'),
    db: AsyncSession = Depends(get_connection),
    ):
    query = select(User)

    if search:
        search_filter = f'%{search}%'
        query = query.where(
            (User.username.ilike(search_filter))
            | (User.email.ilike(search_filter))
        )

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)

    users = result.scalars().all()

    return {
        'users': users,
        'offset': offset,
        'limit': limit,
        }


@router.get(
    path='/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserPublicSchema,
    summary='Search User by ID',
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_connection)):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User Not Found')

    return user


@router.put(
        path="/{user_id}", 
        status_code=status.HTTP_201_CREATED,
        response_model=UserPublicSchema,
        summary='Update user',
        )
async def update_user(user_id: int, user_update: UserUpdateSchema, db: AsyncSession = Depends(get_connection)):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User Not Found',
        )
    
    update_data = user_update.model_dump(exclude_unset=True)

    if 'username' in update_data and update_data['username'] != user.username:
        pass

    if 'email' in update_data and update_data['email'] != user.email:
        pass

    if 'password' in update_data and update_data['password'] != user.password:
        update_data['password'] = get_password_hash(update_data['password'])

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user


@router.delete(path='/{user_id}', status_code=status.HTTP_204_NO_CONTENT, summary='Delete User')
async def delete_user(user_id: int, db: AsyncSession = Depends(get_connection)):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User Not Found')

    await db.delete(user)
    await db.commit()

    return



