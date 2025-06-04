# patterns/moire.py - 濃淡詳細表現版（ベクトル化対応）

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

def hex_to_rgb(hex_color):
    """HEX色をRGBタプルに変換"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_high_frequency_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.015, color1="#000000", color2="#FFFFFF"):
    """
    超高周波モアレ縞模様：明確な縞境界を保ちつつ隠し画像詳細を反映
    1ピクセル単位の明確な縞でモアレ効果を維持し、隠し画像の詳細を微細に調整
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
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.5 + 0.5, 0, 1)
    
    # エッジ検出（詳細保持のため）
    edges = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 80, 150)
    edges_norm = edges.astype(np.float32) / 255.0
    
    # HEX色をRGB値に変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 基本縞パターン生成（1ピクセル単位の明確な境界）
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        stripe_pattern = (y_indices % 2)  # 0または1の明確な区別
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        stripe_pattern = (x_indices % 2)  # 0または1の明確な区別
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    
    # 明るい縞と暗い縞の領域を明確に分離
    light_regions = stripe_pattern == 1
    dark_regions = stripe_pattern == 0
    
    # 隠し画像詳細による微調整（基本縞構造を保ちつつ）
    detail_adjustment = (hidden_contrast - 0.5) * strength * 120  # -30〜+30の範囲
    edge_boost = edges_norm * 20  # エッジ部分の強調
    
    # 結果配列の初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # RGB各チャンネルの処理
    for i in range(3):
        # 明るい縞：基準値 + 隠し画像詳細調整
        light_base = 200 + hidden_contrast * 40  # 200-240の範囲
        light_final = light_base + detail_adjustment + edge_boost
        light_values = np.clip(light_final, 180, 255) * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_values[light_regions]
        
        # 暗い縞：基準値 + 隠し画像詳細調整
        dark_base = 15 + hidden_contrast * 40  # 15-55の範囲
        dark_final = dark_base + detail_adjustment + edge_boost
        dark_values = np.clip(dark_final, 0, 75) * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_values[dark_regions]
    
    return result

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
    モアレ効果を利用した隠し画像埋め込み（明確な縞境界保持版・ベクトル化対応）
    1ピクセル単位の明確な縞でモアレ効果を維持し、隠し画像詳細を微調整で反映
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
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.0 + 0.5, 0, 1)
    
    # エッジ検出（詳細情報取得）
    edges = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 80, 200)
    edges_norm = edges.astype(np.float32) / 255.0
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 明確な1ピクセル縞パターンの生成
    if pattern_type == "horizontal":
        y_coords = np.arange(height).reshape(-1, 1)
        stripe_pattern = (y_coords % 2)  # 0または1の明確な境界
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    else:  # vertical
        x_coords = np.arange(width).reshape(1, -1)
        stripe_pattern = (x_coords % 2)  # 0または1の明確な境界
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 明確な領域分離
    dark_regions = stripe_pattern == 0
    light_regions = stripe_pattern == 1
    
    # 隠し画像詳細による微調整計算
    detail_modulation = (hidden_contrast - 0.5) * strength * 100  # 基本調整
    edge_enhancement = edges_norm * 15  # エッジ強調
    final_adjustment = detail_modulation + edge_enhancement
    
    # RGB各チャンネルの詳細処理
    for i in range(3):
        # 暗い縞：基本的に暗く、隠し画像の詳細で微調整
        dark_base = 20 + hidden_contrast * 35  # 20-55の範囲
        dark_adjusted = dark_base + final_adjustment
        dark_final = np.clip(dark_adjusted, 0, 80) * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_final[dark_regions]
        
        # 明るい縞：基本的に明るく、隠し画像の詳細で微調整
        light_base = 200 + hidden_contrast * 35  # 200-235の範囲
        light_adjusted = light_base + final_adjustment
        light_final = np.clip(light_adjusted, 175, 255) * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_final[light_regions]
    
    return result

