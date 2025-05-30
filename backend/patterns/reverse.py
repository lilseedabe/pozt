# backend/patterns/reverse.py - 超軽量・メモリスパイク対策版（512MB制限対応）
import numpy as np
import cv2
from PIL import Image
import gc
import sys
from core.image_utils import ensure_array, ensure_pil

# **メモリ制限対応: グローバル設定**
MAX_IMAGE_DIMENSION = 1024  # 最大サイズを1024pxに制限
MEMORY_SAFE_SIZE = 800      # 安全サイズ
CHUNK_SIZE = 256           # チャンク処理サイズ

def extract_hidden_image_from_moire(moire_img, method="fourier_analysis", enhancement_level=2.0):
    """
    モアレ効果画像から隠し画像を抽出（超軽量・メモリスパイク対策版）
    512MB制限環境でも安全に動作するよう最適化
    """
    # **メモリ対策1: 即座のガベージコレクション**
    gc.collect()
    
    # **メモリ対策2: 入力画像の軽量化**
    moire_array = prepare_lightweight_image(moire_img)
    
    try:
        if method == "pattern_subtraction":
            # 最もメモリ効率的な方法を優先
            return extract_via_pattern_subtraction_ultra_light(moire_array, enhancement_level)
        elif method == "frequency_filtering":
            return extract_via_frequency_filtering_ultra_light(moire_array, enhancement_level)
        elif method == "adaptive_detection":
            return extract_via_adaptive_detection_ultra_light(moire_array, enhancement_level)
        else:  # fourier_analysis
            return extract_via_fourier_analysis_ultra_light(moire_array, enhancement_level)
    finally:
        # **メモリ対策3: 処理後の即座クリーンアップ**
        del moire_array
        gc.collect()

