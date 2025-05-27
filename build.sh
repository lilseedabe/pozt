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

# ディレクトリ構造を確認（デバッグ用）
echo "Checking build directory structure..."
find build -type f | sort

# 静的ファイルの準備
echo "Preparing static directory..."
mkdir -p ../backend/static
cp -R build/* ../backend/static/

# インデックスファイルの内容を確認（デバッグ用）
echo "Checking index.html content..."
grep -E 'src="|href="' ../backend/static/index.html

# バックエンド静的ディレクトリを確認
echo "Checking backend static directory..."
find ../backend/static -type f | sort

cd ..
echo "Build completed successfully!"
