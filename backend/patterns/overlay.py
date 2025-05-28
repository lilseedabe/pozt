# patterns/overlay.py の完全版（隠蔽効果強化版）

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

def create_overlay_moire_pattern(hidden_img, pattern_type="horizontal", overlay_opacity=0.3):
    """隠蔽効果強化版：オーバーレイモアレパターン生成"""
    hidden_array = ensure_array(hidden_img).astype(np.uint8)
    height, width = hidden_array.shape[:2]
    
    # グレースケール化（OpenCV高速実装）
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array, cv2.COLOR_RGB2GRAY)
    else:
        hidden_gray = hidden_array
    
    # 隠し画像を二値化 - より厳しい閾値で隠蔽効果強化
    _, binary_mask = cv2.threshold(hidden_gray, 140, 255, cv2.THRESH_BINARY_INV)  # 120→140
    
    # マスクをより強くぼかして隠蔽効果強化
    blurred_mask = cv2.GaussianBlur(binary_mask, (9, 9), 0)  # (5,5)→(9,9)
    
    # マスクを正規化（より控えめに）
    mask = (blurred_mask.astype(np.float32) / 255.0) * overlay_opacity
    
    # 結果画像を初期化
    result = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 控えめなコントラストの値（隠蔽効果重視）
    base_gray = 128
    stripe_range = 18     # より控えめに (40→18)
    stripe_dark = base_gray - stripe_range   # 110
    stripe_light = base_gray + stripe_range  # 146
    gray_value = 128.0   # 中間グレー
    
    if pattern_type == "horizontal":
        # 横縞パターン（隠蔽効果強化版）
        for y in range(height):
            # 基本縞模様（より控えめなコントラスト）
            stripe_value = stripe_light if (y % 2) == 0 else stripe_dark
            
            # 行全体を一括処理（ベクトル化）
            mask_row = mask[y, :]
            
            # より隠蔽効果の高い合成
            # マスクされた部分は隠し画像の影響を受け、そうでない部分は縞模様
            final_values = stripe_value * (1.0 - mask_row) + gray_value * mask_row
            
            # 隠し画像の明度情報をより控えめに追加
            brightness_adjustment = (hidden_gray[y, :].astype(np.float32) - 128) * 0.15  # 0.3→0.15に削減
            final_values = final_values + brightness_adjustment * mask_row
            
            final_values = np.clip(final_values, 100, 155).astype(np.uint8)  # 範囲を制限
            
            # 全チャンネルに同じ値を設定
            result[y, :, 0] = final_values
            result[y, :, 1] = final_values
            result[y, :, 2] = final_values
    
    else:  # vertical
        # 縦縞パターン（隠蔽効果強化版）
        for x in range(width):
            # 基本縞模様（より控えめなコントラスト）
            stripe_value = stripe_light if (x % 2) == 0 else stripe_dark
            
            # 列全体を一括処理（ベクトル化）
            mask_col = mask[:, x]
            
            # より隠蔽効果の高い合成
            final_values = stripe_value * (1.0 - mask_col) + gray_value * mask_col
            
            # 隠し画像の明度情報をより控えめに追加
            brightness_adjustment = (hidden_gray[:, x].astype(np.float32) - 128) * 0.15
            final_values = final_values + brightness_adjustment * mask_col
            
            final_values = np.clip(final_values, 100, 155).astype(np.uint8)  # 範囲を制限
            
            # 全チャンネルに同じ値を設定
            result[:, x, 0] = final_values
            result[:, x, 1] = final_values
            result[:, x, 2] = final_values
    
    return result
