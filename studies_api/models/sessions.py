from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from studies_api.models.base import Base

if TYPE_CHECKING:  # Isso só roda para o Autocomplete, não no runtime
    from .users import User


class Session(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    topic: Mapped[str]
    duration_minutes: Mapped[int]
    notes: Mapped[str] = mapped_column(Text(120), default=None)
    date: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now(), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    users: Mapped['User'] = relationship(
        'User',
        back_populates='sessions',
    )
