from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check():
    return {"status": "healthy", "service": "sol_de_manana_bot"}


@router.get("/db")
async def db_health():
    return {"status": "healthy", "database": "connected"}
