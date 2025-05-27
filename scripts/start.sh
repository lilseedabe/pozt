#!/bin/bash
set -e

echo "Starting pozt application..."

# 環境変数の設定
export PORT=${PORT:-8000}

# バックエンドの起動
cd backend
uvicorn main:app --host 0.0.0.0 --port $PORT

echo "Server started on port $PORT"
