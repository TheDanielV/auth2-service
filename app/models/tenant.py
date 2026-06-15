from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.oauth_client import OAuthClient
    from app.models.role import Role
    from app.models.user import User


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    oauth_clients: Mapped[list["OAuthClient"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
    users: Mapped[list["User"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan",
    )
    roles: Mapped[list["Role"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan",
    )


