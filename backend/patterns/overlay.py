# patterns/overlay.py - 修正版（自然な濃淡表現）

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

def hex_to_rgb(hex_color):
    """HEX色をRGBタプルに変換"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_overlay_moire_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.6, color1="#000000", color2="#FFFFFF"):
    """
    重ね合わせモード：自然な濃淡表現版（修正版）
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
    
    # 隠し画像の正規化と適度な強調
    hidden_norm = hidden_gray / 255.0
    hidden_enhanced = np.clip((hidden_norm - 0.5) * 1.3 + 0.5, 0, 1)
    
    # シンプルなマスク生成
    _, binary_mask = cv2.threshold(hidden_gray, 110, 255, cv2.THRESH_BINARY_INV)
    
    # 軽いガウシアンブラー（詳細保持のため）
    blurred_mask = cv2.GaussianBlur(binary_mask, (5, 5), 0)
    
    # 適応的マスクの生成
    adaptive_mask = blurred_mask.astype(np.float32) / 255.0 * overlay_opacity
    
    # 縞模様パターンの生成（シンプル化）
    if pattern_type == "horizontal":
        y_coords = np.arange(height, dtype=np.uint8).reshape(-1, 1)
        stripe_pattern = (y_coords % 2)
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    else:  # vertical
        x_coords = np.arange(width, dtype=np.uint8).reshape(1, -1)
        stripe_pattern = (x_coords % 2)
        stripe_pattern = np.broadcast_to(stripe_pattern, (height, width))
    
    # 自然な濃淡縞パターンの生成
    stripes = np.zeros((height, width, 3), dtype=np.float32)
    
    # 暗い縞と明るい縞の領域
    dark_regions = stripe_pattern == 0
    light_regions = stripe_pattern == 1
    
    # 隠し画像に基づく詳細な明度調整（自然な濃淡表現）
    brightness_modulation = 0.7 + hidden_enhanced * 0.3  # 0.7-1.0の範囲
    
    # 基準明度値（自然な中間調）
    dark_base_values = 90 + hidden_enhanced * 25   # 90-115の範囲
    light_base_values = 160 + hidden_enhanced * 20 # 160-180の範囲
    
    # 暗い縞の詳細処理
    for i in range(3):
        dark_value = dark_base_values * brightness_modulation * (color1_rgb[i] / 255.0)
        stripes[dark_regions, i] = dark_value[dark_regions]
    
    # 明るい縞の詳細処理
    for i in range(3):
        light_value = light_base_values * brightness_modulation * (color2_rgb[i] / 255.0)
        stripes[light_regions, i] = light_value[light_regions]
    
    # 適応的なグレー値（隠し画像の詳細を反映）
    grey_base = 120 + hidden_enhanced * 20  # 120-140の範囲
    grey = np.zeros((height, width, 3), dtype=np.float32)
    for i in range(3):
        grey[:, :, i] = grey_base
    
    # マスクを3チャンネルに拡張
    mask_3d = np.stack([adaptive_mask, adaptive_mask, adaptive_mask], axis=2)
    
    # 最終合成（詳細保持）
    result = stripes * (1.0 - mask_3d) + grey * mask_3d
    
    # 適切な範囲にクリッピング（自然な濃淡保持）
    result = np.clip(result, 60, 190)
    
    return result.astype(np.uint8)

