"""
圧縮効果シミュレーション
"""
import numpy as np
from PIL import Image, ImageFilter
import cv2

def simulate_x_post_compression(img, region_fixed, compression_level=0.02):
    """画像圧縮時の見え方をシミュレーション（より均一なグレーに）"""
    if isinstance(img, np.ndarray):
        result_img = img.copy()
    else:
        result_img = np.array(img).copy()
    
    if region_fixed is None:
        return result_img
    
    x, y, width, height = region_fixed
    
    # 選択領域をぼかして均一に
    region_img = result_img[y:y+height, x:x+width]
    
    # 平均色を計算（これが最終的な色になる）
    avg_color = np.mean(region_img, axis=(0, 1))
    
    # より均一なグレーに（個人差をさらに小さく）
    # ブラーの前に領域を均一な平均色にほぼ置き換え
    region_pil = Image.fromarray(region_img)
    region_array = np.array(region_pil).astype(np.float32)
    
    # 平均色に近づける割合を増やす（より均一に）
    uniformed_region = region_array * 0.05 + avg_color * 0.95  # 平均色の割合を増やす
    
    # 強い圧縮をシミュレート
    region_pil = Image.fromarray(uniformed_region.astype('uint8'))
    
    # 極端に小さくリサイズ（情報を失わせる）
    tiny_width = max(1, int(width * 0.01))
    tiny_height = max(1, int(height * 0.01))
    tiny = region_pil.resize((tiny_width, tiny_height), Image.Resampling.BOX)
    
    # 元のサイズに戻す
    blurred = tiny.resize((width, height), Image.Resampling.BILINEAR)
    
    # 強力なガウシアンブラー
    for _ in range(3):
        blurred = blurred.filter(ImageFilter.GaussianBlur(radius=20))
    
    # 平均色に近づける
    blurred_array = np.array(blurred).astype(np.float32)
    final_region = blurred_array * 0.1 + avg_color * 0.9  # さらに平均色に近づける
    
    result_img[y:y+height, x:x+width] = final_region.astype(np.uint8)
    
    return result_img
