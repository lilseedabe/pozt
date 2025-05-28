# patterns/moire.py の高速化版モジュール

import numpy as np
import cv2
from numba import jit, prange
from core.image_utils import ensure_array, get_grayscale

# NumbaのJITコンパイルで数値計算を高速化
@jit(nopython=True, parallel=True, cache=True)
def fast_moire_generation(hidden_gray, height, width, pattern_type, strength=0.02):
    """JITコンパイルされた超高速モアレ生成"""
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 正規化とコントラスト強調（ベクトル化）
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.0 + 0.5, 0, 1)
    
    if pattern_type == 0:  # horizontal
        for y in prange(height):
            base_stripe = (y % 2) * 255
            for x in range(width):
                pixel_brightness = hidden_contrast[y, x]
                
                if base_stripe == 255:
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    stripe_value = 255 + adjustment
                else:
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    stripe_value = 0 + adjustment
                
                stripe_value = max(0, min(255, stripe_value))
                result[y, x, 0] = stripe_value
                result[y, x, 1] = stripe_value
                result[y, x, 2] = stripe_value
    
    else:  # vertical
        for x in prange(width):
            base_stripe = (x % 2) * 255
            for y in range(height):
                pixel_brightness = hidden_contrast[y, x]
                
                if base_stripe == 255:
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    stripe_value = 255 + adjustment
                else:
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    stripe_value = 0 + adjustment
                
                stripe_value = max(0, min(255, stripe_value))
                result[y, x, 0] = stripe_value
                result[y, x, 1] = stripe_value
                result[y, x, 2] = stripe_value
    
    return result

@jit(nopython=True, parallel=True, cache=True)
def fast_high_frequency_generation(hidden_gray, height, width, pattern_type, strength=0.015):
    """JITコンパイルされた高周波パターン生成"""
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.5 + 0.5, 0, 1)
    
    dark_value = 110
    light_value = 146
    
    if pattern_type == 0:  # horizontal
        for y in prange(height):
            for x in range(width):
                base_stripe = 1 if ((y * 2) % 2) == 0 else 0
                pixel_brightness = hidden_contrast[y, x]
                
                if base_stripe == 1:
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    stripe_value = light_value + adjustment
                else:
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    stripe_value = dark_value + adjustment
                
                stripe_value = max(90, min(166, stripe_value))
                result[y, x, 0] = stripe_value
                result[y, x, 1] = stripe_value
                result[y, x, 2] = stripe_value
    
    else:  # vertical
        for x in prange(width):
            for y in range(height):
                base_stripe = 1 if ((x * 2) % 2) == 0 else 0
                pixel_brightness = hidden_contrast[y, x]
                
                if base_stripe == 1:
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    stripe_value = light_value + adjustment
                else:
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    stripe_value = dark_value + adjustment
                
                stripe_value = max(90, min(166, stripe_value))
                result[y, x, 0] = stripe_value
                result[y, x, 1] = stripe_value
                result[y, x, 2] = stripe_value
    
    return result

def create_fast_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.02):
    """高速化されたモアレ縞模様生成"""
    hidden_array = ensure_array(hidden_img).astype(np.uint8)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化（OpenCV高速実装）
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array, cv2.COLOR_RGB2GRAY)
    else:
        hidden_gray = hidden_array
    
    # パターンタイプを数値に変換（JIT用）
    pattern_num = 0 if pattern_type == "horizontal" else 1
    
    # JITコンパイルされた関数を呼び出し
    result = fast_moire_generation(hidden_gray, height, width, pattern_num, strength)
    
    return result

def create_fast_high_frequency_stripes(hidden_img, pattern_type="horizontal", strength=0.015):
    """高速化された高周波縞模様生成"""
    hidden_array = ensure_array(hidden_img).astype(np.uint8)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array, cv2.COLOR_RGB2GRAY)
    else:
        hidden_gray = hidden_array
    
    pattern_num = 0 if pattern_type == "horizontal" else 1
    result = fast_high_frequency_generation(hidden_gray, height, width, pattern_num, strength)
    
    return result

# 既存関数のエイリアス（互換性維持）
def create_adaptive_moire_stripes(hidden_img, pattern_type="horizontal", mode="adaptive"):
    """適応型モアレ縞模様（高速版）"""
    strength_map = {
        "adaptive": 0.02,
        "adaptive_subtle": 0.015,
        "adaptive_strong": 0.03,
        "adaptive_minimal": 0.01,
    }
    strength = strength_map.get(mode, 0.02)
    return create_fast_moire_stripes(hidden_img, pattern_type, strength)

def create_high_frequency_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.015):
    """高周波モアレ縞模様（高速版）"""
    return create_fast_high_frequency_stripes(hidden_img, pattern_type, strength)
