# patterns/overlay.py - 濃淡詳細表現版（デフォルト適用）

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

def hex_to_rgb(hex_color):
    """HEX色をRGBタプルに変換"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_overlay_moire_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.6, color1="#000000", color2="#FFFFFF"):
    """
    重ね合わせモード：濃淡詳細表現版（デフォルト適用）
    隠し画像の詳細を重ね合わせ効果で濃淡として表現
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
    
    # HEX色をRGBに変換
    color1_rgb = hex_to_rgb(color1)
    color2_rgb = hex_to_rgb(color2)
    
    # 隠し画像の正規化と強調
    hidden_norm = hidden_gray / 255.0
    hidden_enhanced = np.clip((hidden_norm - 0.5) * 1.8 + 0.5, 0, 1)
    
    # 複数レベルの二値化マスク生成
    _, binary_mask1 = cv2.threshold(hidden_gray, 100, 255, cv2.THRESH_BINARY_INV)
    _, binary_mask2 = cv2.threshold(hidden_gray, 140, 255, cv2.THRESH_BINARY_INV)
    
    # ガウシアンブラー（詳細保持のため軽い）
    blurred_mask1 = cv2.GaussianBlur(binary_mask1, (3, 3), 0)
    blurred_mask2 = cv2.GaussianBlur(binary_mask2, (7, 7), 0)
    
    # 複合マスクの生成
    composite_mask = (blurred_mask1.astype(np.float32) * 0.7 + blurred_mask2.astype(np.float32) * 0.3) / 255.0
    adaptive_mask = composite_mask * overlay_opacity
    
    # 縞模様パターンの生成（詳細を保持）
    if pattern_type == "horizontal":
        y_coords = np.arange(height, dtype=np.uint8).reshape(-1, 1)
        stripe_pattern = (y_coords % 2)
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    else:  # vertical
        x_coords = np.arange(width, dtype=np.uint8).reshape(1, -1)
        stripe_pattern = (x_coords % 2)
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    
    # 詳細な濃淡縞パターンの生成
    stripes = np.zeros((height, width, 3), dtype=np.float32)
    
    # 暗い縞と明るい縞の領域
    dark_regions = stripe_pattern == 0
    light_regions = stripe_pattern == 1
    
    # 隠し画像に基づく詳細な明度調整（濃淡表現）
    brightness_modulation = 0.5 + hidden_enhanced * 0.5  # 0.5-1.0の範囲
    
    # 暗い縞の詳細処理（濃淡表現）
    dark_base_values = 80 + hidden_enhanced * 40  # 80-120の範囲
    for i in range(3):
        dark_value = dark_base_values * brightness_modulation * (color1_rgb[i] / 255.0)
        stripes[dark_regions, i] = dark_value[dark_regions]
    
    # 明るい縞の詳細処理（濃淡表現）
    light_base_values = 170 + hidden_enhanced * 35  # 170-205の範囲
    for i in range(3):
        light_value = light_base_values * brightness_modulation * (color2_rgb[i] / 255.0)
        stripes[light_regions, i] = light_value[light_regions]
    
    # 適応的グレー値（隠し画像の詳細を反映）
    gray_base = 110 + hidden_enhanced * 45  # 110-155の範囲
    gray = np.zeros((height, width, 3), dtype=np.float32)
    for i in range(3):
        gray[:, :, i] = gray_base
    
    # マスクを3チャンネルに拡張
    mask_3d = np.stack([adaptive_mask, adaptive_mask, adaptive_mask], axis=2)
    
    # 最終合成（詳細保持）
    result = stripes * (1.0 - mask_3d) + gray * mask_3d
    
    # 適切な範囲にクリッピング（濃淡保持）
    result = np.clip(result, 40, 215)
    
    return result.astype(np.uint8)

