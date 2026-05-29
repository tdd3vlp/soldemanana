from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.core.models.base import Base, TimestampMixin
from app.core.enums import SubscriptionTier


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tier: Mapped[str] = mapped_column(
        SAEnum(SubscriptionTier, name="subscription_tier_sub", values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    payment_provider: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payment_id: Mapped[str | None] = mapped_column(String(256), nullable=True)

    user: Mapped["User"] = relationship(back_populates="subscriptions", lazy="noload")
