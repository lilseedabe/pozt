"""
最適化された画像処理モジュール - メモリ使用量最適化版
形状マスク・カラー設定に対応し、512MB環境でも安定動作
"""
import numpy as np
import cv2
from PIL import Image, ImageFilter, ImageEnhance
import uuid
import os
import time
import gc
import json
import psutil
from concurrent.futures import ThreadPoolExecutor
from utils.image_processor import (
    optimize_image_for_processing, 
    vectorized_pattern_generation,
    clear_memory
)
from config.app import get_settings
from core.image_utils import resize_to_fixed_size, add_black_border
from core.shape_masks import (
    create_custom_shape_mask,
    get_mask_memory_usage,
    clear_shape_cache,
    SHAPE_COMPLEXITY
)

def process_hidden_image_optimized(
    base_img_path: str,
    region: tuple,
    pattern_type: str,
    stripe_method: str,
    resize_method: str,
    add_border: bool = True,
    border_width: int = 3,
    overlay_ratio: float = 0.4,
    processing_params: dict = None,  # 最適化パラメータ辞書
    stripe_color1: str = "#000000",  # 縞模様カラー1
    stripe_color2: str = "#FFFFFF",  # 縞模様カラー2
    shape_type: str = "rectangle",   # 形状タイプ
    shape_params: str = "{}"         # 形状パラメータ（JSON文字列）
):
    """
    メモリ最適化された画像処理関数 - 複雑な形状や大きな画像でも512MBで安定動作
    
    Args:
        base_img_path: 元画像のパス
        region: 処理領域 (x, y, width, height)
        pattern_type: パターンタイプ ('horizontal' or 'vertical')
        stripe_method: 縞模様メソッド
        resize_method: リサイズメソッド
        add_border: 枠を追加するかどうか
        border_width: 枠の幅
        overlay_ratio: オーバーレイ比率
        processing_params: 処理パラメータ辞書
        stripe_color1: 縞色1（HEX形式）
        stripe_color2: 縞色2（HEX形式）
        shape_type: 形状タイプ
        shape_params: 形状パラメータ（JSON文字列）
        
    Returns:
        結果ファイル情報の辞書
    """
    # メモリ使用状況のベースライン計測
    process = psutil.Process()
    start_memory = process.memory_info().rss / (1024 * 1024)  # MB単位
    print(f"🧠 Starting memory usage: {start_memory:.2f} MB")
    
    # 最適化されたデフォルトパラメータ設定
    if processing_params is None:
        processing_params = {
            'strength': 0.02,
            'opacity': 0.0,                  # 最適化：完全透明
            'enhancement_factor': 1.2,
            'frequency': 1,
            'blur_radius': 0,                # 最適化：ブラーなし
            'contrast_boost': 1.0,
            'color_shift': 0.0,
            'overlay_ratio': overlay_ratio,
            'sharpness_boost': 0.0,          # 新パラメータ
            'stripe_color1': stripe_color1,  # 縞模様カラー1
            'stripe_color2': stripe_color2   # 縞模様カラー2
        }
    else:
        # 必要なパラメータの設定
        processing_params['overlay_ratio'] = overlay_ratio
        processing_params.setdefault('opacity', 0.0)
        processing_params.setdefault('blur_radius', 0)
        processing_params.setdefault('sharpness_boost', 0.0)
        processing_params['stripe_color1'] = stripe_color1
        processing_params['stripe_color2'] = stripe_color2
    
    start_time = time.time()
    settings = get_settings()

    print(f"🚀 Starting memory-optimized processing...")
    print(f"Parameters: {pattern_type}, {stripe_method}, {resize_method}, shape_type={shape_type}")
    print(f"Region: {region}")
    print(f"Colors: {stripe_color1} - {stripe_color2}")

    try:
        # === フェーズ1: 画像読み込みとリサイズ ===
        phase_start = time.time()

        if not os.path.exists(base_img_path):
            raise FileNotFoundError(f"Base image not found: {base_img_path}")

        # メモリ効率の良い読み込み
        base_img_orig = Image.open(base_img_path)
        original_size = (base_img_orig.width, base_img_orig.height)
        print(f"Original size: {original_size}, mode: {base_img_orig.mode}")
        
        # RGBAの場合はRGBに変換
        if base_img_orig.mode == 'RGBA':
            base_img = Image.new('RGB', base_img_orig.size, (255, 255, 255))
            base_img.paste(base_img_orig, mask=base_img_orig.split()[3])
            base_img_orig.close()
            print(f"Converted base image from RGBA to RGB")
        else:
            base_img = base_img_orig
        
        try:
            
            # 大きな画像は事前リサイズ
            if base_img.width * base_img.height > 4000000:  # 4MP以上は大きい
                print("⚡ Large image detected, applying memory-efficient pre-resize...")
                base_img.thumbnail((2000, 2000), Image.Resampling.BILINEAR)

            # 領域抽出
            x, y, width, height = region
            x = max(0, min(x, base_img.width - 1))
            y = max(0, min(y, base_img.height - 1))
            width = min(width, base_img.width - x)
            height = min(height, base_img.height - y)
            
            region_pil = base_img.crop((x, y, x + width, y + height))
            print(f"Region extracted: {region_pil.size}, mode: {region_pil.mode}")
            
            # RGBAをRGBに変換
            if region_pil.mode == 'RGBA':
                rgb_pil = Image.new('RGB', region_pil.size, (255, 255, 255))
                rgb_pil.paste(region_pil, mask=region_pil.split()[3])
                region_pil = rgb_pil
                print(f"Converted region from RGBA to RGB")

            # 高速リサイズ処理
            base_fixed = resize_to_fixed_size(base_img, method=resize_method)

            # メモリ効率のためにNumPy配列に変換
            hidden_img = np.array(region_pil)
            base_fixed_array = np.array(base_fixed)
            
            # PILオブジェクトを解放
            del region_pil, base_fixed
            clear_memory()
            
        finally:
            # base_imgを確実にclose
            if 'base_img' in locals():
                base_img.close()

        phase_time = time.time() - phase_start
        print(f"⚡ Phase 1 (Image loading): {phase_time:.2f}s")
        
        # メモリ使用状況チェック
        current_memory = process.memory_info().rss / (1024 * 1024)
        print(f"Memory after phase 1: {current_memory:.2f} MB (Δ{current_memory - start_memory:.2f} MB)")

        # === フェーズ2: 座標変換 ===
        phase_start = time.time()
        
        img_width, img_height = original_size
        scale_factors = np.array([settings.TARGET_WIDTH / img_width, settings.TARGET_HEIGHT / img_height])
        
        # 座標変換
        if resize_method == 'contain':
            scale = np.min(scale_factors)
            new_size = np.array([img_width, img_height]) * scale
            offsets = (np.array([settings.TARGET_WIDTH, settings.TARGET_HEIGHT]) - new_size) // 2
            region_coords = np.array([x, y, width, height]) * scale
            final_coords = region_coords + np.array([offsets[0], offsets[1], 0, 0])
        elif resize_method == 'cover':
            scale = np.max(scale_factors)
            crop_offset = ((np.array([img_width, img_height]) * scale - 
                           np.array([settings.TARGET_WIDTH, settings.TARGET_HEIGHT])) / 2).astype(int)
            region_coords = np.array([x, y, width, height]) * scale
            final_coords = region_coords - np.array([crop_offset[0], crop_offset[1], 0, 0])
        else:  # stretch
            final_coords = np.array([x * scale_factors[0], y * scale_factors[1], 
                                   width * scale_factors[0], height * scale_factors[1]])

        # 境界チェック
        x_fixed, y_fixed, width_fixed, height_fixed = final_coords.astype(int)
        x_fixed = max(0, min(x_fixed, settings.TARGET_WIDTH - 1))
        y_fixed = max(0, min(y_fixed, settings.TARGET_HEIGHT - 1))
        width_fixed = min(width_fixed, settings.TARGET_WIDTH - x_fixed)
        height_fixed = min(height_fixed, settings.TARGET_HEIGHT - y_fixed)
        
        print(f"Transformed region: x={x_fixed}, y={y_fixed}, w={width_fixed}, h={height_fixed}")

        phase_time = time.time() - phase_start
        print(f"⚡ Phase 2 (Coordinate transform): {phase_time:.2f}s")

        # === フェーズ3: 隠し画像準備 ===
        phase_start = time.time()
        
        # リサイズ
        hidden_pil = Image.fromarray(hidden_img)
        hidden_resized = hidden_pil.resize((width_fixed, height_fixed), Image.Resampling.BILINEAR)
        
        # RGBAの場合はRGBに変換
        if hidden_resized.mode == 'RGBA':
            rgb_hidden = Image.new('RGB', hidden_resized.size, (255, 255, 255))
            rgb_hidden.paste(hidden_resized, mask=hidden_resized.split()[3])
            hidden_resized = rgb_hidden
            print(f"Converted hidden_resized from RGBA to RGB")
        
        hidden_array = np.array(hidden_resized)
        
        # 不要オブジェクト解放
        del hidden_img, hidden_pil, hidden_resized
        clear_memory()

        phase_time = time.time() - phase_start
        print(f"⚡ Phase 3 (Hidden image prep): {phase_time:.2f}s")
        
        # メモリ使用状況チェック
        current_memory = process.memory_info().rss / (1024 * 1024)
        print(f"Memory after phase 3: {current_memory:.2f} MB (Δ{current_memory - start_memory:.2f} MB)")

        # === フェーズ4: 形状マスク生成と適用 ===
        phase_start = time.time()
        
        # 形状マスク生成（矩形以外の場合）
        if shape_type != "rectangle":
            print(f"🎭 Creating shape mask: {shape_type}")
            
            # 形状パラメータの解析（JSON文字列から辞書へ）
            try:
                if isinstance(shape_params, str):
                    # 空文字列または空白文字列の場合はデフォルト
                    if not shape_params.strip():
                        shape_params_dict = {}
                    else:
                        shape_params_dict = json.loads(shape_params)
                else:
                    shape_params_dict = shape_params if shape_params else {}
            except Exception as e:
                print(f"⚠️ Error parsing shape params: {e}")
                shape_params_dict = {}
                
            # 画像サイズに基づくメモリ使用量評価
            image_area = width_fixed * height_fixed
            image_size_mb = image_area * 3 / (1024 * 1024)  # RGB画像のメモリ使用量（MB）
            
            # 大きな画像+複雑な形状の場合の最適化
            if image_area > 500000:  # 大きい画像
                print(f"⚠️ Large image area: {image_area} pixels, ~{image_size_mb:.2f} MB")
                if image_size_mb > 10 and shape_type in ["japanese", "arabesque"]:
                    print(f"🔄 Simplifying complex shape for large image")
                    # 形状の複雑さを下げる
                    if "complexity" in shape_params_dict:
                        shape_params_dict["complexity"] = min(shape_params_dict.get("complexity", 0.5), 0.3)
            
            # メモリ使用状況の事前チェック
            memory_info = get_mask_memory_usage()
            memory_mb = memory_info.get("estimated_memory_mb", 0)
            
            # 形状の複雑さ取得
            complexity = SHAPE_COMPLEXITY.get(shape_type, 3)
            
            # メモリ使用量が多い場合は事前クリーンアップ
            if memory_mb > 30:  # キャッシュが30MB以上なら事前クリア
                print(f"🧹 Memory usage before shape creation: ~{memory_mb:.2f} MB, clearing caches")
                clear_shape_cache()
            
            # 複雑な形状の場合は特別処理
            if complexity >= 4:  # 和柄やアラベスクなど複雑な形状
                print(f"⚠️ Using complex shape: memory optimization active")
                # 事前にメモリを解放
                clear_memory()
            
            # 形状マスク生成
            shape_mask = create_custom_shape_mask(
                width_fixed, height_fixed, shape_type, **shape_params_dict
            )
            
            # 隠し画像に適用
            if len(hidden_array.shape) == 3:  # カラー画像
                # RGB画像のみを処理（RGBAは既に変換済みのはず）
                if hidden_array.shape[2] == 3:
                    mask_3d = np.stack([shape_mask, shape_mask, shape_mask], axis=2) / 255.0
                    hidden_array = (hidden_array * mask_3d).astype(np.uint8)
                    # メモリ最適化: マスクを解放
                    del mask_3d
                else:
                    # 万が一RGBAならRGBに変換
                    print(f"⚠️ Unexpected RGBA in shape mask application: {hidden_array.shape}")
                    hidden_array = hidden_array[:, :, :3]
            else:
                hidden_array = (hidden_array * (shape_mask / 255.0)).astype(np.uint8)
            
            # 形状マスクのメモリを解放
            del shape_mask
            clear_memory()
            
            print(f"Shape mask applied and memory released")
            
            # 複雑な形状の場合はキャッシュをクリア
            if complexity >= 3:
                clear_shape_cache(shape_type)
                print(f"Cleared shape cache for '{shape_type}'")
        
        # パターン生成
        stripe_pattern = vectorized_pattern_generation(
            hidden_array, pattern_type, stripe_method, processing_params
        )
        
        # パターンがRGBAの場合はRGBに変換
        if len(stripe_pattern.shape) == 3 and stripe_pattern.shape[2] == 4:
            print(f"⚠️ Stripe pattern is RGBA: {stripe_pattern.shape}, converting to RGB")
            stripe_pattern = stripe_pattern[:, :, :3]
        
        print(f"Stripe pattern shape: {stripe_pattern.shape}")
        
        # 不要メモリ解放
        del hidden_array
        clear_memory()

        phase_time = time.time() - phase_start
        print(f"⚡ Phase 4 (Shape mask + Pattern): {phase_time:.2f}s")
        
        # メモリ使用状況チェック
        current_memory = process.memory_info().rss / (1024 * 1024)
        print(f"Memory after phase 4: {current_memory:.2f} MB (Δ{current_memory - start_memory:.2f} MB)")
        
        # メモリ使用量が多い場合は強制GC
        if current_memory > 350:  # 350MB以上なら強制クリーンアップ
            print(f"🧹 High memory usage detected, forcing cleanup")
            clear_memory()
            gc.collect()
            current_memory = process.memory_info().rss / (1024 * 1024)
            print(f"Memory after forced cleanup: {current_memory:.2f} MB")

        # === フェーズ5: 最終合成 ===
        phase_start = time.time()
        
        # 結果画像の作成
        # base_fixed_arrayがRGBAの場合はRGBに変換
        if len(base_fixed_array.shape) == 3 and base_fixed_array.shape[2] == 4:
            print(f"⚠️ Base fixed array is RGBA: {base_fixed_array.shape}, converting to RGB")
            base_fixed_array = base_fixed_array[:, :, :3]
        
        print(f"Base fixed array shape: {base_fixed_array.shape}")
        print(f"Stripe pattern shape for replacement: {stripe_pattern.shape}")
        
        result_fixed = base_fixed_array.copy()
        
        # 形状対応合成
        if shape_type != "rectangle":
            print(f"🎨 Applying shape-aware composition for {shape_type}")
            
            # 形状マスクを再生成（最終合成用）
            composition_mask = create_custom_shape_mask(
                width_fixed, height_fixed, shape_type, **shape_params_dict
            )
            
            # 合成用マスクを正規化 (0-1の範囲)
            if len(stripe_pattern.shape) == 3:  # カラー画像
                mask_3d = np.stack([composition_mask, composition_mask, composition_mask], axis=2) / 255.0
                
                # 形状内のみパターンを適用、形状外は元画像を保持
                region_original = result_fixed[y_fixed:y_fixed + height_fixed, x_fixed:x_fixed + width_fixed].copy()
                blended_region = stripe_pattern * mask_3d + region_original * (1 - mask_3d)
                result_fixed[y_fixed:y_fixed + height_fixed, x_fixed:x_fixed + width_fixed] = blended_region.astype(np.uint8)
                
                # メモリ解放
                del mask_3d, region_original, blended_region
            else:  # グレースケール
                mask_normalized = composition_mask / 255.0
                region_original = result_fixed[y_fixed:y_fixed + height_fixed, x_fixed:x_fixed + width_fixed].copy()
                blended_region = stripe_pattern * mask_normalized + region_original * (1 - mask_normalized)
                result_fixed[y_fixed:y_fixed + height_fixed, x_fixed:x_fixed + width_fixed] = blended_region.astype(np.uint8)
                
                # メモリ解放
                del mask_normalized, region_original, blended_region
            
            # 合成マスクのメモリを解放
            del composition_mask
            print(f"✅ Shape-aware composition completed")
        else:
            # 矩形の場合は従来通りの置換
            result_fixed[y_fixed:y_fixed + height_fixed, x_fixed:x_fixed + width_fixed] = stripe_pattern
            print(f"✅ Rectangle composition completed")
        
        # 枠追加
        if add_border:
            result_fixed = add_black_border(
                result_fixed,
                (x_fixed, y_fixed, width_fixed, height_fixed),
                border_width
            )
        
        # 不要メモリ解放
        del stripe_pattern, base_fixed_array
        clear_memory()

        phase_time = time.time() - phase_start
        print(f"⚡ Phase 5 (Final composition): {phase_time:.2f}s")

        # === フェーズ6: 保存 ===
        phase_start = time.time()
        
        # ファイル名生成
        timestamp = int(time.time())
        result_id = uuid.uuid4().hex[:8]
        result_filename = f"optimized_result_{result_id}_{timestamp}.png"

        # 保存ディレクトリ確保
        os.makedirs("static", exist_ok=True)
        result_path = os.path.join("static", result_filename)
        
        # 最適化された保存
        result_image = Image.fromarray(result_fixed.astype('uint8'))
        result_image.save(
            result_path,
            format="PNG",
            optimize=False,    # 速度優先
            compress_level=3   # 低圧縮で高速化
        )
        
        # 不要メモリ解放
        del result_fixed, result_image
        clear_memory()

        phase_time = time.time() - phase_start
        print(f"⚡ Phase 6 (File saving): {phase_time:.2f}s")

        # === 処理完了 ===
        total_time = time.time() - start_time
        final_memory = process.memory_info().rss / (1024 * 1024)
        print(f"🎉 Memory-optimized processing completed: {total_time:.2f}s")
        print(f"🧠 Final memory usage: {final_memory:.2f} MB (Δ{final_memory - start_memory:.2f} MB)")

        # 最適化状態を記録
        optimization_status = {
            "opacity_optimized": processing_params.get('opacity', 0.6) == 0.0,
            "blur_optimized": processing_params.get('blur_radius', 5) == 0,
            "sharpness_boost_applied": abs(processing_params.get('sharpness_boost', 0.0)) > 0.001,
            "shape_type": shape_type
        }

        # 形状キャッシュを最終クリア
        if shape_type != "rectangle":
            complexity = SHAPE_COMPLEXITY.get(shape_type, 3)
            if complexity >= 4:  # 複雑な形状
                clear_shape_cache()
                print(f"🧹 Final cleanup: cleared all shape caches")

        # メモリ使用量が高い場合は追加クリーンアップ
        if final_memory > 300:
            print(f"🧹 High final memory usage: {final_memory:.2f} MB - additional cleanup")
            gc.collect()
            gc.collect()

        # 結果を返す
        result_dict = {
            "result": result_filename,
            "processing_info": {
                "processing_time": total_time,
                "optimization_status": optimization_status,
                "parameters_used": processing_params,
                "shape_used": shape_type,
                "memory_usage_mb": final_memory
            }
        }
        
        return result_dict

    except Exception as e:
        print(f"❌ Memory-optimized processing error: {e}")
        import traceback
        traceback.print_exc()
        
        # エラー時の強制メモリ解放
        clear_memory()
        
        # メモリ不足の可能性がある場合
        if "memory" in str(e).lower() or "out of memory" in str(e).lower() or "allocation" in str(e).lower():
            print("🔄 Possible memory issue detected, forcing cleanup")
            try:
                clear_shape_cache()  # 全形状キャッシュをクリア
                gc.collect()
                gc.collect()
            except Exception as cache_error:
                print(f"Error during emergency cleanup: {cache_error}")
        
        raise e

# 後方互換性のためのエイリアス（この関数は使用されていません）
# process_hidden_image_optimized = process_hidden_image
