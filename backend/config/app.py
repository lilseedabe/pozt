from pydantic import BaseSettings
from functools import lru_cache
import os
from typing import List

class Settings(BaseSettings):
    """アプリケーション設定（高品質維持・プレビュー削減版）"""
    APP_NAME: str = "pozt"
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    STATIC_DIR: str = "static"
    
    # CORS設定
    CORS_ORIGINS: List[str] = ["*"]
    
    # 画像設定（高品質維持）
    TARGET_WIDTH: int = 2430   # 元のサイズを維持
    TARGET_HEIGHT: int = 3240  # 元のサイズを維持
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MBに設定
    
    # ファイル管理
    TEMP_FILE_EXPIRY: int = 3600  # 1時間（秒）
    
    # メモリ最適化設定（プレビュー削減のみ）
    ENABLE_SINGLE_PREVIEW_MODE: bool = True  # プレビューを1つのみ生成
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """キャッシュされた設定を取得"""
    return Settings()
