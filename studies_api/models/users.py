from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING
from datetime import datetime

from studies_api.models.base import Base
from studies_api.models.sessions import Session


if TYPE_CHECKING:  # Isso só roda para o Autocomplete, não no runtime
    from .sessions import Session


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)

    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now(), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    sessions: Mapped[List['Session']] = relationship(
        back_populates='users',
    )
