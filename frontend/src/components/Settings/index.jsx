import React, { useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { processImage } from '../../services/api';
import './styles.css';

const Settings = ({ onComplete }) => {
  const { state, actions } = useAppContext();
  const { image, region, settings } = state;
  
  const [localSettings, setLocalSettings] = useState({
    patternType: settings.patternType,
    stripeMethod: settings.stripeMethod,
    resizeMethod: settings.resizeMethod,
    addBorder: settings.addBorder,
    borderWidth: settings.borderWidth,
    overlayRatio: settings.overlayRatio
  });
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [processingTime, setProcessingTime] = useState(null);
  const [processingProgress, setProcessingProgress] = useState(0);
  
  // 処理時間の推定
  const estimateProcessingTime = () => {
    const complexityScores = {
      "overlay": 1,
      "high_frequency": 2,
      "adaptive": 1.5,
      "adaptive_subtle": 1.5,
      "adaptive_strong": 1.5,
      "moire_pattern": 3,
      "color_preserving": 4,
      "hue_preserving": 4,
      "blended": 3,
      "hybrid_overlay": 2.5
    };
    
    const baseTime = 8; // 基本処理時間（秒）
    const complexity = complexityScores[localSettings.stripeMethod] || 2;
    return Math.round(baseTime * complexity);
  };
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setLocalSettings({
      ...localSettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  const handleRangeChange = (e) => {
    const { name, value } = e.target;
    setLocalSettings({
      ...localSettings,
      [name]: parseFloat(value)
    });
  };
  
  const simulateProgress = (estimatedTime) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += (100 / estimatedTime) * 0.1; // 0.1秒ごとに更新
      setProcessingProgress(Math.min(progress, 95)); // 95%で停止
      
      if (progress >= 95) {
        clearInterval(interval);
      }
    }, 100);
    
    return interval;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setProcessingTime(null);
    setProcessingProgress(0);
    
    // 必要なデータの検証
    if (!image || !image.filename) {
      setError('画像がアップロードされていません');
      return;
    }
    
    if (!region) {
      setError('領域が選択されていません');
      return;
    }
    
    console.log('🚀 Starting high-speed processing...');
    
    try {
      setIsProcessing(true);
      
      // 設定を更新
      actions.updateSettings(localSettings);
      
      // 処理を開始
      actions.startProcessing();
      if (onComplete) onComplete();
      
      // 処理時間推定とプログレスバー開始
      const estimatedTime = estimateProcessingTime();
      const progressInterval = simulateProgress(estimatedTime);
      
      const startTime = Date.now();
      
      // APIに送信するパラメータを準備
      const params = {
        filename: image.filename,
        region_x: region.x,
        region_y: region.y,
        region_width: region.width,
        region_height: region.height,
        pattern_type: localSettings.patternType,
        stripe_method: localSettings.stripeMethod,
        resize_method: localSettings.resizeMethod,
        add_border: localSettings.addBorder,
        border_width: localSettings.borderWidth,
        overlay_ratio: localSettings.overlayRatio
      };
      
      console.log('⚡ Sending high-speed API request:', params);
      
      // 画像処理を実行
      const result = await processImage(params);
      
      // 実際の処理時間を計算
      const actualTime = (Date.now() - startTime) / 1000;
      setProcessingTime(actualTime);
      
      // プログレスバーを完了
      clearInterval(progressInterval);
      setProcessingProgress(100);
      
      console.log('🎉 High-speed processing completed:', result);
      console.log(`⏱️ Processing time: ${actualTime.toFixed(2)}s`);
      
      // 処理成功
      actions.processingSuccess(result);
      setIsProcessing(false);
      
    } catch (error) {
      console.error('❌ Processing error:', error);
      setIsProcessing(false);
      setProcessingProgress(0);
      
      let errorMessage = '処理中にエラーが発生しました';
      
      if (error.response) {
        if (error.response.data && error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.status === 404) {
          errorMessage = 'ファイルが見つかりません。再度アップロードしてください。';
        } else if (error.response.status === 500) {
          errorMessage = 'サーバー内部エラーが発生しました。';
        }
      } else if (error.request) {
        errorMessage = 'サーバーに接続できません。ネットワーク接続を確認してください。';
      }
      
      setError(errorMessage);
      actions.processingError(errorMessage);
    }
  };
  
  return (
    <div className="settings">
      {error && (
        <div className="error-message" style={{
          padding: '1rem',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid #ef4444',
          borderRadius: '8px',
          color: '#ef4444',
          marginBottom: '1rem'
        }}>
          <strong>エラー:</strong> {error}
        </div>
      )}
      
      {/* 高速化情報表示 */}
      <div className="speed-optimization-info" style={{
        padding: '1rem',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        border: '1px solid #10b981',
        borderRadius: '8px',
        marginBottom: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '1.2rem' }}>⚡</span>
          <strong style={{ color: '#10b981' }}>高速処理モード有効</strong>
        </div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          <div>推定処理時間: {estimateProcessingTime()}秒</div>
          <div>最適化: 並列処理 + JITコンパイル + メモリ効率化</div>
          {processingTime && (
            <div style={{ color: '#10b981', fontWeight: 'bold' }}>
              実際の処理時間: {processingTime.toFixed(2)}秒 🚀
            </div>
          )}
        </div>
      </div>
      
      {/* プログレスバー */}
      {isProcessing && (
        <div className="processing-progress" style={{
          marginBottom: '1rem',
          padding: '1rem',
          backgroundColor: 'var(--bg-tertiary)',
          borderRadius: '8px',
          border: '1px solid var(--border-primary)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span>高速処理中...</span>
            <span>{Math.round(processingProgress)}%</span>
          </div>
          <div style={{
            width: '100%',
            height: '8px',
            backgroundColor: 'var(--bg-secondary)',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${processingProgress}%`,
              height: '100%',
              background: 'var(--gradient-primary)',
              transition: 'width 0.3s ease'
            }} />
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            JITコンパイル + 並列処理による高速化実行中...
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="settings-group">
          <h3>縞パターン設定</h3>
          <div className="form-control">
            <label htmlFor="patternType">パターン方向</label>
            <select 
              id="patternType" 
              name="patternType" 
              value={localSettings.patternType} 
              onChange={handleChange}
              disabled={isProcessing}
            >
              <option value="horizontal">横縞（水平方向）⚡ 高速</option>
              <option value="vertical">縦縞（垂直方向）⚡ 高速</option>
            </select>
          </div>
          
          <div className="form-control">
            <label htmlFor="stripeMethod">縞模様タイプ</label>
            <select 
              id="stripeMethod" 
              name="stripeMethod" 
              value={localSettings.stripeMethod} 
              onChange={handleChange}
              disabled={isProcessing}
            >
              <option value="overlay">🚀 重ね合わせモード（最速・推奨）</option>
              <option value="high_frequency">⚡ 超高周波モード（高速）</option>
              <option value="adaptive">⚡ 標準モアレ効果（高速）</option>
              <option value="adaptive_subtle">⚡ 控えめモアレ効果（高速）</option>
              <option value="adaptive_strong">⚡ 強めモアレ効果（高速）</option>
              <option value="moire_pattern">🐌 完璧なモアレパターン（やや時間要）</option>
              <option value="color_preserving">🐌 色調保存モード（時間要）</option>
              <option value="hue_preserving">🐌 色相保存モード（時間要）</option>
              <option value="blended">🐌 ブレンドモード（やや時間要）</option>
              <option value="hybrid_overlay">⚡ 混合モード（高速）</option>
            </select>
            <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              🚀=超高速 ⚡=高速 🐌=高品質だが時間要
            </small>
          </div>
          
          {localSettings.stripeMethod === 'hybrid_overlay' && (
            <div className="form-control">
              <label htmlFor="overlayRatio">オーバーレイ比率: {localSettings.overlayRatio}</label>
              <input 
                type="range" 
                id="overlayRatio" 
                name="overlayRatio" 
                min="0.2" 
                max="0.8" 
                step="0.05" 
                value={localSettings.overlayRatio} 
                onChange={handleRangeChange}
                disabled={isProcessing}
              />
              <div className="range-labels">
                <span>基本パターン強め</span>
                <span>オーバーレイ強め</span>
              </div>
            </div>
          )}
        </div>
        
        <div className="settings-group">
          <h3>表示オプション</h3>
          <div className="form-control">
            <label htmlFor="resizeMethod">リサイズ方法</label>
            <select 
              id="resizeMethod" 
              name="resizeMethod" 
              value={localSettings.resizeMethod} 
              onChange={handleChange}
              disabled={isProcessing}
            >
              <option value="contain">🚀 アスペクト比保持（高速・推奨）</option>
              <option value="cover">⚡ 画面を埋める（高速）</option>
              <option value="stretch">⚡ 引き伸ばし（最速）</option>
            </select>
          </div>
          
          <div className="form-control checkbox">
            <input 
              type="checkbox" 
              id="addBorder" 
              name="addBorder" 
              checked={localSettings.addBorder} 
              onChange={handleChange}
              disabled={isProcessing}
            />
            <label htmlFor="addBorder">黒枠を追加（同時対比効果）⚡ 高速処理</label>
          </div>
          
          {localSettings.addBorder && (
            <div className="form-control">
              <label htmlFor="borderWidth">枠の幅: {localSettings.borderWidth}px</label>
              <input 
                type="range" 
                id="borderWidth" 
                name="borderWidth" 
                min="1" 
                max="10" 
                value={localSettings.borderWidth} 
                onChange={handleChange}
                disabled={isProcessing}
              />
            </div>
          )}
        </div>
        
        <div className="settings-group">
          <div className="settings-info">
            <h3>⚡ 高速化技術詳細</h3>
            <ul>
              <li><strong>JITコンパイル:</strong> Numbaによる数値計算の10-50倍高速化</li>
              <li><strong>並列処理:</strong> CPUのマルチコアを活用した同時実行</li>
              <li><strong>メモリ最適化:</strong> プレビュー1つ化で75%メモリ削減</li>
              <li><strong>アルゴリズム最適化:</strong> 高速リサイズとベクトル化処理</li>
              <li><strong>キャッシュ活用:</strong> 設定とパターンの事前計算</li>
              <li><strong>出力品質:</strong> 2430×3240px高品質を完全維持</li>
            </ul>
          </div>
        </div>
        
        <button 
          type="submit" 
          className="generate-btn"
          disabled={isProcessing || !image || !region}
          style={{
            background: isProcessing ? 'var(--bg-secondary)' : 'var(--gradient-primary)'
          }}
        >
          {isProcessing ? (
            <>
              <span className="loading-spinner"></span>
              高速処理中... ({Math.round(processingProgress)}%)
            </>
          ) : (
            <>
              ⚡ 高速生成開始 (予想: {estimateProcessingTime()}秒)
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default Settings;
