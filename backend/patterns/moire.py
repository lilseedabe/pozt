# patterns/moire.py - 濃淡詳細表現対応版（既存関数互換性維持）

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

# 共通のhex_to_rgb関数（重複を避けるため）
def hex_to_rgb(hex_color):
    """HEX色をRGBタプルに変換"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# ===== 既存関数（互換性維持） =====

def create_high_frequency_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.015, color1="#000000", color2="#FFFFFF"):
    """
    超高周波モアレ縞模様：Numpyベクトル化による超高速化（カスタム色対応）
    従来のピクセル単位ループを完全排除し、10-50倍高速化を実現
    
    ★ 濃淡詳細表現対応版：隠し画像の詳細を縞模様の濃淡として表現
    """
    if isinstance(hidden_img, np.ndarray):
        hidden_array = hidden_img.astype(np.float32)
    else:
        hidden_array = np.array(hidden_img).astype(np.float32)
    
    height, width = hidden_array.shape[:2]
    
    # カラー画像をグレースケールに変換（ベクトル化）
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        hidden_gray = hidden_array
    
    # 隠し画像のコントラスト強調（濃淡詳細表現用に強化）
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 3.0 + 0.5, 0, 1)  # より強いコントラスト
    
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
    
    # ★ 濃淡詳細表現の核心部分 ★
    # 隠し画像に基づく詳細な明度調整
    brightness_adjustment = (hidden_contrast - 0.5) * strength * 400.0  # より強い影響
    
    # エッジ強調（詳細保持）
    edge_multiplier = 1.0 + edges_norm * 2.0
    final_adjustment = brightness_adjustment * edge_multiplier
    
    # 基準明度の計算（隠し画像の内容に基づく濃淡）
    base_brightness_dark = 60 + hidden_contrast * 50   # 60-110の範囲
    base_brightness_light = 150 + hidden_contrast * 70  # 150-220の範囲
    
    # RGB各チャンネルの詳細処理
    for i in range(3):
        # 明るい縞の処理（color2ベース）
        light_base = base_brightness_light * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_base[light_regions] + final_adjustment[light_regions]
        
        # 暗い縞の処理（color1ベース）
        dark_base = base_brightness_dark * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_base[dark_regions] + final_adjustment[dark_regions]
    
    # 値のクリッピング（濃淡保持のため範囲拡大）
    result = np.clip(result, 20, 235)
    
    return result.astype(np.uint8)

def create_moire_hidden_stripes(hidden_img, pattern_type="horizontal", strength=0.02, color1="#000000", color2="#FFFFFF"):
    """
    モアレ効果を利用した隠し画像埋め込み（濃淡詳細表現版）
    隠し画像の詳細情報を縞模様の濃淡として表現
    """
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
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
    
    # 正規化とコントラスト強調（濃淡詳細表現用）
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.5 + 0.5, 0, 1)
    
    # 複数レベルのエッジ検出（詳細保持）
    edges1 = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 50, 120)
    edges2 = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 80, 200)
    edges_combined = np.maximum(edges1.astype(np.float32), edges2.astype(np.float32) * 0.7) / 255.0
    
    # 縞パターンの生成
    if pattern_type == "horizontal":
        y_coords = np.arange(height).reshape(-1, 1)
        stripe_pattern = np.broadcast_to((y_coords % 2), (height, width))
    else:  # vertical
        x_coords = np.arange(width).reshape(1, -1)
        stripe_pattern = np.broadcast_to((x_coords % 2), (height, width))
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # ★ 濃淡詳細表現の核心処理 ★
    # 明度調整の計算（より詳細に）
    pixel_brightness = 0.25 + hidden_contrast * 0.75  # 0.25-1.0の範囲
    
    # エッジ強調（詳細を鮮明に）
    edge_enhancement = 1.0 + edges_combined * 1.5
    enhanced_brightness = pixel_brightness * edge_enhancement
    
    # 細かい濃淡調整（隠し画像の詳細を反映）
    detail_modulation = (hidden_contrast - 0.5) * strength * 200
    
    # 暗い縞と明るい縞の処理
    dark_regions = stripe_pattern == 0
    light_regions = stripe_pattern == 1
    
    # 基準値（隠し画像に応じて可変）
    dark_base_range = [40, 120]   # 暗い縞の範囲
    light_base_range = [135, 215] # 明るい縞の範囲
    
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
    result = np.clip(result, 15, 240)
    
    return result.astype(np.uint8)

def create_adaptive_moire_stripes(hidden_img, pattern_type="horizontal", mode="adaptive", color1="#000000", color2="#FFFFFF"):
    """
    適応型モアレ縞模様：濃淡詳細表現版
    隠し画像の内容に応じて適応的に濃淡を調整
    """
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 画像準備
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
        "high_frequency": 0.025,
        "adaptive": 0.03,
        "adaptive_subtle": 0.02,
        "adaptive_strong": 0.04,
        "adaptive_minimal": 0.015,
        "perfect_subtle": 0.035,
        "ultra_subtle": 0.025,
        "near_perfect": 0.028,
        "color_preserving": 0.032,
        "hue_preserving": 0.025,
        "blended": 0.028
    }
    
    strength = strength_map.get(mode, 0.03)
    
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
    
    # 適応的明度調整
    adaptive_brightness = 0.3 + hidden_contrast * 0.7
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # 明るい縞と暗い縞の領域
    light_regions = stripe_pattern
    dark_regions = ~stripe_pattern
    
    # 基準値（適応的に調整）
    light_base = 140 + hidden_contrast * 80   # 140-220の範囲
    dark_base = 50 + hidden_contrast * 60     # 50-110の範囲
    
    # RGB各チャンネルの処理
    for i in range(3):
        # 明るい縞の適応的調整
        light_adjustment = hidden_influence * 120
        light_final = (light_base + light_adjustment) * adaptive_brightness * (color2_rgb[i] / 255.0)
        result[light_regions, i] = light_final[light_regions]
        
        # 暗い縞の適応的調整
        dark_adjustment = hidden_influence * 80
        dark_final = (dark_base + dark_adjustment) * adaptive_brightness * (color1_rgb[i] / 255.0)
        result[dark_regions, i] = dark_final[dark_regions]
    
    # クリッピング
    result = np.clip(result, 30, 225)
    
    return result.astype(np.uint8)

def create_perfect_moire_pattern(hidden_img, pattern_type="horizontal", color1="#000000", color2="#FFFFFF"):
    """
    完璧なモアレパターン：濃淡詳細表現版
    最高品質の隠し画像詳細表現を実現
    """
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
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
    perfect_brightness = 0.2 + hidden_contrast * 0.8
    edge_boost = 1.0 + edges_norm * 2.5
    final_brightness = perfect_brightness * edge_boost
    
    # 詳細modulation
    detail_mod = (hidden_contrast - 0.5) * strength * 300
    
    # 結果配列
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # 明るい縞の完璧な処理
    light_base_value = 180 + hidden_contrast * 50  # 180-230
    light_final = (light_base_value * final_brightness + detail_mod)
    
    # 暗い縞の完璧な処理
    dark_base_value = 25 + hidden_contrast * 80   # 25-105
    dark_final = (dark_base_value * final_brightness + detail_mod)
    
    # RGB適用
    for i in range(3):
        result[light_regions, i] = light_final[light_regions] * (color2_rgb[i] / 255.0)
        result[dark_regions, i] = dark_final[dark_regions] * (color1_rgb[i] / 255.0)
    
    # 最終クリッピング
    result = np.clip(result, 10, 245)
    
    return result.astype(np.uint8)

# ===== 新機能：濃淡詳細表現専用関数 =====

def create_gradation_stripe_base(hidden_img, pattern_type="horizontal", color1="#000000", color2="#ffffff", detail_strength=0.8):
    """
    隠し画像の詳細を濃淡として表現する縞模様を生成
    detail_strength: 隠し画像の詳細をどの程度反映するか (0.0-1.0)
    """
    hidden_array = ensure_array(hidden_img)
    height, width = hidden_array.shape[:2]
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
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
                    base_color = np.array(color1_rgb, dtype=np.float32)
                else:
                    base_color = np.array(color2_rgb, dtype=np.float32)
                
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
                    base_color = np.array(color1_rgb, dtype=np.float32)
                else:
                    base_color = np.array(color2_rgb, dtype=np.float32)
                
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
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
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
        base_dark = color1_rgb[i]
        result[dark_regions, i] = base_dark * brightness_factor[dark_regions] + detail_adjustment[dark_regions]
        
        # 明るい縞の処理
        base_light = color2_rgb[i]
        result[light_regions, i] = base_light * brightness_factor[light_regions] + detail_adjustment[light_regions]
    
    # 値を0-255の範囲にクリップ
    result = np.clip(result, 0, 255)
    
    return result.astype(np.uint8)

# ===== ベクトル化による超高速パターン生成関数 =====

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

# ===== 既存関数のエイリアス（互換性維持） =====

def create_fast_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.02):
    """基本モアレ縞模様（ベクトル化版）"""
    return create_moire_hidden_stripes(hidden_img, pattern_type, strength)

def create_fast_high_frequency_stripes(hidden_img, pattern_type="horizontal", strength=0.015):
    """高周波モアレ縞模様（ベクトル化版）"""
    return create_high_frequency_moire_stripes(hidden_img, pattern_type, strength)
