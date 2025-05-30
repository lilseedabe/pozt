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

/**
 * リバース処理: モアレ画像から隠し画像を抽出
 * @param {File} file - モアレ効果画像ファイル
 * @param {Object} params - リバース処理パラメータ
 * @returns {Promise} - 処理結果
 */
export const reverseProcessImage = async (file, params = {}) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    // パラメータをFormDataに追加
    const {
      extractionMethod = 'fourier_analysis',
      enhancementLevel = 2.0,
      enhancementMethod = 'histogram_equalization',
      applyEnhancement = true
    } = params;

    formData.append('extraction_method', extractionMethod);
    formData.append('enhancement_level', enhancementLevel.toString());
    formData.append('enhancement_method', enhancementMethod);
    formData.append('apply_enhancement', applyEnhancement.toString());

    console.log('🔄 Sending reverse processing request:', {
      fileName: file.name,
      fileSize: file.size,
      extractionMethod,
      enhancementLevel,
      enhancementMethod,
      applyEnhancement
    });

    const response = await api.post('/reverse', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000 // リバース処理は時間がかかる可能性があるため60秒
    });

    console.log('✅ Reverse processing completed:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Reverse processing error:', error);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
      
      if (error.response.status === 413) {
        console.error('⚠️ File too large for reverse processing');
      } else if (error.response.status === 422) {
        console.error('⚠️ Invalid parameters for reverse processing');
      } else if (error.response.status === 500) {
        console.error('⚠️ Server error during reverse processing');
      }
    }
    throw error;
  }
};

/**
 * 利用可能なリバース処理方法を取得
 * @returns {Promise} - 利用可能な処理方法の一覧
 */
export const getReverseMethods = async () => {
  try {
    const response = await api.get('/reverse/methods');
    console.log('📋 Available reverse methods loaded:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Failed to fetch reverse methods:', error);
    throw error;
  }
};

/**
 * リバース処理パラメータの検証
 * @param {Object} params - 検証するパラメータ
 * @returns {Object} - 検証結果
 */
export const validateReverseParams = (params) => {
  const validations = {
    enhancementLevel: { min: 0.5, max: 5.0 }
  };

  const errors = [];
  const warnings = [];

  // 強調レベルの検証
  if (params.enhancementLevel !== undefined) {
    const level = params.enhancementLevel;
    if (level < validations.enhancementLevel.min || level > validations.enhancementLevel.max) {
      errors.push(`enhancementLevel: ${level} is out of range [${validations.enhancementLevel.min}, ${validations.enhancementLevel.max}]`);
    }
    
    // 最適化のヒント
    if (level > 3.0) {
      warnings.push(`enhancementLevel: ${level} - 高すぎる値はノイズを増加させる可能性があります`);
    } else if (level < 1.0) {
      warnings.push(`enhancementLevel: ${level} - 低すぎる値は隠し画像が見えにくくなる可能性があります`);
    }
  }

  // 抽出方法の検証
  const validExtractionMethods = [
    'fourier_analysis', 
    'frequency_filtering', 
    'pattern_subtraction', 
    'adaptive_detection'
  ];
  
  if (params.extractionMethod && !validExtractionMethods.includes(params.extractionMethod)) {
    errors.push(`extractionMethod: '${params.extractionMethod}' is not a valid method`);
  }

  // 強調方法の検証
  const validEnhancementMethods = [
    'histogram_equalization', 
    'clahe', 
    'gamma_correction'
  ];
  
  if (params.enhancementMethod && !validEnhancementMethods.includes(params.enhancementMethod)) {
    errors.push(`enhancementMethod: '${params.enhancementMethod}' is not a valid method`);
  }

  if (errors.length > 0) {
    console.warn('⚠️ Reverse parameter validation errors:', errors);
    return { valid: false, errors, warnings };
  }
  
  if (warnings.length > 0) {
    console.info('💡 Reverse parameter optimization hints:', warnings);
  }
  
  return { valid: true, errors: [], warnings };
};

