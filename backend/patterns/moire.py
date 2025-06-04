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
    超高周波モアレ縞模様：圧縮耐性・詳細強化版
    重ね合わせモード品質の圧縮耐性と4K時の鮮明な詳細表現を両立
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
    
    # 隠し画像のコントラスト強調（詳細強化）
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 4.0 + 0.5, 0, 1)  # より強力な強調
    
    # 多段階エッジ検出（詳細保持）
    edges_fine = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 20, 80)   # 細部検出
    edges_coarse = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 60, 160) # 主要構造
    edges_combined = np.maximum(edges_fine.astype(np.float32), edges_coarse.astype(np.float32) * 0.7) / 255.0
    
    # HEX色をRGB値に変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 1ピクセル縞パターン生成
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        stripe_pattern = (y_indices % 2)
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        stripe_pattern = (x_indices % 2)
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    
    # 明るい縞と暗い縞の領域を明確に分離
    light_regions = stripe_pattern == 1
    dark_regions = stripe_pattern == 0
    
    # 圧縮耐性のための中間グレー基準
    base_gray = 128
    compression_range = 30  # 圧縮耐性範囲
    
    # 詳細強化係数
    detail_strength = 1.2  # 4K詳細表現強化
    
    # 隠し画像詳細による強力な変調
    detail_modulation = (hidden_contrast - 0.5) * detail_strength * 90  # ±54の範囲
    
    # エッジ強調（詳細を際立たせる）
    edge_boost = edges_combined * 50  # 強力なエッジ強調
    
    # 最終調整
    final_adjustment = detail_modulation + edge_boost
    
    # 結果配列の初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # RGB各チャンネルの処理
    for i in range(3):
        # 明るい縞：中間グレー+オフセット、詳細で大幅変調
        light_base = base_gray + compression_range + hidden_contrast * 20  # 148-168
        light_final = light_base + final_adjustment
        light_values = np.clip(light_final, 100, 220) * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_values[light_regions]
        
        # 暗い縞：中間グレー-オフセット、詳細で大幅変調
        dark_base = base_gray - compression_range + hidden_contrast * 20  # 98-118
        dark_final = dark_base + final_adjustment
        dark_values = np.clip(dark_final, 35, 155) * (color1_rgb[i] / 255.0)
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
    モアレ効果を利用した隠し画像埋め込み（圧縮耐性・詳細強化版）
    重ね合わせモードと同等の圧縮耐性を持ちつつ、4K時に詳細を鮮明に表現
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
    
    # 正規化とコントラスト強調（詳細強化）
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 3.5 + 0.5, 0, 1)  # より強いコントラスト
    
    # 高精度エッジ検出（詳細保持）
    edges1 = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 30, 100)
    edges2 = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 60, 180)
    edges_combined = np.maximum(edges1.astype(np.float32), edges2.astype(np.float32) * 0.8) / 255.0
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 明確な1ピクセル縞パターンの生成
    if pattern_type == "horizontal":
        y_coords = np.arange(height).reshape(-1, 1)
        stripe_pattern = (y_coords % 2)
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    else:  # vertical
        x_coords = np.arange(width).reshape(1, -1)
        stripe_pattern = (x_coords % 2)
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 明確な領域分離
    dark_regions = stripe_pattern == 0
    light_regions = stripe_pattern == 1
    
    # 圧縮耐性のための明度範囲調整（重ね合わせモード準拠）
    # 基準値を中間グレーに近づけて圧縮耐性を向上
    base_gray = 128  # 中間グレー基準
    
    # 隠し画像詳細による強い変調（4K時の詳細表現）
    detail_intensity = 0.8  # 詳細強度
    detail_modulation = (hidden_contrast - 0.5) * detail_intensity * 80  # ±32の範囲
    
    # エッジ強調（詳細を際立たせる）
    edge_enhancement = edges_combined * 40  # エッジ部分を強調
    
    # 最終調整値
    final_adjustment = detail_modulation + edge_enhancement
    
    # RGB各チャンネルの処理（圧縮耐性重視）
    for i in range(3):
        # 暗い縞：基準グレーから少し暗く、詳細で大きく変調
        dark_base = base_gray - 25 + hidden_contrast * 15  # 88-118の範囲
        dark_final = dark_base + final_adjustment
        dark_values = np.clip(dark_final, 60, 140) * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_values[dark_regions]
        
        # 明るい縞：基準グレーから少し明るく、詳細で大きく変調
        light_base = base_gray + 25 + hidden_contrast * 15  # 138-168の範囲
        light_final = light_base + final_adjustment
        light_values = np.clip(light_final, 115, 195) * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_values[light_regions]
    
    return result