def create_enhanced_overlay_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.6, enhancement_factor=1.2):
    """
    強化版重ね合わせモード：詳細コントラスト強化版（濃淡表現・デフォルト適用）
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
    
    # 強化処理（詳細を鮮明に）
    hidden_norm = hidden_gray / 255.0
    enhanced_contrast = np.clip((hidden_norm - 0.5) * enhancement_factor * 2.0 + 0.5, 0, 1)
    enhanced_gray = (enhanced_contrast * 255.0).astype(np.uint8)
    
    # 高精度エッジ強調
    edges = cv2.Canny(enhanced_gray, 30, 120)
    edge_enhanced = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
    
    # マスク生成（詳細保持）
    _, binary_mask = cv2.threshold(enhanced_gray, 100, 255, cv2.THRESH_BINARY_INV)
    
    # エッジをマスクに統合
    combined_mask = np.maximum(binary_mask, edge_enhanced)
    
    # 軽いブラー処理（詳細を保持）
    blurred_mask = cv2.GaussianBlur(combined_mask, (5, 5), 0)
    adaptive_mask = (blurred_mask.astype(np.float32) / 255.0) * overlay_opacity
    
    # 詳細な縞パターン生成
    stripe_pattern = create_vectorized_stripe_base(height, width, pattern_type)
    
    # 隠し画像の詳細を反映した縞生成（濃淡表現）
    detail_modulation = (enhanced_contrast - 0.5) * 50  # 詳細変調
    
    # RGB変換（詳細保持・濃淡表現）
    stripes = np.zeros((height, width, 3), dtype=np.float32)
    base_values = np.where(stripe_pattern == 0, 
                          90 + enhanced_contrast * 40,   # 暗い縞: 90-130
                          160 + enhanced_contrast * 45)  # 明るい縞: 160-205
    
    final_values = base_values + detail_modulation
    stripes = np.stack([final_values, final_values, final_values], axis=2)
    
    # 適応的グレー値
    gray_value = 115 + enhanced_contrast * 40  # 115-155
    gray = np.full((height, width, 3), gray_value, dtype=np.float32)
    
    # マスク適用
    mask_3d = np.stack([adaptive_mask, adaptive_mask, adaptive_mask], axis=2)
    result = stripes * (1.0 - mask_3d) + gray * mask_3d
    
    return np.clip(result, 35, 210).astype(np.uint8)

def create_vectorized_stripe_base(height, width, pattern_type="horizontal", frequency=1):
    """
    ベクトル化による詳細縞パターン生成（濃淡表現対応）
    隠し画像の詳細を保持するメモリ効率的実装
    """
    if pattern_type == "horizontal":
        y_coords = np.arange(height, dtype=np.int32).reshape(-1, 1)
        pattern_base = ((y_coords * frequency) % 2) * 255
        return np.broadcast_to(pattern_base, (height, width)).astype(np.float32)
    else:  # vertical
        x_coords = np.arange(width, dtype=np.int32).reshape(1, -1)
        pattern_base = ((x_coords * frequency) % 2) * 255
        return np.broadcast_to(pattern_base, (height, width)).astype(np.float32)

def create_multi_frequency_overlay(hidden_img, pattern_type="horizontal", frequencies=[1, 2], overlay_opacity=0.6):
    """
    多周波数重ね合わせ：複数の縞模様による詳細表現
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
    
    # 隠し画像の詳細分析
    hidden_norm = hidden_gray / 255.0
    hidden_detailed = np.clip((hidden_norm - 0.5) * 2.2 + 0.5, 0, 1)
    
    # 基本マスク生成
    _, binary_mask = cv2.threshold(hidden_gray, 100, 255, cv2.THRESH_BINARY_INV)
    blurred_mask = cv2.GaussianBlur(binary_mask, (5, 5), 0)
    base_mask = blurred_mask.astype(np.float32) / 255.0
    
    # 複数周波数の詳細縞パターンを生成
    stripe_patterns = []
    for freq in frequencies:
        pattern = create_vectorized_stripe_base(height, width, pattern_type, frequency=freq)
        # 隠し画像の詳細を各周波数に反映
        detailed_pattern = pattern + (hidden_detailed - 0.5) * 30  # 詳細変調
        stripe_patterns.append(detailed_pattern)
    
    # パターン合成（詳細保持）
    if len(stripe_patterns) > 1:
        # 重み付き合成（低周波数により多くの重み）
        weights = [1.0 / (i + 1) for i in range(len(stripe_patterns))]
        total_weight = sum(weights)
        normalized_weights = [w / total_weight for w in weights]
        
        combined_stripes = np.zeros_like(stripe_patterns[0])
        for pattern, weight in zip(stripe_patterns, normalized_weights):
            combined_stripes += pattern * weight
    else:
        combined_stripes = stripe_patterns[0]
    
    # RGB変換（詳細保持）
    stripes_rgb = np.stack([combined_stripes, combined_stripes, combined_stripes], axis=2)
    
    # 適応的グレー値（隠し画像詳細を反映）
    gray_detail = 105 + hidden_detailed * 50  # 105-155
    gray = np.full((height, width, 3), gray_detail, dtype=np.float32)
    
    # マスク適用
    mask_3d = np.stack([base_mask * overlay_opacity] * 3, axis=2)
    result = stripes_rgb * (1.0 - mask_3d) + gray * mask_3d
    
    return np.clip(result, 35, 220).astype(np.uint8)

def create_vectorized_stripe_base(height, width, pattern_type="horizontal", frequency=1):
    """
    ベクトル化による詳細縞パターン生成
    隠し画像の詳細を保持するメモリ効率的実装
    """
    if pattern_type == "horizontal":
        y_coords = np.arange(height, dtype=np.int32).reshape(-1, 1)
        pattern_base = ((y_coords * frequency) % 2) * 255
        return np.broadcast_to(pattern_base, (height, width)).astype(np.float32)
    else:  # vertical
        x_coords = np.arange(width, dtype=np.int32).reshape(1, -1)
        pattern_base = ((x_coords * frequency) % 2) * 255
        return np.broadcast_to(pattern_base, (height, width)).astype(np.float32)

