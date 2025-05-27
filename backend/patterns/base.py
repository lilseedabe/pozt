"""
基本的なパターン生成機能
"""
import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale, enhance_contrast, detect_edges
from config.settings import STRENGTH_MAP

def create_stripe_base(height, width, pattern_type="horizontal"):
    """基本的な縞模様を生成"""
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    if pattern_type == "horizontal":
        # 横縞パターン
        for y in range(height):
            stripe_value = 255 if y % 2 == 0 else 0
            result[y, :] = [stripe_value, stripe_value, stripe_value]
    else:  # vertical
        # 縦縞パターン
        for x in range(width):
            stripe_value = 255 if x % 2 == 0 else 0
            result[:, x] = [stripe_value, stripe_value, stripe_value]
    
    return result

def get_adaptive_strength(mode):
    """モードに応じた強度を取得"""
    return STRENGTH_MAP.get(mode, 0.02)
