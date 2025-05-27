import os
import time
import aiofiles
import uuid
from typing import BinaryIO
from fastapi import UploadFile

async def save_upload_file(file_content: BinaryIO, filename: str) -> str:
    """アップロードされたファイルを保存"""
    # 静的ディレクトリが存在することを確認
    os.makedirs("static", exist_ok=True)
    file_path = os.path.join("static", filename)
    
    # ファイルを保存
    async with aiofiles.open(file_path, 'wb') as out_file:
        # ファイルポインタを先頭に戻す
        file_content.seek(0)
        # 内容を書き込む
        await out_file.write(file_content.read())
    
    return file_path

def get_file_path(filename: str) -> str:
    """ファイル名からパスを取得"""
    return os.path.join("static", filename)

async def delete_old_files(expiry_seconds: int = 3600):
    """指定された期間よりも古いファイルを削除"""
    now = time.time()
    directory = "static"
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # ファイルの最終更新時間を取得
        file_mod_time = os.path.getmtime(file_path)
        # 現在時刻との差を計算
        if now - file_mod_time > expiry_seconds:
            try:
                os.remove(file_path)
                print(f"Deleted old file: {filename}")
            except Exception as e:
                print(f"Error deleting file {filename}: {e}")
