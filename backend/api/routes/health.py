from fastapi import APIRouter, Depends
from config.app import get_settings, Settings

router = APIRouter()

@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    """ヘルスチェックエンドポイント"""
    return {
        "status": "ok",
        "app_name": settings.APP_NAME,
        "version": "1.0.0"
    }
