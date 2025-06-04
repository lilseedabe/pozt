# patterns/moire.py - 濃淡詳細表現版（デフォルト適用）

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

def hex_to_rgb(hex_color):
    """HEX色をRGBタプルに変換"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_high_frequency_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.015, color1="#000000", color2="#FFFFFF"):
    """
    超高周波モアレ縞模様：濃淡詳細表現版（デフォルト適用）
    隠し画像の詳細を縞模様の濃淡として表現
    """
    if isinstance(hidden_img, np.ndarray):
        hidden_array = hidden_img.astype(np.float32)
    else:
        hidden_array = np.array(hidden_img).astype(np.float32)
    
    height, width = hidden_array.shape[:2]
    
    # カラー画像をグレースケールに変換
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        hidden_gray = hidden_array
    
    # 隠し画像のコントラスト強調
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 3.0 + 0.5, 0, 1)
    
    # エッジ検出（詳細保持のため）
    edges = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 80, 150)
    edges_norm = edges.astype(np.float32) / 255.0
    
    # HEX色をRGB値に変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 高周波数パターンの生成（詳細を保持）
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
    
    # 隠し画像に基づく詳細な明度調整
    brightness_adjustment = (hidden_contrast - 0.5) * strength * 400.0
    
    # エッジ強調（詳細保持）
    edge_multiplier = 1.0 + edges_norm * 2.0
    final_adjustment = brightness_adjustment * edge_multiplier
    
    # 基準明度の計算（隠し画像の内容に基づく濃淡表現）
    base_brightness_dark = 70 + hidden_contrast * 50   # 70-120の範囲
    base_brightness_light = 150 + hidden_contrast * 70  # 150-220の範囲
    
    # RGB各チャンネルの処理
    for i in range(3):
        # 明るい縞の処理（color2ベース + 濃淡）
        light_base = base_brightness_light * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_base[light_regions] + final_adjustment[light_regions]
        
        # 暗い縞の処理（color1ベース + 濃淡）
        dark_base = base_brightness_dark * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_base[dark_regions] + final_adjustment[dark_regions]
    
    # 値のクリッピング（濃淡を保持）
    result = np.clip(result, 30, 225)  # 完全な黒白を避けて濃淡を保持
    

# ベクトル化による超高速パターン生成関数
def create_vectorized_stripe_pattern(height, width, pattern_type="horizontal", frequency=1):
    """
    完全ベクトル化による縞パターン生成
    従来のループ処理を完全排除し、メモリ効率と速度を両立
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

# 既存関数のエイリアス（互換性維持）
def create_fast_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.02):
    """基本モアレ縞模様（ベクトル化版）"""
    return create_moire_hidden_stripes(hidden_img, pattern_type, strength)

def create_fast_high_frequency_stripes(hidden_img, pattern_type="horizontal", strength=0.015):
    """高周波モアレ縞模様（ベクトル化版）"""
    return create_high_frequency_moire_stripes(hidden_img, pattern_type, strength)

