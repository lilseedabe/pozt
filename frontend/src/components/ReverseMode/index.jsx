// frontend/src/components/ReverseMode/index.jsx - 512MB制限対応・超軽量版
import React, { useState, useRef, useCallback, useMemo } from 'react';
import axios from 'axios';
import { FiUpload, FiImage, FiEye, FiDownload, FiArrowLeft, FiZap, FiAlertTriangle } from 'react-icons/fi';
import './styles.css';

const ReverseMode = ({ onBack }) => {
  const [moireImage, setMoireImage] = useState(null);
  const [moireImageUrl, setMoireImageUrl] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [processingTime, setProcessingTime] = useState(0);
  const [memoryWarning, setMemoryWarning] = useState(false);
  const [settings, setSettings] = useState({
    extractionMethod: 'pattern_subtraction', // 最軽量をデフォルト
    enhancementLevel: 1.5, // デフォルト値を削減
    enhancementMethod: 'histogram_equalization',
    applyEnhancement: false // デフォルトでOFF
  });
  const [availableMethods, setAvailableMethods] = useState(null);
  const [performanceStats, setPerformanceStats] = useState(null);
  const fileInputRef = useRef(null);
  const processingStartTime = useRef(null);

  // **512MB対応: ファイルサイズ制限**
  const MAX_FILE_SIZE = 3 * 1024 * 1024; // 3MB制限
  const RECOMMENDED_SIZE = 1.5 * 1024 * 1024; // 1.5MB推奨

  // **最適化: メモ化された利用可能メソッドの取得**
  const fetchMethods = useCallback(async () => {
    try {
      const [methodsResponse, performanceResponse] = await Promise.all([
        axios.get('/api/reverse/methods'),
        axios.get('/api/reverse/performance').catch(() => null)
      ]);
      
      setAvailableMethods(methodsResponse.data);
      if (performanceResponse) {
        setPerformanceStats(performanceResponse.data);
        
        // メモリ使用率が高い場合の警告
        const memoryUsage = parseFloat(performanceResponse.data.memory_utilization?.replace('%', '') || '0');
        if (memoryUsage > 60) {
          setMemoryWarning(true);
        }
      }
    } catch (error) {
      console.error('Failed to fetch methods:', error);
    }
  }, []);

  React.useEffect(() => {
    fetchMethods();
    
    // 定期的なメモリ監視
    const memoryInterval = setInterval(fetchMethods, 30000); // 30秒ごと
    return () => clearInterval(memoryInterval);
  }, [fetchMethods]);

  // **512MB対応: ファイル処理の強化**
  const handleFileChange = useCallback(async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const isImage = file.type.match('image.*');
    if (!isImage) {
      setError('画像ファイル（JPG、PNG、GIF、WebP）をアップロードしてください');
      return;
    }

    // **厳格なファイルサイズチェック**
    if (file.size > MAX_FILE_SIZE) {
      setError(`ファイルサイズが${MAX_FILE_SIZE/1024/1024}MBを超えています。Render 512MB制限のため、より小さいファイルをご利用ください。`);
      return;
    }

    // **推奨サイズの警告**
    if (file.size > RECOMMENDED_SIZE) {
      setError(`⚠️ ファイルサイズ（${(file.size/1024/1024).toFixed(1)}MB）が推奨サイズ（1.5MB）を超えています。処理が失敗する可能性があります。`);
    }

    // **画像サイズチェック**
    const checkImageSize = (file) => {
      return new Promise((resolve) => {
        const img = new Image();
        const objectUrl = URL.createObjectURL(file);
        
        img.onload = () => {
          URL.revokeObjectURL(objectUrl);
          const dimensions = { width: img.width, height: img.height };
          
          if (Math.max(img.width, img.height) > 1200) {
            setError(`⚠️ 画像サイズ（${img.width}×${img.height}）が大きすぎます。800×600px以下を推奨します。`);
          }
          
          resolve(dimensions);
        };
        
        img.onerror = () => {
          URL.revokeObjectURL(objectUrl);
          resolve({ width: 0, height: 0 });
        };
        
        img.src = objectUrl;
      });
    };

    await checkImageSize(file);

    const imageUrl = URL.createObjectURL(file);
    setMoireImage(file);
    setMoireImageUrl(imageUrl);
    setResult(null);
    setProcessingTime(0);
    
    // エラーメッセージをクリア（警告以外）
    if (!error?.includes('⚠️')) {
      setError(null);
    }
  }, [MAX_FILE_SIZE, RECOMMENDED_SIZE, error]);

  // **512MB対応: リバース処理の最適化**
  const handleReverseProcessing = useCallback(async () => {
    if (!moireImage) {
      setError('モアレ画像をアップロードしてください');
      return;
    }

    // **メモリ安全性チェック**
    if (performanceStats && parseFloat(performanceStats.memory_utilization?.replace('%', '') || '0') > 70) {
      setError('メモリ使用率が高すぎます。しばらく待ってから再試行してください。');
      return;
    }

    setProcessing(true);
    setError(null);
    processingStartTime.current = performance.now();

    try {
      const formData = new FormData();
      formData.append('file', moireImage);
      formData.append('extraction_method', settings.extractionMethod);
      formData.append('enhancement_level', settings.enhancementLevel.toString());
      formData.append('enhancement_method', settings.enhancementMethod);
      formData.append('apply_enhancement', settings.applyEnhancement.toString());

      // **512MB対応: タイムアウトとエラーハンドリング強化**
      const response = await axios.post('/api/reverse', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 180000, // 3分タイムアウト
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`Upload progress: ${percentCompleted}%`);
        }
      });

      const endTime = performance.now();
      const processingDuration = Math.round(endTime - processingStartTime.current);
      setProcessingTime(processingDuration);

      setResult(response.data);
      
      // パフォーマンス統計を更新
      fetchMethods();
      
      console.log(`✅ Ultra-light processing completed in ${processingDuration}ms`);
      
    } catch (error) {
      console.error('Reverse processing error:', error);
      
      let errorMessage = 'リバース処理中にエラーが発生しました';
      
      // **512MB対応: 具体的なエラーメッセージ**
      if (error.response?.status === 413) {
        errorMessage = 'ファイルサイズが大きすぎます。3MB以下の画像をご利用ください。';
      } else if (error.response?.status === 507) {
        errorMessage = 'メモリ不足です。より小さい画像をお試しください。';
      } else if (error.response?.status === 422) {
        errorMessage = '画像形式が対応していません。JPG、PNGファイルをご利用ください。';
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'タイムアウトしました。より小さい画像でお試しください。';
      } else {
        errorMessage = error.response?.data?.detail || errorMessage;
      }
      
      setError(errorMessage);
    } finally {
      setProcessing(false);
    }
  }, [moireImage, settings, performanceStats, fetchMethods]);

  const handleDownload = useCallback(() => {
    if (result?.result_url) {
      const link = document.createElement('a');
      link.href = result.result_url;
      link.download = `extracted_ultra_light_${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }, [result]);

  const handleSettingChange = useCallback((key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
    
    // **自動最適化警告**
    if (key === 'extractionMethod' && value === 'fourier_analysis') {
      setError('⚠️ フーリエ解析は大きな画像でメモリ不足になる可能性があります。');
    } else if (key === 'applyEnhancement' && value === true) {
      setError('⚠️ 画像強調は追加のメモリを使用します。');
    } else if (!error?.includes('ファイルサイズ') && !error?.includes('画像サイズ')) {
      setError(null);
    }
  }, [error]);

  // **メモリ警告表示**
  const memoryWarningDisplay = useMemo(() => {
    if (!performanceStats) return null;
    
    const memoryUsage = parseFloat(performanceStats.memory_utilization?.replace('%', '') || '0');
    const memoryAvailable = parseFloat(performanceStats.memory_available?.replace(' MB', '') || '512');
    
    if (memoryUsage > 60 || memoryAvailable < 200) {
      return (
        <div className="memory-warning-banner">
          <FiAlertTriangle className="warning-icon" />
          <div className="warning-content">
            <strong>メモリ使用量注意</strong>
            <p>使用率 {performanceStats.memory_utilization} | 利用可能 {performanceStats.memory_available}</p>
          </div>
        </div>
      );
    }
    
    return null;
  }, [performanceStats]);

  // **最適化設定の推奨表示**
  const optimizationTips = useMemo(() => {
    return (
      <div className="optimization-tips">
        <h4>🚀 512MB制限環境での推奨設定</h4>
        <div className="tips-grid">
          <div className="tip-item">
            <span className="tip-icon">📏</span>
            <span>画像サイズ: 800×600px以下</span>
          </div>
          <div className="tip-item">
            <span className="tip-icon">💾</span>
            <span>ファイルサイズ: 1.5MB以下推奨</span>
          </div>
          <div className="tip-item">
            <span className="tip-icon">⚡</span>
            <span>推奨方法: パターン減算</span>
          </div>
          <div className="tip-item">
            <span className="tip-icon">🔧</span>
            <span>強調処理: OFF推奨</span>
          </div>
        </div>
      </div>
    );
  }, []);

  return (
    <div className="reverse-mode">
      <div className="reverse-header">
        <button className="back-button" onClick={onBack}>
          <FiArrowLeft />
          通常モードに戻る
        </button>
        <div className="reverse-title">
          <h1>🔄 リバースモード（512MB対応）</h1>
          <p>超軽量処理でモアレ画像から隠し画像を抽出</p>
        </div>
        {performanceStats && (
          <div className="performance-indicator">
            <div className="perf-item">
              <small>メモリ使用率</small>
              <strong style={{color: parseFloat(performanceStats.memory_utilization?.replace('%', '') || '0') > 60 ? '#ef4444' : '#10b981'}}>
                {performanceStats.memory_utilization}
              </strong>
            </div>
          </div>
        )}
      </div>

      {memoryWarningDisplay}
      {optimizationTips}

      <div className="reverse-content">
        {/* ステップ1: 画像アップロード */}
        <div className="reverse-step">
          <div className="step-header">
            <div className="step-number">1</div>
            <h2>モアレ画像をアップロード（3MB制限）</h2>
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
                <h3>512MB制限対応モアレ画像をアップロード</h3>
                <p>隠し画像が埋め込まれたモアレ画像を選択（3MB以下）</p>
                <div className="upload-constraints">
                  <div className="constraint-item">📏 推奨サイズ: 800×600px以下</div>
                  <div className="constraint-item">💾 制限: 3MB以下（1.5MB推奨）</div>
                  <div className="constraint-item">⚡ 超軽量処理で高速実行</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ステップ2: 抽出設定 */}
        {moireImage && (
          <div className="reverse-step">
            <div className="step-header">
              <div className="step-number">2</div>
              <h2>抽出設定（512MB最適化）</h2>
            </div>
            
            <div className="settings-grid">
              <div className="setting-group">
                <label>抽出方法（メモリ効率順）</label>
                <select
                  value={settings.extractionMethod}
                  onChange={(e) => handleSettingChange('extractionMethod', e.target.value)}
                >
                  {availableMethods?.extraction_methods && Object.entries(availableMethods.extraction_methods).map(([key, method]) => (
                    <option key={key} value={key}>
                      {method.name} {method.render_512mb_safe === true ? '🟢' : method.render_512mb_safe === 'small images only' ? '🟡' : '🔴'}
                    </option>
                  ))}
                </select>
                <div className="method-safety">
                  {availableMethods?.extraction_methods?.[settings.extractionMethod]?.render_512mb_safe === true && 
                    <span className="safety-badge safe">✅ 512MB環境で安全</span>
                  }
                  {availableMethods?.extraction_methods?.[settings.extractionMethod]?.render_512mb_safe === 'small images only' && 
                    <span className="safety-badge warning">⚠️ 小画像のみ推奨</span>
                  }
                </div>
              </div>

              <div className="setting-group">
                <label>強調レベル: {settings.enhancementLevel}</label>
                <input
                  type="range"
                  min="0.5"
                  max="3.0"
                  step="0.1"
                  value={settings.enhancementLevel}
                  onChange={(e) => handleSettingChange('enhancementLevel', parseFloat(e.target.value))}
                  className="range-slider"
                />
                <div className="range-labels">
                  <span>軽量（推奨）</span>
                  <span>高品質</span>
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
                  <label htmlFor="applyEnhancement">
                    画像強調を適用 
                    {settings.applyEnhancement && <span className="memory-impact">⚠️ 追加メモリ使用</span>}
                  </label>
                </div>
              </div>

              {settings.applyEnhancement && (
                <div className="setting-group">
                  <label>強調方法（軽量版）</label>
                  <select
                    value={settings.enhancementMethod}
                    onChange={(e) => handleSettingChange('enhancementMethod', e.target.value)}
                  >
                    {availableMethods?.enhancement_methods && Object.entries(availableMethods.enhancement_methods).map(([key, method]) => (
                      <option key={key} value={key}>{method.name}</option>
                    ))}
                  </select>
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
                  超軽量処理実行中...
                </>
              ) : (
                <>
                  <FiEye />
                  <FiZap />
                  512MB環境で安全に抽出
                </>
              )}
            </button>
          </div>
        )}

        {/* エラー表示 */}
        {error && (
          <div className={`error-message ${error.includes('⚠️') ? 'warning' : 'error'}`}>
            <p>{error}</p>
          </div>
        )}

        {/* ステップ3: 結果表示 */}
        {result && (
          <div className="reverse-step">
            <div className="step-header">
              <div className="step-number">3</div>
              <h2>抽出結果（超軽量処理完了）</h2>
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
                <h4>超軽量処理情報</h4>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">処理方法:</span>
                    <span className="info-value">{availableMethods?.extraction_methods?.[result.processing_info.extraction_method]?.name}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">処理時間:</span>
                    <span className="info-value">{processingTime}ms</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">ファイルサイズ:</span>
                    <span className="info-value">{Math.round(result.processing_info.file_size / 1024)} KB</span>
                  </div>
                  {result.processing_info.memory_optimization && (
                    <div className="info-item">
                      <span className="info-label">メモリ節約:</span>
                      <span className="info-value">{result.processing_info.memory_optimization.memory_saved_mb}MB</span>
                    </div>
                  )}
                </div>
                
                {result.processing_info.memory_optimization && (
                  <div className="memory-optimization-info">
                    <h5>🚀 512MB最適化効果</h5>
                    <div className="optimization-badges">
                      <div className="opt-badge">⚡ 超軽量処理</div>
                      <div className="opt-badge">💾 メモリ効率化</div>
                      <div className="opt-badge">🔧 Render対応</div>
                    </div>
                  </div>
                )}
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

export default React.memo(ReverseMode);
