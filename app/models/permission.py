from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import role_permission_table

if TYPE_CHECKING:
    from app.models.role import Role


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permission_table,
        back_populates="permissions",
    )


