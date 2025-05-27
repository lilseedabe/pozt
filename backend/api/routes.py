from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import json
import numpy as np
import cv2
from PIL import Image
import io
import os
import uuid
from typing import Optional
import shutil

from core.region_utils import extract_region_from_image
from core.image_utils import resize_to_fixed_size, calculate_resize_factors, add_black_border
from patterns.moire import create_adaptive_moire_stripes, create_perfect_moire_pattern, create_high_frequency_moire_stripes
from patterns.overlay import create_overlay_moire_pattern
from patterns.color_modes import create_color_preserving_moire_stripes, create_hue_preserving_moire, create_blended_moire_stripes
from patterns.hybrid import create_hybrid_moire_pattern
from simulation.compression import simulate_x_post_compression
from simulation.display import simulate_4k_view, create_zoom_preview
from config.settings import TARGET_WIDTH, TARGET_HEIGHT, STRIPE_METHODS

router = APIRouter()

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """画像をアップロードしてファイルパスを返す"""
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = f"files/uploads/{filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 画像を読み込んで情報を取得
    img = Image.open(file_path)
    
    return {
        "filename": filename,
        "path": file_path,
        "width": img.width,
        "height": img.height
    }

@router.post("/process")
async def process_image(
    image_path: str = Form(...),
    region: str = Form(...),  # JSON文字列として受け取る
    pattern_type: str = Form(...),
    stripe_method: str = Form(...),
    resize_method: str = Form(...),
    add_border: bool = Form(True),
    border_width: int = Form(3),
    overlay_ratio: float = Form(0.4)
):
    """画像処理を行い結果を返す"""
    try:
        # 画像読み込み
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="画像ファイルが見つかりません")
        
        base_img = np.array(Image.open(image_path))
        region = json.loads(region)  # [x, y, width, height]の配列
        
        # 特殊処理
        result_img, x_post_view, view_4k, zoom_view, result_path, message = process_hidden_image(
            base_img, region, pattern_type, stripe_method, resize_method, add_border, border_width, overlay_ratio
        )
        
        if result_img is None:
            raise HTTPException(status_code=500, detail=message)
        
        # プレビュー画像を保存
        preview_paths = save_preview_images(x_post_view, view_4k, zoom_view)
        
        return {
            "result_path": result_path,
            "preview_paths": preview_paths,
            "message": message
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def save_preview_images(x_post_view, view_4k, zoom_view):
    """プレビュー画像を保存してパスを返す"""
    paths = {}
    
    for name, img in [("compression", x_post_view), ("display", view_4k), ("zoom", zoom_view)]:
        if img is not None:
            filename = f"{uuid.uuid4()}.png"
            filepath = f"files/previews/{filename}"
            Image.fromarray(img).save(filepath)
            paths[name] = filepath
    
    return paths

def process_hidden_image(base_img, region, pattern_type, stripe_method, resize_method, add_border=True, border_width=3, overlay_ratio=0.4):
    """特殊視覚効果を利用した隠し画像を生成"""
    if base_img is None:
        return None, None, None, None, None, "ベース画像をアップロードしてください"
    
    if region is None:
        return None, None, None, None, None, "隠したい領域を選択してください"
    
    try:
        # 選択領域を抽出
        hidden_img = extract_region_from_image(base_img, region)
        
        if hidden_img is None:
            return None, None, None, None, None, "領域の抽出に失敗しました"
        
        # 固定サイズにリサイズ
        base_fixed = resize_to_fixed_size(base_img, method=resize_method)
        base_fixed_array = base_fixed if isinstance(base_fixed, np.ndarray) else np.array(base_fixed)
        
        # リサイズの比率を計算
        scale_x, scale_y, scale, offset_x, offset_y = calculate_resize_factors(base_img, resize_method)
        
        # 領域を固定サイズ座標系に変換
        if resize_method != 'stretch':
            x_fixed = int(region[0] * scale + offset_x)
            y_fixed = int(region[1] * scale + offset_y)
            width_fixed = int(region[2] * scale)
            height_fixed = int(region[3] * scale)
        else:
            x_fixed = int(region[0] * scale_x)
            y_fixed = int(region[1] * scale_y)
            width_fixed = int(region[2] * scale_x)
            height_fixed = int(region[3] * scale_y)
        
        # 境界チェック
        x_fixed = max(0, min(x_fixed, TARGET_WIDTH - 1))
        y_fixed = max(0, min(y_fixed, TARGET_HEIGHT - 1))
        width_fixed = min(width_fixed, TARGET_WIDTH - x_fixed)
        height_fixed = min(height_fixed, TARGET_HEIGHT - y_fixed)
        
        # 隠し画像をリサイズ
        if isinstance(hidden_img, np.ndarray):
            from PIL import Image
            hidden_pil = Image.fromarray(hidden_img.astype('uint8'))
        else:
            hidden_pil = hidden_img
        
        hidden_resized = hidden_pil.resize((width_fixed, height_fixed), Image.Resampling.LANCZOS)
        hidden_array = np.array(hidden_resized)
        
        # オーバーレイエフェクトを生成
        overlay_effect = create_overlay_moire_pattern(hidden_array, pattern_type, overlay_opacity=0.6)
        
        # ハイブリッドモードの場合
        if stripe_method == "hybrid":
            stripe_pattern = create_hybrid_moire_pattern(
                hidden_array, pattern_type, "high_frequency", overlay_ratio
            )
        elif stripe_method == "overlay":
            stripe_pattern = overlay_effect
        else:
            # 各モードに応じたベースパターンを生成
            if stripe_method == "high_frequency":
                base_pattern = create_high_frequency_moire_stripes(hidden_array, pattern_type)
            elif stripe_method == "moire_pattern":
                base_pattern = create_perfect_moire_pattern(hidden_array, pattern_type)
            elif stripe_method == "color_preserving":
                base_pattern = create_color_preserving_moire_stripes(
                    hidden_array, base_fixed_array, (x_fixed, y_fixed, width_fixed, height_fixed), pattern_type
                )
            elif stripe_method == "hue_preserving":
                base_pattern = create_hue_preserving_moire(
                    hidden_array, base_fixed_array, (x_fixed, y_fixed, width_fixed, height_fixed), pattern_type
                )
            elif stripe_method == "blended":
                base_pattern = create_blended_moire_stripes(
                    hidden_array, base_fixed_array, (x_fixed, y_fixed, width_fixed, height_fixed), pattern_type
                )
            elif "adaptive" in stripe_method or any(method in stripe_method for method in ["perfect_subtle", "ultra_subtle", "near_perfect"]):
                base_pattern = create_adaptive_moire_stripes(hidden_array, pattern_type, stripe_method)
            else:
                # デフォルト
                base_pattern = create_adaptive_moire_stripes(hidden_array, pattern_type, "adaptive")
            
            # ベースパターンとオーバーレイを融合
            stripe_pattern = cv2.addWeighted(base_pattern, 0.65, overlay_effect, 0.35, 0)
        
        # 結果画像（選択領域のみ変更）
        result_fixed = base_fixed_array.copy()
        result_fixed[y_fixed:y_fixed+height_fixed, x_fixed:x_fixed+width_fixed] = stripe_pattern
        
        # 黒い枠を追加
        if add_border:
            result_fixed = add_black_border(result_fixed, (x_fixed, y_fixed, width_fixed, height_fixed), border_width)
        
        region_fixed = (x_fixed, y_fixed, width_fixed, height_fixed)
        
        # プレビュー生成
        x_post_view = simulate_x_post_compression(result_fixed, region_fixed)
        view_4k = simulate_4k_view(result_fixed, region_fixed)
        zoom_view = create_zoom_preview(result_fixed, region_fixed)
        
        # PNG形式で保存
        filename = f"hidden_image_{uuid.uuid4()}.png"
        output_path = f"files/results/{filename}"
        Image.fromarray(result_fixed).save(output_path)
        
        # 結果メッセージを生成
        stripe_description = STRIPE_METHODS.get(stripe_method, stripe_method)
        pattern_description = "横パターン（水平方向）" if pattern_type == "horizontal" else "縦パターン（垂直方向）"
        border_info = f"黒枠: {'あり（{border_width}px）' if add_border else 'なし'}"
        
        message = f"""
✅ 特殊視覚効果による隠し画像が完成しました！

📍 選択領域
   元画像位置: ({region[0]}, {region[1]}) サイズ: {region[2]}x{region[3]}
   固定サイズ画像位置: ({x_fixed}, {y_fixed}) サイズ: {width_fixed}x{height_fixed}

🎭 パターンタイプ: {stripe_description}
🎨 配置方向: {pattern_description}
📐 リサイズ方法: {resize_method}
🖼️ {border_info}

📄 出力形式: PNG（非圧縮・最高品質）
"""
        
        return result_fixed, x_post_view, view_4k, zoom_view, output_path, message
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return None, None, None, None, None, f"エラーが発生しました: {str(e)}"

@router.get("/download/{filename}")
async def download_file(filename: str):
    """生成された画像をダウンロード"""
    file_path = f"files/results/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="ファイルが見つかりません")
    
    return FileResponse(file_path, filename=filename)
