import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.enums import BotMode, MessageRole
from app.core.models.user import User
from app.infrastructure.llm import (
    LLMTask,
    build_memory_summary_prompt,
    build_system_prompt,
    llm_client,
)
from app.services.ai_usage_service import AIUsageService
from app.services.user_service import UserService

logger = structlog.get_logger()


class ConversationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_service = UserService(session)
        self.usage_service = AIUsageService(session)

    async def process_message(self, user: User, text: str) -> dict:
        memory_context = self.user_service.build_memory_context(user)
        system_prompt = build_system_prompt(
            level=user.level or "A2",
            goal=user.goal or "communication",
            correction_intensity=user.correction_intensity,
            mode="conversation",
            memory_context=memory_context,
        )

        messages = await self.user_service.get_compact_dialog_history(
            user=user,
            mode=BotMode.CONVERSATION,
            limit=settings.dialog_history_size,
        )
        messages.append({"role": "user", "content": text})

        try:
            response = await llm_client.complete(system_prompt, messages, task=LLMTask.CHAT)
            if "error" in response:
                logger.error("LLM response error", response=response)
                return {
                    "error": True,
                    "message": (
                        "Извини, произошла ошибка "
                        "при обработке сообщения. "
                        "Попробуй ещё раз."
                    ),
                }
            await self.usage_service.record(
                user,
                BotMode.CONVERSATION.value,
                response.get("_llm_usage"),
            )
            self._keep_current_message_corrections(response, text)
            self._remove_repeated_correction_reply(response)

            await self.user_service.save_message(
                user=user,
                text=text,
                role=MessageRole.USER,
                mode=BotMode.CONVERSATION,
                corrected_text=response.get("natural_variant"),
                has_errors=response.get("has_errors", False),
            )

            bot_reply = response.get("reply", "No sé qué decir...")
            await self.user_service.save_message(
                user=user,
                text=bot_reply,
                role=MessageRole.ASSISTANT,
                mode=BotMode.CONVERSATION,
            )
            await self._update_memory_if_needed(user)

            return response

        except Exception as e:
            logger.error("Conversation processing error", error=str(e))
            return {
                "error": True,
                "message": "Произошла ошибка. Попробуй позже.",
            }

    async def _update_memory_if_needed(self, user: User) -> None:
        if settings.memory_summary_interval <= 0:
            return
        if user.total_messages == 0 or user.total_messages % settings.memory_summary_interval != 0:
            return

        history = await self.user_service.get_compact_dialog_history(
            user=user,
            mode=BotMode.CONVERSATION,
            limit=settings.dialog_history_size,
        )
        if not history:
            return

        try:
            response = await llm_client.complete(
                build_memory_summary_prompt(user.level or "A2", user.goal or "communication"),
                history,
                temperature=0.2,
                task=LLMTask.SUMMARY,
            )
            await self.usage_service.record(user, "summary", response.get("_llm_usage"))
            await self.user_service.update_learning_memory(
                user,
                memory_summary=response.get("memory_summary"),
                mistake_summary=response.get("mistake_summary"),
                active_topic=response.get("active_topic"),
                learned_vocabulary=response.get("learned_vocabulary"),
                recent_goals=response.get("recent_goals"),
            )
        except Exception as e:
            logger.warning("Memory summary skipped", error=str(e), user_id=user.id)

    @classmethod
    def _keep_current_message_corrections(cls, response: dict, text: str) -> None:
        corrections = response.get("corrections")
        if not isinstance(corrections, list):
            return

        filtered = [
            correction
            for correction in corrections
            if cls._correction_belongs_to_text(correction, text)
        ]
        response["corrections"] = filtered
        response["has_errors"] = bool(filtered)

    @staticmethod
    def _correction_belongs_to_text(correction: dict, text: str) -> bool:
        original = correction.get("original") if isinstance(correction, dict) else None
        if not isinstance(original, str) or not original.strip():
            return False

        normalized_original = " ".join(original.split()).casefold()
        normalized_text = " ".join(text.split()).casefold()
        return normalized_original in normalized_text

    @staticmethod
    def _remove_repeated_correction_reply(response: dict) -> None:
        reply = response.get("reply")
        natural_variant = response.get("natural_variant")
        if not isinstance(reply, str) or not isinstance(natural_variant, str):
            return

        if " ".join(reply.split()).casefold() != " ".join(natural_variant.split()).casefold():
            return

        response["reply"] = ""
        response["reply_translation"] = None