def create_moire_hidden_stripes(hidden_img, pattern_type="horizontal", strength=0.02, color1="#000000", color2="#FFFFFF"):
    """
    モアレ効果を利用した隠し画像埋め込み（濃淡詳細表現版・デフォルト適用）
    隠し画像の詳細情報を縞模様の濃淡として表現
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
    
    # 正規化とコントラスト強調
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.5 + 0.5, 0, 1)
    
    # 複数レベルのエッジ検出
    edges1 = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 50, 120)
    edges2 = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 80, 200)
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
    
    # 明度調整の計算（隠し画像の詳細を詳細に反映）
    pixel_brightness = 0.3 + hidden_contrast * 0.7  # 0.3-1.0の範囲
    
    # エッジ強調（詳細を鮮明に）
    edge_enhancement = 1.0 + edges_combined * 1.5
    enhanced_brightness = pixel_brightness * edge_enhancement
    
    # 細かい濃淡調整（隠し画像の詳細を反映）
    detail_modulation = (hidden_contrast - 0.5) * strength * 200
    
    # 暗い縞と明るい縞の処理
    dark_regions = stripe_pattern == 0
    light_regions = stripe_pattern == 1
    
    # 基準値（隠し画像に応じて可変・濃淡表現）
    dark_base_range = [50, 110]   # 暗い縞の範囲
    light_base_range = [145, 205] # 明るい縞の範囲
    
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
    
    # 適切な範囲にクリッピング（濃淡保持）
    result = np.clip(result, 25, 230)
    
    return result.astype(np.uint8)

def create_adaptive_moire_stripes(hidden_img, pattern_type="horizontal", mode="adaptive", color1="#000000", color2="#FFFFFF"):
    """
    適応型モアレ縞模様：濃淡詳細表現版（デフォルト適用）
    隠し画像の内容に応じて適応的に濃淡を調整
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
    
    # 正規化とコントラスト強調
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.2 + 0.5, 0, 1)
    
    # 強度マッピング（モードに応じた調整）
    strength_map = {
        "high_frequency": 0.035,
        "adaptive": 0.040,
        "adaptive_subtle": 0.025,
        "adaptive_strong": 0.050,
        "adaptive_minimal": 0.020,
        "perfect_subtle": 0.045,
        "ultra_subtle": 0.030,
        "near_perfect": 0.038,
        "color_preserving": 0.042,
        "hue_preserving": 0.030,
        "blended": 0.038
    }
    
    strength = strength_map.get(mode, 0.040)
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 適応的縞模様パターン
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        # 隠し画像の内容に基づく適応的周波数
        frequency_mod = 1.0 + hidden_contrast * 0.3
        stripe_pattern = np.sin(y_indices * frequency_mod * 1.5) > 0
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        frequency_mod = 1.0 + hidden_contrast * 0.3
        stripe_pattern = np.sin(x_indices * frequency_mod * 1.5) > 0
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    
    # 隠し画像影響の計算
    hidden_influence = hidden_contrast * strength
    
    # 適応的明度調整（濃淡表現）
    adaptive_brightness = 0.4 + hidden_contrast * 0.6
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # 明るい縞と暗い縞の領域
    light_regions = stripe_pattern
    dark_regions = ~stripe_pattern
    
    # 基準値（適応的に調整・濃淡表現）
    light_base = 160 + hidden_contrast * 60   # 160-220の範囲
    dark_base = 60 + hidden_contrast * 50     # 60-110の範囲
    
    # RGB各チャンネルの処理
    for i in range(3):
        # 明るい縞の適応的調整
        light_adjustment = hidden_influence * 80
        light_final = (light_base + light_adjustment) * adaptive_brightness * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_final[light_regions]
        
        # 暗い縞の適応的調整
        dark_adjustment = hidden_influence * 60
        dark_final = (dark_base + dark_adjustment) * adaptive_brightness * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_final[dark_regions]
    
    # クリッピング（濃淡保持）
    result = np.clip(result, 35, 220)
    
    return result.astype(np.uint8)

def create_perfect_moire_pattern(hidden_img, pattern_type="horizontal", color1="#000000", color2="#FFFFFF"):
    """
    完璧なモアレパターン：濃淡詳細表現版（デフォルト適用）
    最高品質の隠し画像詳細表現を実現
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
    
    # 前処理（最高品質）
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 4.0 + 0.5, 0, 1)
    
    # 高精度エッジ検出
    edges = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 40, 140)
    edges_norm = edges.astype(np.float32) / 255.0
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 強度設定
    strength = 0.06  # より強い影響
    
    # 縞パターンの生成
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        stripe_base = np.broadcast_to((y_indices % 2), (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        stripe_base = np.broadcast_to((x_indices % 2), (height, width))
    
    # 完璧な濃淡調整
    light_regions = stripe_base == 1
    dark_regions = stripe_base == 0
    
    # 高度な明度計算
    perfect_brightness = 0.3 + hidden_contrast * 0.7
    edge_boost = 1.0 + edges_norm * 2.5
    final_brightness = perfect_brightness * edge_boost
    
    # 詳細modulation
    detail_mod = (hidden_contrast - 0.5) * strength * 300
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # 明るい縞の完璧な処理（濃淡表現）
    light_base_value = 170 + hidden_contrast * 50  # 170-220
    light_final = (light_base_value * final_brightness + detail_mod)
    
    # 暗い縞の完璧な処理（濃淡表現）
    dark_base_value = 45 + hidden_contrast * 65   # 45-110
    dark_final = (dark_base_value * final_brightness + detail_mod)
    
    # RGB適用
    for i in range(3):
        result[light_regions, i] = light_final[light_regions] * (color2_rgb[i] / 255.0)
        result[dark_regions, i] = dark_final[dark_regions] * (color1_rgb[i] / 255.0)
    
    # 最終クリッピング（濃淡保持）
    result = np.clip(result, 20, 235)
    
    return result.astype(np.uint8)

# ベクトル化による超高速パターン生成関数
def create_vectorized_stripe_pattern(height, width, pattern_type="horizontal", frequency=1):
    """
    完全ベクトル化による縞パターン生成
    従来のループ処理を完全排除し、メモリ効率と速度を両立
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

# 既存関数のエイリアス（互換性維持）
def create_fast_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.02):
    """基本モアレ縞模様（ベクトル化版）"""
    return create_moire_hidden_stripes(hidden_img, pattern_type, strength)

def create_fast_high_frequency_stripes(hidden_img, pattern_type="horizontal", strength=0.015):
    """高周波モアレ縞模様（ベクトル化版）"""
    return create_high_frequency_moire_stripes(hidden_img, pattern_type, strength)
