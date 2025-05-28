from fastapi import APIRouter, Depends
from config.app import get_settings, Settings
import psutil
import os

router = APIRouter()

@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    """メモリ監視付きヘルスチェックエンドポイント（高品質維持版）"""
    try:
        # メモリ使用量を取得
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024  # MB単位
        
        # メモリ使用率を計算
        memory_percent = process.memory_percent()
        
        # 警告レベルの設定（高品質版に合わせて調整）
        warning_threshold = 350  # 350MB
        critical_threshold = 450  # 450MB (512MBの88%)
        
        status = "ok"
        if memory_mb > critical_threshold:
            status = "critical"
        elif memory_mb > warning_threshold:
            status = "warning"
        
        return {
            "status": status,
            "app_name": settings.APP_NAME,
            "version": "1.0.0-high-quality-optimized",
            "memory": {
                "usage_mb": round(memory_mb, 2),
                "usage_percent": round(memory_percent, 2),
                "warning_threshold": warning_threshold,
                "critical_threshold": critical_threshold
            },
            "configuration": {
                "target_size": f"{settings.TARGET_WIDTH}x{settings.TARGET_HEIGHT}",
                "max_upload_mb": settings.MAX_UPLOAD_SIZE / 1024 / 1024,
                "single_preview_mode": getattr(settings, 'ENABLE_SINGLE_PREVIEW_MODE', True),
                "quality_level": "high"  # 高品質維持を示す
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "app_name": settings.APP_NAME
        }
