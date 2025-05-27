"""
ハイブリッド/組み合わせパターン生成機能
"""
import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale
from patterns.moire import create_high_frequency_moire_stripes, create_moire_hidden_stripes, create_perfect_moire_pattern
from patterns.overlay import create_overlay_moire_pattern

def create_combined_overlay_pattern(hidden_img, pattern_type="horizontal", base_method="high_frequency", overlay_opacity=0.6):
    """
    ベースとなる縞模様を生成し、その上にoverlay効果を適用
    """
    # まずベースとなる縞模様を生成
    if base_method == "high_frequency":
        base_stripes = create_high_frequency_moire_stripes(hidden_img, pattern_type)
    elif base_method == "moire_pattern":
        base_stripes = create_perfect_moire_pattern(hidden_img, pattern_type)
    else:  # デフォルトは標準のモアレ効果
        base_stripes = create_moire_hidden_stripes(hidden_img, pattern_type)
    
    # 隠し画像を二値化してマスクを作成
    hidden_array = ensure_array(hidden_img)
    hidden_gray = get_grayscale(hidden_array)
    
    # マスク生成 (overlay技法と同様)
    _, binary_mask = cv2.threshold(hidden_gray, 100, 255, cv2.THRESH_BINARY_INV)
    blurred_mask = cv2.GaussianBlur(binary_mask, (5, 5), 0)
    mask = blurred_mask / 255.0 * overlay_opacity
    
    # 均一なグレー
    height, width = base_stripes.shape[:2]
    gray = np.ones((height, width, 3), dtype=np.float32) * 128
    
    # ベースの縞模様にoverlayエフェクトを適用
    result = np.zeros((height, width, 3), dtype=np.float32)
    for i in range(3):
        result[:,:,i] = base_stripes[:,:,i] * (1 - mask) + gray[:,:,i] * mask
    
    return result.astype(np.uint8)

def create_hybrid_moire_pattern(hidden_img, pattern_type="horizontal", 
                              primary_method="high_frequency", 
                              overlay_ratio=0.4,
                              strength=0.02):
    """
    複数の縞模様生成手法を混合した効果を生成
    """
    hidden_array = ensure_array(hidden_img)
    height, width = hidden_array.shape[:2]
    
    # プライマリパターンを生成
    if primary_method == "high_frequency":
        primary_result = create_high_frequency_moire_stripes(hidden_img, pattern_type, strength)
    elif primary_method == "moire_pattern":
        primary_result = create_perfect_moire_pattern(hidden_img, pattern_type)
    else:
        primary_result = create_moire_hidden_stripes(hidden_img, pattern_type, strength)
    
    # オーバーレイパターンを生成 - より強いオーバーレイ効果
    overlay_result = create_overlay_moire_pattern(hidden_img, pattern_type, overlay_opacity=0.8)
    
    # 2つのパターンを混合 - オーバーレイの割合を調整可能に
    result = cv2.addWeighted(primary_result, 1.0 - overlay_ratio, overlay_result, overlay_ratio, 0)
    
    return result

def apply_overlay_fusion(stripe_pattern, hidden_img, pattern_type="horizontal", fusion_ratio=0.35):
    """
    任意の縞パターンにオーバーレイ効果を融合させる汎用関数
    """
    # オーバーレイ効果を生成
    overlay_effect = create_overlay_moire_pattern(hidden_img, pattern_type, overlay_opacity=0.7)
    
    # パターンとオーバーレイを融合
    fused_pattern = cv2.addWeighted(stripe_pattern, 1.0 - fusion_ratio, overlay_effect, fusion_ratio, 0)
    
    return fused_pattern
