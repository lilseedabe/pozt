"""
基本的なパターン生成機能
"""
import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale, enhance_contrast, detect_edges
from config.settings import STRENGTH_MAP

def create_stripe_base(height, width, pattern_type="horizontal", color1="#000000", color2="#ffffff"):
    """基本的な縞模様を生成（カラー対応）"""
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # HEX色をRGBに変換
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    if pattern_type == "horizontal":
        # 横縞パターン
        for y in range(height):
            color = rgb1 if y % 2 == 0 else rgb2
            result[y, :] = color
    else:  # vertical
        # 縦縞パターン
        for x in range(width):
            color = rgb1 if x % 2 == 0 else rgb2
            result[:, x] = color
    
    return result

def get_adaptive_strength(mode):
    """モードに応じた強度を取得"""
    return STRENGTH_MAP.get(mode, 0.02)
