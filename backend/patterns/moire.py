# patterns/moire.py - 修正版（自然な濃淡表現）

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

def hex_to_rgb(hex_color):
    """HEX色をRGBタプルに変換"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_high_freq_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.015, color1="#000000", color2="#FFFFFF"):
    """
    超高周波モアレ縞模様：自然な濃淡表現版（修正版）
    """
    if isinstance(hidden_img, np.ndarray):
        hidden_array = hidden_img.astype(np.float32)
    else:
        hidden_array = np.array(hidden_img).astype(np.float32)
    
    height, width = hidden_array.shape[:2]
    
    # グレースケール変換
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        hidden_gray = hidden_array
    
    # 隠し画像の正規化と軽いコントラスト強調
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 1.8 + 0.5, 0, 1)
    
    # エッジ検出（適度な設定）
    edges = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 60, 120)
    edges_norm = edges.astype(np.float32) / 255.0
    
    # HEX色をRGB値に変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 高周波パターンの生成
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        base_stripes = (y_indices * 2) % 2  # 高周波数化
        stripe_pattern = np.broadcast_to(base_stripes.astype(np.float32), (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        base_stripes = (x_indices * 2) % 2  # 高周波数化
        stripe_pattern = np.broadcast_to(base_stripes.astype(np.float32), (height, width))
    
    # 結果配列の初期化
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # 明るい縞と暗い縞の領域
    light_regions = stripe_pattern == 1.0
    dark_regions = stripe_pattern == 0.0
    
    # 基準明度値（適切な中間調）
    dark_base = 85    # 暗い縞の基準値
    light_base = 170  # 明るい縞の基準値
    
    # 隠し画像に基づく明度調整（シンプル化）
    brightness_adjustment = (hidden_contrast - 0.5) * strength * 300
    
    # エッジ強調（適度な強調）
    edge_multiplier = 1.0 + edges_norm * 1.2
    final_adjustment = brightness_adjustment * edge_multiplier
    
    # RGB各チャンネルの処理
    for i in range(3):
        # 明るい縞の処理
        light_brightness = light_base + hidden_contrast * 30  # 明度の基本範囲
        light_final = light_brightness + final_adjustment
        light_color = light_final * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_color[light_regions]
        
        # 暗い縞の処理
        dark_brightness = dark_base + hidden_contrast * 25   # 明度の基本範囲
        dark_final = dark_brightness + final_adjustment
        dark_color = dark_final * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_color[dark_regions]
    
    # 値のクリッピング（自然な範囲）
    result = np.clip(result, 45, 210)
    
    return result.astype(np.uint8)

def create_moire_hidden_stripes(hidden_img, pattern_type="horizontal", strength=0.02, color1="#000000", color2="#FFFFFF"):
    """
    モアレ効果を利用した隠し画像埋め込み（修正版・自然な濃淡表現）
    """
    if isinstance(hidden_img, np.ndarray):
        hidden_array = hidden_img.astype(np.float32)
    else:
        hidden_array = np.array(hidden_img).astype(np.float32)
    
    height, width = hidden_array.shape[:2]
    
    # グレースケール変換
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        hidden_gray = hidden_array
    
    # 正規化と適度なコントラスト強調
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 1.6 + 0.5, 0, 1)
    
    # エッジ検出（2段階）
    edges1 = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 40, 100)
    edges2 = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 70, 140)
    edges_combined = np.maximum(edges1.astype(np.float32), edges2.astype(np.float32) * 0.7) / 255.0
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 縞パターンの生成
    if pattern_type == "horizontal":
        y_coords = np.arange(height).reshape(-1, 1)
        stripe_pattern = np.broadcast_to((y_coords % 2), (height, width))
    else:  # vertical
        x_coords = np.arange(width).reshape(1, -1)
        stripe_pattern = np.broadcast_to((x_coords % 2), (height, width))
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # 基準明度値の範囲設定
    dark_base_range = [75, 105]   # 暗い縞の範囲
    light_base_range = [150, 190] # 明るい縞の範囲
    
    # 明度調整の計算（隠し画像の詳細を適度に反映）
    pixel_brightness = 0.5 + hidden_contrast * 0.5  # 0.5-1.0の範囲
    
    # エッジ強調（適度な設定）
    edge_enhancement = 1.0 + edges_combined * 0.8
    enhanced_brightness = pixel_brightness * edge_enhancement
    
    # 詳細変調（隠し画像の詳細を反映）
    detail_modulation = (hidden_contrast - 0.5) * strength * 150
    
    # 暗い縞と明るい縞の処理
    dark_regions = stripe_pattern == 0
    light_regions = stripe_pattern == 1
    
    # RGB各チャンネルの詳細処理
    for i in range(3):
        # 暗い縞の詳細処理
        dark_base = dark_base_range[0] + (dark_base_range[1] - dark_base_range[0]) * hidden_contrast
        dark_adjusted = dark_base * enhanced_brightness + detail_modulation
        dark_final = dark_adjusted * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_final[dark_regions]
        
        # 明るい縞の詳細処理
        light_base = light_base_range[0] + (light_base_range[1] - light_base_range[0]) * hidden_contrast
        light_adjusted = light_base * enhanced_brightness + detail_modulation
        light_final = light_adjusted * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_final[light_regions]
    
    # 適切な範囲にクリッピング（自然な濃淡保持）
    result = np.clip(result, 50, 200)
    
    return result.astype(np.uint8)

def create_adaptive_moire_stripes(hidden_img, pattern_type="horizontal", mode="adaptive", color1="#000000", color2="#FFFFFF"):
    """
    適応型モアレ縞模様：自然な濃淡表現版（修正版）
    """
    if isinstance(hidden_img, np.ndarray):
        hidden_array = hidden_img.astype(np.float32)
    else:
        hidden_array = np.array(hidden_img).astype(np.float32)
    
    height, width = hidden_array.shape[:2]
    
    # グレースケール変換
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        hidden_gray = hidden_array
    
    # 正規化と適度なコントラスト強調
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 1.4 + 0.5, 0, 1)
    
    # 強度レベル（モードに応じた調整・簡略化）
    strength_map = {
        "high_freq": 0.025,
        "adaptive": 0.030,
        "adaptive_subtle": 0.020,
        "adaptive_strong": 0.035,
        "adaptive_minimal": 0.015,
        "perfect_subtle": 0.032,
        "ultra_subtle": 0.022,
        "near_perfect": 0.028,
        "color_preserving": 0.030,
        "hue_preserving": 0.025,
        "blended": 0.028
    }
    
    strength = strength_map.get(mode, 0.030)
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 縞模様パターン（シンプル化）
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        stripe_pattern = np.broadcast_to((y_indices % 2), (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        stripe_pattern = np.broadcast_to((x_indices % 2), (height, width))
    
    # 隠し画像影響の計算
    hidden_influence = hidden_contrast * strength
    
    # 適応的な明度調整
    adaptive_brightness = 0.6 + hidden_contrast * 0.4
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # 明るい縞と暗い縞の領域
    light_regions = stripe_pattern == 1
    dark_regions = stripe_pattern == 0
    
    # 基準値（適応的に調整・自然な濃淡表現）
    light_base = 160 + hidden_contrast * 30  # 160-190の範囲
    dark_base = 80 + hidden_contrast * 25    # 80-105の範囲
    
    # RGB各チャンネルの処理
    for i in range(3):
        # 明るい縞の適応調整
        light_adjustment = hidden_influence * 50
        light_final = (light_base + light_adjustment) * adaptive_brightness * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_final[light_regions]
        
        # 暗い縞の適応調整
        dark_adjustment = hidden_influence * 40
        dark_final = (dark_base + dark_adjustment) * adaptive_brightness * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_final[dark_regions]
    
    # クリッピング（自然な濃淡保持）
    result = np.clip(result, 55, 185)
    
    return result.astype(np.uint8)

def create_perfect_moire_pattern(hidden_img, pattern_type="horizontal", color1="#000000", color2="#FFFFFF"):
    """
    完璧なモアレパターン：自然な濃淡表現版（修正版）
    """
    if isinstance(hidden_img, np.ndarray):
        hidden_array = hidden_img.astype(np.float32)
    else:
        hidden_array = np.array(hidden_img).astype(np.float32)
    
    height, width = hidden_array.shape[:2]
    
    # グレースケール化
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        hidden_gray = hidden_array
    
    # 前処理（高品質だが自然）
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.0 + 0.5, 0, 1)
    
    # 高精度エッジ検出
    edges = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 30, 100)
    edges_norm = edges.astype(np.float32) / 255.0
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 強度設定（適度な影響）
    strength = 0.04
    
    # 縞パターンの生成
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        stripe_base = np.broadcast_to((y_indices % 2), (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        stripe_base = np.broadcast_to((x_indices % 2), (height, width))
    
    # 自然な濃淡調整
    light_regions = stripe_base == 1
    dark_regions = stripe_base == 0
    
    # 高品質な明度計算
    perfect_brightness = 0.6 + hidden_contrast * 0.4
    edge_boost = 1.0 + edges_norm * 1.0
    final_brightness = perfect_brightness * edge_boost
    
    # 詳細変調
    detail_mod = (hidden_contrast - 0.5) * strength * 200
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # 明るい縞の完璧な処理（自然な濃淡表現）
    light_base_value = 165 + hidden_contrast * 25  # 165-190
    light_final = (light_base_value * final_brightness + detail_mod)
    
    # 暗い縞の完璧な処理（自然な濃淡表現）
    dark_base_value = 75 + hidden_contrast * 30    # 75-105
    dark_final = (dark_base_value * final_brightness + detail_mod)
    
    # RGB適用
    for i in range(3):
        result[light_regions, i] = light_final[light_regions] * (color2_rgb[i] / 255.0)
        result[dark_regions, i] = dark_final[dark_regions] * (color1_rgb[i] / 255.0)
    
    # 最終クリッピング（自然な濃淡保持）
    result = np.clip(result, 60, 180)
    
    return result.astype(np.uint8)

# 高速化による超高速パターン生成関数
def create_vectorized_stripe_pattern(height, width, pattern_type="horizontal", frequency=1):
    """
    完全ベクトル化による縞パターン生成
    """
    if pattern_type == "horizontal":
        # 行インデックス配列（メモリ効率的）
        indices = np.arange(height).reshape(-1, 1) * frequency
        pattern = (indices % 2).astype(np.float32)
        return np.broadcast_to(pattern, (height, width))
    else:  # vertical
        # 列インデックス配列（メモリ効率的）
        indices = np.arange(width).reshape(1, -1) * frequency
        pattern = (indices % 2).astype(np.float32)
        return np.broadcast_to(pattern, (height, width))

# エイリアス関数（互換性維持）
def create_fast_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.02):
    """基本モアレ縞模様（ベクトル化版）"""
    return create_moire_hidden_stripes(hidden_img, pattern_type, strength)

def create_fast_high_freq_stripes(hidden_img, pattern_type="horizontal", strength=0.015):
    """高周波モアレ縞模様（ベクトル化版）"""
    return create_high_freq_moire_stripes(hidden_img, pattern_type, strength)
