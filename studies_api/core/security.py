from pwdlib import PasswordHash
from typing import Dict, Optional
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import jwt

from studies_api.core.settings import Settings
from studies_api.core.database import get_connection
from studies_api.models.users import User

pwd_context = PasswordHash.recommended()
security = HTTPBearer()
settings = Settings()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRATION_MINUTES
    )
    to_encode.update({'exp': expire})

    # Especificando que o que quero criptografar é o to_encode, passo a senha que quero criptografar
    # (secret_key) e, por fim, qual algoritmo utilizarei para criptografar
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt


def verify_token(token: str) -> Dict:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Expired Token',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could Not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    
async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        return None
    
    # Conferindo se a senha bate com a do usuário encontrado no banco
    if not verify_password(password, user.password):
        return None
    
    return user


# Quando a requisição chamar essa função, ele vai procurar pelo Bearer Token, se não existir, ele já vai retornar erro
async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security), 
        db: AsyncSession = Depends(get_connection)) -> User:
    payload = verify_token(token=credentials.credentials)
    # Verifica se tem um id de usuário no token.
    user_id_str = payload.get('sub')
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    try:
        user_id = int(user_id_str)  # Se tiver id do user, verifico se ele é válido
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    result = await db.execute(select(User).where(User.id == user_id))  
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return user


def verify_study_session_ownership(study_session, current_user) :
    if study_session.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Do not have permissions to access this study session',
        )