"""
形状マスク生成システム - メモリ効率最適化版
様々な形状（円、星、ハート、和柄、アラベスク柄）のマスク生成
"""
import numpy as np
import cv2
from functools import lru_cache
from typing import Tuple, Dict, Any, Optional
import math

# メモリ効率を重視した最適化キャッシュ設定
CACHE_SIZE = 64  # 128から64に削減（バランス重視）

# 形状タイプごとの複雑さランク（1-5、5が最も複雑）
SHAPE_COMPLEXITY = {
    "rectangle": 1,  # 最も単純
    "circle": 1,    # 非常に単純
    "hexagon": 2,   # やや単純
    "star": 3,      # 中程度
    "heart": 3,     # 中程度
    "japanese": 4,  # 複雑
    "arabesque": 5  # 最も複雑
}

# メモリ使用量警告のしきい値（MB）
MEMORY_WARNING_THRESHOLD = 100  # MB

# 複雑な形状使用後の自動キャッシュクリア閾値
COMPLEXITY_THRESHOLD = 4  # この値以上の複雑さでキャッシュ管理を厳格化

@lru_cache(maxsize=CACHE_SIZE)
def create_circle_mask(width: int, height: int, center_x: Optional[float] = None, center_y: Optional[float] = None, radius: Optional[float] = None) -> np.ndarray:
    """円形マスクの高速生成（ベクトル化）"""
    if center_x is None:
        center_x = width / 2
    if center_y is None:
        center_y = height / 2
    if radius is None:
        radius = min(width, height) / 2 * 0.8
    
    # メッシュグリッド生成（メモリ効率重視）
    y_indices, x_indices = np.ogrid[:height, :width]
    
    # 距離計算（ベクトル化）
    distances = np.sqrt((x_indices - center_x) ** 2 + (y_indices - center_y) ** 2)
    
    # マスク生成（Boolean配列で省メモリ）
    mask = distances <= radius
    
    return mask.astype(np.uint8) * 255

@lru_cache(maxsize=CACHE_SIZE)
def create_star_mask(width: int, height: int, num_points: int = 5, inner_radius_ratio: float = 0.4, rotation: float = 0) -> np.ndarray:
    """星形マスクの高速生成（ベクトル化）"""
    print(f"⭐ Creating star mask: {width}x{height}, points={num_points}, inner_ratio={inner_radius_ratio}, rotation={rotation}")
    
    center_x, center_y = width / 2, height / 2
    outer_radius = min(width, height) / 2 * 0.8
    inner_radius = outer_radius * inner_radius_ratio
    
    print(f"⭐ Star geometry: center=({center_x:.1f}, {center_y:.1f}), outer_radius={outer_radius:.1f}, inner_radius={inner_radius:.1f}")
    
    # 角度配列の事前計算
    angle_step = 2 * math.pi / num_points
    angles = np.arange(num_points * 2) * angle_step / 2 + rotation
    
    # 外点と内点の座標計算（ベクトル化）
    radii = np.where(np.arange(num_points * 2) % 2 == 0, outer_radius, inner_radius)
    star_x = center_x + radii * np.cos(angles)
    star_y = center_y + radii * np.sin(angles)
    
    print(f"⭐ Star points: {len(star_x)} points generated")
    
    # OpenCVによる高速ポリゴン描画
    mask = np.zeros((height, width), dtype=np.uint8)
    points = np.column_stack((star_x, star_y)).astype(np.int32)
    cv2.fillPoly(mask, [points], 255)
    
    # マスクの統計情報をログ出力
    white_pixels = np.sum(mask == 255)
    total_pixels = width * height
    coverage = (white_pixels / total_pixels) * 100
    print(f"⭐ Star mask created: {white_pixels}/{total_pixels} pixels ({coverage:.1f}% coverage)")
    
    return mask

@lru_cache(maxsize=CACHE_SIZE)
def create_heart_mask(width: int, height: int, size_factor: float = 0.8) -> np.ndarray:
    """ハート形マスクの高速生成（数学関数）"""
    center_x, center_y = width / 2, height / 2
    scale = min(width, height) / 2 * size_factor
    
    # メッシュグリッド生成
    y_indices, x_indices = np.ogrid[:height, :width]
    
    # 正規化座標
    x_norm = (x_indices - center_x) / scale
    y_norm = (y_indices - center_y) / scale
    
    # ハート方程式: (x^2 + y^2 - 1)^3 - x^2 * y^3 <= 0
    # 回転と調整を加えた最適化版
    heart_eq = (x_norm**2 + y_norm**2 - 1)**3 - x_norm**2 * y_norm**3
    
    # マスク生成
    mask = (heart_eq <= 0).astype(np.uint8) * 255
    
    return mask

