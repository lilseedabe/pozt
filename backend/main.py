import os
from fastapi import FastAPI, Depends, Request
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

# Reactビルドファイルのパスを書き換えるミドルウェア
@app.middleware("http")
async def rewrite_static_paths(request: Request, call_next):
    path = request.url.path
    
    # CSS、JS、メディアファイルのパス変換
    if path.startswith("/static/") or path == "/manifest.json" or path == "/favicon.ico":
        # すでに処理されているパスはそのまま
        pass
    elif path.startswith("/assets/"):
        # アセットパスは/static/assetsに変換
        request.scope["path"] = f"/static{path}"
    elif path.startswith("/static/js/") or path.startswith("/static/css/") or path.startswith("/static/media/"):
        # すでに/static/が含まれているパスはそのまま
        pass
    elif path.startswith("/js/") or path.startswith("/css/") or path.startswith("/media/"):
        # /js/, /css/, /media/パスを/static/js/などに変換
        request.scope["path"] = f"/static{path}"
    
    response = await call_next(request)
    return response

# ルーターの登録
app.include_router(health.router, tags=["Health"])
app.include_router(image.router, prefix="/api", tags=["Image Processing"])

# 静的ファイルディレクトリを作成
os.makedirs("static", exist_ok=True)

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

# ルートパスとその他のパスはindex.htmlにフォールバック
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str = ""):
    # APIパスは既にルーターに登録されているのでここには来ない
    
    # 特定のファイルパスの処理
    if full_path == "favicon.ico" and os.path.exists("static/favicon.ico"):
        return FileResponse("static/favicon.ico")
    elif full_path == "manifest.json" and os.path.exists("static/manifest.json"):
        return FileResponse("static/manifest.json")
    
    # 特定のパスが静的ファイルとして存在する場合はそれを返す
    file_path = f"static/{full_path}"
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        return FileResponse(file_path)
    
    # それ以外のすべてのパスはindex.htmlにフォールバック
    index_path = "static/index.html"
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    # Reactビルドがない場合のフォールバック（開発環境用）
    return FileResponse("static/index.html") if os.path.exists("static/index.html") else {"message": "Frontend not built yet"}
