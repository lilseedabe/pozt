from fastapi import Depends, HTTPException, status
from config.app import get_settings, Settings

async def get_api_settings() -> Settings:
    """API設定の依存関係"""
    return get_settings()

async def validate_file_size(file_size: int, settings: Settings = Depends(get_api_settings)):
    """ファイルサイズのバリデーション"""
    max_size = settings.MAX_UPLOAD_SIZE
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size ({max_size / 1024 / 1024:.1f}MB)"
