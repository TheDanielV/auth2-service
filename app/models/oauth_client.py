from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.tenant import Tenant


class OAuthClient(Base):
    __tablename__ = "oauth_clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    client_secret: Mapped[str] = mapped_column(String(255), nullable=False)
    redirect_uris: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    tenant: Mapped["Tenant"] = relationship(back_populates="oauth_clients")


