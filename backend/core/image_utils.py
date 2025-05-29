# core/image_utils.py - Numpy ベクトル化による超高速化版

import numpy as np
from PIL import Image, ImageDraw
import cv2
from config.settings import TARGET_WIDTH, TARGET_HEIGHT

def ensure_array(img):
    """入力がPIL画像かnumpy配列かを確認し、numpy配列に変換（最適化版）"""
    if isinstance(img, np.ndarray):
        return img
    return np.array(img)

def ensure_pil(img):
    """入力がPIL画像かnumpy配列かを確認し、PIL画像に変換（最適化版）"""
    if isinstance(img, np.ndarray):
        return Image.fromarray(img.astype('uint8'))
    return img

def get_grayscale(img):
    """画像をグレースケールに変換（ベクトル化最適化）"""
    img_array = ensure_array(img)
    
    if len(img_array.shape) == 3:
        # OpenCVによるハードウェア最適化グレースケール変換
        return cv2.cvtColor(img_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    return img_array.astype(np.float32)

def enhance_contrast(img, factor=2.0, center=0.5):
    """画像のコントラストを強調（完全ベクトル化版）"""
    img_array = ensure_array(img).astype(np.float32)
    
    if len(img_array.shape) == 3:
        # RGB画像の場合、輝度成分でコントラスト強調
        img_gray = get_grayscale(img_array)
    else:
        img_gray = img_array
    
    # **完全ベクトル化処理**
    # 正規化（全画素同時処理）
    img_norm = img_gray / 255.0
    
    # コントラスト強調（全画素同時処理）
    img_contrast = np.clip((img_norm - center) * factor + center, 0, 1)
    
    return img_contrast

def detect_edges(img, low_threshold=80, high_threshold=150):
    """エッジ検出（OpenCV最適化活用）"""
    img_array = ensure_array(img)
    
    if len(img_array.shape) == 3:
        # OpenCVによる高速グレースケール変換
        img_gray = cv2.cvtColor(img_array.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    else:
        img_gray = img_array.astype(np.uint8)
    
    # Cannyエッジ検出（OpenCV最適化、ハードウェア加速対応）
    edges = cv2.Canny(img_gray, low_threshold, high_threshold)
    return edges.astype(np.float32) / 255.0  # 正規化

def resize_to_fixed_size(img, method='contain'):
    """画像を固定サイズ（2430×3240）にリサイズ（高速化版）"""
    img_pil = ensure_pil(img)
    
    if method == 'stretch':
        # 最高速：単純リサイズ
        return img_pil.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    orig_width, orig_height = img_pil.size
    orig_aspect = orig_width / orig_height
    target_aspect = TARGET_WIDTH / TARGET_HEIGHT
    
    if method == 'contain':
        # アスペクト比保持（黒帯あり）
        if orig_aspect > target_aspect:
            new_width = TARGET_WIDTH
            new_height = int(TARGET_WIDTH / orig_aspect)
        else:
            new_height = TARGET_HEIGHT
            new_width = int(TARGET_HEIGHT * orig_aspect)
        
        # 高速リサイズ
        resized = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # キャンバス作成と配置（PIL最適化）
        canvas = Image.new('RGB', (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0))
        x_offset = (TARGET_WIDTH - new_width) // 2
        y_offset = (TARGET_HEIGHT - new_height) // 2
        canvas.paste(resized, (x_offset, y_offset))
        
        return canvas
    
    elif method == 'cover':
        # 画面を埋める（クロップあり）
        if orig_aspect > target_aspect:
            new_height = TARGET_HEIGHT
            new_width = int(TARGET_HEIGHT * orig_aspect)
        else:
            new_width = TARGET_WIDTH
            new_height = int(TARGET_WIDTH / orig_aspect)
        
        # 高速リサイズ
        resized = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 中央クロップ
        x_offset = (new_width - TARGET_WIDTH) // 2
        y_offset = (new_height - TARGET_HEIGHT) // 2
        cropped = resized.crop((x_offset, y_offset, x_offset + TARGET_WIDTH, y_offset + TARGET_HEIGHT))
        
        return cropped

def calculate_resize_factors(orig_img, resize_method):
    """リサイズの比率とオフセットを計算（最適化版）"""
    if isinstance(orig_img, np.ndarray):
        orig_height, orig_width = orig_img.shape[:2]
    else:
        orig_width, orig_height = orig_img.size
    
    # **ベクトル化による高速計算**
    if resize_method == 'contain':
        scale_factors = np.array([TARGET_WIDTH / orig_width, TARGET_HEIGHT / orig_height])
        scale = np.min(scale_factors)  # 最小値選択
        
        # オフセット計算（ベクトル化）
        new_size = np.array([orig_width, orig_height]) * scale
        offsets = (np.array([TARGET_WIDTH, TARGET_HEIGHT]) - new_size.astype(int)) // 2
        
        return scale, scale, scale, offsets[0], offsets[1]
        
    elif resize_method == 'cover':
        scale_factors = np.array([TARGET_WIDTH / orig_width, TARGET_HEIGHT / orig_height])
        scale = np.max(scale_factors)  # 最大値選択
        
        # オフセット計算（ベクトル化）
        new_size = np.array([orig_width, orig_height]) * scale
        crop_offsets = ((new_size - np.array([TARGET_WIDTH, TARGET_HEIGHT])) / 2 / scale).astype(int)
        offset_x, offset_y = -crop_offsets[0] * scale, -crop_offsets[1] * scale
        
        return scale, scale, scale, offset_x, offset_y
        
    else:  # stretch
        scale_x = TARGET_WIDTH / orig_width
        scale_y = TARGET_HEIGHT / orig_height
        return scale_x, scale_y, scale_x, 0, 0

def add_black_border(img, region, border_width=3):
    """グレー領域の周りに黒い枠を追加（完全ベクトル化版）"""
    if region is None:
        return img
    
    result = ensure_array(img).copy()
    x, y, w, h = region
    
    # 画像サイズを取得
    height, width = result.shape[:2]
    
    # **ベクトル化による境界計算**
    # 境界座標計算（ベクトル化）
    borders = np.array([
        max(0, y - border_width),      # top
        min(height, y + h + border_width),  # bottom
        max(0, x - border_width),      # left
        min(width, x + w + border_width)   # right
    ])
    
    top, bottom, left, right = borders
    
    # **完全ベクトル化による枠描画**
    # 上枠（存在する場合）
    if y > 0:
        top_border = max(0, y - border_width)
        result[top_border:y, left:right] = 0
    
    # 下枠（存在する場合）
    if y + h < height:
        bottom_border = min(height, y + h + border_width)
        result[y+h:bottom_border, left:right] = 0
    
    # 左枠（存在する場合）
    if x > 0:
        left_border = max(0, x - border_width)
        result[y:y+h, left_border:x] = 0
    
    # 右枠（存在する場合）
    if x + w < width:
        right_border = min(width, x + w + border_width)
        result[y:y+h, x+w:right_border] = 0
    
    return result

def apply_gaussian_blur(img, kernel_size=5, sigma=1.0):
    """ガウシアンブラー適用（OpenCV最適化）"""
    img_array = ensure_array(img)
    
    # OpenCVによる高速ガウシアンブラー（ハードウェア最適化）
    if len(img_array.shape) == 3:
        blurred = cv2.GaussianBlur(img_array.astype(np.uint8), (kernel_size, kernel_size), sigma)
    else:
        blurred = cv2.GaussianBlur(img_array.astype(np.uint8), (kernel_size, kernel_size), sigma)
    
    return blurred

def apply_unsharp_mask(img, radius=2, amount=1.5, threshold=0):
    """アンシャープマスク適用（ベクトル化版）"""
    img_array = ensure_array(img).astype(np.float32)
    
    # **ベクトル化によるアンシャープマスク処理**
    # ガウシアンブラー（OpenCV最適化）
    if len(img_array.shape) == 3:
        blurred = cv2.GaussianBlur(img_array.astype(np.uint8), (radius*2+1, radius*2+1), radius/3.0)
    else:
        blurred = cv2.GaussianBlur(img_array.astype(np.uint8), (radius*2+1, radius*2+1), radius/3.0)
    
    blurred = blurred.astype(np.float32)
    
    # マスク計算（完全ベクトル化）
    mask = img_array - blurred
    
    # 閾値処理（ベクトル化）
    if threshold > 0:
        mask = np.where(np.abs(mask) >= threshold, mask, 0)
    
    # シャープネス適用（ベクトル化）
    sharpened = img_array + amount * mask
    
    # クリッピング（ベクトル化）
    result = np.clip(sharpened, 0, 255)
    
    return result.astype(np.uint8)

def adjust_brightness_contrast(img, brightness=0, contrast=1.0):
    """明度・コントラスト調整（完全ベクトル化）"""
    img_array = ensure_array(img).astype(np.float32)
    
    # **完全ベクトル化処理**
    # コントラスト調整（全画素同時）
    adjusted = img_array * contrast
    
    # 明度調整（全画素同時）
    adjusted = adjusted + brightness
    
    # クリッピング（ベクトル化）
    result = np.clip(adjusted, 0, 255)
    
    return result.astype(np.uint8)

def apply_gamma_correction(img, gamma=1.0):
    """ガンマ補正（ベクトル化版）"""
    if gamma == 1.0:
        return img  # 処理不要
    
    img_array = ensure_array(img).astype(np.float32)
    
    # **完全ベクトル化ガンマ補正**
    # 正規化（全画素同時）
    normalized = img_array / 255.0
    
    # ガンマ補正（全画素同時）
    corrected = np.power(normalized, gamma)
    
    # 再スケール（全画素同時）
    result = corrected * 255.0
    
    # クリッピング（ベクトル化）
    result = np.clip(result, 0, 255)
    
    return result.astype(np.uint8)

def create_gradient_mask(height, width, gradient_type="radial", center=None):
    """グラデーションマスク生成（完全ベクトル化）"""
    if center is None:
        center = (height // 2, width // 2)
    
    center_y, center_x = center
    
    # **ベクトル化によるグラデーション生成**
    if gradient_type == "radial":
        # 放射状グラデーション（ベクトル化）
        y_coords, x_coords = np.ogrid[:height, :width]
        distances = np.sqrt((y_coords - center_y)**2 + (x_coords - center_x)**2)
        max_distance = np.sqrt(center_y**2 + center_x**2)
        gradient = 1.0 - (distances / max_distance)
        
    elif gradient_type == "linear_horizontal":
        # 水平グラデーション（ベクトル化）
        x_coords = np.arange(width).reshape(1, -1).astype(np.float32)
        gradient = x_coords / (width - 1)
        gradient = np.broadcast_to(gradient, (height, width))
        
    elif gradient_type == "linear_vertical":
        # 垂直グラデーション（ベクトル化）
        y_coords = np.arange(height).reshape(-1, 1).astype(np.float32)
        gradient = y_coords / (height - 1)
        gradient = np.broadcast_to(gradient, (height, width))
        
    elif gradient_type == "diagonal":
        # 対角グラデーション（ベクトル化）
        y_coords, x_coords = np.ogrid[:height, :width]
        gradient = (y_coords + x_coords) / (height + width - 2)
        
    else:  # uniform
        gradient = np.ones((height, width), dtype=np.float32)
    
    # 値をクリップ（ベクトル化）
    gradient = np.clip(gradient, 0.0, 1.0)
    
    return gradient

def apply_morphological_operations(img, operation="opening", kernel_size=3, iterations=1):
    """モルフォロジー演算（OpenCV最適化）"""
    img_array = ensure_array(img)
    
    # カーネル生成
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    
    # **OpenCVによる高速モルフォロジー演算**
    if operation == "opening":
        result = cv2.morphologyEx(img_array, cv2.MORPH_OPEN, kernel, iterations=iterations)
    elif operation == "closing":
        result = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel, iterations=iterations)
    elif operation == "erosion":
        result = cv2.erode(img_array, kernel, iterations=iterations)
    elif operation == "dilation":
        result = cv2.dilate(img_array, kernel, iterations=iterations)
    elif operation == "gradient":
        result = cv2.morphologyEx(img_array, cv2.MORPH_GRADIENT, kernel, iterations=iterations)
    else:
        result = img_array
    
    return result

def compute_local_statistics(img, window_size=9):
    """局所統計量計算（ベクトル化版）"""
    img_array = ensure_array(img).astype(np.float32)
    
    if len(img_array.shape) == 3:
        img_gray = get_grayscale(img_array)
    else:
        img_gray = img_array
    
    # **ベクトル化による局所統計計算**
    # 畳み込みカーネル
    kernel = np.ones((window_size, window_size), np.float32) / (window_size * window_size)
    
    # 局所平均（OpenCV最適化）
    local_mean = cv2.filter2D(img_gray, -1, kernel)
    
    # 局所分散（ベクトル化）
    img_squared = img_gray ** 2
    local_mean_squared = cv2.filter2D(img_squared, -1, kernel)
    local_variance = local_mean_squared - local_mean ** 2
    
    # 局所標準偏差（ベクトル化）
    local_std = np.sqrt(np.maximum(local_variance, 0))  # 負の値を防ぐ
    
    return {
        'mean': local_mean,
        'variance': local_variance,
        'std': local_std
    }

def normalize_image(img, method="minmax", target_range=(0, 255)):
    """画像正規化（ベクトル化版）"""
    img_array = ensure_array(img).astype(np.float32)
    
    if method == "minmax":
        # **Min-Max正規化（完全ベクトル化）**
        img_min = np.min(img_array)
        img_max = np.max(img_array)
        
        if img_max > img_min:
            normalized = (img_array - img_min) / (img_max - img_min)
        else:
            normalized = np.zeros_like(img_array)
            
    elif method == "zscore":
        # **Z-score正規化（完全ベクトル化）**
        img_mean = np.mean(img_array)
        img_std = np.max([np.std(img_array), 1e-8])  # ゼロ除算防止
        normalized = (img_array - img_mean) / img_std
        
        # 0-1範囲にクリップ
        normalized = np.clip(normalized, -3, 3) / 6.0 + 0.5
        
    else:  # no normalization
        normalized = img_array / 255.0
    
    # ターゲット範囲にスケール（ベクトル化）
    target_min, target_max = target_range
    result = normalized * (target_max - target_min) + target_min
    
    return result.astype(np.uint8)
