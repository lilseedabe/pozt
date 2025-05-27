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
    
    // オブジェクトのキーと値をFormDataに追加
    Object.keys(params).forEach(key => {
      formData.append(key, params[key]);
    });
    
    const response = await api.post('/process', formData);
    return response.data;
  } catch (error) {
    console.error('Error processing image:', error);
    throw error;
  }
};

export const downloadImage = (filename) => {
  return `${API_URL}/download/${filename}`;
};

export default {
  uploadImage,
  processImage,
  downloadImage
};
