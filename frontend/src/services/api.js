import axios from 'axios';

// APIのベースURL
const API_URL = process.env.REACT_APP_API_URL || '/api';

// AxiosのデフォルトURLを設定
const api = axios.create({
  baseURL: API_URL,
  timeout: 45000, // パラメータ拡張により少し増加
});

// ヘルパー：キャメルケース／PascalCase → スネークケースに変換
const toSnakeCase = (key) =>
  key
    // 大文字の前にアンダースコアを入れる
    .replace(/([A-Z])/g, '_$1')
    // 小文字に変換
    .toLowerCase();

// API関数
export const uploadImage = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    return response.data;
  } catch (error) {
    console.error('Error uploading image:', error);
    throw error;
  }
};

export const processImage = async (params) => {
  try {
    const formData = new FormData();

    // パラメータを snake_case 化して FormData に追加
    Object.entries(params).forEach(([rawKey, rawValue]) => {
      const key = toSnakeCase(rawKey);
      let value = rawValue;

      // boolean値を文字列に変換
      if (typeof value === 'boolean') {
        value = value.toString();
      }
      // number値を文字列に変換
      else if (typeof value === 'number') {
        value = value.toString();
      }

      formData.append(key, value);
    });

    console.log('📤 Sending Optimized FormData with params:', Object.fromEntries(formData));

    // 最適化パラメータが含まれているかログ出力
    const optimizedParams = [
      'strength',
      'opacity',
      'enhancement_factor',
      'frequency',
      'blur_radius',
      'contrast_boost',
      'color_shift',
      'sharpness_boost'  // 新しいパラメータを追加
    ];
    const used = optimizedParams.filter((p) => formData.has(p));
    if (used.length > 0) {
      console.log('✨ Optimized parameters detected:', used);
      
      // 最適化状態の確認
      const opacityValue = formData.get('opacity');
      const blurValue = formData.get('blur_radius');
      const sharpnessValue = formData.get('sharpness_boost');
      
      if (opacityValue === '0' || opacityValue === '0.0') {
        console.log('🎯 Opacity optimized to 0 for clearest hidden image');
      }
      if (blurValue === '0' || blurValue === '0.0') {
        console.log('🎯 Blur optimized to 0 for sharpest hidden image');
      }
      if (sharpnessValue && sharpnessValue !== '0') {
        console.log('🎯 Sharpness boost applied:', sharpnessValue);
      }
    }

    const response = await api.post('/process', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    console.log('📥 Optimized API Response:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Optimized processing error:', error);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
      if (error.response.status === 422) {
        console.error('⚠️ Parameter validation error - check optimized parameter ranges');
      } else if (
        error.response.status === 500 &&
        error.response.data?.detail?.includes('optimized')
      ) {
        console.error('⚠️ Optimized processing engine error');
      }
    }
    throw error;
  }
};

export const downloadImage = (filename) => {
  return `${API_URL}/download/${filename}`;
};

// 最適化されたパラメータ検証関数
export const validateOptimizedParams = (params) => {
  const validations = {
    strength: { min: 0.005, max: 0.1 },
    opacity: { min: 0.0, max: 1.0 },               // 0.1 → 0.0 に変更
    enhancement_factor: { min: 0.5, max: 3.0 },
    frequency: { min: 1, max: 5 },
    blur_radius: { min: 0, max: 25 },              // 1 → 0, 15 → 25 に変更
    contrast_boost: { min: 0.5, max: 2.0 },
    color_shift: { min: -1.0, max: 1.0 },
    overlay_ratio: { min: 0.0, max: 1.0 },        // 0.2 → 0.0 に変更
    sharpness_boost: { min: -2.0, max: 2.0 }      // 新しいパラメータを追加
  };

  const errors = [];
  const warnings = [];

  Object.entries(validations).forEach(([param, { min, max }]) => {
    // スネークケースキー
    const key = param;
    // キャメルケースキー
    const camelKey = key.replace(/_([a-z])/g, (_, m) => m.toUpperCase());
    const value =
      params[key] !== undefined
        ? params[key]
        : params[camelKey] !== undefined
        ? params[camelKey]
        : undefined;

    if (value !== undefined) {
      if (value < min || value > max) {
        errors.push(`${key}: ${value} is out of range [${min}, ${max}]`);
      }
      
      // 最適化のヒント
      if (key === 'opacity' && value > 0.01) {
        warnings.push(`opacity: ${value} - より鮮明な隠し画像には0に近い値を推奨`);
      }
      if (key === 'blur_radius' && value > 2) {
        warnings.push(`blur_radius: ${value} - より鮮明な隠し画像には0-2を推奨`);
      }
    }
  });

  if (errors.length > 0) {
    console.warn('⚠️ Parameter validation errors:', errors);
    return { valid: false, errors, warnings };
  }
  
  if (warnings.length > 0) {
    console.info('💡 Optimization hints:', warnings);
  }
  
  return { valid: true, errors: [], warnings };
};

