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

    console.log('📤 Sending Enhanced FormData with params:', Object.fromEntries(formData));

    // 拡張パラメータが含まれているかログ出力
    const enhancedParams = [
      'strength',
      'opacity',
      'enhancement_factor',
      'frequency',
      'blur_radius',
      'contrast_boost',
      'color_shift'
    ];
    const used = enhancedParams.filter((p) => formData.has(p));
    if (used.length > 0) {
      console.log('✨ Enhanced parameters detected:', used);
    }

    const response = await api.post('/process', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });

    console.log('📥 Enhanced API Response:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Enhanced processing error:', error);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
      if (error.response.status === 422) {
        console.error('⚠️ Parameter validation error - check enhanced parameter ranges');
      } else if (
        error.response.status === 500 &&
        error.response.data?.detail?.includes('enhanced')
      ) {
        console.error('⚠️ Enhanced processing engine error');
      }
    }
    throw error;
  }
};

export const downloadImage = (filename) => {
  return `${API_URL}/download/${filename}`;
};

// 新しい機能: パラメータ検証関数
export const validateEnhancedParams = (params) => {
  const validations = {
    strength: { min: 0.005, max: 0.1 },
    opacity: { min: 0.1, max: 1.0 },
    enhancement_factor: { min: 0.5, max: 3.0 },
    frequency: { min: 1, max: 5 },
    blur_radius: { min: 1, max: 15 },
    contrast_boost: { min: 0.5, max: 2.0 },
    color_shift: { min: -1.0, max: 1.0 },
    overlay_ratio: { min: 0.2, max: 0.8 }
  };

  const errors = [];

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

    if (value !== undefined && (value < min || value > max)) {
      errors.push(`${key}: ${value} is out of range [${min}, ${max}]`);
    }
  });

  if (errors.length > 0) {
    console.warn('⚠️ Parameter validation warnings:', errors);
    return { valid: false, errors };
  }
  return { valid: true, errors: [] };
};

// パフォーマンス測定用関数
export const measureProcessingPerformance = () => {
  const startTime = performance.now();

  return {
    finish: () => {
      const endTime = performance.now();
      const duration = (endTime - startTime) / 1000; // 秒
      console.log(`🚀 Enhanced processing completed in ${duration.toFixed(2)} seconds`);

      let performanceLevel;
      if (duration < 5) performanceLevel = '🚀 Ultra Fast';
      else if (duration < 10) performanceLevel = '⚡ Fast';
      else if (duration < 20) performanceLevel = '🐌 Normal';
      else performanceLevel = '🚧 Slow';

      console.log(`Performance Level: ${performanceLevel}`);
      return { duration, performanceLevel, isEnhanced: true };
    }
  };
};

const apiService = {
  uploadImage,
  processImage,
  downloadImage,
  validateEnhancedParams,
  measureProcessingPerformance
};

export default apiService;
