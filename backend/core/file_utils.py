"""
ファイル操作関連のユーティリティ
"""
import os
import tempfile
from PIL import Image
import numpy as np
from core.image_utils import ensure_pil
from config.settings import TARGET_WIDTH, TARGET_HEIGHT

def save_as_png(img_array, filename_prefix="hidden_image"):
    """画像をPNG形式で保存（最高品質）"""
    try:
        # PIL画像に変換
        img_pil = ensure_pil(img_array)
        
        # ファイル名を生成
        timestamp = tempfile.gettempprefix()
        filename = f"{filename_prefix}_{TARGET_WIDTH}x{TARGET_HEIGHT}_{timestamp}.png"
        
        # 一時ディレクトリにPNG形式で保存
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, filename)
        
        # PNG保存オプション
        png_info = img_pil.info
        img_pil.save(
            output_path, 
            "PNG", 
            optimize=True,      # ファイルサイズ最適化
            compress_level=9,   # 最高圧縮レベル（品質は劣化しない）
            **png_info         # メタデータを保持
        )
        
        return output_path
    except Exception as e:
        print(f"PNG保存エラー: {e}")
        return None
