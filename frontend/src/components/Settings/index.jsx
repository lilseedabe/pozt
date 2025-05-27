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
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // 設定を更新
    actions.updateSettings(localSettings);
    
    // 処理を開始
    actions.startProcessing();
    if (onComplete) onComplete();
    
    try {
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
      
      // 画像処理を実行
      const result = await processImage(params);
      
      // 処理成功
      actions.processingSuccess(result);
    } catch (error) {
      console.error('Processing error:', error);
      actions.processingError(error.message || '処理中にエラーが発生しました');
    }
  };
  
  return (
    <div className="settings">
      <form onSubmit={handleSubmit}>
        <div className="settings-group">
          <h3>縞パターン</h3>
          <div className="form-control">
            <label htmlFor="patternType">パターン方向</label>
            <select 
              id="patternType" 
              name="patternType" 
              value={localSettings.patternType} 
              onChange={handleChange}
            >
              <option value="horizontal">横縞（水平方向）</option>
              <option value="vertical">縦縞（垂直方向）</option>
            </select>
          </div>
          
          <div className="form-control">
            <label htmlFor="stripeMethod">縞模様タイプ</label>
            <select 
              id="stripeMethod" 
              name="stripeMethod" 
              value={localSettings.stripeMethod} 
              onChange={handleChange}
            >
              <option value="overlay">重ね合わせモード（グレーマスク方式）</option>
              <option value="high_frequency">超高周波モード（理想的なモアレ効果）</option>
              <option value="moire_pattern">完璧なモアレパターン</option>
              <option value="adaptive">モアレ効果型・標準</option>
              <option value="adaptive_subtle">モアレ効果型・控えめ</option>
              <option value="adaptive_strong">モアレ効果型・強め</option>
              <option value="adaptive_minimal">モアレ効果型・最小</option>
              <option value="perfect_subtle">モアレ効果型・やや強め</option>
              <option value="ultra_subtle">モアレ効果型・中程度</option>
              <option value="near_perfect">モアレ効果型・やや控えめ</option>
              <option value="color_preserving">色調保存モード（背景に馴染む）</option>
              <option value="hue_preserving">色相保存モード（背景色を維持）</option>
              <option value="blended">ブレンドモード（透明度効果）</option>
              <option value="overlay_high_frequency">重ね合わせ+超高周波の組み合わせ</option>
              <option value="overlay_moire_pattern">重ね合わせ+モアレパターンの組み合わせ</option>
              <option value="hybrid_overlay">混合モード（可変比率）</option>
            </select>
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
            >
              <option value="contain">アスペクト比保持（黒帯あり）</option>
              <option value="cover">画面を埋める</option>
              <option value="stretch">引き伸ばし</option>
            </select>
          </div>
          
          <div className="form-control checkbox">
            <input 
              type="checkbox" 
              id="addBorder" 
              name="addBorder" 
              checked={localSettings.addBorder} 
              onChange={handleChange}
            />
            <label htmlFor="addBorder">黒枠を追加（同時対比効果）</label>
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
              />
            </div>
          )}
        </div>
        
        <div className="settings-group">
          <div className="settings-info">
            <h3>技術詳細</h3>
            <ul>
              <li>基本縞：完全な白（255）と黒（0）の1ピクセル幅縞模様</li>
              <li>オーバーレイ効果：隠し画像の形状を強調する重ね合わせ処理</li>
              <li>隠し画像の明度に基づいて縞の明暗を微調整</li>
              <li>エッジ部分は強調処理</li>
              <li>表示解像度との干渉でモアレ効果が発生</li>
              <li>黒枠を追加することで、同時対比効果により縞模様がより均一に見える</li>
            </ul>
          </div>
        </div>
        
        <button type="submit" className="generate-btn">
          モアレ効果型隠し画像を生成
        </button>
      </form>
    </div>
  );
};

export default Settings;
