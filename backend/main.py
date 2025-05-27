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
    
    # CSSとJSファイルのパスを書き換え
    if path.startswith("/css/") or path.startswith("/js/") or path.startswith("/media/"):
        # /css/ -> /static/static/css/
        new_path = f"/static/static{path}"
        request.scope["path"] = new_path
    
    response = await call_next(request)
    return response

# ルーターの登録
app.include_router(health.router, tags=["Health"])
app.include_router(image.router, prefix="/api", tags=["Image Processing"])

# 静的ファイルディレクトリを作成
os.makedirs("static", exist_ok=True)

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

# Reactの静的ファイルディレクトリのマウント（存在する場合）
# create-react-appのビルド構造に対応
if os.path.exists("static/static"):
    try:
        # 追加のマウントポイント - Reactビルドの静的アセット用
        if os.path.exists("static/static/css"):
            app.mount("/css", StaticFiles(directory="static/static/css"), name="css")
        if os.path.exists("static/static/js"):
            app.mount("/js", StaticFiles(directory="static/static/js"), name="js")
        if os.path.exists("static/static/media"):
            app.mount("/media", StaticFiles(directory="static/static/media"), name="media")
    except Exception as e:
        print(f"Reactの静的ファイルマウント中にエラーが発生しました: {e}")

# 通常のアセットディレクトリもマウント
try:
    if os.path.exists("static/assets"):
        app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
except Exception as e:
    print(f"アセットマウント中にエラーが発生しました: {e}")

# マニフェストファイルのルート
@app.get("/manifest.json")
async def serve_manifest():
    if os.path.exists("static/manifest.json"):
        return FileResponse("static/manifest.json")
    return {"error": "Manifest not found"}

# ファビコンのルート
@app.get("/favicon.ico")
async def serve_favicon():
    if os.path.exists("static/favicon.ico"):
        return FileResponse("static/favicon.ico")
    return {"error": "Favicon not found"}

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
    
    # 特定のパターンのファイルパスを確認
    if full_path.startswith("static/"):
        direct_path = full_path
        if os.path.exists(direct_path):
            return FileResponse(direct_path)
    
    # SPA用のフォールバック
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    
    # index.htmlも無い場合はAPIのルートを示す
    return {"error": "Not found", "message": "API endpoints are available at /api"}
