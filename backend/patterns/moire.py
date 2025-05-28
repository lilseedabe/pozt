# patterns/moire.py の修正版

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

def create_fast_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.3):
    """修正版：高速化されたモアレ縞模様生成"""
    hidden_array = ensure_array(hidden_img).astype(np.uint8)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化（OpenCV高速実装）
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array, cv2.COLOR_RGB2GRAY)
    else:
        hidden_gray = hidden_array
    
    # 正規化とコントラスト強調（より強い効果）
    hidden_norm = hidden_gray.astype(np.float32) / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 3.0 + 0.5, 0, 1)  # 強化
    
    # 結果画像を初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 縞模様の基本値（より強いコントラスト）
    dark_value = 50   # より暗く
    light_value = 205  # より明るく
    
    if pattern_type == "horizontal":
        # 横縞（水平方向の縞）- 修正版
        for y in range(height):
            # 基本縞模様（1ピクセル単位で交互）
            base_stripe = light_value if (y % 2) == 0 else dark_value
            
            # 隠し画像の影響を計算（より強く）
            pixel_brightness = hidden_contrast[y, :]
            adjustment = (pixel_brightness - 0.5) * strength * 255
            
            # 最終的な値を計算
            stripe_values = np.clip(base_stripe + adjustment, 0, 255)
            
            # 全チャンネルに同じ値を設定
            result[y, :, 0] = stripe_values
            result[y, :, 1] = stripe_values  
            result[y, :, 2] = stripe_values
    
    elif pattern_type == "vertical":
        # 縦縞（垂直方向の縞）- 修正版
        for x in range(width):
            # 基本縞模様（1ピクセル単位で交互）
            base_stripe = light_value if (x % 2) == 0 else dark_value
            
            # 隠し画像の影響を計算（より強く）
            pixel_brightness = hidden_contrast[:, x]
            adjustment = (pixel_brightness - 0.5) * strength * 255
            
            # 最終的な値を計算
            stripe_values = np.clip(base_stripe + adjustment, 0, 255)
            
            # 全チャンネルに同じ値を設定
            result[:, x, 0] = stripe_values
            result[:, x, 1] = stripe_values
            result[:, x, 2] = stripe_values
    
    return result

def create_fast_high_frequency_stripes(hidden_img, pattern_type="horizontal", strength=0.25):
    """修正版：高速化された高周波縞模様生成"""
    hidden_array = ensure_array(hidden_img).astype(np.uint8)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array, cv2.COLOR_RGB2GRAY)
    else:
        hidden_gray = hidden_array
    
    # 隠し画像のコントラスト強調（より強く）
    hidden_norm = hidden_gray.astype(np.float32) / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 4.0 + 0.5, 0, 1)  # さらに強化
    
    # 結果画像を初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 縞模様の基本値（より強いコントラスト）
    dark_value = 80
    light_value = 175
    
    if pattern_type == "horizontal":
        # 横縞パターン（より細かい縞）
        for y in range(height):
            # 基本縞模様
            base_stripe = light_value if (y % 2) == 0 else dark_value
            
            # 隠し画像の影響を適用
            pixel_brightness = hidden_contrast[y, :]
            adjustment = (pixel_brightness - 0.5) * strength * 255
            stripe_values = np.clip(base_stripe + adjustment, 20, 235)
            
            # 全チャンネルに同じ値を設定
            result[y, :, 0] = stripe_values
            result[y, :, 1] = stripe_values
            result[y, :, 2] = stripe_values
    
    elif pattern_type == "vertical":
        # 縦縞パターン
        for x in range(width):
            base_stripe = light_value if (x % 2) == 0 else dark_value
            
            pixel_brightness = hidden_contrast[:, x]
            adjustment = (pixel_brightness - 0.5) * strength * 255
            stripe_values = np.clip(base_stripe + adjustment, 20, 235)
            
            # 全チャンネルに同じ値を設定
            result[:, x, 0] = stripe_values
            result[:, x, 1] = stripe_values
            result[:, x, 2] = stripe_values
    
    return result

# 既存関数のエイリアス（互換性維持・強度調整）
def create_adaptive_moire_stripes(hidden_img, pattern_type="horizontal", mode="adaptive"):
    """適応型モアレ縞模様（修正版）"""
    strength_map = {
        "adaptive": 0.25,           # 大幅増加
        "adaptive_subtle": 0.2,     # 大幅増加
        "adaptive_strong": 0.35,    # 大幅増加
        "adaptive_minimal": 0.15,   # 大幅増加
        "perfect_subtle": 0.3,      # 大幅増加
        "ultra_subtle": 0.25,       # 大幅増加
        "near_perfect": 0.22,       # 大幅増加
    }
    strength = strength_map.get(mode, 0.25)
    return create_fast_moire_stripes(hidden_img, pattern_type, strength)

def create_high_frequency_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.25):
    """高周波モアレ縞模様（修正版）"""
    return create_fast_high_frequency_stripes(hidden_img, pattern_type, strength)

def create_moire_hidden_stripes(hidden_img, pattern_type="horizontal", strength=0.25):
    """基本モアレ縞模様（修正版）"""
    return create_fast_moire_stripes(hidden_img, pattern_type, strength)
