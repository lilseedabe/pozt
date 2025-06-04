"""
基本的なパターン生成機能（濃淡詳細表現対応版）
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
    """基本的な縞模様を生成（カラー対応）"""
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # HEX色をRGBに変換
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

def create_gradation_stripe_base(hidden_img, pattern_type="horizontal", color1="#000000", color2="#ffffff", detail_strength=0.8):
    """
    隠し画像の詳細を濃淡として表現する縞模様を生成
    detail_strength: 隠し画像の詳細をどの程度反映するか (0.0-1.0)
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
    
    # エッジ強調で詳細を保持
    edges = cv2.Canny(hidden_gray.astype(np.uint8), 50, 150).astype(np.float32) / 255.0
    
    # 結果配列を初期化
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    if pattern_type == "horizontal":
        # 横縞パターン（濃淡付き）
        for y in range(height):
            # 基本の縞パターン（0または1）
            stripe_base = y % 2
            
            # 隠し画像の値を基に濃淡を計算
            for x in range(width):
                hidden_value = hidden_norm[y, x]
                edge_value = edges[y, x]
                
                # 基本色を選択
                if stripe_base == 0:
                    base_color = np.array(rgb1, dtype=np.float32)
                else:
                    base_color = np.array(rgb2, dtype=np.float32)
                
                # 隠し画像の値に基づいて明度を調整
                # hidden_valueが高い（明るい）ほど明るく、低いほど暗く
                brightness_factor = 0.3 + hidden_value * 0.7  # 0.3-1.0の範囲
                
                # エッジ部分はさらにコントラストを強調
                if edge_value > 0.5:
                    brightness_factor = brightness_factor * (1.0 + detail_strength * 0.5)
                
                # 細かい濃淡調整
                detail_adjustment = (hidden_value - 0.5) * detail_strength * 50  # -25 to +25
                
                # 最終的な色を計算
                final_color = base_color * brightness_factor + detail_adjustment
                result[y, x] = final_color
                
    else:  # vertical
        # 縦縞パターン（濃淡付き）
        for x in range(width):
            # 基本の縞パターン（0または1）
            stripe_base = x % 2
            
            # 隠し画像の値を基に濃淡を計算
            for y in range(height):
                hidden_value = hidden_norm[y, x]
                edge_value = edges[y, x]
                
                # 基本色を選択
                if stripe_base == 0:
                    base_color = np.array(rgb1, dtype=np.float32)
                else:
                    base_color = np.array(rgb2, dtype=np.float32)
                
                # 隠し画像の値に基づいて明度を調整
                brightness_factor = 0.3 + hidden_value * 0.7  # 0.3-1.0の範囲
                
                # エッジ部分はさらにコントラストを強調
                if edge_value > 0.5:
                    brightness_factor = brightness_factor * (1.0 + detail_strength * 0.5)
                
                # 細かい濃淡調整
                detail_adjustment = (hidden_value - 0.5) * detail_strength * 50  # -25 to +25
                
                # 最終的な色を計算
                final_color = base_color * brightness_factor + detail_adjustment
                result[y, x] = final_color
    
    # 値を0-255の範囲にクリップ
    result = np.clip(result, 0, 255)
    
    return result.astype(np.uint8)

def create_enhanced_gradation_stripe(hidden_img, pattern_type="horizontal", color1="#000000", color2="#ffffff", 
                                   detail_strength=0.8, contrast_boost=1.5):
    """
    より高度な濃淡表現の縞模様（コントラスト強化版）
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
    result = np.zeros((height, width, 3), dtype=np.float32)
    
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
    
    # 明度調整係数を計算
    brightness_factor = 0.2 + hidden_contrast * 0.8  # 0.2-1.0の範囲
    
    # エッジ強調係数
    edge_boost = 1.0 + edges_combined * detail_strength * 0.8
    brightness_factor = brightness_factor * edge_boost
    
    # 細かい濃淡調整
    detail_adjustment = (hidden_contrast - 0.5) * detail_strength * 60  # -30 to +30
    
    # RGB各チャンネルに適用
    for i in range(3):
        # 暗い縞の処理
        base_dark = rgb1[i]
        result[dark_regions, i] = base_dark * brightness_factor[dark_regions] + detail_adjustment[dark_regions]
        
        # 明るい縞の処理
        base_light = rgb2[i]
        result[light_regions, i] = base_light * brightness_factor[light_regions] + detail_adjustment[light_regions]
    
    # 値を0-255の範囲にクリップ
    result = np.clip(result, 0, 255)
    
    return result.astype(np.uint8)

def get_adaptive_strength(mode):
    """モードに応じた強度を取得"""
    return STRENGTH_MAP.get(mode, 0.02)
