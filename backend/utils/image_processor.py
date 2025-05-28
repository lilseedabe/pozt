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

def fast_edge_detection(img_gray, low_threshold=50, high_threshold=100):
    """高速化されたエッジ検出（パラメータ調整）"""
    # より軽いパラメータでエッジ検出を高速化
    edges = cv2.Canny(img_gray, low_threshold, high_threshold, apertureSize=3)
    return edges / 255.0

def parallel_pattern_generation(hidden_array, pattern_type, stripe_method, overlay_ratio=0.4):
    """並列処理でパターン生成を高速化"""
    config = get_cached_pattern_config(stripe_method)
    
    def generate_base_pattern():
        if config["base_method"] == "high_frequency":
            return create_high_frequency_moire_stripes(hidden_array, pattern_type, strength=0.015)
        elif config["base_method"] and "adaptive" in config["base_method"]:
            return create_adaptive_moire_stripes(hidden_array, pattern_type, config["base_method"])
        return None
    
    def generate_overlay_pattern():
        return create_overlay_moire_pattern(hidden_array, pattern_type, overlay_opacity=0.6)
    
    # 並列実行（base_methodがNoneの場合はオーバーレイのみ）
    if config["base_method"] is None:
        return generate_overlay_pattern()
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        # 2つのパターンを並列生成
        base_future = executor.submit(generate_base_pattern)
        overlay_future = executor.submit(generate_overlay_pattern)
        
        base_pattern = base_future.result()
        overlay_pattern = overlay_future.result()
        
        # 加重合成（OpenCVの高速実装を使用）
        result = cv2.addWeighted(
            base_pattern, config["base_weight"], 
            overlay_pattern, config["overlay_weight"], 
            0
        )
        
        # 中間データを即座に削除
        del base_pattern, overlay_pattern
        return result