def prepare_lightweight_image(moire_img):
    """
    画像を軽量化して準備（メモリスパイク防止）
    """
    # **軽量化1: 配列変換の最適化**
    if isinstance(moire_img, np.ndarray):
        img_array = moire_img
    else:
        img_array = np.array(moire_img, dtype=np.uint8)  # 最初からuint8
    
    height, width = img_array.shape[:2]
    
    # **軽量化2: 積極的なサイズ制限**
    if max(height, width) > MAX_IMAGE_DIMENSION:
        # アスペクト比保持でリサイズ
        scale = MAX_IMAGE_DIMENSION / max(height, width)
        new_height = int(height * scale)
        new_width = int(width * scale)
        
        # OpenCVで高速リサイズ（メモリ効率的）
        img_array = cv2.resize(img_array, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        print(f"📏 Image resized to {new_width}x{new_height} for memory efficiency")
    
    # **軽量化3: さらに大きい場合の緊急サイズ制限**
    if max(img_array.shape[:2]) > MEMORY_SAFE_SIZE:
        scale = MEMORY_SAFE_SIZE / max(img_array.shape[:2])
        new_h = int(img_array.shape[0] * scale)
        new_w = int(img_array.shape[1] * scale)
        img_array = cv2.resize(img_array, (new_w, new_h), interpolation=cv2.INTER_AREA)
        print(f"⚠️ Emergency resize to {new_w}x{new_h} for memory safety")
    
    return img_array

def extract_via_pattern_subtraction_ultra_light(moire_array, enhancement_level=2.0):
    """
    パターン減算による抽出（超軽量版）- 最もメモリ効率的な方法
    """
    height, width = moire_array.shape[:2]
    
    # **軽量化1: グレースケール変換の最適化**
    if len(moire_array.shape) == 3:
        gray = cv2.cvtColor(moire_array, cv2.COLOR_RGB2GRAY)
        del moire_array  # 即座に削除
        gc.collect()
    else:
        gray = moire_array.copy()
        del moire_array
    
    # **軽量化2: 小さなサンプルでの相関計算**
    sample_size = min(64, height // 8, width // 8)  # さらに小さなサンプル
    sample_y = height // 4
    sample_x = width // 4
    
    gray_sample = gray[sample_y:sample_y+sample_size, sample_x:sample_x+sample_size].astype(np.float32)
    
    # **軽量化3: 効率的パターン生成（メモリを使い回し）**
    y_pattern = np.arange(sample_size, dtype=np.uint8).reshape(-1, 1)
    h_pattern_sample = np.broadcast_to((y_pattern % 2) * 255, (sample_size, sample_size)).astype(np.float32)
    
    x_pattern = np.arange(sample_size, dtype=np.uint8).reshape(1, -1)
    v_pattern_sample = np.broadcast_to((x_pattern % 2) * 255, (sample_size, sample_size)).astype(np.float32)
    
    # **軽量化4: 相関計算の効率化**
    h_corr = np.corrcoef(gray_sample.flatten(), h_pattern_sample.flatten())[0, 1]
    v_corr = np.corrcoef(gray_sample.flatten(), v_pattern_sample.flatten())[0, 1]
    
    # 中間データを削除
    del gray_sample, h_pattern_sample, v_pattern_sample
    gc.collect()
    
    # **軽量化5: チャンク処理によるパターン減算**
    if abs(h_corr) > abs(v_corr):
        # 水平パターン
        pattern_type = "horizontal"
        correlation_strength = abs(h_corr)
    else:
        # 垂直パターン
        pattern_type = "vertical"
        correlation_strength = abs(v_corr)
    
    # **軽量化6: メモリ効率的な結果生成**
    result = process_in_chunks(gray, pattern_type, correlation_strength, enhancement_level)
    
    del gray
    gc.collect()
    
    # **軽量化7: RGB変換の最適化**
    if len(result.shape) == 2:
        # グレースケールのまま返す（メモリ節約）
        return result
    else:
        return result

def process_in_chunks(gray, pattern_type, correlation_strength, enhancement_level):
    """
    チャンク処理でメモリ使用量を制限
    """
    height, width = gray.shape
    result = np.zeros_like(gray, dtype=np.uint8)
    
    # **チャンク処理: 行ごとに処理**
    chunk_height = min(CHUNK_SIZE, height)
    
    for start_y in range(0, height, chunk_height):
        end_y = min(start_y + chunk_height, height)
        chunk = gray[start_y:end_y].astype(np.float32)
        
        # パターン生成
        if pattern_type == "horizontal":
            y_indices = np.arange(start_y, end_y).reshape(-1, 1)
            pattern_chunk = np.broadcast_to((y_indices % 2) * 255.0, chunk.shape)
        else:  # vertical
            x_indices = np.arange(width).reshape(1, -1)
            pattern_chunk = np.broadcast_to((x_indices % 2) * 255.0, chunk.shape)
        
        # パターン減算
        subtraction_strength = np.clip(correlation_strength * 0.6, 0.2, 0.7)
        difference = chunk - pattern_chunk * subtraction_strength
        
        # 強調処理
        enhanced = difference * enhancement_level + 128
        result[start_y:end_y] = np.clip(enhanced, 0, 255).astype(np.uint8)
        
        # チャンクデータを削除
        del chunk, pattern_chunk, difference, enhanced
    
    return result

def extract_via_frequency_filtering_ultra_light(moire_array, enhancement_level=2.0):
    """
    周波数フィルタリング（超軽量版）
    """
    height, width = moire_array.shape[:2]
    
    # グレースケール変換
    if len(moire_array.shape) == 3:
        gray = cv2.cvtColor(moire_array, cv2.COLOR_RGB2GRAY)
        del moire_array
        gc.collect()
    else:
        gray = moire_array.copy()
        del moire_array
    
    # **軽量化: 小さなカーネルサイズ**
    kernel_size = max(3, min(height, width) // 300) | 1
    
    # ブラー処理
    blurred = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
    
    # エッジ検出
    mean_intensity = np.mean(blurred)
    low_threshold = max(15, int(mean_intensity * 0.2))
    high_threshold = min(100, int(mean_intensity * 0.6))
    
    edges = cv2.Canny(blurred, low_threshold, high_threshold)
    del blurred
    
    # モルフォロジー演算
    morph_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    processed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, morph_kernel)
    del edges
    
    # マスク処理
    stripe_mask = (processed_edges > 0).astype(np.float32)
    del processed_edges
    
    # ブラー
    smoothed_mask = cv2.GaussianBlur(stripe_mask, (5, 5), 0)
    del stripe_mask
    
    # 結果生成
    hidden_mask = 1.0 - smoothed_mask
    result = gray.astype(np.float32) * hidden_mask * enhancement_level
    
    del gray, smoothed_mask, hidden_mask
    gc.collect()
    
    return np.clip(result, 0, 255).astype(np.uint8)

def extract_via_adaptive_detection_ultra_light(moire_array, enhancement_level=2.0):
    """
    適応的検出（超軽量版）
    """
    height, width = moire_array.shape[:2]
    
    # グレースケール変換
    if len(moire_array.shape) == 3:
        gray = cv2.cvtColor(moire_array, cv2.COLOR_RGB2GRAY)
        del moire_array
        gc.collect()
    else:
        gray = moire_array.copy()
        del moire_array
    
    # **軽量化: 小さなウィンドウサイズ**
    window_size = max(5, min(height, width) // 150) | 1
    
    # 局所統計計算（軽量版）
    kernel = np.ones((window_size, window_size), np.float32) / (window_size * window_size)
    local_mean = cv2.filter2D(gray.astype(np.float32), -1, kernel)
    
    # 簡易的な分散計算
    diff = gray.astype(np.float32) - local_mean
    local_variance = cv2.filter2D(diff ** 2, -1, kernel)
    local_std = np.sqrt(np.maximum(local_variance, 1.0))
    
    del diff, local_variance
    
    # 適応的閾値
    global_std = np.std(gray)
    adaptive_factor = np.clip(global_std / 60.0, 0.2, 1.2)
    adaptive_threshold = local_mean + local_std * adaptive_factor
    
    del local_mean, local_std
    
    # マスク生成
    hidden_mask = (gray.astype(np.float32) > adaptive_threshold).astype(np.float32)
    del adaptive_threshold
    
    # 結果生成
    result = gray.astype(np.float32) * hidden_mask * enhancement_level
    
    del gray, hidden_mask
    gc.collect()
    
    return np.clip(result, 0, 255).astype(np.uint8)

def extract_via_fourier_analysis_ultra_light(moire_array, enhancement_level=2.0):
    """
    フーリエ解析（超軽量版）- 最小限の実装
    """
    height, width = moire_array.shape[:2]
    
    # サイズ制限をさらに厳しく
    if max(height, width) > 512:
        scale = 512 / max(height, width)
        new_h = int(height * scale)
        new_w = int(width * scale)
        if len(moire_array.shape) == 3:
            resized = cv2.resize(moire_array, (new_w, new_h))
            gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
        else:
            gray = cv2.resize(moire_array, (new_w, new_h))
        del moire_array, resized
    else:
        if len(moire_array.shape) == 3:
            gray = cv2.cvtColor(moire_array, cv2.COLOR_RGB2GRAY)
            del moire_array
        else:
            gray = moire_array.copy()
            del moire_array
    
    gc.collect()
    
    # 簡易的なFFT処理
    try:
        f_transform = np.fft.fft2(gray.astype(np.float32))
        f_shift = np.fft.fftshift(f_transform)
        del f_transform
        
        # 簡易フィルタ
        h, w = gray.shape
        center_y, center_x = h // 2, w // 2
        radius = min(h, w) // 8
        
        y, x = np.ogrid[:h, :w]
        mask = ((x - center_x)**2 + (y - center_y)**2) <= radius**2
        
        filtered = f_shift * mask.astype(np.float32)
        del f_shift, mask
        
        # 逆FFT
        f_ishift = np.fft.ifftshift(filtered)
        img_back = np.abs(np.fft.ifft2(f_ishift))
        del filtered, f_ishift
        
        # 正規化
        img_min, img_max = np.min(img_back), np.max(img_back)
        if img_max > img_min:
            result = (img_back - img_min) / (img_max - img_min) * 255 * enhancement_level
        else:
            result = np.full_like(img_back, 128)
        
        del img_back
        
    except Exception as e:
        print(f"⚠️ FFT failed, using fallback: {e}")
        # フォールバック：単純な処理
        result = gray.astype(np.float32) * enhancement_level
    
    del gray
    gc.collect()
    
    return np.clip(result, 0, 255).astype(np.uint8)

def enhance_extracted_image_optimized(extracted_img, method="histogram_equalization"):
    """
    抽出された隠し画像を強調（超軽量版）
    """
    if method == "histogram_equalization":
        if len(extracted_img.shape) == 3:
            # チャンネル別処理
            result = np.zeros_like(extracted_img)
            for i in range(3):
                result[:,:,i] = cv2.equalizeHist(extracted_img[:,:,i])
            return result
        else:
            return cv2.equalizeHist(extracted_img)
    
    elif method == "clahe":
        # 軽量CLAHE設定
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        
        if len(extracted_img.shape) == 3:
            result = np.zeros_like(extracted_img)
            for i in range(3):
                result[:,:,i] = clahe.apply(extracted_img[:,:,i])
            return result
        else:
            return clahe.apply(extracted_img)
    
    elif method == "gamma_correction":
        # 軽量ガンマ補正
        gamma = 0.7
        normalized = extracted_img.astype(np.float32) / 255.0
        corrected = np.power(normalized, gamma)
        result = (corrected * 255.0).astype(np.uint8)
        del normalized, corrected
        return result
    
    return extracted_img

# エイリアス関数
def enhance_extracted_image(extracted_img, method="histogram_equalization"):
    """エイリアス関数（互換性維持）"""
    return enhance_extracted_image_optimized(extracted_img, method)