def create_enhanced_overlay_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.6, enhanced_factor=1.2):
    """
    強化版重ね合わせモード：詳細コントラスト強化版（修正版）
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
    
    # 強化処理（詳細を保持）
    hidden_norm = hidden_gray / 255.0
    enhanced_contrast = np.clip((hidden_norm - 0.5) * enhanced_factor * 1.5 + 0.5, 0, 1)
    enhanced_gray = (enhanced_contrast * 255.0).astype(np.uint8)
    
    # エッジ強調（適度な設定）
    edges = cv2.Canny(enhanced_gray, 40, 100)
    edge_enhanced = cv2.dilate(edges, np.ones((3,3), np.uint8), iterations=1)
    
    # マスク生成（詳細保持）
    _, binary_mask = cv2.threshold(enhanced_gray, 115, 255, cv2.THRESH_BINARY_INV)
    
    # エッジをマスクに統合
    combined_mask = np.maximum(binary_mask, edge_enhanced)
    
    # 適度なブラー処理（詳細を保持）
    blurred_mask = cv2.GaussianBlur(combined_mask, (5, 5), 0)
    adaptive_mask = (blurred_mask.astype(np.float32) / 255.0) * overlay_opacity
    
    # シンプルな縞パターン生成
    stripe_pattern = create_vectorized_stripe_base(height, width, pattern_type)
    
    # 隠し画像の詳細を反映した縞生成（自然な濃淡表現）
    detail_modulation = (enhanced_contrast - 0.5) * 25  # 詳細変調を適度に
    
    # RGB変換（詳細保持・自然な濃淡表現）
    stripes = np.zeros((height, width, 3), dtype=np.float32)
    base_values = np.where(stripe_pattern == 0,
                          100 + enhanced_contrast * 20,  # 暗い縞: 100-120
                          155 + enhanced_contrast * 25)  # 明るい縞: 155-180
    
    final_values = base_values + detail_modulation
    stripes = np.stack([final_values, final_values, final_values], axis=2)
    
    # 適応的なグレー値
    gray_value = 125 + enhanced_contrast * 15  # 125-140
    grey = np.full((height, width, 3), gray_value, dtype=np.float32)
    
    # マスク適用
    mask_3d = np.stack([adaptive_mask, adaptive_mask, adaptive_mask], axis=2)
    result = stripes * (1.0 - mask_3d) + grey * mask_3d
    
    return np.clip(result, 70, 175).astype(np.uint8)

def create_vectorized_stripe_base(height, width, pattern_type="horizontal", frequency=1):
    """
    ベクトル化による詳細縞パターン生成（自然な濃淡表現対応）
    """
    if pattern_type == "horizontal":
        y_coords = np.arange(height, dtype=np.int32).reshape(-1, 1)
        pattern_base = ((y_coords * frequency) % 2) * 255
        return np.broadcast_to(pattern_base, (height, width)).astype(np.float32)
    else:  # vertical
        x_coords = np.arange(width, dtype=np.int32).reshape(1, -1)
        pattern_base = ((x_coords * frequency) % 2) * 255
        return np.broadcast_to(pattern_base, (height, width)).astype(np.float32)

def create_multi_freq_overlay(hidden_img, pattern_type="horizontal", frequencies=[1, 2], overlay_opacity=0.6):
    """
    多周波数重ね合わせ：複数の縞模様による詳細表現（修正版）
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
    hidden_detailed = np.clip((hidden_norm - 0.5) * 1.4 + 0.5, 0, 1)
    
    # 基本マスク生成
    _, binary_mask = cv2.threshold(hidden_gray, 115, 255, cv2.THRESH_BINARY_INV)
    blurred_mask = cv2.GaussianBlur(binary_mask, (5, 5), 0)
    base_mask = blurred_mask.astype(np.float32) / 255.0
    
    # 複数周波数の詳細縞パターンを生成
    stripe_patterns = []
    for freq in frequencies:
        pattern = create_vectorized_stripe_base(height, width, pattern_type, frequency=freq)
        # 隠し画像の詳細を各周波数に反映
        detailed_pattern = pattern + (hidden_detailed - 0.5) * 20  # 詳細変調を適度に
        stripe_patterns.append(detailed_pattern)
    
    # パターン合成（詳細保持）
    if len(stripe_patterns) > 1:
        # 重み付き合成（低周波により多くの重み）
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
    
    # 適応的なグレー値（隠し画像詳細を反映）
    gray_detail = 115 + hidden_detailed * 25  # 115-140
    grey = np.full((height, width, 3), gray_detail, dtype=np.float32)
    
    # マスク適用
    mask_3d = np.stack([base_mask * overlay_opacity] * 3, axis=2)
    result = stripes_rgb * (1.0 - mask_3d) + grey * mask_3d
    
    return np.clip(result, 65, 185).astype(np.uint8)

