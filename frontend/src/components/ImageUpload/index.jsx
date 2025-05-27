import React, { useRef, useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { uploadImage } from '../../services/api';
import { FiUpload, FiImage } from 'react-icons/fi';
import './styles.css';

const ImageUpload = () => {
  const { actions } = useAppContext();
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const isImage = file.type.match('image.*');
    if (!isImage) {
      setError('画像ファイルをアップロードしてください');
      return;
    }
    
    try {
      setUploading(true);
      setError(null);
      
      // APIにアップロード
      const result = await uploadImage(file);
      
      // 画像URLを生成
      const imageUrl = `${window.location.origin}/static/${result.filename}`;
      
      // コンテキストに画像情報を設定
      actions.setImage(result, imageUrl);
      
      setUploading(false);
    } catch (error) {
      console.error('Upload error:', error);
      setError('アップロード中にエラーが発生しました');
      setUploading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInputRef.current.files = files;
      handleFileChange({ target: { files } });
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="image-upload">
      <div 
        className={`upload-area ${isDragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleButtonClick}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          onChange={handleFileChange} 
          accept="image/*" 
          className="file-input" 
        />
        
        {uploading ? (
          <div className="upload-status">
            <div className="spinner"></div>
            <p>アップロード中...</p>
          </div>
        ) : (
          <div className="upload-content">
            <FiUpload className="upload-icon" />
            <h3>画像をアップロード</h3>
            <p>クリックまたはドラッグ&ドロップでファイルを選択</p>
            <div className="supported-formats">
              <FiImage className="format-icon" />
              <span>対応フォーマット: JPG, PNG, GIF, WebP</span>
            </div>
          </div>
        )}
      </div>
      
      {error && (
        <div className="upload-error">
          <p>{error}</p>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
