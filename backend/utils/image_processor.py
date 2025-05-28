import numpy as np
import cv2
from PIL import Image
import uuid
import os
import time
import gc
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from config.app import get_settings
from core.image_utils import resize_to_fixed_size, calculate_resize_factors, add_black_border
from core.region_utils import extract_region_from_image
from patterns.moire import create_adaptive_moire_stripes, create_high_frequency_moire_stripes
from patterns.overlay import create_overlay_moire_pattern

def clear_memory():
    """メモリを明示的に解放"""
    gc.collect()

@lru_cache(maxsize=32)
def get_cached_pattern_config(stripe_method: str):
    """パターン設定をキャッシュして高速化"""
    configs = {
        "overlay": {"base_method": None, "overlay_weight": 1.0, "base_weight": 0.0},
        "high_frequency": {"base_method": "high_frequency", "overlay_weight": 0.4, "base_weight": 0.6},
        "adaptive": {"base_method": "adaptive", "overlay_weight": 0.35, "base_weight": 0.65},
        "adaptive_subtle": {"base_method": "adaptive_subtle", "overlay_weight": 0.35, "base_weight": 0.65},
        "adaptive_strong": {"base_method": "adaptive_strong", "overlay_weight": 0.35, "base_weight": 0.65},
        "moire_pattern": {"base_method": "moire_pattern", "overlay_weight": 0.4, "base_weight": 0.6},
        "color_preserving": {"base_method": "color_preserving", "overlay_weight": 0.3, "base_weight": 0.7},
        "hue_preserving": {"base_method": "hue_preserving", "overlay_weight": 0.3, "base_weight": 0.7},
        "blended": {"base_method": "blended", "overlay_weight": 0.5, "base_weight": 0.5},
        "hybrid_overlay": {"base_method": "adaptive", "overlay_weight": 0.4, "base_weight": 0.6},
    }
    return configs.get(stripe_method, configs["adaptive"])

def optimize_image_for_processing(img_array):
    """画像データの型と形状を最適化"""
    # uint8に統一（メモリ効率とCV2互換性）
    if img_array.dtype != np.uint8:
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
    
    # 連続配列に変換（処理速度向上）
    if not img_array.flags['C_CONTIGUOUS']:
        img_array = np.ascontiguousarray(img_array)
    
    return img_array

