import numpy as np
import cv2
from PIL import Image
import uuid
import os
import time
import gc  # ガベージコレクション追加
from config.app import get_settings
from core.image_utils import resize_to_fixed_size, calculate_resize_factors, add_black_border
from core.region_utils import extract_region_from_image
from patterns.moire import create_adaptive_moire_stripes, create_perfect_moire_pattern, create_high_frequency_moire_stripes
from patterns.overlay import create_overlay_moire_pattern
from patterns.color_modes import create_color_preserving_moire_stripes, create_hue_preserving_moire, create_blended_moire_stripes
from patterns.hybrid import create_combined_overlay_pattern, create_hybrid_moire_pattern

def clear_memory():
    """メモリを明示的に解放"""
    gc.collect()

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
    """高品質維持・プレビュー削減版：モアレ効果を利用した隠し画像を生成"""
    settings = get_settings()
    
    print(f"Processing with high quality mode: {settings.TARGET_WIDTH}x{settings.TARGET_HEIGHT}")
    print(f"Single preview mode: {getattr(settings, 'ENABLE_SINGLE_PREVIEW_MODE', True)}")
    
    try:
        # 画像の読み込み
        base_img = Image.open(base_img_path)
        base_img_array = np.array(base_img)
        
        # 領域情報の解析
        x, y, width, height = region
        
        # 選択領域を抽出（これが隠したい画像）
        hidden_img = extract_region_from_image(base_img_array, region)
        
        if hidden_img is None:
            raise ValueError("領域の抽出に失敗しました")
        
        # 固定サイズにリサイズ（元の高品質サイズを維持）
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
        
        # 中間データを削除してメモリ解放
        if base_pattern is not None:
            del base_pattern
        del overlay_effect, hidden_array
        clear_memory()
        
        # 結果画像（選択領域のみ変更）
        result_fixed = base_fixed_array.copy()
        result_fixed[y_fixed:y_fixed+height_fixed, x_fixed:x_fixed+width_fixed] = stripe_pattern
        
        # 黒い枠を追加
        if add_border:
            result_fixed = add_black_border(result_fixed, (x_fixed, y_fixed, width_fixed, height_fixed), border_width)
        
        region_fixed = (x_fixed, y_fixed, width_fixed, height_fixed)
        
        # 中間データを削除
        del stripe_pattern, base_fixed_array
        clear_memory()
        
        # **重要：プレビューは生成せず、メイン結果のみ保存**
        print("Generating main result only (single preview mode)")
        
        # 結果ファイルを保存
        timestamp = int(time.time())
        result_id = uuid.uuid4().hex[:8]
        
        # メイン結果のみ保存
        result_filename = f"result_{result_id}_{timestamp}.png"
        
        # 結果を保存
        os.makedirs("static", exist_ok=True)
        result_path = os.path.join("static", result_filename)
        
        # PNG保存（最高品質で保存）
        Image.fromarray(result_fixed.astype('uint8')).save(
            result_path, 
            format="PNG", 
            optimize=True, 
            compress_level=9  # 最高品質で保存
        )
        
        # メモリクリーンアップ
        del result_fixed
        clear_memory()
        
        print("High-quality processing completed successfully (single preview mode)")
        
        # 結果のファイルパスを返す（メイン結果のみ）
        result_paths = {
            "result": result_filename,
            # 他のプレビューは削除してメモリ節約
        }
        
        return result_paths
        
    except Exception as e:
        print(f"Processing error: {e}")
        # エラー時もメモリクリーンアップ
        clear_memory()
        raise e
