from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.associations import role_permission_table, user_role_table

if TYPE_CHECKING:
    from app.models.permission import Permission
    from app.models.tenant import Tenant
    from app.models.user import User


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_roles_tenant_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="roles")
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permission_table,
        back_populates="roles",
    )
    users: Mapped[list["User"]] = relationship(
        secondary=user_role_table,
        back_populates="roles",
    )


