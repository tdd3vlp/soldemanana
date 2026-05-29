from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/bot")
async def webhook_handler(request: Request):
    return {"status": "webhook_not_configured", "message": "Use polling mode for MVP"}