def fast_resize_with_optimization(img, target_size, method='contain'):
    """最適化された高速リサイズ"""
    target_width, target_height = target_size
    
    if isinstance(img, np.ndarray):
        img_pil = Image.fromarray(img)
    else:
        img_pil = img
    
    # 既に目標サイズの場合はスキップ
    if img_pil.size == (target_width, target_height):
        return img_pil
    
    # LANCZOSの代わりにBILINEARを使用（速度優先）
    if method == 'stretch':
        return img_pil.resize((target_width, target_height), Image.Resampling.BILINEAR)
    
    # contain/cover処理も高速化版を使用
    orig_width, orig_height = img_pil.size
    orig_aspect = orig_width / orig_height
    target_aspect = target_width / target_height
    
    if method == 'contain':
        if orig_aspect > target_aspect:
            new_width = target_width
            new_height = int(target_width / orig_aspect)
        else:
            new_height = target_height
            new_width = int(target_height * orig_aspect)
        
        resized = img_pil.resize((new_width, new_height), Image.Resampling.BILINEAR)
        
        # 黒背景キャンバス（高速生成）
        canvas = Image.new('RGB', (target_width, target_height), (0, 0, 0))
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        canvas.paste(resized, (x_offset, y_offset))
        
        return canvas
    
    elif method == 'cover':
        if orig_aspect > target_aspect:
            new_height = target_height
            new_width = int(target_height * orig_aspect)
        else:
            new_width = target_width
            new_height = int(target_width / orig_aspect)
        
        resized = img_pil.resize((new_width, new_height), Image.Resampling.BILINEAR)
        
        x_offset = (new_width - target_width) // 2
        y_offset = (new_height - target_height) // 2
        cropped = resized.crop((x_offset, y_offset, x_offset + target_width, y_offset + target_height))
        
        return cropped

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
    """超高速版：モアレ効果を利用した隠し画像を生成"""
    start_time = time.time()
    settings = get_settings()
    
    print(f"🚀 Starting high-speed processing...")
    
    try:
        # === フェーズ1: 画像読み込み（最適化） ===
        phase_start = time.time()
        
        with Image.open(base_img_path) as base_img:
            # 巨大な画像は事前に軽くリサイズ（処理速度向上）
            if base_img.width * base_img.height > 8000000:  # 8MP以上
                print("⚡ Large image detected, applying fast pre-resize...")
                base_img.thumbnail((3000, 3000), Image.Resampling.BILINEAR)
            
            base_img_array = optimize_image_for_processing(np.array(base_img))
        
        print(f"📁 Image loading: {time.time() - phase_start:.2f}s")
        
        # === フェーズ2: 領域抽出と前処理 ===
        phase_start = time.time()
        
        x, y, width, height = region
        hidden_img = extract_region_from_image(base_img_array, region)
        
        if hidden_img is None:
            raise ValueError("領域の抽出に失敗しました")
        
        # 高速リサイズを使用
        base_fixed = fast_resize_with_optimization(
            base_img_array, 
            (settings.TARGET_WIDTH, settings.TARGET_HEIGHT), 
            method=resize_method
        )
        base_fixed_array = optimize_image_for_processing(np.array(base_fixed))
        
        # 元のデータを即座に削除
        del base_img_array
        clear_memory()
        
        print(f"🔄 Preprocessing: {time.time() - phase_start:.2f}s")
        
        # === フェーズ3: 座標変換（高速化） ===
        phase_start = time.time()
        
        # スケール計算を簡略化
        if resize_method != 'stretch':
            scale = min(settings.TARGET_WIDTH / (x + width), settings.TARGET_HEIGHT / (y + height))
            x_fixed = int(x * scale)
            y_fixed = int(y * scale)
            width_fixed = int(width * scale)
            height_fixed = int(height * scale)
        else:
            scale_x = settings.TARGET_WIDTH / base_img_array.shape[1] if 'base_img_array' in locals() else 1
            scale_y = settings.TARGET_HEIGHT / base_img_array.shape[0] if 'base_img_array' in locals() else 1
            x_fixed = int(x * scale_x)
            y_fixed = int(y * scale_y)
            width_fixed = int(width * scale_x)
            height_fixed = int(height * scale_y)
        
        # 境界チェック（高速化）
        x_fixed = max(0, min(x_fixed, settings.TARGET_WIDTH - 1))
        y_fixed = max(0, min(y_fixed, settings.TARGET_HEIGHT - 1))
        width_fixed = min(width_fixed, settings.TARGET_WIDTH - x_fixed)
        height_fixed = min(height_fixed, settings.TARGET_HEIGHT - y_fixed)
        
        print(f"📐 Coordinate mapping: {time.time() - phase_start:.2f}s")
        
        # === フェーズ4: 隠し画像準備（高速化） ===
        phase_start = time.time()
        
        hidden_pil = Image.fromarray(hidden_img.astype('uint8'))
        hidden_resized = hidden_pil.resize((width_fixed, height_fixed), Image.Resampling.BILINEAR)
        hidden_array = optimize_image_for_processing(np.array(hidden_resized))
        
        del hidden_img, hidden_pil, hidden_resized
        clear_memory()
        
        print(f"🖼️ Hidden image prep: {time.time() - phase_start:.2f}s")
        
        # === フェーズ5: パターン生成（並列処理） ===
        phase_start = time.time()
        
        stripe_pattern = parallel_pattern_generation(hidden_array, pattern_type, stripe_method, overlay_ratio)
        stripe_pattern = optimize_image_for_processing(stripe_pattern)
        
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
            # OpenCVの高速rectangle描画を使用
            cv2.rectangle(
                result_fixed, 
                (x_fixed - border_width, y_fixed - border_width),
                (x_fixed + width_fixed + border_width, y_fixed + height_fixed + border_width),
                (0, 0, 0), 
                border_width
            )
        
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
        
        # PNG保存の最適化（compress_level=6で速度と品質のバランス）
        Image.fromarray(result_fixed.astype('uint8')).save(
            result_path, 
            format="PNG", 
            optimize=False,  # optimizeを無効化して高速化
            compress_level=6  # 適度な圧縮で高速化
        )
        
        del result_fixed
        clear_memory()
        
        print(f"💾 File saving: {time.time() - phase_start:.2f}s")
        
        total_time = time.time() - start_time
        print(f"🎉 Total processing time: {total_time:.2f}s")
        
        return {
            "result": result_filename,
            "processing_time": round(total_time, 2)
        }
        
    except Exception as e:
        print(f"❌ Processing error: {e}")
        clear_memory()
        raise e
