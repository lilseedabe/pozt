# backend/api/routes/reverse.py - 超軽量・512MB制限対応版
import os
import uuid
import gc
import sys
import psutil
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
    enhance_extracted_image_optimized
)

router = APIRouter()

# **512MB制限対応: メモリ監視設定**
MEMORY_WARNING_THRESHOLD = 350  # 350MB
MEMORY_CRITICAL_THRESHOLD = 450  # 450MB  
MAX_FILE_SIZE = 3 * 1024 * 1024  # 3MBに制限（従来の10MBから大幅削減）

def get_memory_usage():
    """現在のメモリ使用量を取得（MB単位）"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def check_memory_safety():
    """メモリ安全性をチェック"""
    current_memory = get_memory_usage()
    if current_memory > MEMORY_CRITICAL_THRESHOLD:
        raise HTTPException(
            status_code=507,
            detail=f"Insufficient memory available ({current_memory:.1f}MB used). Please try with a smaller image."
        )
    return current_memory

@router.post("/reverse")
async def reverse_moire_image_ultra_light(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    extraction_method: str = Form("pattern_subtraction"),  # デフォルトを最軽量に変更
    enhancement_level: float = Form(1.5),  # デフォルト値を軽減
    enhancement_method: str = Form("histogram_equalization"),
    apply_enhancement: str = Form("false"),  # デフォルトでOFF
    settings: Settings = Depends(get_api_settings)
):
    """
    モアレ効果画像から隠し画像を抽出（512MB制限対応・超軽量版）
    """
    initial_memory = get_memory_usage()
    print(f"🚀 Ultra-light reverse processing started (Initial memory: {initial_memory:.1f}MB)")
    print(f"  Method: {extraction_method}")
    print(f"  Enhancement: {enhancement_level}")
    print(f"  Apply enhancement: {apply_enhancement}")
    
    # **メモリ安全性チェック1: 処理開始前**
    check_memory_safety()
    
    try:
        # **メモリ対策1: ファイルサイズを厳しく制限**
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File size ({len(file_content)/1024/1024:.1f}MB) exceeds 3MB limit for memory efficiency"
            )
        
        print(f"  File size: {len(file_content)} bytes ({len(file_content)/1024/1024:.2f}MB)")
        
        # **メモリ対策2: 画像読み込みの最適化**
        try:
            image_bytes = io.BytesIO(file_content)
            
            with Image.open(image_bytes) as image:
                original_size = image.size
                
                # **メモリ対策3: 積極的なサイズ制限**
                max_dimension = 800  # さらに小さく制限
                if max(image.width, image.height) > max_dimension:
                    ratio = max_dimension / max(image.width, image.height)
                    new_size = (int(image.width * ratio), int(image.height * ratio))
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                    print(f"  Resized from {original_size} to {image.size} for memory safety")
                
                # **メモリ対策4: RGB統一（メモリ使用量予測可能）**
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # **メモリ対策5: 最小限の配列変換**
                image_array = np.array(image, dtype=np.uint8)
                
            # ファイル内容を即座に削除
            del file_content, image_bytes
            gc.collect()
            
            current_memory = get_memory_usage()
            print(f"  Memory after image load: {current_memory:.1f}MB")
            
        except Exception as e:
            gc.collect()
            raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
        
        # **メモリ安全性チェック2: 画像読み込み後**
        check_memory_safety()
        
        # **メモリ対策6: パラメータ検証の簡素化**
        valid_methods = ["pattern_subtraction", "frequency_filtering", "adaptive_detection", "fourier_analysis"]
        if extraction_method not in valid_methods:
            extraction_method = "pattern_subtraction"  # 最軽量をデフォルト
        
        # **メモリ対策: フーリエ解析を小画像のみに制限**
        if extraction_method == "fourier_analysis" and max(image_array.shape[:2]) > 512:
            print("  ⚠️ Fourier analysis switched to pattern_subtraction for large images")
            extraction_method = "pattern_subtraction"
        
        enhancement_level = max(0.5, min(3.0, enhancement_level))  # 範囲をより制限
        apply_enhancement_bool = apply_enhancement.lower() in ('true', '1', 'yes', 'on')
        
        print(f"✅ Starting ultra-light processing...")
        
        # **メモリ対策7: 処理実行前のメモリクリーンアップ**
        gc.collect()
        
        try:
            # **メモリ安全性チェック3: 処理直前**
            processing_memory = get_memory_usage()
            print(f"  Memory before processing: {processing_memory:.1f}MB")
            
            if processing_memory > MEMORY_WARNING_THRESHOLD:
                print(f"  ⚠️ Memory warning: {processing_memory:.1f}MB used")
                # 強制ガベージコレクション
                for _ in range(3):
                    gc.collect()
            
            # **超軽量処理実行**
            extracted_image = extract_hidden_image_from_moire(
                image_array, 
                method=extraction_method, 
                enhancement_level=enhancement_level
            )
            
            # 入力画像を即座に削除
            del image_array
            gc.collect()
            
            processing_complete_memory = get_memory_usage()
            print(f"✅ Extraction completed (Memory: {processing_complete_memory:.1f}MB)")
            
            # **メモリ対策8: 強調処理の条件分岐**
            if apply_enhancement_bool:
                # メモリ使用量をチェック
                current_mem = get_memory_usage()
                if current_mem > MEMORY_WARNING_THRESHOLD:
                    print("  ⚠️ Skipping enhancement due to memory constraints")
                    final_image = extracted_image
                else:
                    enhanced_image = enhance_extracted_image_optimized(
                        extracted_image, 
                        method=enhancement_method
                    )
                    del extracted_image  # 元画像を削除
                    final_image = enhanced_image
                    print(f"✅ Enhancement applied")
            else:
                final_image = extracted_image
                print(f"✅ No enhancement applied (memory efficient)")
                
        except Exception as processing_error:
            # 処理エラー時のメモリクリーンアップ
            if 'image_array' in locals():
                del image_array
            if 'extracted_image' in locals():
                del extracted_image
            gc.collect()
            
            print(f"❌ Processing error: {str(processing_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Ultra-light processing failed: {str(processing_error)}"
            )
        
        # **メモリ対策9: 結果保存の最適化**
        try:
            result_filename = f"reversed_{uuid.uuid4().hex[:8]}.png"  # ファイル名をさらに短縮
            result_path = get_file_path(result_filename)
            
            # PIL変換（メモリ効率重視）
            if len(final_image.shape) == 3:
                result_pil = Image.fromarray(final_image, 'RGB')
            else:
                result_pil = Image.fromarray(final_image, 'L')
            
            # 最終画像を削除
            del final_image
            gc.collect()
            
            # PNG保存（軽量設定）
            result_pil.save(
                result_path, 
                "PNG", 
                optimize=False,  # 高速化優先
                compress_level=1  # 最低圧縮（高速）
            )
            
            result_file_size = os.path.getsize(result_path)
            final_memory = get_memory_usage()
            
            print(f"✅ Result saved: {result_filename} ({result_file_size} bytes)")
            print(f"  Final memory usage: {final_memory:.1f}MB")
            
        except Exception as save_error:
            # 保存エラー時のクリーンアップ
            if 'final_image' in locals():
                del final_image
            if 'result_pil' in locals():
                del result_pil
            gc.collect()
            
            print(f"❌ Save error: {str(save_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save result: {str(save_error)}"
            )
        
        # **メモリ対策10: 最終クリーンアップ**
        if 'result_pil' in locals():
            del result_pil
        gc.collect()
        
        # バックグラウンドタスク
        background_tasks.add_task(delete_old_files, settings.TEMP_FILE_EXPIRY)
        background_tasks.add_task(gc.collect)
        
        # **メモリ効率的なレスポンス**
        memory_saved = initial_memory - final_memory if final_memory < initial_memory else 0
        response_data = {
            "success": True,
            "result_url": f"/uploads/{result_filename}",
            "message": "隠し画像の抽出が完了しました（超軽量処理）",
            "processing_info": {
                "filename": result_filename,
                "file_size": result_file_size,
                "extraction_method": extraction_method,
                "enhancement_level": enhancement_level,
                "enhancement_method": enhancement_method if apply_enhancement_bool else "none",
                "original_size": f"{original_size[0]}x{original_size[1]}" if 'original_size' in locals() else "unknown",
                "result_size": f"{result_pil.width}x{result_pil.height}" if 'result_pil' in locals() else "unknown",
                "memory_optimization": {
                    "initial_memory_mb": f"{initial_memory:.1f}",
                    "final_memory_mb": f"{final_memory:.1f}",
                    "memory_saved_mb": f"{memory_saved:.1f}",
                    "max_file_size_mb": MAX_FILE_SIZE / 1024 / 1024,
                    "ultra_lightweight": True,
                    "render_512mb_optimized": True
                }
            }
        }
        
        print(f"📤 Ultra-light processing response sent")
        return response_data
        
    except HTTPException:
        # HTTPExceptionはそのまま再発生
        raise
        
    except Exception as e:
        # 予期しないエラー時の完全クリーンアップ
        gc.collect()
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500, 
            detail=f"Ultra-light reverse processing failed: {str(e)}"
        )

@router.get("/reverse/methods")
async def get_reverse_methods_ultra_light():
    """利用可能なリバース処理方法を取得（512MB制限対応版）"""
    return {
        "extraction_methods": {
            "pattern_subtraction": {
                "name": "パターン減算（超軽量）",
                "description": "推定した縞パターンを元画像から減算（最小メモリ使用）",
                "best_for": "単純な縞パターン",
                "processing_time": "最高速",
                "memory_usage": "最小（推奨）",
                "render_512mb_safe": True
            },
            "frequency_filtering": {
                "name": "周波数フィルタリング（軽量）", 
                "description": "特定周波数帯域をフィルタリングして抽出（軽量版）",
                "best_for": "規則的な縞模様",
                "processing_time": "高速",
                "memory_usage": "少",
                "render_512mb_safe": True
            },
            "adaptive_detection": {
                "name": "適応的検出（軽量）",
                "description": "局所統計量を用いた適応的な検出（軽量版）",
                "best_for": "複雑なパターン",
                "processing_time": "中程度",
                "memory_usage": "中",
                "render_512mb_safe": True
            },
            "fourier_analysis": {
                "name": "フーリエ解析（小画像のみ）",
                "description": "周波数領域での解析（512px以下の画像のみ）",
                "best_for": "小さい高品質画像",
                "processing_time": "中程度",
                "memory_usage": "中〜大",
                "render_512mb_safe": "小画像のみ"
            }
        },
        "enhancement_methods": {
            "histogram_equalization": {
                "name": "ヒストグラム均等化（軽量）",
                "description": "コントラストを均等化して明瞭化（軽量版）",
                "memory_impact": "最小"
            },
            "clahe": {
                "name": "制限付き適応ヒストグラム均等化（軽量）",
                "description": "局所的なコントラスト強調（軽量設定）",
                "memory_impact": "小"
            },
            "gamma_correction": {
                "name": "ガンマ補正（軽量）",
                "description": "明度曲線を調整（軽量版）",
                "memory_impact": "最小"
            }
        },
        "render_optimization": {
            "max_file_size_mb": MAX_FILE_SIZE / 1024 / 1024,
            "max_image_dimension": 800,
            "memory_limit_mb": 512,
            "recommended_method": "pattern_subtraction",
            "enhancement_default": False,
            "ultra_lightweight_mode": True
        }
    }

@router.get("/reverse/performance")
async def get_performance_stats_ultra_light():
    """パフォーマンス統計を取得（512MB制限対応版）"""
    current_memory = get_memory_usage()
    
    return {
        "current_memory_usage": f"{current_memory:.1f} MB",
        "memory_limit": "512 MB (Render)",
        "memory_utilization": f"{(current_memory/512)*100:.1f}%",
        "memory_available": f"{512-current_memory:.1f} MB",
        "optimization_status": {
            "ultra_lightweight_mode": True,
            "render_512mb_optimized": True,
            "max_file_size_mb": MAX_FILE_SIZE / 1024 / 1024,
            "aggressive_garbage_collection": True,
            "memory_spike_prevention": True,
            "chunk_processing": True
        },
        "performance_limits": {
            "max_image_dimension": "800px",
            "max_file_size": "3MB", 
            "memory_warning_threshold": f"{MEMORY_WARNING_THRESHOLD}MB",
            "memory_critical_threshold": f"{MEMORY_CRITICAL_THRESHOLD}MB"
        },
        "recommendations": {
            "best_method": "pattern_subtraction",
            "enable_enhancement": False,
            "max_image_size": "800x600px for best performance"
        }
    }
