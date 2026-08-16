from fastapi import FastAPI
from app.api.routes.tenders import router as tenders_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(tenders_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
