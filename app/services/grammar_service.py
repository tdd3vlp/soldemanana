import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.user import User
from app.core.enums import BotMode, MessageRole
from app.infrastructure.llm import (
    LLMTask,
    build_grammar_check_prompt,
    get_grammar_intro,
    llm_client,
)
from app.services.ai_usage_service import AIUsageService
from app.services.user_service import UserService

logger = structlog.get_logger()


class GrammarService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_service = UserService(session)
        self.usage_service = AIUsageService(session)

    async def start_topic(self, user: User, topic_id: str, topic_title: str) -> dict:
        return get_grammar_intro(topic_id, topic_title, user.level or "A2")

    async def check_answer(
        self,
        user: User,
        topic_id: str,
        topic_title: str,
        user_answer: str,
        exercise: str | None = None,
    ) -> dict:
        prompt = build_grammar_check_prompt(topic_id, topic_title, user.level or "A2", exercise)
        messages = [{"role": "user", "content": user_answer}]

        try:
            response = await llm_client.complete(
                prompt,
                messages,
                task=LLMTask.GRAMMAR,
                premium=user.subscription_tier == "premium",
            )
            if "error" in response:
                logger.error("Grammar check error", response=response)
                return {
                    "error": True,
                    "message": "Ошибка проверки ответа.",
                }
            await self.usage_service.record(
                user,
                BotMode.GRAMMAR.value,
                response.get("_llm_usage"),
            )

            await self.user_service.save_message(
                user=user,
                text=user_answer,
                role=MessageRole.USER,
                mode=BotMode.GRAMMAR,
                grammar_topic=topic_id,
            )

            return response

        except Exception as e:
            logger.error("Grammar check error", error=str(e))
            return {
                "error": True,
                "message": "Произошла ошибка.",
            }
