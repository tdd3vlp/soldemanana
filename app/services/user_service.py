from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.models.user import User
from app.core.models.message import Message
from app.core.enums import BotMode, MessageRole
from app.config import settings


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def update_onboarding(
        self,
        user: User,
        level: str,
        goal: str,
        correction_intensity: str,
    ) -> User:
        user.level = level
        user.goal = goal
        user.correction_intensity = correction_intensity
        user.is_onboarded = True
        await self.session.flush()
        return user

    async def update_level(self, user: User, level: str) -> User:
        user.level = level
        await self.session.flush()
        return user

    async def update_goal(self, user: User, goal: str) -> User:
        user.goal = goal
        await self.session.flush()
        return user

    async def update_correction_intensity(self, user: User, intensity: str) -> User:
        user.correction_intensity = intensity
        await self.session.flush()
        return user

    async def increment_message_count(self, user: User) -> User:
        today = date.today()
        if user.last_message_date != today:
            user.messages_today = 0
            user.last_message_date = today
        user.messages_today += 1
        user.total_messages += 1
        await self.session.flush()
        return user

    async def save_message(
        self,
        user: User,
        text: str,
        role: MessageRole,
        mode: BotMode,
        corrected_text: str | None = None,
        scenario_id: str | None = None,
        grammar_topic: str | None = None,
        has_errors: bool = False,
    ) -> Message:
        message = Message(
            user_id=user.id,
            text=text,
            role=role,
            mode=mode,
            corrected_text=corrected_text,
            scenario_id=scenario_id,
            grammar_topic=grammar_topic,
            has_errors=has_errors,
        )
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_dialog_history(
        self,
        user: User,
        mode: BotMode,
        limit: int = 8,
        scenario_id: str | None = None,
    ) -> list[Message]:
        query = (
            select(Message)
            .where(Message.user_id == user.id, Message.mode == mode)
        )
        if scenario_id:
            query = query.where(Message.scenario_id == scenario_id)
        query = query.order_by(Message.created_at.desc()).limit(limit)
        result = await self.session.execute(query)
        messages = list(result.scalars().all())
        return list(reversed(messages))

    async def get_compact_dialog_history(
        self,
        user: User,
        mode: BotMode,
        limit: int | None = None,
        scenario_id: str | None = None,
    ) -> list[dict]:
        history = await self.get_dialog_history(
            user=user,
            mode=mode,
            limit=limit or settings.dialog_history_size,
            scenario_id=scenario_id,
        )
        return self.build_compact_messages(history)

    def build_compact_messages(self, history: list[Message]) -> list[dict]:
        compact_messages = []
        for msg in history:
            role = "user" if msg.role == MessageRole.USER else "assistant"
            text = self._trim_text(msg.text, settings.dialog_message_char_limit)
            compact_messages.append({"role": role, "content": text})
        return compact_messages

    def build_memory_context(self, user: User) -> str:
        parts = [
            user.memory_summary,
            f"Ошибки: {user.mistake_summary}" if user.mistake_summary else None,
            f"Тема: {user.active_topic}" if user.active_topic else None,
            f"Лексика: {user.learned_vocabulary}" if user.learned_vocabulary else None,
            f"Цели: {user.recent_goals}" if user.recent_goals else None,
        ]
        context = " | ".join(part for part in parts if part)
        return self._trim_text(context, settings.memory_summary_char_limit)

    async def update_learning_memory(
        self,
        user: User,
        *,
        memory_summary: str | None = None,
        mistake_summary: str | None = None,
        active_topic: str | None = None,
        learned_vocabulary: str | None = None,
        recent_goals: str | None = None,
    ) -> None:
        if memory_summary:
            user.memory_summary = self._trim_text(
                memory_summary,
                settings.memory_summary_char_limit,
            )
        if mistake_summary:
            user.mistake_summary = self._trim_text(mistake_summary, 500)
        if active_topic:
            user.active_topic = self._trim_text(active_topic, 128)
        if learned_vocabulary:
            user.learned_vocabulary = self._trim_text(learned_vocabulary, 500)
        if recent_goals:
            user.recent_goals = self._trim_text(recent_goals, 500)
        await self.session.flush()

    @staticmethod
    def _trim_text(text: str | None, limit: int) -> str:
        if not text:
            return ""
        normalized = " ".join(text.split())
        if len(normalized) <= limit:
            return normalized
        return normalized[: limit - 1].rstrip() + "…"
