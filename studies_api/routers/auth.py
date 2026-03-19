from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from studies_api.core.database import get_connection
from studies_api.core.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from studies_api.models.users import User
from studies_api.schemas.auth import LoginRequest, Token

router = APIRouter()


@router.post(
    path='/token',
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary='Generate Access Token',
)
async def token(login_data: LoginRequest, db: AsyncSession = Depends(get_connection)):
    user = await authenticate_user(
        email=login_data.email,
        password=login_data.password,
        db=db,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = create_access_token(data={'sub': str(user.id)})

    return {
        'access_token': access_token,
        'token_type': 'bearer',
    }


@router.post(
    path='/refresh_token',
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary='Update Access Token',
)
async def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(data={'sub': str(current_user.id)})

    return {
        'access_token': access_token,
        'token_type': 'bearer',
    }
