// frontend/src/components/ReverseMode/index.jsx
import React, { useState, useRef } from 'react';
import axios from 'axios';
import { FiUpload, FiImage, FiEye, FiDownload, FiArrowLeft } from 'react-icons/fi';
import './styles.css';

const ReverseMode = ({ onBack }) => {
  const [moireImage, setMoireImage] = useState(null);
  const [moireImageUrl, setMoireImageUrl] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [settings, setSettings] = useState({
    extractionMethod: 'fourier_analysis',
    enhancementLevel: 2.0,
    enhancementMethod: 'histogram_equalization',
    applyEnhancement: true
  });
  const [availableMethods, setAvailableMethods] = useState(null);
  const fileInputRef = useRef(null);

  // 利用可能な処理方法を取得
  React.useEffect(() => {
    const fetchMethods = async () => {
      try {
        const response = await axios.get('/api/reverse/methods');
        setAvailableMethods(response.data);
      } catch (error) {
        console.error('Failed to fetch methods:', error);
      }
    };
    fetchMethods();
  }, []);

  // ファイルアップロード処理
  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const isImage = file.type.match('image.*');
    if (!isImage) {
      setError('画像ファイル（JPG、PNG、GIF、WebP）をアップロードしてください');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('ファイルサイズが10MBを超えています。');
      return;
    }

    const imageUrl = URL.createObjectURL(file);
    setMoireImage(file);
    setMoireImageUrl(imageUrl);
    setError(null);
    setResult(null);
  };

  // リバース処理実行
  const handleReverseProcessing = async () => {
    if (!moireImage) {
      setError('モアレ画像をアップロードしてください');
      return;
    }

    setProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', moireImage);
      formData.append('extraction_method', settings.extractionMethod);
      formData.append('enhancement_level', settings.enhancementLevel.toString());
      formData.append('enhancement_method', settings.enhancementMethod);
      formData.append('apply_enhancement', settings.applyEnhancement.toString());

      const response = await axios.post('/api/reverse', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000 // 60秒タイムアウト
      });

      setResult(response.data);
    } catch (error) {
      console.error('Reverse processing error:', error);
      const errorMessage = error.response?.data?.detail || 'リバース処理中にエラーが発生しました';
      setError(errorMessage);
    } finally {
      setProcessing(false);
    }
  };

  // ダウンロード処理
  const handleDownload = () => {
    if (result?.result_url) {
      const link = document.createElement('a');
      link.href = result.result_url;
      link.download = `extracted_hidden_image_${new Date().getTime()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  // 設定変更
  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="reverse-mode">
      <div className="reverse-header">
        <button className="back-button" onClick={onBack}>
          <FiArrowLeft />
          通常モードに戻る
        </button>
        <div className="reverse-title">
          <h1>🔄 リバースモード</h1>
          <p>モアレ効果画像から隠し画像を抽出します</p>
        </div>
      </div>

      <div className="reverse-content">
        {/* ステップ1: 画像アップロード */}
        <div className="reverse-step">
          <div className="step-header">
            <div className="step-number">1</div>
            <h2>モアレ画像をアップロード</h2>
          </div>
          
          <div 
            className={`upload-area ${!moireImage ? 'empty' : 'has-image'}`}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/*"
              className="file-input"
            />
            
            {moireImageUrl ? (
              <div className="uploaded-image">
                <img src={moireImageUrl} alt="アップロードされたモアレ画像" />
                <div className="image-overlay">
                  <FiImage className="overlay-icon" />
                  <span>クリックで画像を変更</span>
                </div>
              </div>
            ) : (
              <div className="upload-placeholder">
                <FiUpload className="upload-icon" />
                <h3>モアレ効果画像をアップロード</h3>
                <p>隠し画像が埋め込まれたモアレ画像を選択してください</p>
              </div>
            )}
          </div>
        </div>

        {/* ステップ2: 抽出設定 */}
        {moireImage && (
          <div className="reverse-step">
            <div className="step-header">
              <div className="step-number">2</div>
              <h2>抽出設定</h2>
            </div>
            
            <div className="settings-grid">
              <div className="setting-group">
                <label>抽出方法</label>
                <select
                  value={settings.extractionMethod}
                  onChange={(e) => handleSettingChange('extractionMethod', e.target.value)}
                >
                  {availableMethods?.extraction_methods && Object.entries(availableMethods.extraction_methods).map(([key, method]) => (
                    <option key={key} value={key}>{method.name}</option>
                  ))}
                </select>
                {availableMethods?.extraction_methods?.[settings.extractionMethod] && (
                  <small className="method-description">
                    {availableMethods.extraction_methods[settings.extractionMethod].description}
                  </small>
                )}
              </div>

              <div className="setting-group">
                <label>強調レベル: {settings.enhancementLevel}</label>
                <input
                  type="range"
                  min="0.5"
                  max="5.0"
                  step="0.1"
                  value={settings.enhancementLevel}
                  onChange={(e) => handleSettingChange('enhancementLevel', parseFloat(e.target.value))}
                  className="range-slider"
                />
                <div className="range-labels">
                  <span>控えめ</span>
                  <span>強調</span>
                </div>
              </div>

              <div className="setting-group">
                <div className="checkbox-group">
                  <input
                    type="checkbox"
                    id="applyEnhancement"
                    checked={settings.applyEnhancement}
                    onChange={(e) => handleSettingChange('applyEnhancement', e.target.checked)}
                  />
                  <label htmlFor="applyEnhancement">画像強調を適用</label>
                </div>
              </div>

              {settings.applyEnhancement && (
                <div className="setting-group">
                  <label>強調方法</label>
                  <select
                    value={settings.enhancementMethod}
                    onChange={(e) => handleSettingChange('enhancementMethod', e.target.value)}
                  >
                    {availableMethods?.enhancement_methods && Object.entries(availableMethods.enhancement_methods).map(([key, method]) => (
                      <option key={key} value={key}>{method.name}</option>
                    ))}
                  </select>
                  {availableMethods?.enhancement_methods?.[settings.enhancementMethod] && (
                    <small className="method-description">
                      {availableMethods.enhancement_methods[settings.enhancementMethod].description}
                    </small>
                  )}
                </div>
              )}
            </div>
            
            <button 
              className="process-button"
              onClick={handleReverseProcessing}
              disabled={processing || !moireImage}
            >
              {processing ? (
                <>
                  <div className="spinner"></div>
                  処理中...
                </>
              ) : (
                <>
                  <FiEye />
                  隠し画像を抽出
                </>
              )}
            </button>
          </div>
        )}

        {/* エラー表示 */}
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}

        {/* ステップ3: 結果表示 */}
        {result && (
          <div className="reverse-step">
            <div className="step-header">
              <div className="step-number">3</div>
              <h2>抽出結果</h2>
            </div>
            
            <div className="result-content">
              <div className="result-comparison">
                <div className="comparison-item">
                  <h3>元のモアレ画像</h3>
                  <img src={moireImageUrl} alt="元のモアレ画像" />
                </div>
                
                <div className="comparison-arrow">→</div>
                
                <div className="comparison-item">
                  <h3>抽出された隠し画像</h3>
                  <img src={result.result_url} alt="抽出された隠し画像" />
                </div>
              </div>
              
              <div className="result-info">
                <h4>処理情報</h4>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">抽出方法:</span>
                    <span className="info-value">{availableMethods?.extraction_methods?.[result.processing_info.extraction_method]?.name || result.processing_info.extraction_method}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">強調レベル:</span>
                    <span className="info-value">{result.processing_info.enhancement_level}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">画像サイズ:</span>
                    <span className="info-value">{result.processing_info.result_size}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">ファイルサイズ:</span>
                    <span className="info-value">{Math.round(result.processing_info.file_size / 1024)} KB</span>
                  </div>
                </div>
              </div>
              
              <button className="download-button" onClick={handleDownload}>
                <FiDownload />
                抽出画像をダウンロード
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReverseMode;
