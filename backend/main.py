import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import image, health
from config.app import get_settings

# アプリケーションの作成
app = FastAPI(
    title="pozt API",
    description="Pattern Optical Zone Technology - 視覚の魔法を体験しよう",
    version="1.0.0"
)

# 設定の取得
settings = get_settings()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(health.router, tags=["Health"])
app.include_router(image.router, prefix="/api", tags=["Image Processing"])

# 静的ファイルの提供設定
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時に実行される処理"""
    # 一時ディレクトリの初期化
    os.makedirs("static", exist_ok=True)
    print("pozt API server started successfully")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
