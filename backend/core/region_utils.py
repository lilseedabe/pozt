"""
領域選択・操作関連のユーティリティ
"""
import numpy as np
from PIL import Image, ImageDraw
from core.image_utils import ensure_array, ensure_pil

def draw_region_preview(img, region, label="", color="red"):
    """画像に領域を描画して表示"""
    preview = ensure_pil(img).copy()
    draw = ImageDraw.Draw(preview)
    
    if region:
        x, y, width, height = region
        draw.rectangle([x, y, x+width, y+height], outline=color, width=3)
        
        if label:
            text_position = (x, y - 20) if y > 20 else (x, y + height + 5)
            draw.text(text_position, label, fill=color)
    
    return np.array(preview)

def extract_region_from_image(img, region):
    """画像から指定された領域を切り出す"""
    if region and img is not None:
        img_pil = ensure_pil(img)
        x, y, width, height = region
        cropped = img_pil.crop((x, y, x+width, y+height))
        return np.array(cropped)
    return None

def update_preview_with_region(img, evt):
    """画像クリックで領域を設定"""
    if img is None:
        return None, None
    
    try:
        x_start, y_start = img.shape[1] // 2 - 75, img.shape[0] // 2 - 75
        width, height = 150, 150
        
        x_start = max(0, min(x_start, img.shape[1] - width))
        y_start = max(0, min(y_start, img.shape[0] - height))
            
        region = [x_start, y_start, width, height]
        preview = draw_region_preview(img, region, "選択領域")
        
        return preview, region
    except Exception as e:
        print(f"Error in update_preview_with_region: {e}")
        return None, None

def select_grid_position(img, grid_pos, current_region=None):
    """グリッド位置で領域を選択"""
    if img is None:
        return None, None, None
    
    try:
        height, width = img.shape[:2]
        
        if current_region:
            _, _, region_width, region_height = current_region
        else:
            region_width = min(150, width // 3)
            region_height = min(150, height // 3)
        
        grid_row = (grid_pos - 1) // 3
        grid_col = (grid_pos - 1) % 3
        
        x = grid_col * (width // 3) + (width // 6) - (region_width // 2)
        y = grid_row * (height // 3) + (height // 6) - (region_height // 2)
        
        x = max(0, min(x, width - region_width))
        y = max(0, min(y, height - region_height))
        
        region = [x, y, region_width, region_height]
        preview = draw_region_preview(img, region, f"グリッド位置 {grid_pos}")
        extracted = extract_region_from_image(img, region)
        
        return preview, region, extracted
    except Exception as e:
        print(f"グリッド選択エラー: {e}")
        return None, None, None

def move_region(img, region, direction, step=20):
    """領域を指定方向に移動"""
    if img is None or region is None:
        return None, None, None
    
    try:
        x, y, width, height = region
        
        if direction == "up":
            y = max(0, y - step)
        elif direction == "down":
            y = min(img.shape[0] - height, y + step)
        elif direction == "left":
            x = max(0, x - step)
        elif direction == "right":
            x = min(img.shape[1] - width, x + step)
        
        updated_region = [x, y, width, height]
        preview = draw_region_preview(img, updated_region, f"{direction}に移動")
        extracted = extract_region_from_image(img, updated_region)
        
        return preview, updated_region, extracted
    except Exception as e:
        print(f"移動エラー: {e}")
        return None, None, None

def adjust_region_size(img, region, width, height):
    """領域のサイズを調整"""
    if img is None or region is None:
        return None, None, None
    
    try:
        x, y, _, _ = region
        
        max_width = img.shape[1] - x
        max_height = img.shape[0] - y
        
        new_width = min(int(width), max_width)
        new_height = min(int(height), max_height)
        
        updated_region = [x, y, new_width, new_height]
        preview = draw_region_preview(img, updated_region, "サイズ調整")
        extracted = extract_region_from_image(img, updated_region)
        
        return preview, updated_region, extracted
    except Exception as e:
        print(f"サイズ調整エラー: {e}")
        return None, None, None

def update_region_position(img, region, x_pos, y_pos):
    """領域の位置を更新"""
    if img is None or region is None:
        return None, None, None
    
    try:
        _, _, width, height = region
        
        max_x = img.shape[1] - width
        max_y = img.shape[0] - height
        x_pos = max(0, min(int(x_pos), max_x))
        y_pos = max(0, min(int(y_pos), max_y))
        
        updated_region = [x_pos, y_pos, width, height]
        preview = draw_region_preview(img, updated_region, "位置移動")
        extracted = extract_region_from_image(img, updated_region)
        
        return preview, updated_region, extracted
    except Exception as e:
        print(f"位置更新エラー: {e}")
        return None, None, None
