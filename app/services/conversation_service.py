import re

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


def _find_next(chars: list[str], target: str, start: int) -> int:
    try:
        return chars.index(target, start)
    except ValueError:
        return -1


def _find_next_sentence_end(chars: list[str], start: int) -> int:
    for index in range(start, len(chars)):
        if chars[index] in ".\n":
            return index
    return -1


def _trim_insert_position(chars: list[str], index: int) -> int:
    while index > 0 and chars[index - 1].isspace():
        index -= 1
    return index


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

        history = await self.user_service.get_dialog_history(
            user=user,
            mode=BotMode.CONVERSATION,
            limit=settings.dialog_history_size,
        )
        messages = self.user_service.build_compact_messages(history)
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
            self._normalize_response_spanish_punctuation(response)
            self._keep_current_message_corrections(response, text)
            self._remove_stale_natural_variant(response, history)
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

    @classmethod
    def _normalize_response_spanish_punctuation(cls, response: dict) -> None:
        for key in ("natural_variant", "reply"):
            value = response.get(key)
            if isinstance(value, str):
                response[key] = cls._normalize_spanish_punctuation(value)

        for key in ("corrections",):
            items = response.get(key)
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                corrected = item.get("corrected")
                if isinstance(corrected, str):
                    item["corrected"] = cls._normalize_spanish_punctuation(corrected)

    @staticmethod
    def _normalize_spanish_punctuation(text: str) -> str:
        def normalize_match(match: re.Match[str]) -> str:
            segment = match.group(0)
            stripped = segment.lstrip()
            leading = segment[: len(segment) - len(stripped)]
            if segment.rstrip().endswith("?") and "¿" not in segment:
                comma_index = segment.rfind(",")
                if comma_index >= 0:
                    tail = segment[comma_index + 1 :].strip()
                    if 0 < len(tail.split()) <= 4:
                        return f"{segment[:comma_index + 1]} ¿{tail}"
                return f"{leading}¿{stripped}"
            if segment.rstrip().endswith("!") and "¡" not in segment:
                return f"{leading}¡{stripped}"
            return segment

        normalized = re.sub(r"[^.!?]*[?!]+", normalize_match, text)
        return ConversationService._close_unpaired_spanish_marks(normalized)

    @staticmethod
    def _close_unpaired_spanish_marks(text: str) -> str:
        chars = list(text)
        index = 0
        while index < len(chars):
            opener = chars[index]
            closer = "?" if opener == "¿" else "!" if opener == "¡" else None
            if closer is None:
                index += 1
                continue

            next_same = _find_next(chars, opener, index + 1)
            next_closer = _find_next(chars, closer, index + 1)
            sentence_end = _find_next_sentence_end(chars, index + 1)
            boundary = min(
                candidate
                for candidate in (next_same, sentence_end, len(chars))
                if candidate != -1
            )

            if next_closer == -1 or next_closer > boundary:
                insert_at = _trim_insert_position(chars, boundary)
                chars.insert(insert_at, closer)
                index = insert_at + 1
            else:
                index = next_closer + 1

        return "".join(chars)

    @staticmethod
    def _remove_stale_natural_variant(response: dict, history: list) -> None:
        natural_variant = response.get("natural_variant")
        if not isinstance(natural_variant, str) or not natural_variant.strip():
            return

        normalized_variant = " ".join(natural_variant.split()).casefold()
        for message in history:
            candidates = [
                getattr(message, "text", None),
                getattr(message, "corrected_text", None),
            ]
            for candidate in candidates:
                if not isinstance(candidate, str) or not candidate.strip():
                    continue
                if normalized_variant == " ".join(candidate.split()).casefold():
                    response["natural_variant"] = None
                    return
