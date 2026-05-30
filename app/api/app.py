from fastapi import FastAPI

from app.api.routes import health, subscription, webhook

app = FastAPI(title="Sol de Mañana Bot API", version="0.1.0")

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
app.include_router(subscription.router, tags=["subscription"])


@app.get("/")
async def root():
    return {"status": "ok", "service": "Sol de Mañana Bot API"}
