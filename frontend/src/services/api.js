import axios from 'axios';

// APIのベースURL
const API_URL = process.env.REACT_APP_API_URL || '/api';

// AxiosのデフォルトURLを設定
const api = axios.create({
  baseURL: API_URL,
  timeout: 45000, // パラメータ拡張により少し増加
});

// API関数
export const uploadImage = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
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
    
    // パラメータの型を適切に変換して追加（拡張版）
    Object.keys(params).forEach(key => {
      let value = params[key];
      
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
    
    // パラメータ詳細ログ
    const enhancedParams = [
      'strength', 'opacity', 'enhancement_factor', 'frequency', 
      'blur_radius', 'contrast_boost', 'color_shift'
    ];
    
    const enhancedParamsUsed = enhancedParams.filter(param => 
      params.hasOwnProperty(param.replace('_', '')) || params.hasOwnProperty(param)
    );
    
    if (enhancedParamsUsed.length > 0) {
      console.log('✨ Enhanced parameters detected:', enhancedParamsUsed);
    }
    
    const response = await api.post('/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    console.log('📥 Enhanced API Response:', response.data);
    
    return response.data;
  } catch (error) {
    console.error('❌ Enhanced processing error:', error);
    // より詳細なエラー情報を提供
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
      
      // 拡張パラメータ関連のエラーハンドリング
      if (error.response.status === 422) {
        console.error('⚠️ Parameter validation error - check enhanced parameter ranges');
      } else if (error.response.status === 500 && error.response.data?.detail?.includes('enhanced')) {
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
  
  Object.keys(validations).forEach(param => {
    const snakeParam = param.replace(/([A-Z])/g, '_$1').toLowerCase();
    const camelParam = param.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
    
    const value = params[param] || params[snakeParam] || params[camelParam];
    
    if (value !== undefined) {
      const { min, max } = validations[param];
      if (value < min || value > max) {
        errors.push(`${param}: ${value} is out of range [${min}, ${max}]`);
      }
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
      
      // パフォーマンス分類
      let performanceLevel;
      if (duration < 5) {
        performanceLevel = '🚀 Ultra Fast';
      } else if (duration < 10) {
        performanceLevel = '⚡ Fast';
      } else if (duration < 20) {
        performanceLevel = '🐌 Normal';
      } else {
        performanceLevel = '🚧 Slow';
      }
      
      console.log(`Performance Level: ${performanceLevel}`);
      
      return {
        duration,
        performanceLevel,
        isEnhanced: true
      };
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
