# patterns/moire.py のシンプル版（Numbaなしで安定性重視）

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

def create_fast_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.02):
    """高速化されたモアレ縞模様生成（Numbaなし・安定版）"""
    hidden_array = ensure_array(hidden_img).astype(np.uint8)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化（OpenCV高速実装）
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array, cv2.COLOR_RGB2GRAY)
    else:
        hidden_gray = hidden_array
    
    # 正規化とコントラスト強調（ベクトル化）
    hidden_norm = hidden_gray.astype(np.float32) / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.0 + 0.5, 0, 1)
    
    # 結果画像を初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    if pattern_type == "horizontal":
        # 横縞（水平方向の縞）- ベクトル化で高速化
        for y in range(height):
            base_stripe = (y % 2) * 255
            # 行全体を一括処理（ベクトル化）
            pixel_brightness = hidden_contrast[y, :]
            
            if base_stripe == 255:
                adjustment = (pixel_brightness - 0.5) * strength * 255
                stripe_values = np.clip(255 + adjustment, 0, 255)
            else:
                adjustment = (pixel_brightness - 0.5) * strength * 255
                stripe_values = np.clip(0 + adjustment, 0, 255)
            
            # 全チャンネルに同じ値を設定
            result[y, :, 0] = stripe_values
            result[y, :, 1] = stripe_values
            result[y, :, 2] = stripe_values
    
    elif pattern_type == "vertical":
        # 縦縞（垂直方向の縞）- ベクトル化で高速化
        for x in range(width):
            base_stripe = (x % 2) * 255
            # 列全体を一括処理（ベクトル化）
            pixel_brightness = hidden_contrast[:, x]
            
            if base_stripe == 255:
                adjustment = (pixel_brightness - 0.5) * strength * 255
                stripe_values = np.clip(255 + adjustment, 0, 255)
            else:
                adjustment = (pixel_brightness - 0.5) * strength * 255
                stripe_values = np.clip(0 + adjustment, 0, 255)
            
            # 全チャンネルに同じ値を設定
            result[:, x, 0] = stripe_values
            result[:, x, 1] = stripe_values
            result[:, x, 2] = stripe_values
    
    return result

def create_fast_high_frequency_stripes(hidden_img, pattern_type="horizontal", strength=0.015):
    """高速化された高周波縞模様生成（Numbaなし・安定版）"""
    hidden_array = ensure_array(hidden_img).astype(np.uint8)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array, cv2.COLOR_RGB2GRAY)
    else:
        hidden_gray = hidden_array
    
    # 隠し画像のコントラスト強調
    hidden_norm = hidden_gray.astype(np.float32) / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.5 + 0.5, 0, 1)
    
    # 結果画像を初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 縞模様の基本値
    dark_value = 110
    light_value = 146
    
    if pattern_type == "horizontal":
        # 横縞パターン
        for y in range(height):
            # 2倍の周波数で縞模様を生成
            base_stripe = 1 if ((y * 2) % 2) == 0 else 0
            
            # 行全体を一括処理
            pixel_brightness = hidden_contrast[y, :]
            
            if base_stripe == 1:
                adjustment = (pixel_brightness - 0.5) * strength * 255
                stripe_values = np.clip(light_value + adjustment, 90, 166)
            else:
                adjustment = (pixel_brightness - 0.5) * strength * 255
                stripe_values = np.clip(dark_value + adjustment, 90, 166)
            
            # 全チャンネルに同じ値を設定
            result[y, :, 0] = stripe_values
            result[y, :, 1] = stripe_values
            result[y, :, 2] = stripe_values
    
    elif pattern_type == "vertical":
        # 縦縞パターン
        for x in range(width):
            base_stripe = 1 if ((x * 2) % 2) == 0 else 0
            
            # 列全体を一括処理
            pixel_brightness = hidden_contrast[:, x]
            
            if base_stripe == 1:
                adjustment = (pixel_brightness - 0.5) * strength * 255
                stripe_values = np.clip(light_value + adjustment, 90, 166)
            else:
                adjustment = (pixel_brightness - 0.5) * strength * 255
                stripe_values = np.clip(dark_value + adjustment, 90, 166)
            
            # 全チャンネルに同じ値を設定
            result[:, x, 0] = stripe_values
            result[:, x, 1] = stripe_values
            result[:, x, 2] = stripe_values
    
    return result

# 既存関数のエイリアス（互換性維持）
def create_adaptive_moire_stripes(hidden_img, pattern_type="horizontal", mode="adaptive"):
    """適応型モアレ縞模様（高速版）"""
    strength_map = {
        "adaptive": 0.02,
        "adaptive_subtle": 0.015,
        "adaptive_strong": 0.03,
        "adaptive_minimal": 0.01,
        "perfect_subtle": 0.025,
        "ultra_subtle": 0.02,
        "near_perfect": 0.018,
    }
    strength = strength_map.get(mode, 0.02)
    return create_fast_moire_stripes(hidden_img, pattern_type, strength)

def create_high_frequency_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.015):
    """高周波モアレ縞模様（高速版）"""
    return create_fast_high_frequency_stripes(hidden_img, pattern_type, strength)

def create_moire_hidden_stripes(hidden_img, pattern_type="horizontal", strength=0.02):
    """基本モアレ縞模様（互換性維持）"""
    return create_fast_moire_stripes(hidden_img, pattern_type, strength)
