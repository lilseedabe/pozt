"""
基本的なパターン生成機能（濃淡詳細表現版）
"""
import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale, enhance_contrast, detect_edges
from config.settings import STRENGTH_MAP

def hex_to_rgb(hex_color):
    """HEX色をRGBタプルに変換"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_stripe_base(height, width, pattern_type="horizontal", color1="#000000", color2="#ffffff"):
    """基本的な縞模様を生成（明確な境界版）- モアレ効果のため1ピクセル単位の明確な縞"""
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # HEX色をRGBに変換
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    if pattern_type == "horizontal":
        # 横縞パターン（明確な境界）
        for y in range(height):
            if y % 2 == 0:
                # 暗い縞
                result[y, :] = rgb1
            else:
                # 明るい縞
                result[y, :] = rgb2
    else:  # vertical
        # 縦縞パターン（明確な境界）
        for x in range(width):
            if x % 2 == 0:
                # 暗い縞
                result[:, x] = rgb1
            else:
                # 明るい縞
                result[:, x] = rgb2
    
    return result

def get_adaptive_strength(mode):
    """モードに応じた強度を取得"""
    return STRENGTH_MAP.get(mode, 0.02)

def create_gradation_stripe_base(hidden_img, pattern_type="horizontal", color1="#000000", color2="#ffffff", detail_strength=0.8):
    """
    隠し画像の詳細を微調整として表現する明確な縞模様を生成
    明確な1ピクセル縞境界を保ちつつ、隠し画像詳細を微調整で反映
    """
    hidden_array = ensure_array(hidden_img)
    height, width = hidden_array.shape[:2]
    
    # HEX色をRGBに変換
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    # グレースケール変換
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        hidden_gray = hidden_array.astype(np.float32)
    
    # 隠し画像の正規化（0-1の範囲）
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.0 + 0.5, 0, 1)
    
    # 輪郭強調で詳細を保持
    edges = cv2.Canny(hidden_gray.astype(np.uint8), 50, 150).astype(np.float32) / 255.0
    
    # 結果配列を初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    if pattern_type == "horizontal":
        # 横縞パターン（明確な境界 + 微調整）
        for y in range(height):
            stripe_base = y % 2  # 0または1の明確な境界
            
            for x in range(width):
                hidden_value = hidden_contrast[y, x]
                edge_value = edges[y, x]
                
                # 基本色の選択（明確な境界）
                if stripe_base == 0:
                    base_color = np.array(rgb1, dtype=np.float32)
                    base_brightness = 25 + hidden_value * 30  # 25-55の範囲
                else:
                    base_color = np.array(rgb2, dtype=np.float32)
                    base_brightness = 200 + hidden_value * 35  # 200-235の範囲
                
                # エッジ部分の微調整
                edge_adjustment = edge_value * detail_strength * 15
                
                # 詳細微調整
                detail_adjustment = (hidden_value - 0.5) * detail_strength * 20
                
                # 最終的な明度
                final_brightness = base_brightness + detail_adjustment + edge_adjustment
                
                # RGB値に適用
                for i in range(3):
                    result[y, x, i] = np.clip(final_brightness * (base_color[i] / 255.0), 0, 255)
                
    else:  # vertical
        # 縦縞パターン（明確な境界 + 微調整）
        for x in range(width):
            stripe_base = x % 2  # 0または1の明確な境界
            
            for y in range(height):
                hidden_value = hidden_contrast[y, x]
                edge_value = edges[y, x]
                
                # 基本色の選択（明確な境界）
                if stripe_base == 0:
                    base_color = np.array(rgb1, dtype=np.float32)
                    base_brightness = 25 + hidden_value * 30  # 25-55の範囲
                else:
                    base_color = np.array(rgb2, dtype=np.float32)
                    base_brightness = 200 + hidden_value * 35  # 200-235の範囲
                
                # エッジ部分の微調整
                edge_adjustment = edge_value * detail_strength * 15
                
                # 詳細微調整
                detail_adjustment = (hidden_value - 0.5) * detail_strength * 20
                
                # 最終的な明度
                final_brightness = base_brightness + detail_adjustment + edge_adjustment
                
                # RGB値に適用
                for i in range(3):
                    result[y, x, i] = np.clip(final_brightness * (base_color[i] / 255.0), 0, 255)
    
    return result

def create_enhanced_gradation_stripe(hidden_img, pattern_type="horizontal", color1="#000000", color2="#ffffff",
                                   detail_strength=0.8, contrast_boost=1.5):
    """
    より高度な詳細表現の明確な縞模様（コントラスト強化版）
    明確な1ピクセル縞境界を保ちつつ、隠し画像詳細をより強く反映
    """
    hidden_array = ensure_array(hidden_img)
    height, width = hidden_array.shape[:2]
    
    # HEX色をRGBに変換
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    # グレースケール変換
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        hidden_gray = hidden_array.astype(np.float32)
    
    # 隠し画像の正規化（0-1の範囲）
    hidden_norm = hidden_gray / 255.0
    
    # コントラスト強化
    hidden_contrast = np.clip((hidden_norm - 0.5) * contrast_boost + 0.5, 0, 1)
    
    # エッジ検出（複数の手法を組み合わせ）
    edges1 = cv2.Canny(hidden_gray.astype(np.uint8), 50, 150).astype(np.float32) / 255.0
    edges2 = cv2.Canny(hidden_gray.astype(np.uint8), 80, 200).astype(np.float32) / 255.0
    edges_combined = np.maximum(edges1, edges2 * 0.7)
    
    # 結果配列を初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # ベクトル化による高速処理
    if pattern_type == "horizontal":
        # 横縞パターンをベクトル化
        y_indices = np.arange(height).reshape(-1, 1)
        stripe_pattern = np.broadcast_to((y_indices % 2), (height, width))
    else:  # vertical
        # 縦縞パターンをベクトル化
        x_indices = np.arange(width).reshape(1, -1)
        stripe_pattern = np.broadcast_to((x_indices % 2), (height, width))
    
    # 暗い縞と明るい縞の領域を分離
    dark_regions = stripe_pattern == 0
    light_regions = stripe_pattern == 1
    
    # エッジ強調係数
    edge_boost = edges_combined * detail_strength * 25
    
    # 細かい詳細調整
    detail_adjustment = (hidden_contrast - 0.5) * detail_strength * 40
    
    # RGB各チャンネルへの適用
    for i in range(3):
        # 暗い縞の処理（明確な基準値 + 微調整）
        dark_base = 20 + hidden_contrast * 35  # 20-55の範囲
        dark_final = dark_base + detail_adjustment + edge_boost
        dark_values = np.clip(dark_final, 0, 80) * (rgb1[i] / 255.0)
        result[dark_regions, i] = dark_values[dark_regions]
        
        # 明るい縞の処理（明確な基準値 + 微調整）
        light_base = 200 + hidden_contrast * 35  # 200-235の範囲
        light_final = light_base + detail_adjustment + edge_boost
        light_values = np.clip(light_final, 175, 255) * (rgb2[i] / 255.0)
        result[light_regions, i] = light_values[light_regions]
    
    return result

def get_adaptive_strength(mode):
    """モードに応じた強度を取得"""
    return STRENGTH_MAP.get(mode, 0.02)
