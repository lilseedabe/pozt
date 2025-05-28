# patterns/overlay.py の高速化版

import numpy as np
import cv2
from numba import jit, prange
from core.image_utils import ensure_array, get_grayscale

@jit(nopython=True, parallel=True, cache=True)
def fast_overlay_generation(hidden_gray, height, width, pattern_type, overlay_opacity=0.6):
    """JITコンパイルされた高速オーバーレイ生成"""
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 二値化マスクの生成（簡略化）
    mask = np.zeros((height, width), dtype=np.float32)
    for y in prange(height):
        for x in range(width):
            if hidden_gray[y, x] < 100:  # 閾値100で二値化
                mask[y, x] = overlay_opacity
    
    # 縞模様とグレーの合成
    if pattern_type == 0:  # horizontal
        for y in prange(height):
            stripe_value = (y % 2) * 255
            for x in range(width):
                mask_val = mask[y, x]
                final_value = stripe_value * (1 - mask_val) + 128 * mask_val
                final_value = max(0, min(255, final_value))
                result[y, x, 0] = final_value
                result[y, x, 1] = final_value
                result[y, x, 2] = final_value
    else:  # vertical
        for x in prange(width):
            stripe_value = (x % 2) * 255
            for y in range(height):
                mask_val = mask[y, x]
                final_value = stripe_value * (1 - mask_val) + 128 * mask_val
                final_value = max(0, min(255, final_value))
                result[y, x, 0] = final_value
                result[y, x, 1] = final_value
                result[y, x, 2] = final_value
    
    return result

def create_overlay_moire_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.6):
    """高速化されたオーバーレイモアレパターン生成"""
    hidden_array = ensure_array(hidden_img).astype(np.uint8)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化（OpenCV高速実装）
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array, cv2.COLOR_RGB2GRAY)
    else:
        hidden_gray = hidden_array
    
    # パターンタイプを数値に変換
    pattern_num = 0 if pattern_type == "horizontal" else 1
    
    # JITコンパイルされた関数を呼び出し
    result = fast_overlay_generation(hidden_gray, height, width, pattern_num, overlay_opacity)
    
    return result
