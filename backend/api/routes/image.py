import os
import uuid
import shutil
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends, status
from fastapi.responses import FileResponse
import numpy as np
from PIL import Image
import io
from api.dependencies import validate_file_size, get_api_settings
from config.app import Settings
from utils.file_handler import save_upload_file, get_file_path, delete_old_files
from utils.image_processor import process_hidden_image

router = APIRouter()

@router.post("/upload")
async def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    settings: Settings = Depends(get_api_settings)
):
    """画像をアップロードして処理用に保存"""
    try:
        # ファイルサイズの検証
        file_content = await file.read()
        await validate_file_size(len(file_content), settings)
        
        # ファイルを一時保存
        image = Image.open(io.BytesIO(file_content))
        filename = f"{uuid.uuid4()}.png"
        file_path = await save_upload_file(io.BytesIO(file_content), filename)
        
        # 古いファイルのクリーンアップをバックグラウンドで実行
        background_tasks.add_task(delete_old_files, settings.TEMP_FILE_EXPIRY)
        
        return {
            "success": True,
            "filename": filename,
            "width": image.width,
            "height": image.height,
            "url": f"/static/{filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/process")
async def process_image(
    background_tasks: BackgroundTasks,
    filename: str = Form(...),
    region_x: int = Form(...),
    region_y: int = Form(...),
    region_width: int = Form(...),
    region_height: int = Form(...),
    pattern_type: str = Form("horizontal"),
    stripe_method: str = Form("overlay"),
    resize_method: str = Form("contain"),
    add_border: bool = Form(True),
    border_width: int = Form(3),
    overlay_ratio: float = Form(0.4),
    settings: Settings = Depends(get_api_settings)
):
    """画像を処理してモアレ効果を適用"""
    try:
        # ファイルパスの取得
        file_path = get_file_path(filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # 領域情報の構築
        region = (region_x, region_y, region_width, region_height)
        
        # 画像処理の実行
        result_files = process_hidden_image(
            file_path,
            region,
            pattern_type,
            stripe_method,
            resize_method,
            add_border,
            border_width,
            overlay_ratio
        )
        
        # 古いファイルのクリーンアップをバックグラウンドで実行
        background_tasks.add_task(delete_old_files, settings.TEMP_FILE_EXPIRY)
        
        # 結果のURLを構築
        result_urls = {
            key: f"/static/{os.path.basename(path)}" 
            for key, path in result_files.items()
        }
        
        return {
            "success": True,
            "urls": result_urls,
            "message": "処理が完了しました"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_image(filename: str):
    """生成された画像をダウンロード"""
    file_path = get_file_path(filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path, 
        media_type="image/png",
        filename=f"pozt_{filename}"
    )
