# patterns/overlay.py のシンプル版（Numbaなし・安定版）

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

def create_overlay_moire_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.6):
    """高速化されたオーバーレイモアレパターン生成（Numbaなし・安定版）"""
    hidden_array = ensure_array(hidden_img).astype(np.uint8)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化（OpenCV高速実装）
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array, cv2.COLOR_RGB2GRAY)
    else:
        hidden_gray = hidden_array
    
    # 隠し画像を二値化 - 黒い部分（暗い部分）だけを抽出
    _, binary_mask = cv2.threshold(hidden_gray, 100, 255, cv2.THRESH_BINARY_INV)
    
    # マスクをぼかして滑らかにする（軽量化：カーネルサイズを小さく）
    blurred_mask = cv2.GaussianBlur(binary_mask, (3, 3), 0)
    
    # マスクを正規化（0-1の範囲に）
    mask = (blurred_mask.astype(np.float32) / 255.0) * overlay_opacity
    
    # 結果画像を初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 均一なグレー値
    gray_value = 128.0
    
    if pattern_type == "horizontal":
        # 横縞パターン（ベクトル化で高速化）
        for y in range(height):
            stripe_value = (y % 2) * 255.0
            
            # 行全体を一括処理（ベクトル化）
            mask_row = mask[y, :]
            final_values = stripe_value * (1.0 - mask_row) + gray_value * mask_row
            final_values = np.clip(final_values, 0, 255).astype(np.uint8)
            
            # 全チャンネルに同じ値を設定
            result[y, :, 0] = final_values
            result[y, :, 1] = final_values
            result[y, :, 2] = final_values
    
    else:  # vertical
        # 縦縞パターン（ベクトル化で高速化）
        for x in range(width):
            stripe_value = (x % 2) * 255.0
            
            # 列全体を一括処理（ベクトル化）
            mask_col = mask[:, x]
            final_values = stripe_value * (1.0 - mask_col) + gray_value * mask_col
            final_values = np.clip(final_values, 0, 255).astype(np.uint8)
            
            # 全チャンネルに同じ値を設定
            result[:, x, 0] = final_values
            result[:, x, 1] = final_values
            result[:, x, 2] = final_values
    
    return result
