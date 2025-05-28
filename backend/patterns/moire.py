# patterns/moire.py - Gradioコードの数値に完全準拠

import numpy as np
import cv2
from core.image_utils import ensure_array, get_grayscale

def create_high_frequency_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.015):
    """
    超高周波モアレ縞模様：非常に細かい縞模様で、通常表示では見えにくいが拡大すると現れる
    （Gradioコードと完全に同じ実装）
    """
    if isinstance(hidden_img, np.ndarray):
        hidden_array = hidden_img.astype(np.float32)
    else:
        hidden_array = np.array(hidden_img).astype(np.float32)
    
    height, width = hidden_array.shape[:2]
    
    # カラー画像をグレースケールに変換
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        hidden_gray = hidden_array
    
    # 隠し画像のコントラスト強調（より強く）
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.5 + 0.5, 0, 1)  # コントラスト強化
    
    # エッジ検出（より明確に）
    edges = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 80, 150)  # 閾値を調整
    edges_norm = edges / 255.0
    
    # 結果画像を初期化
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # 縞模様の基本値（グレーではなく、より明確な白黒に）
    dark_value = 110  # 暗い部分の値
    light_value = 146  # 明るい部分の値
    
    if pattern_type == "horizontal":
        # 横縞パターン（より密に）
        for y in range(height):
            for x in range(width):
                # 2倍の周波数で縞模様を生成
                base_stripe = 1 if ((y * 2) % 2) == 0 else 0
                
                # 隠し画像の情報を取得
                pixel_brightness = hidden_contrast[y, x]
                pixel_edge = edges_norm[y, x]
                
                # 縞の明度を隠し画像に基づいて調整（より明確に）
                if base_stripe == 1:  # 明るい縞
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    if pixel_edge > 0.5:  # エッジをより強調
                        adjustment *= 2.0  # エッジ強調を強化
                    stripe_value = light_value + adjustment
                else:  # 暗い縞
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    if pixel_edge > 0.5:
                        adjustment *= 2.0
                    stripe_value = dark_value + adjustment
                
                # 値をクリップ（範囲を広げてコントラストを強化）
                stripe_value = np.clip(stripe_value, 90, 166)
                
                # 全チャンネルに同じ値を設定
                result[y, x] = [stripe_value, stripe_value, stripe_value]
    
    elif pattern_type == "vertical":
        # 縦縞パターン（横縞と同様の処理）
        for x in range(width):
            for y in range(height):
                base_stripe = 1 if ((x * 2) % 2) == 0 else 0
                
                pixel_brightness = hidden_contrast[y, x]
                pixel_edge = edges_norm[y, x]
                
                if base_stripe == 1:
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    if pixel_edge > 0.5:
                        adjustment *= 2.0
                    stripe_value = light_value + adjustment
                else:
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    if pixel_edge > 0.5:
                        adjustment *= 2.0
                    stripe_value = dark_value + adjustment
                
                stripe_value = np.clip(stripe_value, 90, 166)
                result[y, x] = [stripe_value, stripe_value, stripe_value]
    
    return result.astype(np.uint8)

def create_moire_hidden_stripes(hidden_img, pattern_type="horizontal", strength=0.02):
    """
    モアレ効果を利用した隠し画像埋め込み（改良版）
    均一な縞模様に隠し画像の情報を埋め込む
    （Gradioコードと完全に同じ実装）
    """
    if isinstance(hidden_img, np.ndarray):
        hidden_array = hidden_img.astype(np.float32)
    else:
        hidden_array = np.array(hidden_img).astype(np.float32)
    
    height, width = hidden_array.shape[:2]
    
    # カラー画像をグレースケールに変換
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        hidden_gray = hidden_array
    
    # 隠し画像の正規化とコントラスト強調
    hidden_norm = hidden_gray / 255.0
    hidden_contrast = np.clip((hidden_norm - 0.5) * 2.0 + 0.5, 0, 1)
    
    # エッジ検出（より強いエッジを検出）- 閾値を上げて検出を厳しく
    edges = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 80, 200)
    edges_norm = edges / 255.0
    
    # 結果画像を初期化
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    if pattern_type == "horizontal":
        # 横縞（水平方向の縞）
        for y in range(height):
            # 基本の縞パターン（1ピクセル幅の縞）
            base_stripe = (y % 2) * 255
            
            for x in range(width):
                # 隠し画像の情報を取得
                pixel_brightness = hidden_contrast[y, x]
                pixel_edge = edges_norm[y, x]
                
                # 縞の明度を隠し画像に基づいて微調整（強度を下げる）
                if base_stripe == 255:  # 白い縞
                    # 明るい部分は少し明るく、暗い部分は少し暗く
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    if pixel_edge > 0.5:  # エッジ閾値を上げる（0.3→0.5）
                        adjustment *= 1.5  # エッジ強調を弱める（2.0→1.5）
                    stripe_value = 255 + adjustment
                else:  # 黒い縞
                    # 暗い部分は少し暗く、明るい部分は少し明るく
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    if pixel_edge > 0.5:  # エッジ閾値を上げる
                        adjustment *= 1.5  # エッジ強調を弱める
                    stripe_value = 0 + adjustment
                
                # 値をクリップ
                stripe_value = np.clip(stripe_value, 0, 255)
                
                # 全チャンネルに同じ値を設定
                result[y, x] = [stripe_value, stripe_value, stripe_value]
    
    elif pattern_type == "vertical":
        # 縦縞（垂直方向の縞）
        for x in range(width):
            # 基本の縞パターン（1ピクセル幅の縞）
            base_stripe = (x % 2) * 255
            
            for y in range(height):
                # 隠し画像の情報を取得
                pixel_brightness = hidden_contrast[y, x]
                pixel_edge = edges_norm[y, x]
                
                # 縞の明度を隠し画像に基づいて微調整
                if base_stripe == 255:  # 白い縞
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    if pixel_edge > 0.5:
                        adjustment *= 1.5
                    stripe_value = 255 + adjustment
                else:  # 黒い縞
                    adjustment = (pixel_brightness - 0.5) * strength * 255
                    if pixel_edge > 0.5:
                        adjustment *= 1.5
                    stripe_value = 0 + adjustment
                
                # 値をクリップ
                stripe_value = np.clip(stripe_value, 0, 255)
                
                # 全チャンネルに同じ値を設定
                result[y, x] = [stripe_value, stripe_value, stripe_value]
    
    return result.astype(np.uint8)

