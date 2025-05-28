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

        if stripe_method == "overlay":
            overlay_pattern = create_overlay_moire_pattern(hidden_array, pattern_type, overlay_opacity=0.3)
            return overlay_pattern

        overlay_pattern = create_overlay_moire_pattern(hidden_array, pattern_type, overlay_opacity=0.25)

        if config["base_method"] is None:
            print("Using overlay-only pattern")
            return overlay_pattern

        base_pattern = None
        if config["base_method"] == "high_frequency":
            print("Generating high frequency pattern")
            base_pattern = create_high_frequency_moire_stripes(hidden_array, pattern_type, strength=0.08)
        elif config["base_method"] and "adaptive" in config["base_method"]:
            print(f"Generating adaptive pattern: {config['base_method']}")
            base_pattern = create_adaptive_moire_stripes(hidden_array, pattern_type, config["base_method"])
        else:
            print("Using default adaptive pattern")
            base_pattern = create_adaptive_moire_stripes(hidden_array, pattern_type, "adaptive")
        if base_pattern is None:
            print("Base pattern is None, using overlay only")
            return overlay_pattern

        print(f"Base pattern shape: {base_pattern.shape}")
        print(f"Overlay pattern shape: {overlay_pattern.shape}")
        if base_pattern.shape != overlay_pattern.shape:
            print("Shape mismatch detected, using overlay only")
            del base_pattern
            return overlay_pattern

        result = cv2.addWeighted(
            optimize_image_for_processing(base_pattern), config["base_weight"] * 0.6,
            optimize_image_for_processing(overlay_pattern), config["overlay_weight"] * 0.4,
            0
        )
        del base_pattern, overlay_pattern
        clear_memory()
        return result

    except Exception as e:
        print(f"Pattern generation error: {e}")
        try:
            overlay_pattern = create_overlay_moire_pattern(hidden_array, pattern_type, overlay_opacity=0.2)
            return overlay_pattern
        except Exception as fallback_error:
            print(f"Fallback pattern generation error: {fallback_error}")
            height, width = hidden_array.shape[:2]
            fallback_result = np.zeros((height, width, 3), dtype=np.uint8)
            base_gray = 128
            stripe_amplitude = 30
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
    """修正版：PILでcropしてからNumPy化し、メモリ効率を最大化"""
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
            original_size = (base_img.width, base_img.height)
            print(f"Original image size: {original_size}")
            if base_img.width * base_img.height > 8000000:
                print("⚡ Large image detected, applying fast pre-resize...")
                base_img.thumbnail((3000, 3000), Image.Resampling.BILINEAR)

            # 修正ポイント: PILのまま領域cropし、その部分だけNumPy化
            x, y, width, height = region
            # 境界チェック（PIL画像サイズで）
            x = max(0, min(x, base_img.width - 1))
            y = max(0, min(y, base_img.height - 1))
            width = min(width, base_img.width - x)
            height = min(height, base_img.height - y)
            region_pil = base_img.crop((x, y, x + width, y + height))
            print(f"🖼️ PIL crop done: {region_pil.size}")

        # NumPy化は小領域だけ
        hidden_img = np.array(region_pil)
        hidden_img = optimize_image_for_processing(hidden_img)
        print(f"Hidden image shape: {hidden_img.shape}")

        # 固定サイズにリサイズ
        base_fixed = resize_to_fixed_size(base_img, method=resize_method)
        base_fixed_array = optimize_image_for_processing(np.array(base_fixed))

        del base_img, region_pil
        clear_memory()

        # === フェーズ3: 座標変換（リサイズ後の座標） ===
        img_width, img_height = original_size
        scale_x = settings.TARGET_WIDTH / img_width
        scale_y = settings.TARGET_HEIGHT / img_height
        print(f"Scale factors: scale_x={scale_x:.4f}, scale_y={scale_y:.4f}")

        if resize_method == 'contain':
            scale = min(scale_x, scale_y)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            offset_x = (settings.TARGET_WIDTH - new_width) // 2
            offset_y = (settings.TARGET_HEIGHT - new_height) // 2
            x_fixed = int(x * scale) + offset_x
            y_fixed = int(y * scale) + offset_y
            width_fixed = int(width * scale)
            height_fixed = int(height * scale)
        elif resize_method == 'cover':
            scale = max(scale_x, scale_y)
            crop_offset_x = int((img_width * scale - settings.TARGET_WIDTH) / 2)
            crop_offset_y = int((img_height * scale - settings.TARGET_HEIGHT) / 2)
            x_fixed = int(x * scale) - crop_offset_x
            y_fixed = int(y * scale) - crop_offset_y
            width_fixed = int(width * scale)
            height_fixed = int(height * scale)
        else:  # stretch
            x_fixed = int(x * scale_x)
            y_fixed = int(y * scale_y)
            width_fixed = int(width * scale_x)
            height_fixed = int(height * scale_y)

        # 境界チェック
        x_fixed = max(0, min(x_fixed, settings.TARGET_WIDTH - 1))
        y_fixed = max(0, min(y_fixed, settings.TARGET_HEIGHT - 1))
        width_fixed = min(width_fixed, settings.TARGET_WIDTH - x_fixed)
        height_fixed = min(height_fixed, settings.TARGET_HEIGHT - y_fixed)
        print(f"Fixed region (corrected): x={x_fixed}, y={y_fixed}, w={width_fixed}, h={height_fixed}")

        # === フェーズ4: 隠し画像準備 ===
        hidden_pil = Image.fromarray(hidden_img.astype('uint8'))
        hidden_resized = hidden_pil.resize((width_fixed, height_fixed), Image.Resampling.BILINEAR)
        hidden_array = optimize_image_for_processing(np.array(hidden_resized))
        print(f"Hidden array final shape: {hidden_array.shape}")
        del hidden_img, hidden_pil, hidden_resized
        clear_memory()

        # === フェーズ5: パターン生成 ===
        stripe_pattern = safe_pattern_generation(hidden_array, pattern_type, stripe_method, overlay_ratio)
        stripe_pattern = optimize_image_for_processing(stripe_pattern)
        print(f"Final stripe pattern shape: {stripe_pattern.shape}")
        del hidden_array
        clear_memory()

        # === フェーズ6: 最終合成 ===
        result_fixed = base_fixed_array.copy()
        result_fixed[y_fixed:y_fixed + height_fixed, x_fixed:x_fixed + width_fixed] = stripe_pattern
        if add_border:
            result_fixed = add_black_border(result_fixed, (x_fixed, y_fixed, width_fixed, height_fixed), border_width)
        del stripe_pattern, base_fixed_array
        clear_memory()

        # === フェーズ7: 保存 ===
        timestamp = int(time.time())
        result_id = uuid.uuid4().hex[:8]
        result_filename = f"result_{result_id}_{timestamp}.png"

        os.makedirs("static", exist_ok=True)
        result_path = os.path.join("static", result_filename)
        result_image = Image.fromarray(result_fixed.astype('uint8'))
        result_image.save(
            result_path,
            format="PNG",
            optimize=False,
            compress_level=6
        )
        del result_fixed, result_image
        clear_memory()

        total_time = time.time() - start_time
        print(f"🎉 Total processing time: {total_time:.2f}s")

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
