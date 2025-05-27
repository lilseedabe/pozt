#!/bin/bash
set -e

echo "Building pozt application..."

# バックエンド依存関係のインストール
echo "Installing backend dependencies..."
pip install -r requirements.txt

# フロントエンド依存関係のインストール
echo "Installing frontend dependencies..."
cd frontend && npm install

# フロントエンドのビルド
echo "Building frontend..."
npm run build

# 静的ファイルの準備
echo "Preparing static directory..."
mkdir -p ../backend/static
cp -R build/* ../backend/static/
ls -la ../backend/static/

cd ..
echo "Build completed successfully!"