@lru_cache(maxsize=CACHE_SIZE)
def create_hexagon_mask(width: int, height: int, size_factor: float = 0.8) -> np.ndarray:
    """六角形マスクの高速生成"""
    center_x, center_y = width / 2, height / 2
    radius = min(width, height) / 2 * size_factor
    
    # 六角形の頂点計算
    angles = np.arange(6) * math.pi / 3
    hex_x = center_x + radius * np.cos(angles)
    hex_y = center_y + radius * np.sin(angles)
    
    # OpenCVによる高速描画
    mask = np.zeros((height, width), dtype=np.uint8)
    points = np.column_stack((hex_x, hex_y)).astype(np.int32)
    cv2.fillPoly(mask, [points], 255)
    
    return mask

@lru_cache(maxsize=CACHE_SIZE)
def create_traditional_japanese_mask(width: int, height: int, pattern_type: str = "sakura") -> np.ndarray:
    """和柄マスクの生成（桜、麻の葉、青海波）"""
    mask = np.zeros((height, width), dtype=np.uint8)
    center_x, center_y = width / 2, height / 2
    
    if pattern_type == "sakura":
        # 桜の花びら（5枚の楕円組み合わせ）
        petal_radius = min(width, height) / 2 * 0.3
        for i in range(5):
            angle = i * 2 * math.pi / 5
            petal_x = center_x + petal_radius * 0.6 * math.cos(angle)
            petal_y = center_y + petal_radius * 0.6 * math.sin(angle)
            
            # 楕円の花びら描画
            axes = (int(petal_radius * 0.8), int(petal_radius * 0.4))
            cv2.ellipse(mask, (int(petal_x), int(petal_y)), axes, 
                       math.degrees(angle), 0, 360, 255, -1)
    
    elif pattern_type == "asanoha":
        # 麻の葉パターン（六角形の組み合わせ）
        base_radius = min(width, height) / 6
        for i in range(3):
            for j in range(3):
                hex_x = center_x + (i - 1) * base_radius * 1.5
                hex_y = center_y + (j - 1) * base_radius * math.sqrt(3)
                
                # 六角形描画
                angles = np.arange(6) * math.pi / 3
                hex_points_x = hex_x + base_radius * np.cos(angles)
                hex_points_y = hex_y + base_radius * np.sin(angles)
                points = np.column_stack((hex_points_x, hex_points_y)).astype(np.int32)
                cv2.polylines(mask, [points], True, 255, 2)
    
    elif pattern_type == "seigaiha":
        # 青海波（重なる円弧）
        wave_radius = min(width, height) / 4
        for i in range(-2, 3):
            for j in range(-1, 2):
                wave_x = center_x + i * wave_radius * 0.8
                wave_y = center_y + j * wave_radius * 1.2
                cv2.circle(mask, (int(wave_x), int(wave_y)), int(wave_radius), 255, 3)
    
    return mask

@lru_cache(maxsize=CACHE_SIZE)
def create_arabesque_mask(width: int, height: int, complexity: int = 3) -> np.ndarray:
    """アラベスク柄マスクの生成（幾何学模様）"""
    mask = np.zeros((height, width), dtype=np.uint8)
    center_x, center_y = width / 2, height / 2
    base_radius = min(width, height) / 2 * 0.8
    
    # フラクタル的なパターン生成
    for level in range(complexity):
        radius = base_radius * (0.7 ** level)
        points = 8 * (level + 1)
        
        for i in range(points):
            angle = i * 2 * math.pi / points
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # 複雑な幾何学模様
            inner_radius = radius * 0.3
            for j in range(6):
                inner_angle = angle + j * math.pi / 3
                inner_x = x + inner_radius * math.cos(inner_angle)
                inner_y = y + inner_radius * math.sin(inner_angle)
                
                cv2.circle(mask, (int(inner_x), int(inner_y)), 
                          max(1, int(inner_radius * 0.2)), 255, -1)
    
    # 中心部の装飾
    cv2.circle(mask, (int(center_x), int(center_y)), 
               int(base_radius * 0.1), 255, -1)
    
    return mask

