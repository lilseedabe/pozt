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
    overlayRatio: settings.overlayRatio,
    // 最適化されたデフォルト値
    strength: settings.strength || 0.02,
    opacity: settings.opacity || 0.0,                         // デフォルト0.0
    enhancementFactor: settings.enhancementFactor || 1.2,
    frequency: settings.frequency || 1,
    blurRadius: settings.blurRadius || 0,                     // デフォルト0
    contrastBoost: settings.contrastBoost || 1.0,
    colorShift: settings.colorShift || 0.0,
    sharpnessBoost: settings.sharpnessBoost || 0.0            // 新しいパラメータ
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
    
    const baseTime = 6; // パラメータ拡張により少し増加
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
      progress += (100 / estimatedTime) * 0.1;
      setProcessingProgress(Math.min(progress, 95));
      
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
    
    if (!image || !image.filename) {
      setError('画像がアップロードされていません');
      return;
    }
    
    if (!region) {
      setError('領域が選択されていません');
      return;
    }
    
    console.log('🚀 Starting enhanced high-speed processing...');
    
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
      
      // APIに送信するパラメータを準備（拡張版）
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
        overlay_ratio: localSettings.overlayRatio,
        // 最適化されたパラメータを追加
        strength: localSettings.strength,
        opacity: localSettings.opacity,
        enhancement_factor: localSettings.enhancementFactor,
        frequency: localSettings.frequency,
        blur_radius: localSettings.blurRadius,
        contrast_boost: localSettings.contrastBoost,
        color_shift: localSettings.colorShift,
        sharpness_boost: localSettings.sharpnessBoost  // 新しいパラメータを追加
      };
      
      console.log('⚡ Sending enhanced high-speed API request:', params);
      
      // 画像処理を実行
      const result = await processImage(params);
      
      // 実際の処理時間を計算
      const actualTime = (Date.now() - startTime) / 1000;
      setProcessingTime(actualTime);
      
      // プログレスバーを完了
      clearInterval(progressInterval);
      setProcessingProgress(100);
      
      console.log('🎉 Enhanced high-speed processing completed:', result);
      console.log(`⏱️ Processing time: ${actualTime.toFixed(2)}s`);
      
      // 処理成功
      actions.processingSuccess(result);
      setIsProcessing(false);
      
    } catch (error) {
      console.error('❌ Enhanced processing error:', error);
      setIsProcessing(false);
      setProcessingProgress(0);
      
      let errorMessage = '拡張処理中にエラーが発生しました';
      
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

  // モード別パラメータ表示の判定
  const showOverlayParams = ['overlay', 'hybrid_overlay'].includes(localSettings.stripeMethod);
  const showFrequencyParams = ['high_frequency', 'moire_pattern'].includes(localSettings.stripeMethod);
  const showAdaptiveParams = localSettings.stripeMethod.includes('adaptive');
  const showColorParams = ['color_preserving', 'hue_preserving', 'blended'].includes(localSettings.stripeMethod);
  const showEnhancementParams = ['perfect_subtle', 'ultra_subtle', 'near_perfect'].includes(localSettings.stripeMethod);
  
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
      
      {/* 最適化機能情報表示 */}
      <div className="speed-optimization-info" style={{
        padding: '1rem',
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        border: '1px solid #10b981',
        borderRadius: '8px',
        marginBottom: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '1.2rem' }}>✨</span>
          <strong style={{ color: '#10b981' }}>最適化モード有効（隠し画像最優先）</strong>
        </div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          <div>推定処理時間: {estimateProcessingTime()}秒</div>
          <div>機能: 不透明度6~10、ブラー0で最鮮明な隠し画像 + 微細調整</div>
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
            <span>最適化高速処理中...</span>
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
            最適化パラメータ処理 + 並列処理による高速化実行中...
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
              <option value="overlay">🚀 重ね合わせモード（最速・推奨・最適）</option>
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
              🚀=超高速 ⚡=高速 🐌=高品質だが時間要 | overlayが隠し画像最適
            </small>
          </div>
        </div>

        {/* モード別専用パラメータ */}
        <div className="settings-group">
          <h3>✨ 最適化詳細調整パラメータ</h3>
          
          {/* オーバーレイ系パラメータ - 最適化済み */}
          {showOverlayParams && (
            <div className="parameter-section">
              <h4>🎨 オーバーレイ調整（隠し画像最優先）</h4>
              
              <div className="form-control">
                <label htmlFor="opacity">不透明度: {localSettings.opacity.toFixed(3)}</label>
                <input 
                  type="range" 
                  id="opacity" 
                  name="opacity" 
                  min="0.0"      // 0.1 → 0.0 に変更
                  max="1.0" 
                  step="0.001"   // 0.05 → 0.001 により超細かく調整可能
                  value={localSettings.opacity} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>完全透明 (最適)</span>
                  <span>不透明</span>
                </div>
                <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  💡 0.000が隠し画像最鮮明。微調整で効果を調整
                </small>
              </div>

              <div className="form-control">
                <label htmlFor="blurRadius">ブラー半径: {localSettings.blurRadius}px</label>
                <input 
                  type="range" 
                  id="blurRadius" 
                  name="blurRadius" 
                  min="0"        // 1 → 0 に変更
                  max="25"       // 15 → 25 に拡張
                  step="1" 
                  value={localSettings.blurRadius} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>シャープ (最適)</span>
                  <span>ソフト</span>
                </div>
                <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  💡 0pxが隠し画像最鮮明。必要に応じて微調整
                </small>
              </div>
              
              {/* 新たに負の値調整用のパラメータを追加 */}
              <div className="form-control">
                <label htmlFor="sharpnessBoost">シャープネス強化: {localSettings.sharpnessBoost.toFixed(3)}</label>
                <input 
                  type="range" 
                  id="sharpnessBoost" 
                  name="sharpnessBoost" 
                  min="-1.0"     // マイナス値で逆方向の効果
                  max="1.0" 
                  step="0.01" 
                  value={localSettings.sharpnessBoost} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>超ソフト化</span>
                  <span>超シャープ化</span>
                </div>
                <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  💡 マイナス値で逆効果、プラス値で強化効果
                </small>
              </div>

              {localSettings.stripeMethod === 'hybrid_overlay' && (
                <div className="form-control">
                  <label htmlFor="overlayRatio">オーバーレイ比率: {localSettings.overlayRatio.toFixed(3)}</label>
                  <input 
                    type="range" 
                    id="overlayRatio" 
                    name="overlayRatio" 
                    min="0.0"      // 0.2 → 0.0 により柔軟に
                    max="1.0"      // 0.8 → 1.0 に拡張
                    step="0.001"   // 0.05 → 0.001 により超細かく
                    value={localSettings.overlayRatio} 
                    onChange={handleRangeChange}
                    disabled={isProcessing}
                  />
                  <div className="range-labels">
                    <span>基本パターンのみ</span>
                    <span>オーバーレイのみ</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 高周波・モアレ系パラメータ */}
          {showFrequencyParams && (
            <div className="parameter-section">
              <h4>🌊 周波数調整</h4>
              
              <div className="form-control">
                <label htmlFor="frequency">周波数倍率: {localSettings.frequency}x</label>
                <input 
                  type="range" 
                  id="frequency" 
                  name="frequency" 
                  min="1" 
                  max="5" 
                  step="1" 
                  value={localSettings.frequency} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>低周波</span>
                  <span>高周波</span>
                </div>
              </div>

              <div className="form-control">
                <label htmlFor="strength">強度: {localSettings.strength.toFixed(3)}</label>
                <input 
                  type="range" 
                  id="strength" 
                  name="strength" 
                  min="0.005" 
                  max="0.1" 
                  step="0.005" 
                  value={localSettings.strength} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>弱</span>
                  <span>強</span>
                </div>
              </div>

              <div className="form-control">
                <label htmlFor="enhancementFactor">エンハンス係数: {localSettings.enhancementFactor.toFixed(1)}</label>
                <input 
                  type="range" 
                  id="enhancementFactor" 
                  name="enhancementFactor" 
                  min="0.5" 
                  max="3.0" 
                  step="0.1" 
                  value={localSettings.enhancementFactor} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>控えめ</span>
                  <span>強力</span>
                </div>
              </div>
            </div>
          )}

          {/* 適応系パラメータ */}
          {showAdaptiveParams && (
            <div className="parameter-section">
              <h4>🎯 適応調整</h4>
              
              <div className="form-control">
                <label htmlFor="strength">適応強度: {localSettings.strength.toFixed(3)}</label>
                <input 
                  type="range" 
                  id="strength" 
                  name="strength" 
                  min="0.005" 
                  max="0.08" 
                  step="0.005" 
                  value={localSettings.strength} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>最小</span>
                  <span>最大</span>
                </div>
              </div>

              <div className="form-control">
                <label htmlFor="contrastBoost">コントラスト倍率: {localSettings.contrastBoost.toFixed(1)}</label>
                <input 
                  type="range" 
                  id="contrastBoost" 
                  name="contrastBoost" 
                  min="0.5" 
                  max="2.0" 
                  step="0.1" 
                  value={localSettings.contrastBoost} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>低コントラスト</span>
                  <span>高コントラスト</span>
                </div>
              </div>
            </div>
          )}

          {/* 色調系パラメータ */}
          {showColorParams && (
            <div className="parameter-section">
              <h4>🎨 色調調整</h4>
              
              <div className="form-control">
                <label htmlFor="colorShift">色相シフト: {(localSettings.colorShift * 180).toFixed(0)}°</label>
                <input 
                  type="range" 
                  id="colorShift" 
                  name="colorShift" 
                  min="-1.0" 
                  max="1.0" 
                  step="0.05" 
                  value={localSettings.colorShift} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>-180°</span>
                  <span>+180°</span>
                </div>
              </div>

              <div className="form-control">
                <label htmlFor="strength">色調強度: {localSettings.strength.toFixed(3)}</label>
                <input 
                  type="range" 
                  id="strength" 
                  name="strength" 
                  min="0.01" 
                  max="0.1" 
                  step="0.005" 
                  value={localSettings.strength} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>自然</span>
                  <span>鮮やか</span>
                </div>
              </div>
            </div>
          )}

          {/* エンハンスメント系パラメータ */}
          {showEnhancementParams && (
            <div className="parameter-section">
              <h4>✨ エンハンスメント</h4>
              
              <div className="form-control">
                <label htmlFor="enhancementFactor">エンハンス強度: {localSettings.enhancementFactor.toFixed(1)}</label>
                <input 
                  type="range" 
                  id="enhancementFactor" 
                  name="enhancementFactor" 
                  min="0.8" 
                  max="2.5" 
                  step="0.1" 
                  value={localSettings.enhancementFactor} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>ソフト</span>
                  <span>シャープ</span>
                </div>
              </div>

              <div className="form-control">
                <label htmlFor="contrastBoost">コントラスト補正: {localSettings.contrastBoost.toFixed(1)}</label>
                <input 
                  type="range" 
                  id="contrastBoost" 
                  name="contrastBoost" 
                  min="0.7" 
                  max="1.8" 
                  step="0.1" 
                  value={localSettings.contrastBoost} 
                  onChange={handleRangeChange}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>フラット</span>
                  <span>鮮明</span>
                </div>
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
            <h3>✨ 最適化機能詳細（隠し画像最優先）</h3>
            <ul>
              <li><strong>最適デフォルト値:</strong> 不透明度6~10、ブラー0で隠し画像が最も鮮明に</li>
              <li><strong>超細かい調整:</strong> 0.001ステップでの微細な効果調整が可能</li>
              <li><strong>負の値調整:</strong> シャープネス強化で逆方向の効果も実現</li>
              <li><strong>モード別最適化:</strong> 各縞模様タイプに最適化された調整項目</li>
              <li><strong>高速処理維持:</strong> 最適化でも処理速度を維持</li>
              <li><strong>品質保証:</strong> 2430×3240px高品質出力を完全維持</li>
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
              最適化高速処理中... ({Math.round(processingProgress)}%)
            </>
          ) : (
            <>
              ✨ 最適化生成開始 (予想: {estimateProcessingTime()}秒)
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default Settings;
