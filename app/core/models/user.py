from sqlalchemy import BigInteger, String, Integer, Boolean, Date, Enum as SAEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from app.core.models.base import Base, TimestampMixin
from app.core.enums import (
    LanguageLevel,
    LearningGoal,
    CorrectionIntensity,
    SubscriptionTier,
)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(64), nullable=True)

    level: Mapped[str | None] = mapped_column(
        SAEnum(LanguageLevel, name="language_level", values_callable=lambda x: [e.value for e in x]), nullable=True
    )
    goal: Mapped[str | None] = mapped_column(
        SAEnum(LearningGoal, name="learning_goal", values_callable=lambda x: [e.value for e in x]), nullable=True
    )
    correction_intensity: Mapped[str] = mapped_column(
        SAEnum(CorrectionIntensity, name="correction_intensity", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )

    subscription_tier: Mapped[str] = mapped_column(
        SAEnum(SubscriptionTier, name="subscription_tier", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    is_onboarded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    messages_today: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_message_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    memory_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    mistake_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    active_topic: Mapped[str | None] = mapped_column(String(128), nullable=True)
    learned_vocabulary: Mapped[str | None] = mapped_column(Text, nullable=True)
    recent_goals: Mapped[str | None] = mapped_column(Text, nullable=True)

    messages: Mapped[list["Message"]] = relationship(back_populates="user", lazy="noload")
    vocabulary: Mapped[list["VocabularyEntry"]] = relationship(back_populates="user", lazy="noload")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user", lazy="noload")
    ai_usage: Mapped[list["AIUsage"]] = relationship(back_populates="user", lazy="noload")

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} @{self.username}>"
