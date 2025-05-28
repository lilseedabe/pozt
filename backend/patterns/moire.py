# patterns/moire.py の隠蔽効果強化版

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

def create_fast_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.12):
    """隠蔽効果強化版：モアレ縞模様生成"""
    hidden_array = ensure_array(hidden_img).astype(np.uint8)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化（OpenCV高速実装）
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array, cv2.COLOR_RGB2GRAY)
    else:
        hidden_gray = hidden_array
    
    # より控えめなコントラスト強調（隠蔽効果重視）
    hidden_norm = hidden_gray.astype(np.float32) / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 1.8 + 0.5, 0, 1)  # 3.0→1.8に削減
    
    # 結果画像を初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # より控えめな縞模様（隠蔽効果重視）
    base_gray = 128    # 基準グレー
    stripe_range = 25  # 縞の幅を狭く（50→25）
    dark_value = base_gray - stripe_range   # 103
    light_value = base_gray + stripe_range  # 153
    
    if pattern_type == "horizontal":
        # 横縞（水平方向の縞）- 隠蔽効果強化版
        for y in range(height):
            # 基本縞模様（より控えめ）
            base_stripe = light_value if (y % 2) == 0 else dark_value
            
            # 隠し画像の影響を計算（より控えめ）
            pixel_brightness = hidden_contrast[y, :]
            adjustment = (pixel_brightness - 0.5) * strength * 255 * 0.6  # さらに控えめに
            
            # 最終的な値を計算（範囲を制限）
            stripe_values = np.clip(base_stripe + adjustment, 80, 175)
            
            # 全チャンネルに同じ値を設定
            result[y, :, 0] = stripe_values
            result[y, :, 1] = stripe_values  
            result[y, :, 2] = stripe_values
    
    elif pattern_type == "vertical":
        # 縦縞（垂直方向の縞）- 隠蔽効果強化版
        for x in range(width):
            # 基本縞模様（より控えめ）
            base_stripe = light_value if (x % 2) == 0 else dark_value
            
            # 隠し画像の影響を計算（より控えめ）
            pixel_brightness = hidden_contrast[:, x]
            adjustment = (pixel_brightness - 0.5) * strength * 255 * 0.6
            
            # 最終的な値を計算（範囲を制限）
            stripe_values = np.clip(base_stripe + adjustment, 80, 175)
            
            # 全チャンネルに同じ値を設定
            result[:, x, 0] = stripe_values
            result[:, x, 1] = stripe_values
            result[:, x, 2] = stripe_values
    
    return result

def create_fast_high_frequency_stripes(hidden_img, pattern_type="horizontal", strength=0.08):
    """隠蔽効果強化版：高周波縞模様生成"""
    hidden_array = ensure_array(hidden_img).astype(np.uint8)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array, cv2.COLOR_RGB2GRAY)
    else:
        hidden_gray = hidden_array
    
    # 隠し画像のコントラスト強調（控えめ）
    hidden_norm = hidden_gray.astype(np.float32) / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.2 + 0.5, 0, 1)  # 4.0→2.2に削減
    
    # 結果画像を初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # より控えめな縞模様の基本値
    base_gray = 128
    stripe_range = 20  # さらに狭く
    dark_value = base_gray - stripe_range   # 108
    light_value = base_gray + stripe_range  # 148
    
    if pattern_type == "horizontal":
        # 横縞パターン（隠蔽効果重視）
        for y in range(height):
            # 基本縞模様
            base_stripe = light_value if (y % 2) == 0 else dark_value
            
            # 隠し画像の影響を適用（より控えめ）
            pixel_brightness = hidden_contrast[y, :]
            adjustment = (pixel_brightness - 0.5) * strength * 255 * 0.5
            stripe_values = np.clip(base_stripe + adjustment, 90, 165)
            
            # 全チャンネルに同じ値を設定
            result[y, :, 0] = stripe_values
            result[y, :, 1] = stripe_values
            result[y, :, 2] = stripe_values
    
    elif pattern_type == "vertical":
        # 縦縞パターン（隠蔽効果重視）
        for x in range(width):
            base_stripe = light_value if (x % 2) == 0 else dark_value
            
            pixel_brightness = hidden_contrast[:, x]
            adjustment = (pixel_brightness - 0.5) * strength * 255 * 0.5
            stripe_values = np.clip(base_stripe + adjustment, 90, 165)
            
            # 全チャンネルに同じ値を設定
            result[:, x, 0] = stripe_values
            result[:, x, 1] = stripe_values
            result[:, x, 2] = stripe_values
    
    return result

# 既存関数のエイリアス（隠蔽効果重視・強度調整）
def create_adaptive_moire_stripes(hidden_img, pattern_type="horizontal", mode="adaptive"):
    """適応型モアレ縞模様（隠蔽効果強化版）"""
    strength_map = {
        "adaptive": 0.12,           # 0.25→0.12
        "adaptive_subtle": 0.08,    # 0.2→0.08
        "adaptive_strong": 0.15,    # 0.35→0.15
        "adaptive_minimal": 0.06,   # 0.15→0.06
        "perfect_subtle": 0.1,      # 0.3→0.1
        "ultra_subtle": 0.09,       # 0.25→0.09
        "near_perfect": 0.08,       # 0.22→0.08
    }
    strength = strength_map.get(mode, 0.12)
    return create_fast_moire_stripes(hidden_img, pattern_type, strength)

def create_high_frequency_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.08):
    """高周波モアレ縞模様（隠蔽効果強化版）"""
    return create_fast_high_frequency_stripes(hidden_img, pattern_type, strength)

def create_moire_hidden_stripes(hidden_img, pattern_type="horizontal", strength=0.12):
    """基本モアレ縞模様（隠蔽効果強化版）"""
    return create_fast_moire_stripes(hidden_img, pattern_type, strength)
