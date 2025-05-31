import React, { useState, useEffect } from 'react';
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
    sharpnessBoost: settings.sharpnessBoost || 0.0,           // 新しいパラメータ
    // 縞模様の色設定を追加
    stripeColor1: settings.stripeColor1 || '#000000',         // 縞色1（デフォルト黒）
    stripeColor2: settings.stripeColor2 || '#ffffff',         // 縞色2（デフォルト白）
    // 形状設定を追加
    shapeType: settings.shapeType || 'rectangle',            // 形状タイプ
    shapeParams: settings.shapeParams || {}                  // 形状パラメータ
  });
  
  // AppContextの設定が変更された時にlocalSettingsを同期
  useEffect(() => {
    setLocalSettings({
      patternType: settings.patternType,
      stripeMethod: settings.stripeMethod,
      resizeMethod: settings.resizeMethod,
      addBorder: settings.addBorder,
      borderWidth: settings.borderWidth,
      overlayRatio: settings.overlayRatio,
      strength: settings.strength || 0.02,
      opacity: settings.opacity || 0.0,
      enhancementFactor: settings.enhancementFactor || 1.2,
      frequency: settings.frequency || 1,
      blurRadius: settings.blurRadius || 0,
      contrastBoost: settings.contrastBoost || 1.0,
      colorShift: settings.colorShift || 0.0,
      sharpnessBoost: settings.sharpnessBoost || 0.0,
      stripeColor1: settings.stripeColor1 || '#000000',
      stripeColor2: settings.stripeColor2 || '#ffffff',
      shapeType: settings.shapeType || 'rectangle',
      shapeParams: settings.shapeParams || {}
    });
  }, [settings]);
  
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
    const newValue = type === 'checkbox' ? checked : value;
    const newSettings = {
      ...localSettings,
      [name]: newValue
    };
    
    setLocalSettings(newSettings);
    
    // shapeTypeが変更された場合、AppContextも即座に更新
    if (name === 'shapeType') {
      actions.updateSettings(newSettings);
    }
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
      
      // 設定を更新（処理前に必ず更新）
      actions.updateSettings(localSettings);
      console.log('🔧 Updated settings:', localSettings);
      
      // 処理を開始
      actions.startProcessing();
      if (onComplete) onComplete();
      
      // 処理時間推定とプログレスバー開始
      const estimatedTime = estimateProcessingTime();
      const progressInterval = simulateProgress(estimatedTime);
      
      const startTime = Date.now();
      
      // 形状パラメータのデバッグログ
      console.log('🔍 Form submission debug info:');
      console.log('🎭 Current shapeType:', localSettings.shapeType);
      console.log('🔧 Current shapeParams:', localSettings.shapeParams);
      console.log('📦 AppContext settings:', settings);
      
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
        sharpness_boost: localSettings.sharpnessBoost,  // 新しいパラメータを追加
        // 縞模様の色パラメータを追加
        stripe_color1: localSettings.stripeColor1,
        stripe_color2: localSettings.stripeColor2,
        // 形状選択パラメータを追加（JSON文字列化）
        shape_type: localSettings.shapeType || 'rectangle',
        shape_params: JSON.stringify(localSettings.shapeParams || {})
      };
      
      console.log('⚡ Sending enhanced high-speed API request:', params);
      console.log('🎭 Shape parameters being sent:');
      console.log('   - shape_type:', params.shape_type);
      console.log('   - shape_params:', params.shape_params);
      
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
      
      // 処理成功後も設定を保持
      console.log('✅ Processing completed, maintaining settings:', localSettings);
      
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

          {/* 縞模様の色設定を追加 */}
          <div className="parameter-section" style={{ marginTop: '20px' }}>
            <h4>🎨 縞模様カラー設定</h4>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
              <div className="form-control">
                <label htmlFor="stripeColor1">縞色1（メイン）</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <input
                    type="color"
                    id="stripeColor1"
                    name="stripeColor1"
                    value={localSettings.stripeColor1}
                    onChange={handleChange}
                    disabled={isProcessing}
                    style={{
                      width: '60px',
                      height: '40px',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                    }}
                  />
                  <input
                    type="text"
                    value={localSettings.stripeColor1}
                    onChange={handleChange}
                    name="stripeColor1"
                    disabled={isProcessing}
                    style={{
                      flex: 1,
                      padding: '8px',
                      border: '1px solid var(--border-primary)',
                      borderRadius: '6px',
                      fontSize: '0.9rem',
                      fontFamily: 'monospace'
                    }}
                  />
                </div>
              </div>

              <div className="form-control">
                <label htmlFor="stripeColor2">縞色2（サブ）</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <input
                    type="color"
                    id="stripeColor2"
                    name="stripeColor2"
                    value={localSettings.stripeColor2}
                    onChange={handleChange}
                    disabled={isProcessing}
                    style={{
                      width: '60px',
                      height: '40px',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                    }}
                  />
                  <input
                    type="text"
                    value={localSettings.stripeColor2}
                    onChange={handleChange}
                    name="stripeColor2"
                    disabled={isProcessing}
                    style={{
                      flex: 1,
                      padding: '8px',
                      border: '1px solid var(--border-primary)',
                      borderRadius: '6px',
                      fontSize: '0.9rem',
                      fontFamily: 'monospace'
                    }}
                  />
                </div>
              </div>
            </div>

            {/* プリセットカラー */}
            <div style={{ marginTop: '15px' }}>
              <label style={{ display: 'block', marginBottom: '10px', fontSize: '0.9rem', fontWeight: '600' }}>
                プリセットカラー
              </label>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {[
                  { name: 'デフォルト', color1: '#000000', color2: '#ffffff' },
                  { name: '暖色系', color1: '#FF6B6B', color2: '#FFE4E4' },
                  { name: '寒色系', color1: '#4ECDC4', color2: '#E4F8F7' },
                  { name: '青空', color1: '#45B7D1', color2: '#E1F3FA' },
                  { name: '森林', color1: '#96CEB4', color2: '#F0F8F5' },
                  { name: '夕焼け', color1: '#FFA07A', color2: '#FFEEE6' }
                ].map((preset, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => {
                      setLocalSettings({
                        ...localSettings,
                        stripeColor1: preset.color1,
                        stripeColor2: preset.color2
                      });
                    }}
                    disabled={isProcessing}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '5px',
                      padding: '5px 10px',
                      border: '1px solid var(--border-primary)',
                      borderRadius: '6px',
                      background: 'var(--bg-secondary)',
                      cursor: 'pointer',
                      fontSize: '0.8rem',
                      transition: 'all 0.2s ease'
                    }}
                    onMouseOver={(e) => e.target.style.background = 'var(--bg-tertiary)'}
                    onMouseOut={(e) => e.target.style.background = 'var(--bg-secondary)'}
                  >
                    <div style={{
                      width: '16px',
                      height: '16px',
                      background: `linear-gradient(90deg, ${preset.color1} 50%, ${preset.color2} 50%)`,
                      borderRadius: '2px'
                    }} />
                    {preset.name}
                  </button>
                ))}
              </div>
            </div>

            {/* カラープレビュー */}
            <div style={{ marginTop: '15px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', fontWeight: '600' }}>
                プレビュー
              </label>
              <div style={{
                width: '100%',
                height: '40px',
                background: `linear-gradient(90deg, ${localSettings.stripeColor1} 0%, ${localSettings.stripeColor1} 50%, ${localSettings.stripeColor2} 50%, ${localSettings.stripeColor2} 100%)`,
                backgroundSize: '20px 100%',
                borderRadius: '8px',
                border: '1px solid var(--border-primary)',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
              }} />
            </div>

            <small style={{
              color: 'var(--text-muted)',
              fontSize: '0.8rem',
              display: 'block',
              marginTop: '10px'
            }}>
              💡 縞模様の色を自由に変更できます。HEX形式（#000000）での直接入力も可能です。
            </small>
          </div>
        </div>

        {/* 形状選択設定を追加 */}
        <div className="settings-group">
          <h3>🎭 隠し画像の形状設定</h3>
          
          <div className="form-control">
            <label htmlFor="shapeType">マスク形状</label>
            <select
              id="shapeType"
              name="shapeType"
              value={localSettings.shapeType}
              onChange={handleChange}
              disabled={isProcessing}
            >
              <option value="rectangle">📦 四角形（標準・高速）</option>
              <option value="circle">⭕ 円形</option>
              <option value="star">⭐ 星形</option>
              <option value="heart">💖 ハート形</option>
              <option value="japanese">🌸 和柄模様</option>
              <option value="arabesque">🌿 アラベスク模様</option>
            </select>
            <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              📦=最高速 ⭕⭐💖=高速 🌸🌿=高品質だが処理時間増
            </small>
          </div>

          {/* 形状別パラメータ */}
          {localSettings.shapeType !== 'rectangle' && (
            <div className="parameter-section" style={{ marginTop: '20px' }}>
              <h4>🔧 形状詳細設定</h4>
              
              {/* 基本サイズ設定（全形状共通） */}
              <div className="form-control">
                <label htmlFor="shapeSize">サイズ: {(localSettings.shapeParams.size || 0.8).toFixed(2)}</label>
                <input
                  type="range"
                  id="shapeSize"
                  name="shapeSize"
                  min="0.1"
                  max="1.0"
                  step="0.05"
                  value={localSettings.shapeParams.size || 0.8}
                  onChange={(e) => {
                    const newShapeParams = { ...localSettings.shapeParams, size: parseFloat(e.target.value) };
                    setLocalSettings({ ...localSettings, shapeParams: newShapeParams });
                  }}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>小</span>
                  <span>大</span>
                </div>
              </div>

              {/* 回転設定（全形状共通） */}
              <div className="form-control">
                <label htmlFor="shapeRotation">回転: {localSettings.shapeParams.rotation || 0}°</label>
                <input
                  type="range"
                  id="shapeRotation"
                  name="shapeRotation"
                  min="0"
                  max="360"
                  step="15"
                  value={localSettings.shapeParams.rotation || 0}
                  onChange={(e) => {
                    const newShapeParams = { ...localSettings.shapeParams, rotation: parseInt(e.target.value) };
                    setLocalSettings({ ...localSettings, shapeParams: newShapeParams });
                  }}
                  disabled={isProcessing}
                />
                <div className="range-labels">
                  <span>0°</span>
                  <span>360°</span>
                </div>
              </div>

              {/* 星形専用パラメータ */}
              {localSettings.shapeType === 'star' && (
                <>
                  <div className="form-control">
                    <label htmlFor="starPoints">頂点数: {localSettings.shapeParams.points || 5}</label>
                    <input
                      type="range"
                      id="starPoints"
                      name="starPoints"
                      min="3"
                      max="12"
                      step="1"
                      value={localSettings.shapeParams.points || 5}
                      onChange={(e) => {
                        const newShapeParams = { ...localSettings.shapeParams, points: parseInt(e.target.value) };
                        setLocalSettings({ ...localSettings, shapeParams: newShapeParams });
                      }}
                      disabled={isProcessing}
                    />
                    <div className="range-labels">
                      <span>3</span>
                      <span>12</span>
                    </div>
                  </div>

                  <div className="form-control">
                    <label htmlFor="starInnerRadius">内径比: {(localSettings.shapeParams.innerRadius || 0.5).toFixed(2)}</label>
                    <input
                      type="range"
                      id="starInnerRadius"
                      name="starInnerRadius"
                      min="0.1"
                      max="0.9"
                      step="0.05"
                      value={localSettings.shapeParams.innerRadius || 0.5}
                      onChange={(e) => {
                        const newShapeParams = { ...localSettings.shapeParams, innerRadius: parseFloat(e.target.value) };
                        setLocalSettings({ ...localSettings, shapeParams: newShapeParams });
                      }}
                      disabled={isProcessing}
                    />
                    <div className="range-labels">
                      <span>尖り</span>
                      <span>丸み</span>
                    </div>
                  </div>
                </>
              )}

              {/* 和柄・アラベスク専用パラメータ */}
              {(localSettings.shapeType === 'japanese' || localSettings.shapeType === 'arabesque') && (
                <>
                  <div className="form-control">
                    <label htmlFor="patternComplexity">複雑度: {(localSettings.shapeParams.complexity || 0.5).toFixed(2)}</label>
                    <input
                      type="range"
                      id="patternComplexity"
                      name="patternComplexity"
                      min="0.1"
                      max="1.0"
                      step="0.1"
                      value={localSettings.shapeParams.complexity || 0.5}
                      onChange={(e) => {
                        const newShapeParams = { ...localSettings.shapeParams, complexity: parseFloat(e.target.value) };
                        setLocalSettings({ ...localSettings, shapeParams: newShapeParams });
                      }}
                      disabled={isProcessing}
                    />
                    <div className="range-labels">
                      <span>シンプル</span>
                      <span>複雑</span>
                    </div>
                    <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                      ⚠️ 複雑度が高いほど処理時間が増加します
                    </small>
                  </div>

                  {localSettings.shapeType === 'japanese' && (
                    <div className="form-control">
                      <label htmlFor="japanesePattern">和柄パターン</label>
                      <select
                        id="japanesePattern"
                        name="japanesePattern"
                        value={localSettings.shapeParams.pattern || 'sakura'}
                        onChange={(e) => {
                          const newShapeParams = { ...localSettings.shapeParams, pattern: e.target.value };
                          setLocalSettings({ ...localSettings, shapeParams: newShapeParams });
                        }}
                        disabled={isProcessing}
                      >
                        <option value="sakura">🌸 桜模様</option>
                        <option value="seigaiha">🌊 青海波</option>
                        <option value="asanoha">🍃 麻の葉</option>
                        <option value="kumiko">⚪ 組子</option>
                      </select>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          <small style={{
            color: 'var(--text-muted)',
            fontSize: '0.8rem',
            display: 'block',
            marginTop: '15px'
          }}>
            💡 形状を変えることで、隠し画像をより魅力的に表現できます。複雑な形状は処理時間が増加します。
          </small>
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
