import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models.user import User
from app.core.enums import BotMode, MessageRole
from app.infrastructure.llm import LLMTask, build_scenario_context, build_system_prompt, llm_client
from app.services.ai_usage_service import AIUsageService
from app.services.user_service import UserService
from app.config import settings

logger = structlog.get_logger()


class ScenarioService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_service = UserService(session)
        self.usage_service = AIUsageService(session)

    async def start_scenario(self, user: User, scenario_id: str, scenario_title: str) -> str:
        scenario_context = build_scenario_context(scenario_id, scenario_title)
        system_prompt = build_system_prompt(
            level=user.level or "A2",
            goal=user.goal or "communication",
            correction_intensity=user.correction_intensity,
            mode="scenarios",
            extra_context=scenario_context,
        )

        messages = [{"role": "user", "content": "Начни ситуацию. Ты первый."}]

        try:
            response = await llm_client.complete(system_prompt, messages, task=LLMTask.SCENARIO)
            if "error" in response:
                logger.error("Scenario start error", response=response)
                return "Ошибка запуска сценария."
            await self.usage_service.record(
                user,
                BotMode.SCENARIOS.value,
                response.get("_llm_usage"),
            )

            role_reply = response.get("role_reply", "¡Hola!")
            await self.user_service.save_message(
                user=user,
                text=role_reply,
                role=MessageRole.ASSISTANT,
                mode=BotMode.SCENARIOS,
                scenario_id=scenario_id,
            )

            result = [f"🇪🇸 {role_reply}"]
            if response.get("role_reply_translation"):
                result.append(f"<i>({response['role_reply_translation']})</i>")
            if response.get("useful_phrase"):
                result.append(
                    f"\n💡 <b>Полезная фраза:</b> {response['useful_phrase']}"
                )

            return "\n".join(result)

        except Exception as e:
            logger.error("Scenario start error", error=str(e))
            return "Произошла ошибка при запуске сценария."

    async def process_scenario_message(
        self, user: User, text: str, scenario_id: str
    ) -> dict:
        scenario_title = scenario_id.replace("_", " ").title()
        scenario_context = build_scenario_context(scenario_id, scenario_title)
        system_prompt = build_system_prompt(
            level=user.level or "A2",
            goal=user.goal or "communication",
            correction_intensity=user.correction_intensity,
            mode="scenarios",
            extra_context=scenario_context,
        )

        messages = await self.user_service.get_compact_dialog_history(
            user=user,
            mode=BotMode.SCENARIOS,
            limit=settings.dialog_history_size,
            scenario_id=scenario_id,
        )
        messages.append({"role": "user", "content": text})

        try:
            response = await llm_client.complete(system_prompt, messages, task=LLMTask.SCENARIO)
            if "error" in response:
                logger.error("Scenario processing error", response=response)
                return {
                    "error": True,
                    "message": "Ошибка обработки.",
                }
            await self.usage_service.record(
                user,
                BotMode.SCENARIOS.value,
                response.get("_llm_usage"),
            )

            await self.user_service.save_message(
                user=user,
                text=text,
                role=MessageRole.USER,
                mode=BotMode.SCENARIOS,
                scenario_id=scenario_id,
                has_errors=response.get("has_errors", False),
            )

            bot_reply = response.get("role_reply", "...")
            await self.user_service.save_message(
                user=user,
                text=bot_reply,
                role=MessageRole.ASSISTANT,
                mode=BotMode.SCENARIOS,
                scenario_id=scenario_id,
            )

            return response

        except Exception as e:
            logger.error("Scenario message error", error=str(e))
            return {
                "error": True,
                "message": "Произошла ошибка.",
            }
