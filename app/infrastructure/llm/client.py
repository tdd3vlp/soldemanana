import json
from enum import StrEnum
import structlog
from openai import AsyncOpenAI
from app.config import settings

logger = structlog.get_logger()


class LLMTask(StrEnum):
    CHAT = "chat"
    CORRECTION = "correction"
    SCENARIO = "scenario"
    GRAMMAR = "grammar"
    SUMMARY = "summary"


class LLMClient:
    def __init__(self) -> None:
        client_kwargs = {
            "api_key": settings.openai_api_key,
            "max_retries": 2,
            "timeout": 30,
        }
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url

        self._client = AsyncOpenAI(**client_kwargs)

    def _model_for_task(self, task: LLMTask, premium: bool = False) -> str:
        if task == LLMTask.SUMMARY:
            return settings.openai_summary_model
        if task in {LLMTask.CORRECTION, LLMTask.GRAMMAR} and premium:
            return settings.openai_strong_model
        return settings.openai_fast_model or settings.openai_model

    def _max_tokens_for_task(self, task: LLMTask, max_tokens: int | None) -> int:
        if max_tokens is not None:
            return max_tokens
        if task == LLMTask.SUMMARY:
            return settings.openai_summary_max_tokens
        if task in {LLMTask.CORRECTION, LLMTask.GRAMMAR}:
            return settings.openai_correction_max_tokens
        return settings.openai_max_tokens

    def _usage_meta(self, response, model: str) -> dict:
        usage = getattr(response, "usage", None)
        return {
            "model": model,
            "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
            "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
            "total_tokens": getattr(usage, "total_tokens", 0) if usage else 0,
        }

    async def complete(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
        task: LLMTask = LLMTask.CHAT,
        premium: bool = False,
    ) -> dict:
        temp = temperature if temperature is not None else settings.openai_temperature
        tokens = self._max_tokens_for_task(task, max_tokens)
        model = self._model_for_task(task, premium=premium)

        openai_messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            response = await self._client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temp,
                max_tokens=tokens,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            payload = json.loads(content)
            if isinstance(payload, dict):
                payload["_llm_usage"] = self._usage_meta(response, model)
            return payload
        except json.JSONDecodeError as e:
            logger.error("LLM JSON parse error", error=str(e), content=content)
            return {"error": "parse_error", "raw": content}
        except Exception as e:
            logger.error("LLM API error", error=str(e), task=task, model=model)
            raise

    async def complete_text(
        self,
        system_prompt: str,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
        task: LLMTask = LLMTask.CHAT,
        premium: bool = False,
    ) -> str:
        temp = temperature if temperature is not None else settings.openai_temperature
        tokens = self._max_tokens_for_task(task, max_tokens)
        model = self._model_for_task(task, premium=premium)

        openai_messages = [{"role": "system", "content": system_prompt}] + messages

        response = await self._client.chat.completions.create(
            model=model,
            messages=openai_messages,
            temperature=temp,
            max_tokens=tokens,
        )
        return response.choices[0].message.content or ""


llm_client = LLMClient()