def create_gradient_overlay_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.6, gradient_direction="radial"):
    """
    グラデーション重ね合わせ：空間的に変化する詳細オーバーレイ効果
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
    
    # 隠し画像の詳細分析
    hidden_norm = hidden_gray / 255.0
    hidden_enhanced = np.clip((hidden_norm - 0.5) * 2.0 + 0.5, 0, 1)
    
    # グラデーション生成（詳細対応）
    if gradient_direction == "radial":
        center_y, center_x = height // 2, width // 2
        y_coords, x_coords = np.ogrid[:height, :width]
        distances = np.sqrt((y_coords - center_y)**2 + (x_coords - center_x)**2)
        max_distance = np.sqrt(center_y**2 + center_x**2)
        gradient = 1.0 - (distances / max_distance)
    elif gradient_direction == "linear_horizontal":
        x_coords = np.arange(width).reshape(1, -1)
        gradient = x_coords / (width - 1)
        gradient = np.broadcast_to(gradient, (height, width))
    elif gradient_direction == "linear_vertical":
        y_coords = np.arange(height).reshape(-1, 1)
        gradient = y_coords / (height - 1)
        gradient = np.broadcast_to(gradient, (height, width))
    else:  # uniform
        gradient = np.ones((height, width), dtype=np.float32)
    
    # 基本処理
    _, binary_mask = cv2.threshold(hidden_gray, 100, 255, cv2.THRESH_BINARY_INV)
    blurred_mask = cv2.GaussianBlur(binary_mask, (5, 5), 0)
    base_mask = blurred_mask.astype(np.float32) / 255.0
    
    # グラデーションと隠し画像の詳細を合成
    detail_gradient = gradient * (0.7 + hidden_enhanced * 0.3)
    final_mask = base_mask * detail_gradient * overlay_opacity
    
    # 詳細縞パターン生成
    stripes = create_vectorized_stripe_base(height, width, pattern_type)
    # 隠し画像詳細の追加
    stripes_detailed = stripes + (hidden_enhanced - 0.5) * 40
    stripes_rgb = np.stack([stripes_detailed, stripes_detailed, stripes_detailed], axis=2)
    
    # 適応的グレー値
    gray_adaptive = 110 + hidden_enhanced * 45 + gradient * 20  # 詳細とグラデーション反映
    gray = np.stack([gray_adaptive, gray_adaptive, gray_adaptive], axis=2)
    
    # 合成
    mask_3d = np.stack([final_mask, final_mask, final_mask], axis=2)
    result = stripes_rgb * (1.0 - mask_3d) + gray * mask_3d
    
    return np.clip(result, 40, 215).astype(np.uint8)

def create_adaptive_overlay_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.6, adaptation_strength=1.0):
    """
    適応的重ね合わせ：画像内容に応じて自動調整（詳細版）
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
    
    # 局所詳細分析
    kernel = np.ones((7, 7), np.float32) / 49
    local_mean = cv2.filter2D(hidden_gray, -1, kernel)
    local_variance = cv2.filter2D((hidden_gray - local_mean)**2, -1, kernel)
    local_std = np.sqrt(local_variance)
    
    # 正規化
    contrast_map = local_std / (np.max(local_std) + 1e-8)
    
    # 適応的強度調整（詳細保持）
    adaptive_strength = overlay_opacity * (0.5 + contrast_map * adaptation_strength)
    adaptive_strength = np.clip(adaptive_strength, 0.0, 1.0)
    
    # 基本マスク処理
    _, binary_mask = cv2.threshold(hidden_gray, 100, 255, cv2.THRESH_BINARY_INV)
    blurred_mask = cv2.GaussianBlur(binary_mask, (5, 5), 0)
    base_mask = blurred_mask.astype(np.float32) / 255.0
    
    # 適応的マスク（詳細反映）
    final_mask = base_mask * adaptive_strength
    
    # 詳細縞パターン生成
    stripes = create_vectorized_stripe_base(height, width, pattern_type)
    # 局所詳細の反映
    detail_enhancement = (contrast_map - 0.5) * 50
    stripes_enhanced = stripes + detail_enhancement
    stripes_rgb = np.stack([stripes_enhanced, stripes_enhanced, stripes_enhanced], axis=2)
    
    # 適応的グレー値
    gray_adaptive = 108 + contrast_map * 47  # 詳細に応じて変化
    gray = np.stack([gray_adaptive, gray_adaptive, gray_adaptive], axis=2)
    
    # 合成
    mask_3d = np.stack([final_mask, final_mask, final_mask], axis=2)
    result = stripes_rgb * (1.0 - mask_3d) + gray * mask_3d
    
    return np.clip(result, 45, 210).astype(np.uint8)
