# patterns/base.py - 修正版（自然な濃淡表現）

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale, enhance_contrast, detect_edges
from config.settings import STRENGTH_MAP

def hex_to_rgb(hex_color):
    """HEX色をRGBタプルに変換"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_stripe_base(height, width, pattern_type="horizontal", color1="#000000", color2="#ffffff"):
    """基本的な縞模様を生成（シンプル版）"""
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # HEX色をRGBに変換
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)
    
    if pattern_type == "horizontal":
        # 横縞パターン
        for y in range(height):
            if y % 2 == 0:
                # 暗い縞（color1ベース）
                for i in range(3):
                    result[y, :, i] = rgb1[i]
            else:
                # 明るい縞（color2ベース）
                for i in range(3):
                    result[y, :, i] = rgb2[i]
    else:  # vertical
        # 縦縞パターン
        for x in range(width):
            if x % 2 == 0:
                # 暗い縞（color1ベース）
                for i in range(3):
                    result[:, x, i] = rgb1[i]
            else:
                # 明るい縞（color2ベース）
                for i in range(3):
                    result[:, x, i] = rgb2[i]
    
    return result

def get_adaptive_strength(mode):
    """モードに応じた強度を取得"""
    return STRENGTH_MAP.get(mode, 0.02)

def create_gradation_stripe_base(hidden_img, pattern_type="horizontal", color1="#000000", color2="#ffffff", detail_strength=0.6):
    """
    隠し画像の詳細を自然な濃淡として表現する縞模様を生成（修正版）
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
    
    # 軽いコントラスト強調
    hidden_enhanced = np.clip((hidden_norm - 0.5) * 1.5 + 0.5, 0, 1)
    
    # エッジ検出（詳細保持）
    edges = cv2.Canny(hidden_gray.astype(np.uint8), 30, 100).astype(np.float32) / 255.0
    
    # 結果配列を初期化
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # 基準色値の設定（グレーの中間調を使用）
    dark_base = 80   # 暗い縞の基準値
    light_base = 175 # 明るい縞の基準値
    variation_range = 40  # 濃淡の変化幅
    
    if pattern_type == "horizontal":
        # 横縞パターン
        for y in range(height):
            stripe_base = y % 2  # 0 or 1
            
            for x in range(width):
                hidden_value = hidden_enhanced[y, x]
                edge_value = edges[y, x]
                
                # 基本色を選択
                if stripe_base == 0:
                    base_color = np.array(rgb1, dtype=np.float32)
                    target_brightness = dark_base
                else:
                    base_color = np.array(rgb2, dtype=np.float32)
                    target_brightness = light_base
                
                # 隠し画像の値に基づいて明度を調整
                brightness_variation = (hidden_value - 0.5) * variation_range
                
                # エッジ部分はコントラストを強調
                if edge_value > 0.3:
                    brightness_variation *= (1.0 + edge_value * detail_strength)
                
                # 最終的な明度を計算
                final_brightness = target_brightness + brightness_variation
                final_brightness = np.clip(final_brightness, 40, 215)
                
                # 色の正規化率を計算
                brightness_factor = final_brightness / 255.0
                
                # RGB各チャンネルに適用
                for i in range(3):
                    result[y, x, i] = base_color[i] * brightness_factor
                    
    else:  # vertical
        # 縦縞パターン
        for x in range(width):
            stripe_base = x % 2  # 0 or 1
            
            for y in range(height):
                hidden_value = hidden_enhanced[y, x]
                edge_value = edges[y, x]
                
                # 基本色を選択
                if stripe_base == 0:
                    base_color = np.array(rgb1, dtype=np.float32)
                    target_brightness = dark_base
                else:
                    base_color = np.array(rgb2, dtype=np.float32)
                    target_brightness = light_base
                
                # 隠し画像の値に基づいて明度を調整
                brightness_variation = (hidden_value - 0.5) * variation_range
                
                # エッジ部分はコントラストを強調
                if edge_value > 0.3:
                    brightness_variation *= (1.0 + edge_value * detail_strength)
                
                # 最終的な明度を計算
                final_brightness = target_brightness + brightness_variation
                final_brightness = np.clip(final_brightness, 40, 215)
                
                # 色の正規化率を計算
                brightness_factor = final_brightness / 255.0
                
                # RGB各チャンネルに適用
                for i in range(3):
                    result[y, x, i] = base_color[i] * brightness_factor
    
    # 値を0-255の範囲にクリップ
    result = np.clip(result, 0, 255)
    
    return result.astype(np.uint8)

def create_enhanced_gradation_stripe(hidden_img, pattern_type="horizontal", color1="#000000", color2="#ffffff",
                                   detail_strength=0.7, contrast_boost=1.2):
    """
    より高精度な濃淡表現の縞模様（修正版）
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
    
    # 隠し画像の正規化
    hidden_norm = hidden_gray / 255.0
    
    # 適度なコントラスト強調
    hidden_contrast = np.clip((hidden_norm - 0.5) * contrast_boost + 0.5, 0, 1)
    
    # マルチレベルエッジ検出
    edges1 = cv2.Canny(hidden_gray.astype(np.uint8), 50, 120).astype(np.float32) / 255.0
    edges2 = cv2.Canny(hidden_gray.astype(np.uint8), 80, 180).astype(np.float32) / 255.0
    edges_combined = np.maximum(edges1, edges2 * 0.8)
    
    # ベクトル化による高速処理
    if pattern_type == "horizontal":
        y_indices = np.arange(height).reshape(-1, 1)
        stripe_pattern = np.broadcast_to((y_indices % 2), (height, width))
    else:  # vertical
        x_indices = np.arange(width).reshape(1, -1)
        stripe_pattern = np.broadcast_to((x_indices % 2), (height, width))
    
    # 明るい縞と暗い縞の領域
    dark_regions = stripe_pattern == 0
    light_regions = stripe_pattern == 1
    
    # 明度調整係数を計算
    brightness_factor = 0.6 + hidden_contrast * 0.4  # 0.6-1.0の範囲
    
    # エッジ強調係数
    edge_boost = 1.0 + edges_combined * detail_strength * 0.6
    brightness_factor = brightness_factor * edge_boost
    
    # 詳細変調（隠し画像の細かな違いを反映）
    detail_adjustment = (hidden_contrast - 0.5) * detail_strength * 30  # -15 から +15
    
    # 基準明度値
    dark_base_value = 70 + hidden_contrast * 35   # 70-105
    light_base_value = 155 + hidden_contrast * 45 # 155-200
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # RGB各チャンネルの処理
    for i in range(3):
        # 暗い縞の処理
        dark_brightness = dark_base_value * brightness_factor + detail_adjustment
        dark_final = dark_brightness * (rgb1[i] / 255.0)
        result[dark_regions, i] = dark_final[dark_regions]
        
        # 明るい縞の処理
        light_brightness = light_base_value * brightness_factor + detail_adjustment
        light_final = light_brightness * (rgb2[i] / 255.0)
        result[light_regions, i] = light_final[light_regions]
    
    # 値を適切な範囲にクリップ
    result = np.clip(result, 30, 225)
    
    return result.astype(np.uint8)