def create_adaptive_moire_stripes(hidden_img, pattern_type="horizontal", mode="adaptive"):
    """
    適応型モアレ縞模様：モードに応じて効果の強さを調整
    （Gradioコードと完全に同じ実装）
    """
    # モードに応じた強度設定（Gradioコードの値そのまま）
    strength_map = {
        "high_frequency": 0.015,    # 超高周波モード（強度を上げる）
        "adaptive": 0.02,           # 標準
        "adaptive_subtle": 0.015,   # 控えめ
        "adaptive_strong": 0.03,    # 強め
        "adaptive_minimal": 0.01,   # 最小
        "perfect_subtle": 0.025,    # 弱めに調整
        "ultra_subtle": 0.02,       # 弱めに調整
        "near_perfect": 0.018,      # 弱めに調整
        "color_preserving": 0.025,  # 色調保存モード
        "hue_preserving": 0.02,     # 色相保存モード
        "blended": 0.022           # ブレンドモード
    }
    
    strength = strength_map.get(mode, 0.02)
    
    # モードに応じて関数を選択
    if mode == "high_frequency":
        return create_high_frequency_moire_stripes(hidden_img, pattern_type, strength)
    else:
        # モアレ縞模様を生成
        return create_moire_hidden_stripes(hidden_img, pattern_type, strength)

def create_perfect_moire_pattern(hidden_img, pattern_type="horizontal"):
    """
    完璧なモアレパターン：均一な縞模様に隠し画像を控えめに埋め込む
    （Gradioコードと完全に同じ実装）
    """
    if isinstance(hidden_img, np.ndarray):
        hidden_array = hidden_img.astype(np.float32)
    else:
        hidden_array = np.array(hidden_img).astype(np.float32)
    
    height, width = hidden_array.shape[:2]
    
    # グレースケール化
    if len(hidden_array.shape) == 3:
        hidden_gray = cv2.cvtColor(hidden_array.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32)
    else:
        hidden_gray = hidden_array
    
    # 隠し画像の前処理
    hidden_norm = hidden_gray / 255.0
    
    # コントラストを大幅に強化
    hidden_contrast = np.clip((hidden_norm - 0.5) * 3.0 + 0.5, 0, 1)
    
    # エッジを強く検出
    edges = cv2.Canny((hidden_contrast * 255).astype(np.uint8), 50, 150)
    edges_norm = edges / 255.0
    
    # 結果画像
    result = np.zeros((height, width, 3), dtype=np.float32)
    
    # 強度を下げる
    strength = 0.04  # 0.08から0.04に下げる
    
    if pattern_type == "horizontal":
        # 横縞パターン
        for y in range(height):
            # 基本の縞（1ピクセル幅）
            base_stripe = (y % 2) * 255
            
            for x in range(width):
                pixel_value = hidden_contrast[y, x]
                edge_value = edges_norm[y, x]
                
                # 縞の値を計算（調整を控えめに）
                if base_stripe == 255:
                    # 白い縞：隠し画像が明るいほどより白く
                    adjustment = pixel_value * strength * 255
                    if edge_value > 0.3:
                        adjustment *= 1.2  # エッジ強調を弱める（1.5→1.2）
                    stripe_value = 220 + adjustment  # ベース白を明るく（200→220）
                else:
                    # 黒い縞：隠し画像が暗いほどより黒く
                    adjustment = (1 - pixel_value) * strength * 255
                    if edge_value > 0.3:
                        adjustment *= 1.2
                    stripe_value = 40 - adjustment  # ベース黒を少し明るく（55→40）
                
                stripe_value = np.clip(stripe_value, 0, 255)
                result[y, x] = [stripe_value, stripe_value, stripe_value]
                
    else:  # vertical
        # 縦縞パターン
        for x in range(width):
            base_stripe = (x % 2) * 255
            
            for y in range(height):
                pixel_value = hidden_contrast[y, x]
                edge_value = edges_norm[y, x]
                
                if base_stripe == 255:
                    adjustment = pixel_value * strength * 255
                    if edge_value > 0.3:
                        adjustment *= 1.2
                    stripe_value = 220 + adjustment
                else:
                    adjustment = (1 - pixel_value) * strength * 255
                    if edge_value > 0.3:
                        adjustment *= 1.2
                    stripe_value = 40 - adjustment
                
                stripe_value = np.clip(stripe_value, 0, 255)
                result[y, x] = [stripe_value, stripe_value, stripe_value]
    
    return result.astype(np.uint8)

# 既存関数のエイリアス（互換性維持）
def create_fast_moire_stripes(hidden_img, pattern_type="horizontal", strength=0.02):
    """基本モアレ縞模様（互換性維持）"""
    return create_moire_hidden_stripes(hidden_img, pattern_type, strength)

def create_fast_high_frequency_stripes(hidden_img, pattern_type="horizontal", strength=0.015):
    """高周波モアレ縞模様（互換性維持）"""
    return create_high_frequency_moire_stripes(hidden_img, pattern_type, strength)
