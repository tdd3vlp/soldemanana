from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.models.ai_usage import AIUsage
from app.core.models.user import User


class AIUsageService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_cost = prompt_tokens * settings.ai_input_cost_per_1m / 1_000_000
        output_cost = completion_tokens * settings.ai_output_cost_per_1m / 1_000_000
        return round(input_cost + output_cost, 6)

    async def record(self, user: User, mode: str, meta: dict | None) -> None:
        if not meta:
            return

        prompt_tokens = int(meta.get("prompt_tokens") or 0)
        completion_tokens = int(meta.get("completion_tokens") or 0)
        total_tokens = int(meta.get("total_tokens") or prompt_tokens + completion_tokens)
        estimated_cost = self.estimate_cost(prompt_tokens, completion_tokens)

        self.session.add(
            AIUsage(
                user_id=user.id,
                mode=mode,
                model=str(meta.get("model") or "unknown"),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=Decimal(str(estimated_cost)),
            )
        )
        await self.session.flush()

    async def get_user_month_estimate(self, user: User) -> dict:
        result = await self.session.execute(
            select(
                func.coalesce(func.sum(AIUsage.prompt_tokens), 0),
                func.coalesce(func.sum(AIUsage.completion_tokens), 0),
                func.coalesce(func.sum(AIUsage.estimated_cost_usd), 0),
            ).where(
                AIUsage.user_id == user.id,
                func.date_trunc("month", AIUsage.created_at)
                == func.date_trunc("month", func.now()),
            )
        )
        prompt_tokens, completion_tokens, estimated_cost = result.one()
        return {
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "total_tokens": int(prompt_tokens) + int(completion_tokens),
            "estimated_cost_usd": float(estimated_cost),
        }
