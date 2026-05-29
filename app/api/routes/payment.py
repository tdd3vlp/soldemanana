from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select
from datetime import datetime, timedelta
import structlog
import json

from app.core.database import sessionmaker
from app.core.models.user import User
from app.core.models.subscription import Subscription
from app.infrastructure.payments import YooKassaService

logger = structlog.get_logger()
router = APIRouter()


@router.post("/yookassa/webhook")
async def yookassa_webhook(request: Request):
    try:
        payload = await request.json()
        event_type = payload.get("event")
        
        if event_type == "payment.succeeded":
            payment_object = payload.get("object", {})
            payment_id = payment_object.get("id")
            metadata = payment_object.get("metadata", {})
            telegram_id = int(metadata.get("telegram_id", 0))
            
            if not telegram_id:
                logger.warning("No telegram_id in payment metadata", payment_id=payment_id)
                return {"status": "error", "message": "No telegram_id"}
            
            async with sessionmaker() as db:
                result = await db.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
                
                if user:
                    user.subscription_tier = "premium"
                    
                    subscription = Subscription(
                        user_id=user.id,
                        tier="premium",
                        valid_from=datetime.utcnow(),
                        valid_until=datetime.utcnow() + timedelta(days=30),
                        is_active=True,
                        payment_provider="yookassa",
                        payment_id=payment_id,
                    )
                    db.add(subscription)
                    await db.commit()
                    
                    logger.info(
                        "Subscription activated via YooKassa",
                        telegram_id=telegram_id,
                        payment_id=payment_id
                    )
                else:
                    logger.warning("User not found", telegram_id=telegram_id)
        
        elif event_type == "payment.canceled":
            payment_object = payload.get("object", {})
            payment_id = payment_object.get("id")
            logger.info("Payment canceled", payment_id=payment_id)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error("YooKassa webhook error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