def create_custom_shape_mask(width: int, height: int, shape_type: str, **params) -> np.ndarray:
    """カスタム形状マスクの統一インターフェース（メモリ最適化版）"""
    # まずメモリ使用状況をチェック
    memory_info = get_mask_memory_usage()
    memory_mb = memory_info.get("estimated_memory_mb", 0)
    
    # 大きなサイズのマスクの場合、簡略化を検討
    large_mask = (width * height > 250000)  # 500x500以上は大きいとみなす
    
    # 複雑な形状かどうかをチェック
    complexity = SHAPE_COMPLEXITY.get(shape_type, 3)
    complex_shape = (complexity >= COMPLEXITY_THRESHOLD)
    
    # メモリ警告しきい値に近づいている場合、またはとても大きなマスクで複雑な形状の場合
    if memory_mb > MEMORY_WARNING_THRESHOLD * 0.7 or (large_mask and complex_shape):
        # 自動キャッシュクリア（複雑な形状のみ）
        if complex_shape:
            clear_shape_cache(shape_type)
    
    try:
        if shape_type == "circle":
            # center_x, center_y, radiusのみを渡す
            filtered_params = {k: v for k, v in params.items() if k in ['center_x', 'center_y', 'radius']}
            return create_circle_mask(width, height, **filtered_params)
        elif shape_type == "star":
            # フロントエンドからのパラメータ名をバックエンド形式にマッピング
            star_params = {}
            if 'points' in params:
                star_params['num_points'] = int(params['points'])
            elif 'num_points' in params:
                star_params['num_points'] = int(params['num_points'])
            else:
                star_params['num_points'] = 5  # デフォルト値
                
            if 'innerRadius' in params:
                star_params['inner_radius_ratio'] = float(params['innerRadius'])
            elif 'inner_radius_ratio' in params:
                star_params['inner_radius_ratio'] = float(params['inner_radius_ratio'])
            else:
                star_params['inner_radius_ratio'] = 0.4  # デフォルト値
                
            if 'rotation' in params:
                star_params['rotation'] = float(params['rotation'])
            else:
                star_params['rotation'] = 0.0  # デフォルト値
            
            print(f"🌟 Star mask parameters received: {params}")
            print(f"🌟 Star mask mapped parameters: {star_params}")
            
            result = create_star_mask(width, height, **star_params)
            print(f"🌟 Star mask created successfully with shape: {result.shape}")
            
            # 星形は中程度の複雑さ - 大きいサイズの場合のみ注意
            if large_mask and memory_mb > MEMORY_WARNING_THRESHOLD * 0.5:
                clear_shape_cache("star")
            return result
        elif shape_type == "heart":
            # フロントエンドからのパラメータをマッピング
            heart_params = {}
            if 'size' in params:
                heart_params['size_factor'] = float(params['size'])
            elif 'size_factor' in params:
                heart_params['size_factor'] = float(params['size_factor'])
            else:
                heart_params['size_factor'] = 0.8  # デフォルト値
                
            print(f"💖 Heart mask parameters: {heart_params}")
            result = create_heart_mask(width, height, **heart_params)
            # ハート形も中程度の複雑さ - 大きいサイズの場合のみ注意
            if large_mask and memory_mb > MEMORY_WARNING_THRESHOLD * 0.5:
                clear_shape_cache("heart")
            return result
            
        elif shape_type == "circle":
            # フロントエンドからのパラメータをマッピング
            circle_params = {}
            if 'size' in params:
                radius = min(width, height) / 2 * float(params['size'])
                circle_params['radius'] = radius
            print(f"⭕ Circle mask parameters: {circle_params}")
            return create_circle_mask(width, height, **circle_params)
            
        elif shape_type == "hexagon":
            # フロントエンドからのパラメータをマッピング
            hex_params = {}
            if 'size' in params:
                hex_params['size_factor'] = float(params['size'])
            elif 'size_factor' in params:
                hex_params['size_factor'] = float(params['size_factor'])
            else:
                hex_params['size_factor'] = 0.8  # デフォルト値
            print(f"🔷 Hexagon mask parameters: {hex_params}")
            return create_hexagon_mask(width, height, **hex_params)
            
        elif shape_type == "japanese":
            # フロントエンドからのパラメータをマッピング
            japanese_params = {}
            if 'pattern' in params:
                japanese_params['pattern_type'] = str(params['pattern'])
            elif 'pattern_type' in params:
                japanese_params['pattern_type'] = str(params['pattern_type'])
            else:
                japanese_params['pattern_type'] = 'sakura'  # デフォルト値
            print(f"🌸 Japanese mask parameters: {japanese_params}")
            result = create_traditional_japanese_mask(width, height, **japanese_params)
            # 和柄は複雑 - 使用後にキャッシュをクリア
            if memory_mb > MEMORY_WARNING_THRESHOLD * 0.3:
                clear_shape_cache("japanese")
            return result
            
        elif shape_type == "arabesque":
            # フロントエンドからのパラメータをマッピング
            arabesque_params = {}
            if 'complexity' in params:
                arabesque_params['complexity'] = float(params['complexity'])
            else:
                arabesque_params['complexity'] = 0.5  # デフォルト値
            print(f"🌿 Arabesque mask parameters: {arabesque_params}")
            result = create_arabesque_mask(width, height, **arabesque_params)
            # アラベスクは最も複雑 - 必ず使用後にキャッシュをクリア
            clear_shape_cache("arabesque")
            return result
        else:
            # デフォルトは円形（最も効率的）
            return create_circle_mask(width, height)
    except Exception as e:
        print(f"❌ Shape mask generation error: {e}")
        # メモリ不足の可能性がある場合は全キャッシュをクリア
        if "memory" in str(e).lower():
            print("⚠️ Possible memory issue detected, clearing all caches")
            clear_shape_cache()
        # フォールバック：単純な円形マスク
        return create_circle_mask(width, height)

