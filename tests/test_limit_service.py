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
