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
            "url": f"/uploads/{filename}"
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
    add_border: str = Form("true"),
    border_width: int = Form(3),
    overlay_ratio: float = Form(0.4),
    # 新しいパラメータを追加
    strength: float = Form(0.02),
    opacity: float = Form(0.6),
    enhancement_factor: float = Form(1.2),
    frequency: int = Form(1),
    blur_radius: int = Form(5),
    contrast_boost: float = Form(1.0),
    color_shift: float = Form(0.0),
    settings: Settings = Depends(get_api_settings)
):
    """画像を処理してモアレ効果を適用（パラメータ拡張版）"""
    try:
        # デバッグ用ログ
        print(f"🚀 Enhanced process request received:")
        print(f"  filename: {filename}")
        print(f"  region: ({region_x}, {region_y}, {region_width}, {region_height})")
        print(f"  pattern_type: {pattern_type}")
        print(f"  stripe_method: {stripe_method}")
        print(f"  resize_method: {resize_method}")
        print(f"  add_border: {add_border}")
        print(f"  border_width: {border_width}")
        print(f"  overlay_ratio: {overlay_ratio}")
        print(f"  strength: {strength}")
        print(f"  opacity: {opacity}")
        print(f"  enhancement_factor: {enhancement_factor}")
        print(f"  frequency: {frequency}")
        print(f"  blur_radius: {blur_radius}")
        print(f"  contrast_boost: {contrast_boost}")
        print(f"  color_shift: {color_shift}")
        
        # ファイルパスの取得と確認
        file_path = get_file_path(filename)
        print(f"  file_path: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            raise HTTPException(status_code=404, detail=f"File not found: {filename}")
        
        # ファイルサイズとアクセス権確認
        file_size = os.path.getsize(file_path)
        print(f"  file_size: {file_size} bytes")
        
        # 領域情報の構築と検証
        region = (region_x, region_y, region_width, region_height)
        
        # 領域の妥当性チェック
        if region_width <= 0 or region_height <= 0:
            raise HTTPException(status_code=400, detail="Invalid region dimensions")
        
        if region_x < 0 or region_y < 0:
            raise HTTPException(status_code=400, detail="Invalid region position")
        
        # boolean値の変換（文字列から真偽値へ）
        add_border_bool = add_border.lower() in ('true', '1', 'yes', 'on')
        print(f"  add_border_bool: {add_border_bool}")
        
        # 処理パラメータの検証
        valid_pattern_types = ["horizontal", "vertical"]
        if pattern_type not in valid_pattern_types:
            pattern_type = "horizontal"
            print(f"  Invalid pattern_type, using default: {pattern_type}")
        
        valid_stripe_methods = [
            "overlay", "high_frequency", "moire_pattern", "adaptive", 
            "adaptive_subtle", "adaptive_strong", "adaptive_minimal",
            "perfect_subtle", "ultra_subtle", "near_perfect",
            "color_preserving", "hue_preserving", "blended", "hybrid_overlay"
        ]
        if stripe_method not in valid_stripe_methods:
            stripe_method = "overlay"
            print(f"  Invalid stripe_method, using default: {stripe_method}")
        
        valid_resize_methods = ["contain", "cover", "stretch"]
        if resize_method not in valid_resize_methods:
            resize_method = "contain"
            print(f"  Invalid resize_method, using default: {resize_method}")
        
        print(f"✅ Starting enhanced image processing...")
        
        # パラメータ辞書を作成
        processing_params = {
            'strength': strength,
            'opacity': opacity,
            'enhancement_factor': enhancement_factor,
            'frequency': frequency,
            'blur_radius': blur_radius,
            'contrast_boost': contrast_boost,
            'color_shift': color_shift,
            'overlay_ratio': overlay_ratio
        }
        
        # 画像処理の実行
        result_files = process_hidden_image(
            file_path,
            region,
            pattern_type,
            stripe_method,
            resize_method,
            add_border_bool,
            border_width,
            overlay_ratio,
            processing_params  # 新しいパラメータを渡す
        )
        
        print(f"✅ Enhanced processing completed. Result: {result_files}")
        
        # 結果ファイルの存在確認
        if not result_files or "result" not in result_files:
            raise HTTPException(status_code=500, detail="Processing failed: No result generated")
        
        result_filename = result_files["result"]
        result_file_path = get_file_path(result_filename)
        
        if not os.path.exists(result_file_path):
            print(f"❌ Result file not found: {result_file_path}")
            raise HTTPException(status_code=500, detail="Processing failed: Result file not created")
        
        result_file_size = os.path.getsize(result_file_path)
        print(f"✅ Result file created: {result_filename} ({result_file_size} bytes)")
        
        # 古いファイルのクリーンアップをバックグラウンドで実行
        background_tasks.add_task(delete_old_files, settings.TEMP_FILE_EXPIRY)
        
        # 結果のURLを構築
        result_urls = {
            "result": f"/uploads/{result_filename}"
        }
        
        print(f"✅ Enhanced processing completed successfully. URLs: {result_urls}")
        
        # レスポンスを構築
        response_data = {
            "success": True,
            "urls": result_urls,
            "message": "拡張パラメータによる処理が完了しました",
            "processing_info": {
                "filename": result_filename,
                "file_size": result_file_size,
                "pattern_type": pattern_type,
                "stripe_method": stripe_method,
                "parameters_used": processing_params
            }
        }
        
        print(f"📤 Sending enhanced response: {response_data}")
        
        return response_data
        
    except HTTPException:
        # HTTPExceptionはそのまま再発生
        raise
        
    except Exception as e:
        print(f"❌ Unexpected enhanced processing error: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        
        # 詳細なエラー情報を含むレスポンス
        error_detail = {
            "error": str(e),
            "error_type": type(e).__name__,
            "processing_stage": "enhanced_processing"
        }
        
        raise HTTPException(
            status_code=500, 
            detail=f"Enhanced processing failed: {str(e)}"
        )

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