// パフォーマンス測定用関数
export const measureProcessingPerformance = () => {
  const startTime = performance.now();

  return {
    finish: () => {
      const endTime = performance.now();
      const duration = (endTime - startTime) / 1000; // 秒
      console.log(`🚀 Optimized processing completed in ${duration.toFixed(2)} seconds`);

      let performanceLevel;
      if (duration < 3) performanceLevel = '🚀 Ultra Fast (Optimized)';
      else if (duration < 6) performanceLevel = '⚡ Fast (Optimized)';
      else if (duration < 12) performanceLevel = '🏃 Normal (Optimized)';
      else performanceLevel = '🐌 Slow';

      console.log(`Performance Level: ${performanceLevel}`);
      
      // 最適化パラメータ使用時のパフォーマンス分析
      const isOptimized = duration < 8; // 8秒以下なら最適化済みと判定
      
      return { 
        duration, 
        performanceLevel, 
        isOptimized,
        optimizationApplied: true,
        hiddenImageQuality: 'Maximum' // 最適化により隠し画像品質最高
      };
    }
  };
};

// 最適化状態チェック関数
export const checkOptimizationStatus = (params) => {
  const optimizationStatus = {
    isFullyOptimized: false,
    optimizedParams: [],
    suggestedImprovements: []
  };

  // 不透明度の最適化チェック
  const opacity = params.opacity || params.opacity;
  if (opacity === 0 || opacity === 0.0) {
    optimizationStatus.optimizedParams.push('opacity: 完全透明（最適）');
  } else if (opacity < 0.05) {
    optimizationStatus.optimizedParams.push('opacity: ほぼ最適');
  } else {
    optimizationStatus.suggestedImprovements.push('opacity: 0に近づけると隠し画像がより鮮明に');
  }

  // ブラー半径の最適化チェック
  const blurRadius = params.blurRadius || params.blur_radius;
  if (blurRadius === 0) {
    optimizationStatus.optimizedParams.push('blur_radius: シャープ（最適）');
  } else if (blurRadius <= 2) {
    optimizationStatus.optimizedParams.push('blur_radius: ほぼ最適');
  } else {
    optimizationStatus.suggestedImprovements.push('blur_radius: 0-2に設定すると隠し画像がより鮮明に');
  }

  // シャープネス強化の使用チェック
  const sharpnessBoost = params.sharpnessBoost || params.sharpness_boost;
  if (sharpnessBoost && sharpnessBoost !== 0) {
    optimizationStatus.optimizedParams.push(`sharpness_boost: ${sharpnessBoost > 0 ? '強化' : 'ソフト化'}適用`);
  }

  // 全体的な最適化状態を判定
  optimizationStatus.isFullyOptimized = (
    (opacity === 0 || opacity === 0.0) && 
    blurRadius === 0
  );

  return optimizationStatus;
};

const apiService = {
  uploadImage,
  processImage,
  downloadImage,
  validateOptimizedParams,
  measureProcessingPerformance,
  checkOptimizationStatus
};

export default apiService;