def create_gradient_overlay_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.6, gradient_direction="radial"):
    """
    グラデーション重ね合わせ：空間的に変化する詳細オーバーレイ効果（修正版）
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
    hidden_enhanced = np.clip((hidden_norm - 0.5) * 1.5 + 0.5, 0, 1)
    
    # グラデーション生成（詳細対応）
    if gradient_direction == "radial":
        center_y, center_x = height // 2, width // 2
        y_coords, x_coords = np.ogrid[:height, :width]
        distance = np.sqrt((y_coords - center_y)**2 + (x_coords - center_x)**2)
        max_distance = np.sqrt(center_y**2 + center_x**2)
        gradient = 1.0 - (distance / max_distance)
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
    
    # 基本マスク処理
    _, binary_mask = cv2.threshold(hidden_gray, 115, 255, cv2.THRESH_BINARY_INV)
    blurred_mask = cv2.GaussianBlur(binary_mask, (5, 5), 0)
    base_mask = blurred_mask.astype(np.float32) / 255.0
    
    # グラデーションと隠し画像の詳細を合成
    detail_gradient = gradient * (0.8 + hidden_enhanced * 0.2)
    final_mask = base_mask * detail_gradient * overlay_opacity
    
    # 詳細縞パターン生成
    stripes = create_vectorized_stripe_base(height, width, pattern_type)
    # 隠し画像詳細の追加
    stripes_detailed = stripes + (hidden_enhanced - 0.5) * 25
    stripes_rgb = np.stack([stripes_detailed, stripes_detailed, stripes_detailed], axis=2)
    
    # 適応的なグレー値
    gray_adaptive = 118 + hidden_enhanced * 22 + gradient * 15  # 詳細とグラデーション反映
    grey = np.stack([gray_adaptive, gray_adaptive, gray_adaptive], axis=2)
    
    # 合成
    mask_3d = np.stack([final_mask, final_mask, final_mask], axis=2)
    result = stripes_rgb * (1.0 - mask_3d) + grey * mask_3d
    
    return np.clip(result, 68, 182).astype(np.uint8)

def create_adaptive_overlay_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.6, adaptation_strength=1.0):
    """
    適応的な重ね合わせ：画像内容に応じて自動調整（修正版）
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
    
    # 適応的な強度調整（詳細保持）
    adaptive_strength = overlay_opacity * (0.6 + contrast_map * adaptation_strength * 0.4)
    adaptive_strength = np.clip(adaptive_strength, 0.0, 1.0)
    
    # 基本マスク処理
    _, binary_mask = cv2.threshold(hidden_gray, 115, 255, cv2.THRESH_BINARY_INV)
    blurred_mask = cv2.GaussianBlur(binary_mask, (5, 5), 0)
    base_mask = blurred_mask.astype(np.float32) / 255.0
    
    # 適応的なマスク（詳細反映）
    final_mask = base_mask * adaptive_strength
    
    # 詳細縞パターン生成
    stripes = create_vectorized_stripe_base(height, width, pattern_type)
    # 局所詳細の反映
    detail_enhanced = (contrast_map - 0.5) * 30
    stripes_enhanced = stripes + detail_enhanced
    stripes_rgb = np.stack([stripes_enhanced, stripes_enhanced, stripes_enhanced], axis=2)
    
    # 適応的なグレー値
    gray_adaptive = 112 + contrast_map * 28  # 詳細に応じて変化
    grey = np.stack([gray_adaptive, gray_adaptive, gray_adaptive], axis=2)
    
    # 合成
    mask_3d = np.stack([final_mask, final_mask, final_mask], axis=2)
    result = stripes_rgb * (1.0 - mask_3d) + grey * mask_3d
    
    return np.clip(result, 72, 178).astype(np.uint8)
