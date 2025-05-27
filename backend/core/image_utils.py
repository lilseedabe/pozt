"""
基本的な画像処理ユーティリティ
"""
import numpy as np
from PIL import Image, ImageDraw
import cv2
from config.settings import TARGET_WIDTH, TARGET_HEIGHT

def ensure_array(img):
    """入力がPIL画像かnumpy配列かを確認し、numpy配列に変換"""
    if isinstance(img, np.ndarray):
        return img
    return np.array(img)

def ensure_pil(img):
    """入力がPIL画像かnumpy配列かを確認し、PIL画像に変換"""
    if isinstance(img, np.ndarray):
        return Image.fromarray(img.astype('uint8'))
    return img

def get_grayscale(img):
    """画像をグレースケールに変換"""
    img_array = ensure_array(img)
    
    if len(img_array.shape) == 3:
        return cv2.cvtColor(img_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    return img_array.astype(np.float32)

def enhance_contrast(img, factor=2.0, center=0.5):
    """画像のコントラストを強調"""
    img_array = ensure_array(img).astype(np.float32)
    
    if len(img_array.shape) == 3:
        img_gray = get_grayscale(img_array)
    else:
        img_gray = img_array
    
    # 正規化とコントラスト強調
    img_norm = img_gray / 255.0
    img_contrast = np.clip((img_norm - center) * factor + center, 0, 1)
    
    return img_contrast

def detect_edges(img, low_threshold=80, high_threshold=150):
    """エッジ検出"""
    img_array = ensure_array(img)
    
    if len(img_array.shape) == 3:
        img_gray = cv2.cvtColor(img_array.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    else:
        img_gray = img_array.astype(np.uint8)
    
    edges = cv2.Canny(img_gray, low_threshold, high_threshold)
    return edges / 255.0  # 正規化

def resize_to_fixed_size(img, method='contain'):
    """画像を固定サイズ（2430×3240）にリサイズ"""
    img_pil = ensure_pil(img)
    
    if method == 'stretch':
        return img_pil.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    orig_width, orig_height = img_pil.size
    orig_aspect = orig_width / orig_height
    target_aspect = TARGET_WIDTH / TARGET_HEIGHT
    
    if method == 'contain':
        if orig_aspect > target_aspect:
            new_width = TARGET_WIDTH
            new_height = int(TARGET_WIDTH / orig_aspect)
        else:
            new_height = TARGET_HEIGHT
            new_width = int(TARGET_HEIGHT * orig_aspect)
        
        resized = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        canvas = Image.new('RGB', (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0))
        x_offset = (TARGET_WIDTH - new_width) // 2
        y_offset = (TARGET_HEIGHT - new_height) // 2
        canvas.paste(resized, (x_offset, y_offset))
        
        return canvas
    
    elif method == 'cover':
        if orig_aspect > target_aspect:
            new_height = TARGET_HEIGHT
            new_width = int(TARGET_HEIGHT * orig_aspect)
        else:
            new_width = TARGET_WIDTH
            new_height = int(TARGET_WIDTH / orig_aspect)
        
        resized = img_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        x_offset = (new_width - TARGET_WIDTH) // 2
        y_offset = (new_height - TARGET_HEIGHT) // 2
        cropped = resized.crop((x_offset, y_offset, x_offset + TARGET_WIDTH, y_offset + TARGET_HEIGHT))
        
        return cropped

def calculate_resize_factors(orig_img, resize_method):
    """リサイズの比率とオフセットを計算"""
    if isinstance(orig_img, np.ndarray):
        orig_height, orig_width = orig_img.shape[:2]
    else:
        orig_width, orig_height = orig_img.size
    
    if resize_method == 'contain':
        scale_x = TARGET_WIDTH / orig_width
        scale_y = TARGET_HEIGHT / orig_height
        scale = min(scale_x, scale_y)
        offset_x = (TARGET_WIDTH - int(orig_width * scale)) // 2
        offset_y = (TARGET_HEIGHT - int(orig_height * scale)) // 2
    elif resize_method == 'cover':
        scale_x = TARGET_WIDTH / orig_width
        scale_y = TARGET_HEIGHT / orig_height
        scale = max(scale_x, scale_y)
        offset_x = -int((orig_width * scale - TARGET_WIDTH) / 2 / scale) * scale
        offset_y = -int((orig_height * scale - TARGET_HEIGHT) / 2 / scale) * scale
    else:  # stretch
        scale_x = TARGET_WIDTH / orig_width
        scale_y = TARGET_HEIGHT / orig_height
        scale = scale_x  # 水平方向のスケールを基準に
        offset_x = 0
        offset_y = 0
    
    return scale_x, scale_y, scale, offset_x, offset_y

def add_black_border(img, region, border_width=3):
    """グレー領域の周りに黒い枠を追加（同時対比効果を利用）"""
    if region is None:
        return img
    
    result = ensure_array(img).copy()
    x, y, w, h = region
    
    # 画像サイズを取得
    height, width = result.shape[:2]
    
    # 境界チェック
    top = max(0, y - border_width)
    bottom = min(height, y + h + border_width)
    left = max(0, x - border_width)
    right = min(width, x + w + border_width)
    
    # 上枠（存在する場合）
    if y > 0:
        top_border = max(0, y - border_width)
        result[top_border:y, max(0, x-border_width):min(width, x+w+border_width)] = 0
    
    # 下枠（存在する場合）
    if y + h < height:
        bottom_border = min(height, y + h + border_width)
        result[y+h:bottom_border, max(0, x-border_width):min(width, x+w+border_width)] = 0
    
    # 左枠（存在する場合）
    if x > 0:
        left_border = max(0, x - border_width)
        result[y:y+h, left_border:x] = 0
    
    # 右枠（存在する場合）
    if x + w < width:
        right_border = min(width, x + w + border_width)
        result[y:y+h, x+w:right_border] = 0
    
    return result
