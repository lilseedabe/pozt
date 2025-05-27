"""
オーバーレイパターン生成機能
"""
import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale
from patterns.base import create_stripe_base

def create_overlay_moire_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.6):
    """
    重ね合わせモード：均一な縞模様の上に隠し画像をグレーで重ねる
    """
    hidden_array = ensure_array(hidden_img).astype(np.float32)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化
    hidden_gray = get_grayscale(hidden_array)
    
    # 隠し画像を二値化 - 黒い部分（暗い部分）だけを抽出
    _, binary_mask = cv2.threshold(hidden_gray, 100, 255, cv2.THRESH_BINARY_INV)
    
    # マスクをぼかして滑らかにする
    blurred_mask = cv2.GaussianBlur(binary_mask, (5, 5), 0)
    
    # マスクを正規化（0-1の範囲に）
    mask = blurred_mask / 255.0 * overlay_opacity
    
    # 均一な縞模様を作成
    stripes = create_stripe_base(height, width, pattern_type)
    
    # 均一なグレー（隠し画像の部分を上書きするため）
    gray = np.ones((height, width, 3), dtype=np.float32) * 128
    
    # マスクを使って縞模様とグレーを合成
    result = np.zeros((height, width, 3), dtype=np.float32)
    for i in range(3):
        result[:,:,i] = stripes[:,:,i] * (1 - mask) + gray[:,:,i] * mask
    
    return result.astype(np.uint8)
