#!/bin/bash
set -e

echo "Building pozt application..."

# バックエンド依存のインストール
pip install -r requirements.txt

# フロントエンド依存＆ビルド
cd frontend
npm install
npm run build
cd ..

echo "Build completed!"
