import numpy as np
import cv2
from PIL import Image
import uuid
import os
import time
from config.app import get_settings
from core.image_utils import resize_to_fixed_size, calculate_resize_factors, add_black_border
from core.region_utils import extract_region_from_image
from patterns.moire import create_adaptive_moire_stripes, create_perfect_moire_pattern, create_high_frequency_moire_stripes
from patterns.overlay import create_overlay_moire_pattern
from patterns.color_modes import create_color_preserving_moire_stripes, create_hue_preserving_moire, create_blended_moire_stripes
from patterns.hybrid import create_combined_overlay_pattern, create_hybrid_moire_pattern
from simulation.compression import simulate_x_post_compression
from simulation.display import simulate_4k_view, create_zoom_preview

def process_hidden_image(
    base_img_path: str, 
    region: tuple, 
    pattern_type: str, 
    stripe_method: str, 
    resize_method: str, 
    add_border: bool = True, 
    border_width: int = 3, 
    overlay_ratio: float = 0.4
):
    """モアレ効果を利用した隠し画像を生成"""
    settings = get_settings()
    
    # 画像の読み込み
    base_img = Image.open(base_img_path)
    base_img_array = np.array(base_img)
    
    # 領域情報の解析
    x, y, width, height = region
    
    # 選択領域を抽出（これが隠したい画像）
    hidden_img = extract_region_from_image(base_img_array, region)
    
    if hidden_img is None:
        raise ValueError("領域の抽出に失敗しました")
    
    # 固定サイズにリサイズ
    base_fixed = resize_to_fixed_size(base_img, method=resize_method)
    base_fixed_array = np.array(base_fixed)
    
    # リサイズの比率を計算
    scale_x, scale_y, scale, offset_x, offset_y = calculate_resize_factors(base_img, resize_method)
    
    # 領域を固定サイズ座標系に変換
    if resize_method != 'stretch':
        x_fixed = int(x * scale + offset_x)
        y_fixed = int(y * scale + offset_y)
        width_fixed = int(width * scale)
        height_fixed = int(height * scale)
    else:
        x_fixed = int(x * scale_x)
        y_fixed = int(y * scale_y)
        width_fixed = int(width * scale_x)
        height_fixed = int(height * scale_y)
    
    # 境界チェック
    TARGET_WIDTH = settings.TARGET_WIDTH
    TARGET_HEIGHT = settings.TARGET_HEIGHT
    
    x_fixed = max(0, min(x_fixed, TARGET_WIDTH - 1))
    y_fixed = max(0, min(y_fixed, TARGET_HEIGHT - 1))
    width_fixed = min(width_fixed, TARGET_WIDTH - x_fixed)
    height_fixed = min(height_fixed, TARGET_HEIGHT - y_fixed)
    
    # 隠し画像を領域サイズにリサイズ
    hidden_pil = Image.fromarray(hidden_img.astype('uint8')) if isinstance(hidden_img, np.ndarray) else hidden_img
    hidden_resized = hidden_pil.resize((width_fixed, height_fixed), Image.Resampling.LANCZOS)
    hidden_array = np.array(hidden_resized)
    
    # 常にオーバーレイと融合させる（stripe_methodに関わらず）
    base_pattern = None
    overlay_effect = create_overlay_moire_pattern(hidden_array, pattern_type, overlay_opacity=0.6)
    
    # 各モードに応じたベースパターンを生成
    if stripe_method == "overlay":
        # オーバーレイのみの場合はそのまま使用
        stripe_pattern = overlay_effect
    elif stripe_method == "high_frequency":
        # 高周波パターンをベースとして生成
        base_pattern = create_high_frequency_moire_stripes(hidden_array, pattern_type)
        # 高周波パターンとオーバーレイを融合
        stripe_pattern = cv2.addWeighted(base_pattern, 0.6, overlay_effect, 0.4, 0)
    elif stripe_method == "moire_pattern":
        base_pattern = create_perfect_moire_pattern(hidden_array, pattern_type)
        stripe_pattern = cv2.addWeighted(base_pattern, 0.6, overlay_effect, 0.4, 0)
    elif stripe_method == "color_preserving":
        base_pattern = create_color_preserving_moire_stripes(
            hidden_array, base_fixed_array, (x_fixed, y_fixed, width_fixed, height_fixed), pattern_type
        )
        stripe_pattern = cv2.addWeighted(base_pattern, 0.7, overlay_effect, 0.3, 0)
    elif stripe_method == "hue_preserving":
        base_pattern = create_hue_preserving_moire(
            hidden_array, base_fixed_array, (x_fixed, y_fixed, width_fixed, height_fixed), pattern_type
        )
        stripe_pattern = cv2.addWeighted(base_pattern, 0.7, overlay_effect, 0.3, 0)
    elif stripe_method == "blended":
        base_pattern = create_blended_moire_stripes(
            hidden_array, base_fixed_array, (x_fixed, y_fixed, width_fixed, height_fixed), pattern_type
        )
        stripe_pattern = cv2.addWeighted(base_pattern, 0.5, overlay_effect, 0.5, 0)
    elif stripe_method == "overlay_high_frequency":
        stripe_pattern = create_combined_overlay_pattern(hidden_array, pattern_type, "high_frequency")
    elif stripe_method == "overlay_moire_pattern":
        stripe_pattern = create_combined_overlay_pattern(hidden_array, pattern_type, "moire_pattern")
    elif stripe_method == "hybrid_overlay":
        stripe_pattern = create_hybrid_moire_pattern(
            hidden_array, pattern_type, "high_frequency", overlay_ratio
        )
    elif "adaptive" in stripe_method or any(method in stripe_method for method in ["perfect_subtle", "ultra_subtle", "near_perfect"]):
        base_pattern = create_adaptive_moire_stripes(hidden_array, pattern_type, stripe_method)
        stripe_pattern = cv2.addWeighted(base_pattern, 0.65, overlay_effect, 0.35, 0)
    else:
        # デフォルト
        base_pattern = create_adaptive_moire_stripes(hidden_array, pattern_type, "adaptive")
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
    
    # 結果ファイルを保存
    timestamp = int(time.time())
    result_id = uuid.uuid4().hex[:8]
    
    # ファイル名を生成
    result_filename = f"result_{result_id}_{timestamp}.png"
    x_post_filename = f"x_post_{result_id}_{timestamp}.png"
    view_4k_filename = f"view_4k_{result_id}_{timestamp}.png"
    zoom_filename = f"zoom_{result_id}_{timestamp}.png"
    
    # 結果を保存
    os.makedirs("static", exist_ok=True)
    result_path = os.path.join("static", result_filename)
    x_post_path = os.path.join("static", x_post_filename)
    view_4k_path = os.path.join("static", view_4k_filename)
    zoom_path = os.path.join("static", zoom_filename)
    
    Image.fromarray(result_fixed.astype('uint8')).save(result_path, format="PNG", optimize=True, compress_level=9)
    Image.fromarray(x_post_view.astype('uint8')).save(x_post_path, format="PNG")
    Image.fromarray(view_4k.astype('uint8')).save(view_4k_path, format="PNG")
    Image.fromarray(zoom_view.astype('uint8')).save(zoom_path, format="PNG")
    
    # 結果のファイルパスを返す
    result_paths = {
        "result": result_filename,
        "x_post": x_post_filename,
        "view_4k": view_4k_filename,
        "zoom": zoom_filename
    }
    
    return result_paths
