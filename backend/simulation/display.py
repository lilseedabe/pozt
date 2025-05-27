"""
表示効果シミュレーション
"""
import numpy as np
from PIL import Image, ImageFilter
import cv2

def simulate_4k_view(img, region_fixed, compression_level=0.5):
    """4K読み込み時の見え方（縞模様がより鮮明に、隠し画像が明確に見える）"""
    if isinstance(img, np.ndarray):
        result = img.copy().astype(np.float32)
    else:
        result = np.array(img).astype(np.float32)
    
    if region_fixed is None:
        return result.astype(np.uint8)
    
    x, y, width, height = region_fixed
    
    # 選択領域のシャープネス強調
    region = result[y:y+height, x:x+width]
    
    # アンシャープマスクを強化
    blurred = cv2.GaussianBlur(region, (3, 3), 0.7)  # ブラー半径を小さく
    sharpened = region + 0.4 * (region - blurred)  # 強調を強める
    
    # コントラストも強める
    region_mean = np.mean(sharpened, axis=(0, 1))
    enhanced = (sharpened - region_mean) * 1.3 + region_mean  # コントラスト強調を強める
    
    result[y:y+height, x:x+width] = np.clip(enhanced, 0, 255)
    
    return result.astype(np.uint8)

def create_zoom_preview(img, region_fixed, zoom_factor=4):
    """拡大表示のプレビュー（モアレ効果により隠し画像が鮮明に）"""
    if region_fixed is None:
        return img
    
    if isinstance(img, np.ndarray):
        result_img = img.copy()
    else:
        result_img = np.array(img).copy()
    
    x, y, width, height = region_fixed
    
    # 領域の中心部分を拡大
    center_x = x + width // 2
    center_y = y + height // 2
    
    # ズーム領域のサイズ
    zoom_width = width // zoom_factor
    zoom_height = height // zoom_factor
    
    # ズーム領域の座標
    zoom_x = max(0, center_x - zoom_width // 2)
    zoom_y = max(0, center_y - zoom_height // 2)
    zoom_x2 = min(result_img.shape[1], zoom_x + zoom_width)
    zoom_y2 = min(result_img.shape[0], zoom_y + zoom_height)
    
    # ズーム領域を抽出
    zoom_region = result_img[zoom_y:zoom_y2, zoom_x:zoom_x2].astype(np.float32)
    
    # モアレ効果を最大化するための処理
    # 1. 高周波成分を強調
    kernel = np.array([[-1, -2, -1],
                       [-2, 17, -2],
                       [-1, -2, -1]]) / 4.0
    enhanced = cv2.filter2D(zoom_region, -1, kernel)
    
    # 2. コントラストを大幅に強調
    enhanced_mean = np.mean(enhanced, axis=(0, 1))
    enhanced = (enhanced - enhanced_mean) * 5.0 + enhanced_mean
    
    # 3. ガンマ補正で中間調を調整
    enhanced = np.power(np.clip(enhanced / 255.0, 0, 1), 0.5) * 255
    
    enhanced = np.clip(enhanced, 0, 255)
    
    # 拡大（NEARESTで縞模様を保持）
    zoom_pil = Image.fromarray(enhanced.astype('uint8'))
    zoomed = zoom_pil.resize((result_img.shape[1], result_img.shape[0]), Image.Resampling.NEAREST)
    
    # 最終的なシャープネス調整
    zoomed_array = np.array(zoomed).astype(np.float32)
    
    # アンシャープマスク
    blurred = cv2.GaussianBlur(zoomed_array, (3, 3), 0.8)
    sharpened = zoomed_array + 2.2 * (zoomed_array - blurred)
    sharpened = np.clip(sharpened, 0, 255)
    
    return sharpened.astype(np.uint8)
