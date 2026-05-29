from sqlalchemy import BigInteger, String, Text, ForeignKey, Enum as SAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.models.base import Base, TimestampMixin
from app.core.enums import BotMode, MessageRole


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mode: Mapped[str] = mapped_column(
        SAEnum(BotMode, name="bot_mode", values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    role: Mapped[str] = mapped_column(
        SAEnum(MessageRole, name="message_role", values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    scenario_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    grammar_topic: Mapped[str | None] = mapped_column(String(64), nullable=True)
    has_errors: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="messages", lazy="noload")
    corrections: Mapped[list["Correction"]] = relationship(back_populates="message", lazy="noload")
