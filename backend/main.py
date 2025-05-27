import os
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, Response
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

# ルートパス処理 - 高機能なランディングページをインラインで提供
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
            :root {
                --bg-primary: #141a2b;
                --bg-secondary: #1c2438;
                --bg-tertiary: #252e42;
                --accent-primary: #00a8ff;
                --accent-secondary: #7a5af8;
                --text-primary: #ffffff;
                --text-secondary: #a0aec0;
                --border-color: #2d3748;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                background-color: var(--bg-primary);
                color: var(--text-primary);
                line-height: 1.6;
                min-height: 100vh;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            header {
                text-align: center;
                padding: 3rem 0;
            }
            
            .gradient-text {
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                display: inline-block;
            }
            
            h1 {
                font-size: 4rem;
                margin-bottom: 0.5rem;
                letter-spacing: -0.05em;
            }
            
            h2 {
                font-size: 1.5rem;
                font-weight: 400;
                color: var(--text-secondary);
                margin-bottom: 2rem;
            }
            
            h3 {
                font-size: 1.75rem;
                margin-bottom: 1rem;
                color: var(--accent-primary);
            }
            
            .hero {
                text-align: center;
                margin-bottom: 4rem;
            }
            
            .card {
                background-color: var(--bg-secondary);
                border-radius: 12px;
                padding: 2rem;
                margin-bottom: 2rem;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
                border: 1px solid var(--border-color);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            }
            
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                margin-bottom: 4rem;
            }
            
            .feature-card {
                background-color: var(--bg-tertiary);
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                border: 1px solid var(--border-color);
            }
            
            .feature-icon {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                color: var(--accent-primary);
            }
            
            .btn {
                display: inline-block;
                padding: 0.75rem 1.5rem;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 500;
                transition: all 0.3s ease;
                margin-top: 1rem;
                border: none;
                cursor: pointer;
            }
            
            .btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 20px rgba(0, 168, 255, 0.3);
            }
            
            .secondary-btn {
                background: var(--bg-tertiary);
                border: 1px solid var(--border-color);
                margin-left: 1rem;
            }
            
            .cta {
                text-align: center;
                padding: 3rem;
                background-color: var(--bg-secondary);
                border-radius: 12px;
                margin-bottom: 4rem;
            }
            
            footer {
                text-align: center;
                padding: 2rem;
                border-top: 1px solid var(--border-color);
                color: var(--text-secondary);
            }
            
            .demo-img {
                width: 100%;
                height: auto;
                border-radius: 8px;
                margin-top: 1rem;
                border: 1px solid var(--border-color);
            }
            
            @media (max-width: 768px) {
                h1 {
                    font-size: 2.5rem;
                }
                
                .features {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1 class="gradient-text">pozt</h1>
                <h2>Pattern Optical Zone Technology - 視覚の魔法を体験しよう</h2>
            </header>
            
            <section class="hero">
                <div class="card">
                    <h3>モアレ効果で生まれる不思議な視覚体験</h3>
                    <p>poztは、独自の光学パターン技術を活用して、見る角度や表示環境によって変化する驚きの視覚アート作品を作成できる無料のウェブアプリケーションです。</p>
                    <p>特殊なモアレ効果を応用した技術により、通常時には見えない情報が特定の条件下で現れる驚きの体験を提供します。</p>
                    <div style="margin-top: 2rem;">
                        <a href="/api/docs" class="btn">API ドキュメントを見る</a>
                    </div>
                </div>
            </section>
            
            <section>
                <h3 style="text-align: center; margin-bottom: 2rem;">主な機能</h3>
                <div class="features">
                    <div class="feature-card">
                        <div class="feature-icon">🎯</div>
                        <h4>マルチステージ表示</h4>
                        <p>同じ画像が表示条件により異なる見え方をします - 通常表示、圧縮時、4K表示、拡大時で変化します。</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔄</div>
                        <h4>複数のパターン生成モード</h4>
                        <p>オーバーレイモード、高周波モード、適応型モード、色調保存モードなど、多彩な技術を駆使します。</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🖌️</div>
                        <h4>直感的なUI</h4>
                        <p>簡単な領域選択、リアルタイムプレビュー、多段階シミュレーション表示で簡単に作成できます。</p>
                    </div>
                </div>
            </section>
            
            <section class="cta">
                <h3>今すぐ体験しませんか？</h3>
                <p>APIドキュメントをチェックして、poztの機能を探索してみましょう。</p>
                <div style="margin-top: 1.5rem;">
                    <a href="/api/docs" class="btn">API ドキュメントを見る</a>
                </div>
            </section>
            
            <footer>
                <p>&copy; 2025 pozt - Pattern Optical Zone Technology</p>
            </footer>
        </div>
        
        <script>
            // 背景にアニメーション効果を追加（オプション）
            document.addEventListener('DOMContentLoaded', function() {
                const cards = document.querySelectorAll('.card');
                cards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transition = 'transform 0.3s ease, box-shadow 0.3s ease';
                        this.style.transform = 'translateY(-5px)';
                        this.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.2)';
                    });
                    
                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0)';
                        this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.15)';
                    });
                });
            });
        </script>
    </body>
    </html>
    """
    return html_content

# ファビコンのルート
@app.get("/favicon.ico")
async def serve_favicon():
    if os.path.exists("static/favicon.ico"):
        return FileResponse("static/favicon.ico")
    return Response(content=b"", media_type="image/x-icon")

# APIドキュメントへのリダイレクト
@app.get("/docs")
async def redirect_to_docs():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/docs")

# その他のパスに対するフォールバック
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # APIドキュメントへのリダイレクト
    if full_path == "docs":
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/api/docs")
    
    # 特定のファイルパスの処理
    if os.path.exists(f"static/{full_path}"):
        return FileResponse(f"static/{full_path}")
    
    # 他のパスはルートにリダイレクト
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/")
