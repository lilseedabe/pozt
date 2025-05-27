"""
色調操作関連の縞パターン生成機能
"""
import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale
from patterns.moire import create_moire_hidden_stripes

def create_color_preserving_moire_stripes(hidden_img, base_img, region, pattern_type="horizontal", strength=0.025):
    """色調保存モード: 基本のモアレ縞模様を生成し、元画像の色調を保存"""
    # 基本のモアレ縞模様を生成
    stripes = create_moire_hidden_stripes(hidden_img, pattern_type, strength)
    
    # 基本画像から選択領域の平均色を抽出
    base_array = ensure_array(base_img)
    
    x, y, w, h = region
    region_img = base_array[y:y+h, x:x+w]
    avg_color = np.mean(region_img, axis=(0, 1))
    
    # グレースケールの縞模様を色付きに変換
    colored_stripes = np.zeros_like(stripes)
    for i in range(3):  # RGB各チャンネル
        # 各チャンネルのコントラストを保持しながら平均色に寄せる
        channel_contrast = (stripes[:,:,0] - 127.5) / 127.5  # -1から1の範囲に
        colored_stripes[:,:,i] = avg_color[i] + channel_contrast * min(avg_color[i], 255-avg_color[i]) * 0.8
    
    return np.clip(colored_stripes, 0, 255).astype(np.uint8)

def create_hue_preserving_moire(hidden_img, base_img, region, pattern_type="horizontal", strength=0.02):
    """色相保存モード: 元画像の色相と彩度を保持し、明度だけ縞模様から取得"""
    # 基本のモアレ縞模様を生成
    stripes = create_moire_hidden_stripes(hidden_img, pattern_type, strength).astype(np.float32)
    
    # 基本画像から選択領域を抽出
    base_array = ensure_array(base_img).astype(np.float32)
    
    x, y, w, h = region
    region_img = base_array[y:y+h, x:x+w]
    
    # RGB→HSV変換
    stripes_hsv = cv2.cvtColor(stripes, cv2.COLOR_RGB2HSV)
    region_hsv = cv2.cvtColor(region_img, cv2.COLOR_RGB2HSV)
    
    # 元画像の色相と彩度を保持し、明度だけ縞模様から取得
    result_hsv = region_hsv.copy()
    result_hsv[:,:,2] = stripes_hsv[:,:,2]  # 明度だけ置き換え
    
    # HSV→RGB変換
    result_rgb = cv2.cvtColor(result_hsv, cv2.COLOR_HSV2RGB)
    
    return result_rgb.astype(np.uint8)

def create_blended_moire_stripes(hidden_img, base_img, region, pattern_type="horizontal", strength=0.022, opacity=0.85):
    """透明度ブレンド: 基本のモアレ縞模様と元画像をブレンド"""
    # 基本のモアレ縞模様を生成
    stripes = create_moire_hidden_stripes(hidden_img, pattern_type, strength)
    
    # 基本画像から選択領域を抽出
    base_array = ensure_array(base_img)
    
    x, y, w, h = region
    region_img = base_array[y:y+h, x:x+w]
    
    # 縞模様と元画像をブレンド
    blended = region_img.astype(np.float32) * (1 - opacity) + stripes.astype(np.float32) * opacity
    
    return blended.astype(np.uint8)
