from sqlalchemy import BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.models.base import Base, TimestampMixin


class Correction(Base, TimestampMixin):
    __tablename__ = "corrections"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    error_type: Mapped[str] = mapped_column(String(64), nullable=False)
    original_fragment: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_fragment: Mapped[str] = mapped_column(Text, nullable=False)
    explanation_ru: Mapped[str] = mapped_column(Text, nullable=False)

    message: Mapped["Message"] = relationship(back_populates="corrections", lazy="noload")