def create_adaptive_moire_stripes(hidden_img, pattern_type="horizontal", mode="adaptive", color1="#000000", color2="#FFFFFF"):
    """
    適応型モアレ縞模様：圧縮耐性・詳細強化版
    モードに応じた最適化と重ね合わせモード品質の圧縮耐性を実現
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
    
    # 正規化とコントラスト強調（モード別最適化）
    hidden_norm = hidden_gray / 255.0
    contrast_multiplier = {
        "high_frequency": 3.5,
        "adaptive": 3.0,
        "adaptive_subtle": 2.5,
        "adaptive_strong": 4.0,
        "adaptive_minimal": 2.0,
        "perfect_subtle": 3.8,
        "ultra_subtle": 2.8,
        "near_perfect": 3.3,
        "color_preserving": 3.2,
        "hue_preserving": 2.7,
        "blended": 3.1
    }
    contrast_factor = contrast_multiplier.get(mode, 3.0)
    hidden_contrast = np.clip((hidden_norm - 0.5) * contrast_factor + 0.5, 0, 1)
    
    # 詳細強度マッピング（モード別）
    detail_strength_map = {
        "high_frequency": 1.3,
        "adaptive": 1.0,
        "adaptive_subtle": 0.7,
        "adaptive_strong": 1.5,
        "adaptive_minimal": 0.5,
        "perfect_subtle": 1.4,
        "ultra_subtle": 0.8,
        "near_perfect": 1.2,
        "color_preserving": 1.1,
        "hue_preserving": 0.9,
        "blended": 1.0
    }
    detail_strength = detail_strength_map.get(mode, 1.0)
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 明確な1ピクセル縞模様パターン
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        stripe_pattern = (y_indices % 2)
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        stripe_pattern = (x_indices % 2)
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    
    # 隠し画像影響の計算（適応的・圧縮耐性）
    base_gray = 128  # 圧縮耐性の基準
    adaptive_range = 32  # 適応範囲
    
    # 詳細変調（強化版）
    detail_modulation = (hidden_contrast - 0.5) * detail_strength * 75  # モード別強度
    
    # エッジ強調（適応的）
    edges = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 40, 140)
    edge_boost = (edges.astype(np.float32) / 255.0) * detail_strength * 35
    
    # 最終調整
    final_adjustment = detail_modulation + edge_boost
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 明確な領域分離
    light_regions = stripe_pattern == 1
    dark_regions = stripe_pattern == 0
    
    # RGB各チャンネルの処理（圧縮耐性重視）
    for i in range(3):
        # 明るい縞：基本値 + 適応調整
        light_base = base_gray + adaptive_range + hidden_contrast * 20  # 148-168
        light_final = light_base + final_adjustment
        light_values = np.clip(light_final, 100, 210) * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_values[light_regions]
        
        # 暗い縞：基本値 + 適応調整
        dark_base = base_gray - adaptive_range + hidden_contrast * 20  # 96-116
        dark_final = dark_base + final_adjustment
        dark_values = np.clip(dark_final, 45, 155) * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_values[dark_regions]
    
    return result

def create_perfect_moire_pattern(hidden_img, pattern_type="horizontal", color1="#000000", color2="#FFFFFF"):
    """
    完璧なモアレパターン：最高品質の圧縮耐性・詳細表現版
    重ね合わせモード品質の圧縮耐性と最高レベルの4K詳細表現
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
    hidden_contrast = np.clip((hidden_norm - 0.5) * 5.0 + 0.5, 0, 1)  # 最強コントラスト
    
    # 超高精度エッジ検出（3段階）
    edges_ultra_fine = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 10, 50)  # 極細部
    edges_fine = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 30, 100)       # 細部
    edges_structure = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 60, 180)  # 構造
    
    # エッジ統合（最高品質）
    edges_combined = (edges_ultra_fine.astype(np.float32) * 1.0 + 
                     edges_fine.astype(np.float32) * 0.8 + 
                     edges_structure.astype(np.float32) * 0.6) / 255.0
    edges_combined = np.clip(edges_combined, 0, 1)
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 明確な1ピクセル縞パターンの生成
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        stripe_base = (y_indices % 2)
        stripe_base = np.broadcast_to(stripe_base, (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        stripe_base = (x_indices % 2)
        stripe_base = np.broadcast_to(stripe_base, (height, width))
    
    # 明確な領域分離
    light_regions = stripe_base == 1
    dark_regions = stripe_base == 0
    
    # 圧縮耐性のための中間グレー基準（完璧版）
    base_gray = 128
    perfect_range = 35  # 完璧な圧縮耐性範囲
    
    # 最高品質詳細強化
    detail_strength = 1.5  # 最強詳細表現
    
    # 隠し画像詳細による超強力変調
    detail_modulation = (hidden_contrast - 0.5) * detail_strength * 110  # ±82.5の範囲
    
    # 超強力エッジ強調
    edge_boost = edges_combined * 70  # 最強エッジ強調
    
    # 最終調整
    final_adjustment = detail_modulation + edge_boost
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # RGB適用
    for i in range(3):
        # 明るい縞の完璧な処理
        light_base = base_gray + perfect_range + hidden_contrast * 25  # 153-178の範囲
        light_final = light_base + final_adjustment
        light_values = np.clip(light_final, 90, 240) * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_values[light_regions]
        
        # 暗い縞の完璧な処理
        dark_base = base_gray - perfect_range + hidden_contrast * 25  # 93-118の範囲
        dark_final = dark_base + final_adjustment
        dark_values = np.clip(dark_final, 15, 165) * (color1_rgb[i] / 255.0)
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
