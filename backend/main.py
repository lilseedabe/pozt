import os
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
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

# ルートパスでHTML直接提供
@app.get("/", response_class=HTMLResponse)
async def serve_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>pozt - 視覚の魔法を体験しよう</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #141a2b;
                color: #ffffff;
                line-height: 1.6;
                margin: 0;
                padding: 2rem;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                width: 100%;
            }
            h1 {
                font-size: 3rem;
                background: linear-gradient(135deg, #00a8ff, #7a5af8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0.5rem;
                text-align: center;
            }
            h2 {
                color: #a0aec0;
                font-weight: 400;
                margin-top: 0;
                text-align: center;
                margin-bottom: 2rem;
            }
            .card {
                background-color: #1c2438;
                border-radius: 8px;
                padding: 2rem;
                margin: 2rem 0;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            }
            p {
                color: #a0aec0;
            }
            .api-link {
                display: inline-block;
                margin-top: 1rem;
                padding: 0.75rem 1.5rem;
                background: linear-gradient(135deg, #00a8ff, #7a5af8);
                color: white;
                text-decoration: none;
                border-radius: 4px;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            .api-link:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0, 168, 255, 0.3);
            }
            footer {
                margin-top: 2rem;
                text-align: center;
                color: #718096;
                font-size: 0.875rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>pozt</h1>
            <h2>Pattern Optical Zone Technology - 視覚の魔法を体験しよう</h2>
            
            <div class="card">
                <p>poztは、独自の光学パターン技術を活用して、見る角度や表示環境によって変化する驚きの視覚アート作品を作成できる無料のウェブアプリケーションです。</p>
                <p>現在、フロントエンド部分を開発中です。APIは既に利用可能です。</p>
                <a href="/api/docs" class="api-link">API ドキュメントを見る</a>
            </div>
            
            <footer>
                <p>&copy; 2025 pozt - Pattern Optical Zone Technology</p>
            </footer>
        </div>
    </body>
    </html>
    """
    return html_content

# マニフェストファイルのルート
@app.get("/manifest.json")
async def serve_manifest():
    return JSONResponse({
        "short_name": "pozt",
        "name": "Pattern Optical Zone Technology",
        "icons": [
            {
                "src": "favicon.ico",
                "sizes": "64x64 32x32 24x24 16x16",
                "type": "image/x-icon"
            }
        ],
        "start_url": ".",
        "display": "standalone",
        "theme_color": "#141a2b",
        "background_color": "#141a2b"
    })

# ファビコンのルート
@app.get("/favicon.ico")
async def serve_favicon():
    if os.path.exists("static/favicon.ico"):
        return FileResponse("static/favicon.ico")
    # デフォルトの空のレスポンス
    return Response(content=b"", media_type="image/x-icon")

# JSとCSSのファイルリクエスト対応
@app.get("/js/{file_path:path}")
async def serve_js(file_path: str):
    return JSONResponse({"message": f"JS file '{file_path}' not available in this version"})

@app.get("/css/{file_path:path}")
async def serve_css(file_path: str):
    return JSONResponse({"message": f"CSS file '{file_path}' not available in this version"})

# その他のパスに対するフォールバック
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # 特定のパスの場合は専用のハンドラーを呼び出す
    if full_path.startswith("js/") or full_path.startswith("css/"):
        parts = full_path.split("/", 1)
        if parts[0] == "js":
            return await serve_js(parts[1] if len(parts) > 1 else "")
        elif parts[0] == "css":
            return await serve_css(parts[1] if len(parts) > 1 else "")
    
    # まず実際のファイルの存在を確認
    file_path = f"static/{full_path}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    # APIドキュメントへのリダイレクト
    if full_path == "docs":
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/api/docs")
    
    # 他のパスはルートハンドラーと同じHTMLを返す
    return await serve_root()
