"""
アクセス制御ミドルウェア
pozt.iodo.co.jpからのアクセスのみを許可し、30分のセッション制限を実装
"""

import time
import hashlib
import json
from typing import Dict, Optional
from urllib.parse import urlparse
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class AccessControlMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, allowed_origin: str = "pozt.iodo.co.jp", session_timeout: int = 1800):
        super().__init__(app)
        self.allowed_origin = allowed_origin  # pozt.iodo.co.jp
        self.session_timeout = session_timeout  # 30分 = 1800秒
        self.sessions: Dict[str, Dict] = {}  # メモリ内セッション管理
        
    def _generate_session_id(self, request: Request) -> str:
        """クライアント情報からセッションIDを生成"""
        client_info = f"{request.client.host}_{request.headers.get('user-agent', '')}"
        return hashlib.sha256(client_info.encode()).hexdigest()
    
    def _is_valid_referrer(self, request: Request) -> bool:
        """Referrerが許可されたドメインからかチェック"""
        referrer = request.headers.get("referer", "")
        if not referrer:
            return False
        
        parsed_referrer = urlparse(referrer)
        return parsed_referrer.netloc == self.allowed_origin
    
    def _is_valid_origin(self, request: Request) -> bool:
        """Originが許可されたドメインからかチェック"""
        origin = request.headers.get("origin", "")
        if not origin:
            return False
        
        parsed_origin = urlparse(origin)
        return parsed_origin.netloc == self.allowed_origin
    
    def _create_session(self, session_id: str) -> Dict:
        """新しいセッションを作成"""
        session_data = {
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 1
        }
        self.sessions[session_id] = session_data
        return session_data
    
    def _update_session(self, session_id: str) -> Dict:
        """既存セッションを更新"""
        if session_id in self.sessions:
            self.sessions[session_id]["last_accessed"] = time.time()
            self.sessions[session_id]["access_count"] += 1
            return self.sessions[session_id]
        return None
    
    def _is_session_valid(self, session_id: str) -> bool:
        """セッションが有効かチェック"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        current_time = time.time()
        
        # 30分経過チェック
        if current_time - session["created_at"] > self.session_timeout:
            # セッション削除
            del self.sessions[session_id]
            return False
        
        return True
    
    def _cleanup_expired_sessions(self):
        """期限切れセッションをクリーンアップ"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            if current_time - session_data["created_at"] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def _is_api_endpoint(self, path: str) -> bool:
        """APIエンドポイントかどうかチェック"""
        api_paths = ["/api", "/health", "/docs", "/openapi.json"]
        return any(path.startswith(api_path) for api_path in api_paths)
    
    async def dispatch(self, request: Request, call_next):
        # 定期的にセッションクリーンアップ
        self._cleanup_expired_sessions()
        
        # 静的ファイルやアップロードファイルはスルー
        if request.url.path.startswith(("/static", "/uploads", "/favicon.ico")):
            return await call_next(request)
        
        # ヘルスチェックはスルー
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        session_id = self._generate_session_id(request)
        current_time = time.time()
        
        # セッション状態をチェック
        session_exists = self._is_session_valid(session_id)
        valid_referrer = self._is_valid_referrer(request)
        valid_origin = self._is_valid_origin(request)
        
        print(f"🔐 Access Control Check:")
        print(f"  Path: {request.url.path}")
        print(f"  Session ID: {session_id[:16]}...")
        print(f"  Session exists: {session_exists}")
        print(f"  Valid referrer: {valid_referrer}")
        print(f"  Valid origin: {valid_origin}")
        print(f"  Referrer: {request.headers.get('referer', 'None')}")
        print(f"  Origin: {request.headers.get('origin', 'None')}")
        
        # アクセス許可の判定
        access_granted = False
        
        if session_exists:
            # 既存の有効セッションがある場合
            self._update_session(session_id)
            access_granted = True
            print(f"  ✅ Access granted: Valid session")
        elif valid_referrer or valid_origin:
            # 正しいドメインからの新規アクセス
            self._create_session(session_id)
            access_granted = True
            print(f"  ✅ Access granted: Valid origin/referrer")
        else:
            # アクセス拒否
            access_granted = False
            print(f"  ❌ Access denied: Invalid origin/referrer and no valid session")
        
        if not access_granted:
            # アクセス拒否レスポンス
            error_response = {
                "error": "Access Denied",
                "message": f"このアプリには {self.allowed_origin} からのみアクセス可能です",
                "redirect_url": f"https://{self.allowed_origin}",
                "session_timeout": self.session_timeout,
                "current_time": current_time
            }
            
            # APIエンドポイントの場合はJSONレスポンス
            if self._is_api_endpoint(request.url.path):
                return JSONResponse(
                    status_code=403,
                    content=error_response
                )
            else:
                # フロントエンドの場合はHTMLレスポンス
                html_content = f"""
                <!DOCTYPE html>
                <html lang="ja">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>アクセス制限 - pozt</title>
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                            background: linear-gradient(135deg, #0a0f1a 0%, #1e2638 100%);
                            color: #ffffff;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            text-align: center;
                        }}
                        .container {{
                            max-width: 600px;
                            padding: 40px;
                            background: rgba(37, 45, 66, 0.8);
                            border-radius: 20px;
                            backdrop-filter: blur(20px);
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.35);
                        }}
                        h1 {{
                            background: linear-gradient(135deg, #00d4ff 0%, #6366f1 100%);
                            -webkit-background-clip: text;
                            -webkit-text-fill-color: transparent;
                            font-size: 2.5rem;
                            margin-bottom: 20px;
                        }}
                        .message {{
                            font-size: 1.2rem;
                            line-height: 1.6;
                            margin-bottom: 30px;
                            color: #94a3b8;
                        }}
                        .redirect-btn {{
                            display: inline-block;
                            padding: 15px 30px;
                            background: linear-gradient(135deg, #00d4ff 0%, #6366f1 100%);
                            color: white;
                            text-decoration: none;
                            border-radius: 12px;
                            font-weight: 600;
                            transition: all 0.3s ease;
                            font-size: 1.1rem;
                        }}
                        .redirect-btn:hover {{
                            transform: translateY(-3px);
                            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
                        }}
                        .info {{
                            margin-top: 30px;
                            padding: 20px;
                            background: rgba(0, 0, 0, 0.2);
                            border-radius: 12px;
                            font-size: 0.9rem;
                            color: #64748b;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🔒 アクセス制限</h1>
                        <div class="message">
                            <p>このアプリケーションは <strong>{self.allowed_origin}</strong> からのみアクセス可能です。</p>
                            <p>セッションの有効期限は30分間です。</p>
                        </div>
                        <a href="https://{self.allowed_origin}" class="redirect-btn">
                            正規サイトへ移動
                        </a>
                        <div class="info">
                            <p><strong>セッション情報:</strong></p>
                            <p>タイムアウト: {self.session_timeout // 60}分</p>
                            <p>アクセス時刻: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))}</p>
                        </div>
                    </div>
                    <script>
                        // 5秒後に自動リダイレクト
                        setTimeout(function() {{
                            window.location.href = 'https://{self.allowed_origin}';
                        }}, 5000);
                    </script>
                </body>
                </html>
                """
                return Response(content=html_content, media_type="text/html", status_code=403)
        
        # アクセス許可された場合、リクエストを処理
        response = await call_next(request)
        
        # セッション情報をヘッダーに追加（デバッグ用）
        if session_id in self.sessions:
            session_data = self.sessions[session_id]
            response.headers["X-Session-ID"] = session_id[:16]
            response.headers["X-Session-Remaining"] = str(
                int(self.session_timeout - (current_time - session_data["created_at"]))
            )
        
        return response
