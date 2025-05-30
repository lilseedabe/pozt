# backend/api/routes/reverse.py - リバース機能のAPIエンドポイント
import os
import uuid
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends, status
from fastapi.responses import FileResponse
import numpy as np
from PIL import Image
import io
from api.dependencies import validate_file_size, get_api_settings
from config.app import Settings
from utils.file_handler import save_upload_file, get_file_path, delete_old_files
from patterns.reverse import (
    extract_hidden_image_from_moire, 
    enhance_extracted_image
)

router = APIRouter()

@router.post("/reverse")
async def reverse_moire_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    extraction_method: str = Form("fourier_analysis"),
    enhancement_level: float = Form(2.0),
    enhancement_method: str = Form("histogram_equalization"),
    apply_enhancement: str = Form("true"),
    settings: Settings = Depends(get_api_settings)
):
    """
    モアレ効果画像から隠し画像を抽出
    
    Args:
        file: モアレ効果画像ファイル
        extraction_method: 抽出方法 (fourier_analysis, frequency_filtering, pattern_subtraction, adaptive_detection)
        enhancement_level: 強調レベル (1.0-5.0)
        enhancement_method: 強調方法 (histogram_equalization, clahe, gamma_correction)
        apply_enhancement: 強調処理を適用するか (true/false)
    """
    try:
        print(f"🔄 Reverse processing request received:")
        print(f"  extraction_method: {extraction_method}")
        print(f"  enhancement_level: {enhancement_level}")
        print(f"  enhancement_method: {enhancement_method}")
        print(f"  apply_enhancement: {apply_enhancement}")
        
        # ファイルサイズの検証
        file_content = await file.read()
        await validate_file_size(len(file_content), settings)
        
        # 画像を読み込み
        try:
            image = Image.open(io.BytesIO(file_content))
            image_array = np.array(image)
            print(f"  Input image size: {image.width}x{image.height}")
            print(f"  Input image channels: {len(image_array.shape)}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
        # パラメータ検証
        valid_extraction_methods = [
            "fourier_analysis", 
            "frequency_filtering", 
            "pattern_subtraction", 
            "adaptive_detection"
        ]
        if extraction_method not in valid_extraction_methods:
            extraction_method = "fourier_analysis"
            print(f"  Invalid extraction_method, using default: {extraction_method}")
        
        valid_enhancement_methods = [
            "histogram_equalization", 
            "clahe", 
            "gamma_correction"
        ]
        if enhancement_method not in valid_enhancement_methods:
            enhancement_method = "histogram_equalization"
            print(f"  Invalid enhancement_method, using default: {enhancement_method}")
        
        # 強調レベルの範囲チェック
        if enhancement_level < 0.5 or enhancement_level > 5.0:
            enhancement_level = max(0.5, min(5.0, enhancement_level))
            print(f"  Enhancement level adjusted to valid range: {enhancement_level}")
        
        # 強調処理適用フラグ
        apply_enhancement_bool = apply_enhancement.lower() in ('true', '1', 'yes', 'on')
        print(f"  apply_enhancement_bool: {apply_enhancement_bool}")
        
        print(f"✅ Starting reverse processing...")
        
        # 隠し画像を抽出
        extracted_image = extract_hidden_image_from_moire(
            image_array, 
            method=extraction_method, 
            enhancement_level=enhancement_level
        )
        
        print(f"✅ Hidden image extracted using {extraction_method}")
        
        # 強調処理を適用
        if apply_enhancement_bool:
            enhanced_image = enhance_extracted_image(
                extracted_image, 
                method=enhancement_method
            )
            final_image = enhanced_image
            print(f"✅ Image enhanced using {enhancement_method}")
        else:
            final_image = extracted_image
            print(f"✅ No enhancement applied")
        
        # 結果画像を保存
        result_filename = f"reversed_{uuid.uuid4()}.png"
        result_path = get_file_path(result_filename)
        
        # PIL Imageに変換して保存
        if len(final_image.shape) == 3:
            result_pil = Image.fromarray(final_image.astype('uint8'), 'RGB')
        else:
            result_pil = Image.fromarray(final_image.astype('uint8'), 'L')
        
        result_pil.save(result_path, "PNG", optimize=True, compress_level=9)
        
        result_file_size = os.path.getsize(result_path)
        print(f"✅ Result saved: {result_filename} ({result_file_size} bytes)")
        
        # 古いファイルのクリーンアップをバックグラウンドで実行
        background_tasks.add_task(delete_old_files, settings.TEMP_FILE_EXPIRY)
        
        # レスポンスを構築
        response_data = {
            "success": True,
            "result_url": f"/uploads/{result_filename}",
            "message": "隠し画像の抽出が完了しました",
            "processing_info": {
                "filename": result_filename,
                "file_size": result_file_size,
                "extraction_method": extraction_method,
                "enhancement_level": enhancement_level,
                "enhancement_method": enhancement_method if apply_enhancement_bool else "none",
                "original_size": f"{image.width}x{image.height}",
                "result_size": f"{result_pil.width}x{result_pil.height}"
            }
        }
        
        print(f"📤 Sending reverse processing response: {response_data}")
        
        return response_data
        
    except HTTPException:
        # HTTPExceptionはそのまま再発生
        raise
        
    except Exception as e:
        print(f"❌ Reverse processing error: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        
        # 詳細なエラー情報を含むレスポンス
        error_detail = {
            "error": str(e),
            "error_type": type(e).__name__,
            "processing_stage": "reverse_processing"
        }
        
        raise HTTPException(
            status_code=500, 
            detail=f"Reverse processing failed: {str(e)}"
        )

@router.get("/reverse/methods")
async def get_reverse_methods():
    """利用可能なリバース処理方法を取得"""
    return {
        "extraction_methods": {
            "fourier_analysis": {
                "name": "フーリエ解析",
                "description": "周波数領域での解析により隠し画像を抽出",
                "best_for": "高品質なモアレ画像",
                "processing_time": "中程度"
            },
            "frequency_filtering": {
                "name": "周波数フィルタリング", 
                "description": "特定周波数帯域をフィルタリングして抽出",
                "best_for": "規則的な縞模様",
                "processing_time": "高速"
            },
            "pattern_subtraction": {
                "name": "パターン減算",
                "description": "推定した縞パターンを元画像から減算",
                "best_for": "単純な縞パターン",
                "processing_time": "高速"
            },
            "adaptive_detection": {
                "name": "適応的検出",
                "description": "局所統計量を用いた適応的な検出",
                "best_for": "複雑なパターン",
                "processing_time": "中程度"
            }
        },
        "enhancement_methods": {
            "histogram_equalization": {
                "name": "ヒストグラム均等化",
                "description": "コントラストを均等化して明瞭化"
            },
            "clahe": {
                "name": "制限付き適応ヒストグラム均等化",
                "description": "局所的なコントラスト強調"
            },
            "gamma_correction": {
                "name": "ガンマ補正",
                "description": "明度曲線を調整"
            }
        }
    }

# main.pyに追加するルート登録
# app.include_router(reverse.router, prefix="/api", tags=["Reverse"])
