import React, { useRef, useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { uploadImage } from '../../services/api';
import { FiUpload, FiImage, FiCheckCircle } from 'react-icons/fi';
import './styles.css';

const ImageUpload = () => {
  const { actions } = useAppContext();
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const isImage = file.type.match('image.*');
    if (!isImage) {
      setError('画像ファイル（JPG、PNG、GIF、WebP）をアップロードしてください');
      return;
    }

    // ファイルサイズチェック（20MB制限）
    if (file.size > 20 * 1024 * 1024) {
      setError('ファイルサイズが20MBを超えています');
      return;
    }
    
    try {
      setUploading(true);
      setError(null);
      setUploadSuccess(false);
      
      // APIにアップロード
      const result = await uploadImage(file);
      
      // 画像URLを生成（修正: /uploads/ を使用）
      const imageUrl = `${window.location.origin}${result.url}`;
      
      // コンテキストに画像情報を設定
      actions.setImage(result, imageUrl);
      
      setUploadSuccess(true);
      setUploading(false);
      
      // 成功メッセージを3秒後に非表示
      setTimeout(() => {
        setUploadSuccess(false);
      }, 3000);
      
    } catch (error) {
      console.error('Upload error:', error);
      const errorMessage = error.response?.data?.detail || 'アップロード中にエラーが発生しました';
      setError(errorMessage);
      setUploading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      // 一時的にファイルを設定
      const dt = new DataTransfer();
      dt.items.add(files[0]);
      fileInputRef.current.files = dt.files;
      
      // ファイル処理を実行
      handleFileChange({ target: { files: dt.files } });
    }
  };

  const handleButtonClick = () => {
    if (!uploading) {
      fileInputRef.current.click();
    }
  };

  const resetUpload = () => {
    setError(null);
    setUploadSuccess(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
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
            <small>しばらくお待ちください</small>
          </div>
        ) : uploadSuccess ? (
          <div className="upload-status success">
            <FiCheckCircle className="success-icon" />
            <p>アップロード完了！</p>
            <small>次のステップに進んでください</small>
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
            <div className="upload-specs">
              <small>最大ファイルサイズ: 20MB</small>
            </div>
          </div>
        )}
      </div>
      
      {error && (
        <div className="upload-error">
          <p>{error}</p>
          <button onClick={resetUpload} className="retry-btn">
            再試行
          </button>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;
