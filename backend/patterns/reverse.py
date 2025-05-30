# backend/patterns/reverse.py - モアレ効果画像から隠し画像を抽出
import numpy as np
import cv2
from PIL import Image
from core.image_utils import ensure_array, ensure_pil

def extract_hidden_image_from_moire(moire_img, method="fourier_analysis", enhancement_level=2.0):
    """
    モアレ効果画像から隠し画像を抽出する
    """
    moire_array = ensure_array(moire_img)
    
    if method == "fourier_analysis":
        return extract_via_fourier_analysis(moire_array, enhancement_level)
    elif method == "frequency_filtering":
        return extract_via_frequency_filtering(moire_array, enhancement_level)
    elif method == "pattern_subtraction":
        return extract_via_pattern_subtraction(moire_array, enhancement_level)
    else:
        return extract_via_adaptive_detection(moire_array, enhancement_level)

def extract_via_fourier_analysis(moire_array, enhancement_level=2.0):
    """
    フーリエ解析による隠し画像抽出
    """
    height, width = moire_array.shape[:2]
    
    # グレースケール変換
    if len(moire_array.shape) == 3:
        gray = cv2.cvtColor(moire_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = moire_array
    
    # フーリエ変換
    f_transform = np.fft.fft2(gray)
    f_shift = np.fft.fftshift(f_transform)
    
    # 周波数領域でのフィルタリング
    # モアレパターンの高周波成分を除去し、隠し画像の低周波成分を強調
    center_y, center_x = height // 2, width // 2
    
    # ローパスフィルタを作成（隠し画像の特徴を抽出）
    mask = np.zeros((height, width), dtype=np.float32)
    radius = min(height, width) // 8  # 調整可能
    y, x = np.ogrid[:height, :width]
    mask_area = (x - center_x)**2 + (y - center_y)**2 <= radius**2
    mask[mask_area] = 1
    
    # バンドパスフィルタで特定周波数帯域を強調
    bandpass_mask = create_bandpass_filter(height, width, 
                                         inner_radius=radius//2, 
                                         outer_radius=radius*2)
    
    # フィルタ適用
    filtered_shift = f_shift * (mask + bandpass_mask * enhancement_level)
    
    # 逆フーリエ変換
    f_ishift = np.fft.ifftshift(filtered_shift)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    
    # 正規化と強調
    result = np.clip((img_back - np.min(img_back)) / 
                    (np.max(img_back) - np.min(img_back)) * 255 * enhancement_level, 0, 255)
    
    # RGB変換
    if len(moire_array.shape) == 3:
        result_rgb = np.stack([result, result, result], axis=2)
        return result_rgb.astype(np.uint8)
    
    return result.astype(np.uint8)

def extract_via_frequency_filtering(moire_array, enhancement_level=2.0):
    """
    周波数フィルタリングによる抽出
    """
    height, width = moire_array.shape[:2]
    
    # グレースケール変換
    if len(moire_array.shape) == 3:
        gray = cv2.cvtColor(moire_array, cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        gray = moire_array.astype(np.float32)
    
    # ガウシアンブラーで高周波ノイズ除去
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # エッジ検出で縞模様を検出
    edges = cv2.Canny(blurred.astype(np.uint8), 30, 100)
    
    # モルフォロジー演算で縞模様を強調
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dilated = cv2.dilate(edges, kernel, iterations=1)
    
    # 縞模様マスクを作成
    stripe_mask = (dilated > 0).astype(np.float32)
    
    # 隠し画像領域を抽出（縞模様ではない部分）
    hidden_mask = 1.0 - stripe_mask
    
    # 隠し画像を強調
    hidden_enhanced = gray * hidden_mask * enhancement_level
    
    # ガウシアンブラーで滑らかに
    result = cv2.GaussianBlur(hidden_enhanced, (7, 7), 0)
    
    # 正規化
    result = np.clip(result, 0, 255)
    
    # RGB変換
    if len(moire_array.shape) == 3:
        result_rgb = np.stack([result, result, result], axis=2)
        return result_rgb.astype(np.uint8)
    
    return result.astype(np.uint8)

def extract_via_pattern_subtraction(moire_array, enhancement_level=2.0):
    """
    パターン減算による抽出
    """
    height, width = moire_array.shape[:2]
    
    # グレースケール変換
    if len(moire_array.shape) == 3:
        gray = cv2.cvtColor(moire_array, cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        gray = moire_array.astype(np.float32)
    
    # 縞パターンを再構成
    # 水平方向の縞パターン
    horizontal_pattern = np.zeros_like(gray)
    for y in range(height):
        horizontal_pattern[y, :] = 255 if y % 2 == 0 else 0
    
    # 垂直方向の縞パターン  
    vertical_pattern = np.zeros_like(gray)
    for x in range(width):
        vertical_pattern[:, x] = 255 if x % 2 == 0 else 0
    
    # パターンマッチングで最適な縞パターンを検出
    h_correlation = cv2.matchTemplate(gray, horizontal_pattern[:100, :100], cv2.TM_CCOEFF_NORMED)
    v_correlation = cv2.matchTemplate(gray, vertical_pattern[:100, :100], cv2.TM_CCOEFF_NORMED)
    
    # より相関の高い方向を選択
    if np.max(h_correlation) > np.max(v_correlation):
        estimated_pattern = horizontal_pattern
    else:
        estimated_pattern = vertical_pattern
    
    # パターン減算
    difference = gray - estimated_pattern * 0.5
    
    # 隠し画像を強調
    result = difference * enhancement_level
    result = np.clip(result + 128, 0, 255)  # バイアス調整
    
    # RGB変換
    if len(moire_array.shape) == 3:
        result_rgb = np.stack([result, result, result], axis=2)
        return result_rgb.astype(np.uint8)
    
    return result.astype(np.uint8)

def extract_via_adaptive_detection(moire_array, enhancement_level=2.0):
    """
    適応的検出による抽出
    """
    height, width = moire_array.shape[:2]
    
    # グレースケール変換
    if len(moire_array.shape) == 3:
        gray = cv2.cvtColor(moire_array, cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        gray = moire_array.astype(np.float32)
    
    # 局所統計量による適応的処理
    # 局所平均
    kernel = np.ones((9, 9), np.float32) / 81
    local_mean = cv2.filter2D(gray, -1, kernel)
    
    # 局所分散
    local_variance = cv2.filter2D((gray - local_mean)**2, -1, kernel)
    local_std = np.sqrt(local_variance)
    
    # 適応的閾値
    adaptive_threshold = local_mean + local_std * 0.5
    
    # 隠し画像領域を検出
    hidden_mask = (gray > adaptive_threshold).astype(np.float32)
    
    # エッジ保存スムージング
    result = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # 隠し画像を強調
    result = result * hidden_mask * enhancement_level
    
    # 正規化
    result = np.clip(result, 0, 255)
    
    # RGB変換
    if len(moire_array.shape) == 3:
        result_rgb = np.stack([result, result, result], axis=2)
        return result_rgb.astype(np.uint8)
    
    return result.astype(np.uint8)

def create_bandpass_filter(height, width, inner_radius, outer_radius):
    """
    バンドパスフィルタを作成
    """
    center_y, center_x = height // 2, width // 2
    y, x = np.ogrid[:height, :width]
    distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    
    # リング形状のフィルタ
    mask = ((distance >= inner_radius) & (distance <= outer_radius)).astype(np.float32)
    
    return mask

def enhance_extracted_image(extracted_img, method="histogram_equalization"):
    """
    抽出された隠し画像を強調
    """
    if method == "histogram_equalization":
        if len(extracted_img.shape) == 3:
            # カラー画像の場合、各チャンネルで均等化
            result = np.zeros_like(extracted_img)
            for i in range(3):
                result[:,:,i] = cv2.equalizeHist(extracted_img[:,:,i])
            return result
        else:
            return cv2.equalizeHist(extracted_img)
    
    elif method == "clahe":
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        if len(extracted_img.shape) == 3:
            result = np.zeros_like(extracted_img)
            for i in range(3):
                result[:,:,i] = clahe.apply(extracted_img[:,:,i])
            return result
        else:
            return clahe.apply(extracted_img)
    
    elif method == "gamma_correction":
        # ガンマ補正
        gamma = 0.7  # 明るく
        lookup_table = np.array([((i / 255.0) ** gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(extracted_img, lookup_table)
    
    return extracted_img