def safe_pattern_generation(hidden_array, pattern_type, stripe_method, overlay_ratio=0.4):
    """安全なパターン生成（隠蔽効果を強化）"""
    try:
        config = get_cached_pattern_config(stripe_method)
        
        print(f"Using pattern config: {config}")
        
        # より隠蔽効果の高い設定に調整
        if stripe_method == "overlay":
            # オーバーレイモードで隠蔽効果を強化
            overlay_pattern = create_overlay_moire_pattern(hidden_array, pattern_type, overlay_opacity=0.3)  # 0.6→0.3に削減
            return overlay_pattern
        
        # オーバーレイパターンは常に生成（隠蔽効果強化）
        overlay_pattern = create_overlay_moire_pattern(hidden_array, pattern_type, overlay_opacity=0.25)  # さらに削減
        
        # ベースパターンが不要な場合はオーバーレイのみ返却
        if config["base_method"] is None:
            print("Using overlay-only pattern")
            return overlay_pattern
        
        # ベースパターンを生成（強度削減で隠蔽効果強化）
        base_pattern = None
        if config["base_method"] == "high_frequency":
            print("Generating high frequency pattern")
            base_pattern = create_high_frequency_moire_stripes(hidden_array, pattern_type, strength=0.08)  # 0.25→0.08に削減
        elif config["base_method"] and "adaptive" in config["base_method"]:
            print(f"Generating adaptive pattern: {config['base_method']}")
            base_pattern = create_adaptive_moire_stripes(hidden_array, pattern_type, config["base_method"])
        else:
            print("Using default adaptive pattern")
            base_pattern = create_adaptive_moire_stripes(hidden_array, pattern_type, "adaptive")
        
        if base_pattern is None:
            print("Base pattern is None, using overlay only")
            return overlay_pattern
        
        # パターンの形状確認
        print(f"Base pattern shape: {base_pattern.shape}")
        print(f"Overlay pattern shape: {overlay_pattern.shape}")
        
        # 形状が一致することを確認
        if base_pattern.shape != overlay_pattern.shape:
            print("Shape mismatch detected, using overlay only")
            del base_pattern
            return overlay_pattern
        
        # 加重合成（オーバーレイ比率を下げて隠蔽効果強化）
        result = cv2.addWeighted(
            optimize_image_for_processing(base_pattern), config["base_weight"] * 0.6,  # ベース比率削減
            optimize_image_for_processing(overlay_pattern), config["overlay_weight"] * 0.4,  # オーバーレイ比率削減
            0
        )
        
        # 中間データを即座に削除
        del base_pattern, overlay_pattern
        clear_memory()
        
        return result
        
    except Exception as e:
        print(f"Pattern generation error: {e}")
        # エラー時はシンプルなオーバーレイパターンを返却（隠蔽効果重視）
        try:
            overlay_pattern = create_overlay_moire_pattern(hidden_array, pattern_type, overlay_opacity=0.2)
            return overlay_pattern
        except Exception as fallback_error:
            print(f"Fallback pattern generation error: {fallback_error}")
            # 最終的なフォールバック：単純な縞模様（隠蔽効果重視）
            height, width = hidden_array.shape[:2]
            fallback_result = np.zeros((height, width, 3), dtype=np.uint8)
            base_gray = 128  # 中間グレー
            stripe_amplitude = 30  # 弱い縞模様
            
            if pattern_type == "horizontal":
                for y in range(height):
                    stripe_value = base_gray + (stripe_amplitude if y % 2 == 0 else -stripe_amplitude)
                    fallback_result[y, :] = [stripe_value, stripe_value, stripe_value]
            else:
                for x in range(width):
                    stripe_value = base_gray + (stripe_amplitude if x % 2 == 0 else -stripe_amplitude)
                    fallback_result[:, x] = [stripe_value, stripe_value, stripe_value]
            return fallback_result

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
    """修正版：座標計算とモアレ効果を正確に処理"""
    start_time = time.time()
    settings = get_settings()
    
    print(f"🚀 Starting processing with corrected coordinates...")
    print(f"Parameters: {pattern_type}, {stripe_method}, {resize_method}")
    print(f"Original region: {region}")
    
    try:
        # === フェーズ1: 画像読み込み（最適化） ===
        phase_start = time.time()
        
        if not os.path.exists(base_img_path):
            raise FileNotFoundError(f"Base image not found: {base_img_path}")
        
        with Image.open(base_img_path) as base_img:
            # 巨大な画像は事前に軽くリサイズ（処理速度向上）
            original_size = (base_img.width, base_img.height)
            print(f"Original image size: {original_size}")
            
            if base_img.width * base_img.height > 8000000:  # 8MP以上
                print("⚡ Large image detected, applying fast pre-resize...")
                base_img.thumbnail((3000, 3000), Image.Resampling.BILINEAR)
            
            base_img_array = optimize_image_for_processing(np.array(base_img))
        
        print(f"📁 Image loading: {time.time() - phase_start:.2f}s")
        
        # === フェーズ2: 領域抽出と前処理（座標修正） ===
        phase_start = time.time()
        
        x, y, width, height = region
        print(f"Region before extraction: x={x}, y={y}, w={width}, h={height}")
        
        # 境界チェック（元画像サイズに対して）
        img_height, img_width = base_img_array.shape[:2]
        x = max(0, min(x, img_width - 1))
        y = max(0, min(y, img_height - 1))
        width = min(width, img_width - x)
        height = min(height, img_height - y)
        
        print(f"Region after boundary check: x={x}, y={y}, w={width}, h={height}")
        
        hidden_img = extract_region_from_image(base_img_array, (x, y, width, height))
        
        if hidden_img is None:
            raise ValueError("領域の抽出に失敗しました")
        
        print(f"Hidden image shape: {hidden_img.shape}")
        
        # 固定サイズにリサイズ
        base_fixed = resize_to_fixed_size(base_img_array, method=resize_method)
        base_fixed_array = optimize_image_for_processing(np.array(base_fixed))
        
        # 元のデータを即座に削除
        del base_img_array
        clear_memory()
        
        print(f"🔄 Preprocessing: {time.time() - phase_start:.2f}s")
        
        # === フェーズ3: 座標変換（修正版） ===
        phase_start = time.time()
        
        # リサイズの比率を正確に計算
        scale_x = settings.TARGET_WIDTH / img_width
        scale_y = settings.TARGET_HEIGHT / img_height
        
        print(f"Scale factors: scale_x={scale_x:.4f}, scale_y={scale_y:.4f}")
        
        if resize_method == 'contain':
            # アスペクト比保持の場合
            scale = min(scale_x, scale_y)
            # リサイズ後の実際のサイズ
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            # 中央配置のオフセット
            offset_x = (settings.TARGET_WIDTH - new_width) // 2
            offset_y = (settings.TARGET_HEIGHT - new_height) // 2
            
            # 領域の座標を変換
            x_fixed = int(x * scale) + offset_x
            y_fixed = int(y * scale) + offset_y
            width_fixed = int(width * scale)
            height_fixed = int(height * scale)
            
        elif resize_method == 'cover':
            # 画面を埋める場合
            scale = max(scale_x, scale_y)
            # クロップオフセット
            crop_offset_x = int((img_width * scale - settings.TARGET_WIDTH) / 2)
            crop_offset_y = int((img_height * scale - settings.TARGET_HEIGHT) / 2)
            
            x_fixed = int(x * scale) - crop_offset_x
            y_fixed = int(y * scale) - crop_offset_y
            width_fixed = int(width * scale)
            height_fixed = int(height * scale)
            
        else:  # stretch
            # 引き伸ばしの場合
            x_fixed = int(x * scale_x)
            y_fixed = int(y * scale_y)
            width_fixed = int(width * scale_x)
            height_fixed = int(height * scale_y)
        
        # 境界チェック（固定サイズに対して）
        x_fixed = max(0, min(x_fixed, settings.TARGET_WIDTH - 1))
        y_fixed = max(0, min(y_fixed, settings.TARGET_HEIGHT - 1))
        width_fixed = min(width_fixed, settings.TARGET_WIDTH - x_fixed)
        height_fixed = min(height_fixed, settings.TARGET_HEIGHT - y_fixed)
        
        print(f"Fixed region (corrected): x={x_fixed}, y={y_fixed}, w={width_fixed}, h={height_fixed}")
        print(f"📐 Coordinate mapping: {time.time() - phase_start:.2f}s")
        
        # === フェーズ4: 隠し画像準備（高速化） ===
        phase_start = time.time()
        
        hidden_pil = Image.fromarray(hidden_img.astype('uint8'))
        hidden_resized = hidden_pil.resize((width_fixed, height_fixed), Image.Resampling.BILINEAR)
        hidden_array = optimize_image_for_processing(np.array(hidden_resized))
        
        print(f"Hidden array final shape: {hidden_array.shape}")
        
        del hidden_img, hidden_pil, hidden_resized
        clear_memory()
        
        print(f"🖼️ Hidden image prep: {time.time() - phase_start:.2f}s")
        
        # === フェーズ5: パターン生成（隠蔽効果強化） ===
        phase_start = time.time()
        
        stripe_pattern = safe_pattern_generation(hidden_array, pattern_type, stripe_method, overlay_ratio)
        stripe_pattern = optimize_image_for_processing(stripe_pattern)
        
        print(f"Final stripe pattern shape: {stripe_pattern.shape}")
        
        del hidden_array
        clear_memory()
        
        print(f"🎨 Pattern generation: {time.time() - phase_start:.2f}s")
        
        # === フェーズ6: 最終合成（高速化） ===
        phase_start = time.time()
        
        # NumPy直接操作で高速合成
        result_fixed = base_fixed_array.copy()
        result_fixed[y_fixed:y_fixed+height_fixed, x_fixed:x_fixed+width_fixed] = stripe_pattern
        
        # 黒い枠を追加（高速化）
        if add_border:
            result_fixed = add_black_border(result_fixed, (x_fixed, y_fixed, width_fixed, height_fixed), border_width)
        
        del stripe_pattern, base_fixed_array
        clear_memory()
        
        print(f"🔧 Final compositing: {time.time() - phase_start:.2f}s")
        
        # === フェーズ7: 保存（最適化） ===
        phase_start = time.time()
        
        timestamp = int(time.time())
        result_id = uuid.uuid4().hex[:8]
        result_filename = f"result_{result_id}_{timestamp}.png"
        
        os.makedirs("static", exist_ok=True)
        result_path = os.path.join("static", result_filename)
        
        # PNG保存の最適化
        result_image = Image.fromarray(result_fixed.astype('uint8'))
        result_image.save(
            result_path, 
            format="PNG", 
            optimize=False,  # optimizeを無効化して高速化
            compress_level=6  # 適度な圧縮で高速化
        )
        
        del result_fixed, result_image
        clear_memory()
        
        print(f"💾 File saving: {time.time() - phase_start:.2f}s")
        
        total_time = time.time() - start_time
        print(f"🎉 Total processing time: {total_time:.2f}s")
        
        # 結果を辞書で返却（エラー修正）
        result_dict = {
            "result": result_filename
        }
        
        print(f"Returning result: {result_dict}")
        
        return result_dict
        
    except Exception as e:
        print(f"❌ Processing error: {e}")
        import traceback
        traceback.print_exc()
        clear_memory()
        raise e
