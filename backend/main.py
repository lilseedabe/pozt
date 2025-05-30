import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, Response, RedirectResponse
from api.routes import image, health
from config.app import get_settings

# アクセス制御ミドルウェアをインポート
from middleware.access_control import AccessControlMiddleware

app = FastAPI(
    title="pozt API",
    description="Pattern Optical Zone Technology",
    version="1.0.0"
)

# アクセス制御ミドルウェアを追加（最初に追加することが重要）
app.add_middleware(
    AccessControlMiddleware,
    allowed_origin="pozt.iodo.co.jp",  # 許可するドメイン
    session_timeout=1800  # 30分 = 1800秒
)

# CORS設定
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pozt.iodo.co.jp", "http://pozt.iodo.co.jp"],  # 特定のオリジンのみ許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルート
app.include_router(health.router, tags=["Health"])
app.include_router(image.router, prefix="/api", tags=["Image"])

# React ビルド成果物へのパス
BASE_DIR = os.path.dirname(__file__)
REACT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "build"))
REACT_STATIC_DIR = os.path.join(REACT_DIR, "static")

# アップロードファイル用の静的ディレクトリ
UPLOAD_STATIC_DIR = os.path.join(BASE_DIR, "static")

# アップロードファイル用の静的ディレクトリを作成
os.makedirs(UPLOAD_STATIC_DIR, exist_ok=True)

# React の静的ファイル（js/css等）の提供
if os.path.isdir(REACT_STATIC_DIR):
    app.mount("/static", StaticFiles(directory=REACT_STATIC_DIR), name="react_static")

# アップロードされた画像ファイルの提供 - より高い優先度で設定
app.mount("/uploads", StaticFiles(directory=UPLOAD_STATIC_DIR), name="upload_static")

# セッション状態確認エンドポイント（デバッグ用）
@app.get("/api/session-status")
async def session_status(request: Request):
    """現在のセッション状態を確認するエンドポイント"""
    session_remaining = request.headers.get("X-Session-Remaining", "Unknown")
    session_id = request.headers.get("X-Session-ID", "Unknown")
    
    return {
        "session_id": session_id,
        "remaining_seconds": session_remaining,
        "remaining_minutes": int(session_remaining) // 60 if session_remaining.isdigit() else "Unknown",
        "access_origin": request.headers.get("origin", "Unknown"),
        "referrer": request.headers.get("referer", "Unknown")
    }

# ルート("/"): React の index.html
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(REACT_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content="<h1>React アプリがビルドされていません。</h1>", status_code=404)

# favicon
@app.get("/favicon.ico")
async def favicon():
    ico = os.path.join(REACT_DIR, "favicon.ico")
    if os.path.isfile(ico):
        return FileResponse(ico)
    return Response(status_code=204)

# /docs → /api/docs
@app.get("/docs")
async def docs():
    return RedirectResponse("/api/docs")

# SPA フォールバック（React Router 対応）
@app.get("/{path:path}", response_class=HTMLResponse)
async def spa(path: str, request: Request):
    if path.startswith("api") or path.startswith("static") or path.startswith("uploads"):
        return Response(status_code=404, content="Not Found")
    index_path = os.path.join(REACT_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content="<h1>React アプリがビルドされていません。</h1>", status_code=404)