def apply_mask_to_region(image_array: np.ndarray, mask: np.ndarray, region: Tuple[int, int, int, int]) -> np.ndarray:
    """画像の指定領域にマスクを適用（メモリ効率最適化）"""
    x, y, width, height = region
    
    # 領域のサイズチェック
    img_height, img_width = image_array.shape[:2]
    x = max(0, min(x, img_width - 1))
    y = max(0, min(y, img_height - 1))
    width = min(width, img_width - x)
    height = min(height, img_height - y)
    
    if width <= 0 or height <= 0:
        return image_array
    
    # マスクのリサイズ（必要な場合のみ）
    if mask.shape != (height, width):
        mask = cv2.resize(mask, (width, height), interpolation=cv2.INTER_NEAREST)
    
    # 結果配列の作成（元画像をコピー）
    result = image_array.copy()
    
    # マスクの適用（ベクトル化）
    if len(image_array.shape) == 3:  # カラー画像
        # マスクを3チャンネルに拡張
        mask_3d = np.stack([mask, mask, mask], axis=2) / 255.0
        
        # 領域に対してマスクを適用
        region_slice = result[y:y+height, x:x+width]
        masked_region = region_slice * mask_3d
        result[y:y+height, x:x+width] = masked_region.astype(image_array.dtype)
    else:  # グレースケール画像
        mask_normalized = mask / 255.0
        region_slice = result[y:y+height, x:x+width]
        masked_region = region_slice * mask_normalized
        result[y:y+height, x:x+width] = masked_region.astype(image_array.dtype)
    
    return result

def get_available_shapes() -> Dict[str, Dict[str, Any]]:
    """利用可能な形状とそのパラメータ情報を返す"""
    return {
        "circle": {
            "name": "円形",
            "description": "基本的な円形マスク",
            "params": {
                "center_x": {"type": "float", "default": None, "description": "中心X座標"},
                "center_y": {"type": "float", "default": None, "description": "中心Y座標"},
                "radius": {"type": "float", "default": None, "description": "半径"}
            },
            "performance": "最高速",
            "memory_usage": "最小"
        },
        "star": {
            "name": "星形",
            "description": "N角星マスク",
            "params": {
                "num_points": {"type": "int", "default": 5, "range": [3, 12], "description": "星の角数"},
                "inner_radius_ratio": {"type": "float", "default": 0.4, "range": [0.1, 0.8], "description": "内半径比率"},
                "rotation": {"type": "float", "default": 0, "description": "回転角度（ラジアン）"}
            },
            "performance": "高速",
            "memory_usage": "小"
        },
        "heart": {
            "name": "ハート形",
            "description": "心臓形マスク",
            "params": {
                "size_factor": {"type": "float", "default": 0.8, "range": [0.3, 1.2], "description": "サイズ係数"}
            },
            "performance": "高速",
            "memory_usage": "小"
        },
        "hexagon": {
            "name": "六角形",
            "description": "正六角形マスク",
            "params": {
                "size_factor": {"type": "float", "default": 0.8, "range": [0.3, 1.2], "description": "サイズ係数"}
            },
            "performance": "高速",
            "memory_usage": "小"
        },
        "japanese": {
            "name": "和柄",
            "description": "日本の伝統的模様",
            "params": {
                "pattern_type": {"type": "str", "default": "sakura", "options": ["sakura", "asanoha", "seigaiha"], "description": "柄の種類"}
            },
            "performance": "中速",
            "memory_usage": "中"
        },
        "arabesque": {
            "name": "アラベスク柄",
            "description": "幾何学的装飾模様",
            "params": {
                "complexity": {"type": "int", "default": 3, "range": [1, 5], "description": "複雑さレベル"}
            },
            "performance": "中速",
            "memory_usage": "中"
        }
    }

