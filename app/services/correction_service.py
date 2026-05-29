import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.user import User
from app.core.enums import BotMode, MessageRole
from app.infrastructure.llm import LLMTask, build_system_prompt, llm_client
from app.services.ai_usage_service import AIUsageService
from app.services.conversation_service import ConversationService
from app.services.user_service import UserService

logger = structlog.get_logger()


class CorrectionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_service = UserService(session)
        self.usage_service = AIUsageService(session)

    async def correct_phrase(self, user: User, text: str) -> dict:
        system_prompt = build_system_prompt(
            level=user.level or "A2",
            goal=user.goal or "communication",
            correction_intensity="all",
            mode="correction",
        )

        messages = [{"role": "user", "content": text}]

        try:
            response = await llm_client.complete(
                system_prompt,
                messages,
                task=LLMTask.CORRECTION,
                premium=user.subscription_tier == "premium",
            )
            if "error" in response:
                logger.error("LLM correction error", response=response)
                return {
                    "error": True,
                    "message": "Ошибка обработки. Попробуй позже.",
                }
            await self.usage_service.record(
                user,
                BotMode.CORRECTION.value,
                response.get("_llm_usage"),
            )
            ConversationService._normalize_response_spanish_punctuation(response)
            if isinstance(response.get("full_corrected"), str):
                response["full_corrected"] = ConversationService._normalize_spanish_punctuation(
                    response["full_corrected"]
                )

            await self.user_service.save_message(
                user=user,
                text=text,
                role=MessageRole.USER,
                mode=BotMode.CORRECTION,
                corrected_text=response.get("full_corrected"),
                has_errors=response.get("has_errors", False),
            )

            return response

        except Exception as e:
            logger.error("Correction error", error=str(e))
            return {
                "error": True,
                "message": "Произошла ошибка. Попробуй позже.",
            }
