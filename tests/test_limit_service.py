from datetime import date

from app.core.enums import CorrectionIntensity, SubscriptionTier
from app.core.models.user import User
from app.services.limit_service import LimitService


def test_admin_has_no_daily_message_limit() -> None:
    user = User(
        telegram_id=181075918,
        first_name="Anton",
        correction_intensity=CorrectionIntensity.IMPORTANT.value,
        subscription_tier=SubscriptionTier.FREE.value,
        messages_today=10,
        last_message_date=date.today(),
        total_messages=10,
    )

    limit_service = LimitService(None)

    assert limit_service.get_daily_limit(user) is None
    assert limit_service.can_send_message(user) is True
    assert limit_service.get_remaining(user) is None


def test_limit_exceeded_text_points_to_subscribe_command() -> None:
    user = User(
        telegram_id=123,
        first_name="User",
        correction_intensity=CorrectionIntensity.IMPORTANT.value,
        subscription_tier=SubscriptionTier.FREE.value,
        messages_today=10,
        last_message_date=date.today(),
        total_messages=10,
    )

    text = LimitService(None).get_limit_exceeded_text(user)

    assert "/subscribe" in text
    assert "/subscription" not in text


def test_basic_plan_has_fifty_daily_messages() -> None:
    user = User(
        telegram_id=123,
        first_name="User",
        correction_intensity=CorrectionIntensity.IMPORTANT.value,
        subscription_tier=SubscriptionTier.BASIC.value,
        messages_today=49,
        last_message_date=date.today(),
        total_messages=49,
    )

    limit_service = LimitService(None)

    assert limit_service.get_daily_limit(user) == 50
    assert limit_service.can_send_message(user) is True
    assert limit_service.get_remaining(user) == 1
