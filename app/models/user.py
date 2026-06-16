from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, CheckConstraint, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import user_role_table

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.tenant import Tenant


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        UniqueConstraint("tenant_id", "username", name="uq_users_tenant_username"),
        CheckConstraint(
            "email IS NOT NULL OR username IS NOT NULL",
            name="ck_users_email_or_username",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid4)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    custom_attributes: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)

    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    roles: Mapped[list["Role"]] = relationship(
        secondary=user_role_table,
        back_populates="users",
    )


