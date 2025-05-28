import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, Response, RedirectResponse
from api.routes import image, health
from config.app import get_settings

app = FastAPI(
    title="pozt API",
    description="Pattern Optical Zone Technology",
    version="1.0.0"
)

# CORS設定
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
STATIC_DIR = os.path.join(REACT_DIR, "static")

# 静的ファイル（js/css等）の提供
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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
    if path.startswith("api") or path.startswith("static"):
        return Response(status_code=404, content="Not Found")
    index_path = os.path.join(REACT_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content="<h1>React アプリがビルドされていません。</h1>", status_code=404)