def create_adaptive_moire_stripes(hidden_img, pattern_type="horizontal", mode="adaptive", color1="#000000", color2="#FFFFFF"):
    """
    適応型モアレ縞模様：明確な縞境界保持版（ベクトル化対応）
    隠し画像の内容に応じて適応的に詳細を調整しつつ、明確な縞でモアレ効果を維持
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
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.0 + 0.5, 0, 1)
    
    # 強度レベル（モードに応じた調整）
    strength_map = {
        "high_frequency": 0.025,
        "adaptive": 0.030,
        "adaptive_subtle": 0.020,
        "adaptive_strong": 0.040,
        "adaptive_minimal": 0.015,
        "perfect_subtle": 0.035,
        "ultra_subtle": 0.025,
        "near_perfect": 0.028,
        "color_preserving": 0.032,
        "hue_preserving": 0.025,
        "blended": 0.028
    }
    
    strength = strength_map.get(mode, 0.030)
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 明確な1ピクセル縞模様パターン
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        stripe_pattern = (y_indices % 2)  # 0または1の明確な境界
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        stripe_pattern = (x_indices % 2)  # 0または1の明確な境界
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    
    # 隠し画像影響の計算
    hidden_influence = (hidden_contrast - 0.5) * strength * 80  # 微調整範囲
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 明確な領域分離
    light_regions = stripe_pattern == 1
    dark_regions = stripe_pattern == 0
    
    # RGB各チャンネルの処理
    for i in range(3):
        # 明るい縞：基本値 + 適応調整
        light_base = 205 + hidden_contrast * 30  # 205-235の範囲
        light_final = light_base + hidden_influence
        light_values = np.clip(light_final, 180, 255) * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_values[light_regions]
        
        # 暗い縞：基本値 + 適応調整
        dark_base = 15 + hidden_contrast * 40  # 15-55の範囲
        dark_final = dark_base + hidden_influence
        dark_values = np.clip(dark_final, 0, 75) * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_values[dark_regions]
    
    return result

def create_perfect_moire_pattern(hidden_img, pattern_type="horizontal", color1="#000000", color2="#FFFFFF"):
    """
    完璧なモアレパターン：明確な縞境界保持版（ベクトル化対応）
    最高品質の隠し画像詳細表現を実現しつつ、明確な縞でモアレ効果を保持
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
    hidden_contrast = np.clip((hidden_norm - 0.5) * 3.0 + 0.5, 0, 1)
    
    # 高精度エッジ検出
    edges = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 50, 150)
    edges_norm = edges.astype(np.float32) / 255.0
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 強度設定
    strength = 0.04
    
    # 明確な1ピクセル縞パターンの生成
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        stripe_base = (y_indices % 2)  # 0または1の明確な境界
        stripe_base = np.broadcast_to(stripe_base, (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        stripe_base = (x_indices % 2)  # 0または1の明確な境界
        stripe_base = np.broadcast_to(stripe_base, (height, width))
    
    # 明確な領域分離
    light_regions = stripe_base == 1
    dark_regions = stripe_base == 0
    
    # 隠し画像詳細による微調整
    detail_adjustment = (hidden_contrast - 0.5) * strength * 150  # 基本調整
    edge_boost = edges_norm * 25  # エッジ強調
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # RGB適用
    for i in range(3):
        # 明るい縞の処理（基本的に明るく、詳細で微調整）
        light_base = 210 + hidden_contrast * 30  # 210-240の範囲
        light_final = light_base + detail_adjustment + edge_boost
        light_values = np.clip(light_final, 185, 255) * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_values[light_regions]
        
        # 暗い縞の処理（基本的に暗く、詳細で微調整）
        dark_base = 10 + hidden_contrast * 45  # 10-55の範囲
        dark_final = dark_base + detail_adjustment + edge_boost
        dark_values = np.clip(dark_final, 0, 70) * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_values[dark_regions]
    
    return result

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
