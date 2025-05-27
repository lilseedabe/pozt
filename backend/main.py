import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# 静的ファイルディレクトリを作成
os.makedirs("static", exist_ok=True)

# 静的ファイルの提供設定
app.mount("/static", StaticFiles(directory="static"), name="static")

# フロントエンドのアセットファイル（JSやCSS）を提供するマウント
# 注意: フロントエンドのビルド構造によって変更が必要かもしれません
try:
    if os.path.exists("static/assets"):
        app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
except Exception as e:
    print(f"アセットマウント中にエラーが発生しました: {e}")

# ルートパスでindex.htmlを提供
@app.get("/")
async def serve_root():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Welcome to pozt API"}

# その他のパスに対するフォールバック - SPAルーティング用
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # まず実際のファイルの存在を確認
    file_path = f"static/{full_path}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    # SPA用のフォールバック
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    
    # index.htmlも無い場合はAPIのルートを示す
    return {"error": "Not found", "message": "API endpoints are available at /api"}
