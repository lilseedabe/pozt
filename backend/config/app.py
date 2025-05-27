from pydantic import BaseSettings
from functools import lru_cache
import os
from typing import List

class Settings(BaseSettings):
    """アプリケーション設定"""
    APP_NAME: str = "pozt"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    STATIC_DIR: str = "static"
    
    # CORS設定
    CORS_ORIGINS: List[str] = ["*"]
    
    # 画像設定
    TARGET_WIDTH: int = 2430
    TARGET_HEIGHT: int = 3240
    MAX_UPLOAD_SIZE: int = 20 * 1024 * 1024  # 20MB
    
    # ファイル管理
    TEMP_FILE_EXPIRY: int = 3600  # 1時間（秒）
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """キャッシュされた設定を取得"""
    return Settings()