def optimize_mask_generation_parameters(width: int, height: int, shape_type: str) -> Dict[str, Any]:
    """画像サイズに基づいてマスク生成パラメータを最適化"""
    base_size = min(width, height)
    
    optimizations = {
        "cache_key_suffix": f"_{width}x{height}",
        "use_antialiasing": base_size > 200,
        "detail_level": "high" if base_size > 400 else "medium" if base_size > 150 else "low"
    }
    
    # 形状別の最適化
    if shape_type in ["japanese", "arabesque"]:
        # 複雑な形状は大きなサイズでのみ詳細描画
        if base_size < 200:
            optimizations["complexity_reduction"] = True
            if shape_type == "japanese":
                optimizations["pattern_simplification"] = True
            elif shape_type == "arabesque":
                optimizations["max_complexity"] = 2
    
    return optimizations

# メモリ使用量監視用の関数（拡張版）
def get_mask_memory_usage() -> Dict[str, Any]:
    """マスク生成のメモリ使用状況を取得（詳細版）"""
    import sys
    import psutil
    
    # すべての形状キャッシュ情報を収集
    cache_infos = {
        "circle": create_circle_mask.cache_info(),
        "star": create_star_mask.cache_info(),
        "heart": create_heart_mask.cache_info(),
        "hexagon": create_hexagon_mask.cache_info(),
        "japanese": create_traditional_japanese_mask.cache_info(),
        "arabesque": create_arabesque_mask.cache_info()
    }
    
    # 総キャッシュサイズ計算
    total_cache_size = sum(info.currsize for info in cache_infos.values())
    
    # 平均マスクサイズの見積もり（形状の複雑さに基づく加重平均）
    avg_mask_size_kb = 0
    for shape, info in cache_infos.items():
        # 複雑さに基づくマスクサイズ見積り
        shape_complexity = SHAPE_COMPLEXITY.get(shape, 3)
        # 基本サイズ(KB) = 形状の複雑さ × 0.5
        base_size = shape_complexity * 0.5
        avg_mask_size_kb += info.currsize * base_size
    
    if total_cache_size > 0:
        avg_mask_size_kb /= total_cache_size
    
    # 実際のプロセスメモリ使用量
    process = psutil.Process()
    process_memory = process.memory_info().rss / (1024 * 1024)  # MB単位
    
    # 形状ごとの統計
    shape_stats = {}
    for shape, info in cache_infos.items():
        shape_complexity = SHAPE_COMPLEXITY.get(shape, 3)
        hits_misses = info.hits + info.misses
        shape_stats[shape] = {
            "cache_size": info.currsize,
            "max_size": info.maxsize,
            "hits": info.hits,
            "misses": info.misses,
            "hit_ratio": info.hits / hits_misses if hits_misses > 0 else 0,
            "complexity": shape_complexity,
            "estimated_memory_kb": info.currsize * shape_complexity * 0.5
        }
    
    # 総キャッシュメモリ見積もり (MB単位)
    estimated_total_memory_mb = total_cache_size * avg_mask_size_kb / 1024
    
    return {
        "total_cache_size": total_cache_size,
        "shape_stats": shape_stats,
        "estimated_memory_mb": estimated_total_memory_mb,
        "process_memory_mb": process_memory,
        "memory_warning": process_memory > MEMORY_WARNING_THRESHOLD,
        "avg_mask_size_kb": avg_mask_size_kb
    }

def clear_shape_cache(shape_type=None):
    """形状マスクキャッシュをクリア（メモリ解放）
    
    Args:
        shape_type (str, optional): 特定の形状のキャッシュのみをクリアする場合に指定
    """
    if shape_type is None:
        # 全キャッシュをクリア
        create_circle_mask.cache_clear()
        create_star_mask.cache_clear()
        create_heart_mask.cache_clear()
        create_hexagon_mask.cache_clear()
        create_traditional_japanese_mask.cache_clear()
        create_arabesque_mask.cache_clear()
        print("🧹 All shape mask caches cleared")
        return
    
    # 特定の形状のキャッシュのみクリア
    if shape_type == "circle":
        create_circle_mask.cache_clear()
    elif shape_type == "star":
        create_star_mask.cache_clear()
    elif shape_type == "heart":
        create_heart_mask.cache_clear()
    elif shape_type == "hexagon":
        create_hexagon_mask.cache_clear()
    elif shape_type == "japanese":
        create_traditional_japanese_mask.cache_clear()
    elif shape_type == "arabesque":
        create_arabesque_mask.cache_clear()
    
    print(f"🧹 {shape_type} shape mask cache cleared")
