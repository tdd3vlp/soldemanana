from yookassa import Configuration, Payment
import uuid
from typing import Optional
import structlog

from app.config import settings

Configuration.account_id = settings.yookassa_shop_id
Configuration.secret_key = settings.yookassa_secret_key

logger = structlog.get_logger()


class YooKassaService:
    @staticmethod
    def create_payment(user_id: int, telegram_id: int, amount: float = 599.0) -> Optional[str]:
        try:
            idempotence_key = str(uuid.uuid4())
            
            payment = Payment.create({
                "amount": {
                    "value": str(amount),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"https://t.me/your_bot?start=payment_success"
                },
                "capture": True,
                "description": f"Подписка PREMIUM — Sol de Mañana Bot",
                "metadata": {
                    "user_id": str(user_id),
                    "telegram_id": str(telegram_id),
                }
            }, idempotence_key)
            
            confirmation_url = payment.confirmation.confirmation_url
            logger.info("Payment created", payment_id=payment.id, telegram_id=telegram_id)
            return confirmation_url
            
        except Exception as e:
            logger.error("YooKassa payment creation error", error=str(e))
            return None

    @staticmethod
    def get_payment_info(payment_id: str):
        try:
            payment = Payment.find_one(payment_id)
            return payment
        except Exception as e:
            logger.error("YooKassa get payment error", error=str(e), payment_id=payment_id)
            return None
