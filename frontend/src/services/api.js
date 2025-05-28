import axios from 'axios';

// APIのベースURL
const API_URL = process.env.REACT_APP_API_URL || '/api';

// AxiosのデフォルトURLを設定
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30秒
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
    
    // パラメータの型を適切に変換して追加
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
    
    console.log('Sending FormData with params:', Object.fromEntries(formData));
    
    const response = await api.post('/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error processing image:', error);
    // より詳細なエラー情報を提供
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
};

export const downloadImage = (filename) => {
  return `${API_URL}/download/${filename}`;
};

const apiService = {
  uploadImage,
  processImage,
  downloadImage
};

export default apiService;