/**
 * リバース処理のパフォーマンス測定
 * @param {string} extractionMethod - 使用する抽出方法
 * @returns {Object} - パフォーマンス測定ユーティリティ
 */
export const measureReversePerformance = (extractionMethod = 'fourier_analysis') => {
  const startTime = performance.now();

  return {
    finish: () => {
      const endTime = performance.now();
      const duration = (endTime - startTime) / 1000; // 秒

      console.log(`🔄 Reverse processing (${extractionMethod}) completed in ${duration.toFixed(2)} seconds`);

      let performanceLevel;
      // リバース処理は通常より時間がかかる
      if (duration < 5) performanceLevel = '🚀 Ultra Fast';
      else if (duration < 10) performanceLevel = '⚡ Fast';
      else if (duration < 20) performanceLevel = '🏃 Normal';
      else if (duration < 40) performanceLevel = '🐌 Slow';
      else performanceLevel = '🕒 Very Slow';

      console.log(`Reverse Performance Level: ${performanceLevel}`);
      
      // 抽出方法別の期待パフォーマンス
      const expectedPerformance = {
        'frequency_filtering': 8,
        'pattern_subtraction': 6,
        'fourier_analysis': 15,
        'adaptive_detection': 12
      };

      const expected = expectedPerformance[extractionMethod] || 15;
      const efficiency = expected / duration;

      return { 
        duration, 
        performanceLevel,
        extractionMethod,
        efficiency: efficiency > 1 ? 'Faster than expected' : 'Slower than expected',
        expectedDuration: expected,
        hiddenImageQuality: duration < expected * 1.5 ? 'High' : 'Medium'
      };
    }
  };
};

/**
 * リバース処理結果の品質評価
 * @param {Object} result - リバース処理の結果
 * @returns {Object} - 品質評価
 */
export const evaluateReverseQuality = (result) => {
  const qualityMetrics = {
    extractionSuccess: false,
    estimatedClarity: 'Unknown',
    recommendedEnhancements: [],
    overallScore: 0
  };

  if (!result || !result.processing_info) {
    return qualityMetrics;
  }

  const { extraction_method, enhancement_level, file_size } = result.processing_info;

  // 抽出成功の判定（ファイルサイズベース）
  if (file_size > 10000) {  // 10KB以上
    qualityMetrics.extractionSuccess = true;
  }

  // 抽出方法による品質予測
  const methodQuality = {
    'fourier_analysis': 0.9,
    'frequency_filtering': 0.7,
    'pattern_subtraction': 0.6,
    'adaptive_detection': 0.8
  };

  const baseQuality = methodQuality[extraction_method] || 0.5;

  // 強調レベルによる調整
  let levelMultiplier = 1.0;
  if (enhancement_level < 1.0) levelMultiplier = 0.8;
  else if (enhancement_level > 3.0) levelMultiplier = 0.9;

  const finalScore = baseQuality * levelMultiplier;

  // 品質レベルの決定
  if (finalScore > 0.8) {
    qualityMetrics.estimatedClarity = 'High';
  } else if (finalScore > 0.6) {
    qualityMetrics.estimatedClarity = 'Medium';
  } else {
    qualityMetrics.estimatedClarity = 'Low';
  }

  // 推奨事項
  if (enhancement_level < 1.5) {
    qualityMetrics.recommendedEnhancements.push('強調レベルを上げることで画像がより鮮明になる可能性があります');
  }
  if (extraction_method === 'pattern_subtraction') {
    qualityMetrics.recommendedEnhancements.push('フーリエ解析を試すとより良い結果が得られる可能性があります');
  }

  qualityMetrics.overallScore = Math.round(finalScore * 100);

  return qualityMetrics;
};

// 統一されたデフォルトエクスポート（重複なし）
const apiService = {
  uploadImage,
  processImage,
  downloadImage,
  validateOptimizedParams,
  measureProcessingPerformance,
  checkOptimizationStatus,
  // リバース機能
  reverseProcessImage,
  getReverseMethods,
  validateReverseParams,
  measureReversePerformance,
  evaluateReverseQuality
};

export default apiService;
