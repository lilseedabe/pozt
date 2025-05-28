import React from 'react';
import { useAppContext } from '../../context/AppContext';
import './styles.css';

const Preview = () => {
  const { state } = useAppContext();
  const { result } = state;
  
  if (!result) {
    return null;
  }
  
  const { urls } = result;
  
  return (
    <div className="preview">
      <h3>生成結果プレビュー</h3>
      <div className="preview-single">
        <div className="preview-card main-result">
          <h4>高品質モアレ画像 (2430×3240px)</h4>
          <p>生成された隠し画像の最終版です。拡大縮小や表示環境の変化でモアレ効果が現れます。</p>
          <div className="preview-image">
            <img src={urls.result} alt="生成結果" />
          </div>
          
          <div className="result-details">
            <div className="detail-item">
              <strong>出力サイズ:</strong> 2430×3240ピクセル (約8MP)
            </div>
            <div className="detail-item">
              <strong>効果:</strong> 表示解像度との干渉でモアレパターンが発生
            </div>
            <div className="detail-item">
              <strong>使用方法:</strong> 拡大縮小、印刷、デジタル表示で異なる見え方を楽しめます
            </div>
          </div>
        </div>
        
        <div className="usage-guide">
          <h4>🎨 効果の楽しみ方</h4>
          <div className="usage-methods">
            <div className="usage-method">
              <div className="method-icon">🖥️</div>
              <div className="method-content">
                <h5>デジタル表示</h5>
                <p>ブラウザで拡大縮小することでモアレ効果を確認できます</p>
              </div>
            </div>
            
            <div className="usage-method">
              <div className="method-icon">📱</div>
              <div className="method-content">
                <h5>SNS投稿</h5>
                <p>画像圧縮により隠し画像が目立たなくなる効果を体験</p>
              </div>
            </div>
            
            <div className="usage-method">
              <div className="method-icon">🖨️</div>
              <div className="method-content">
                <h5>高品質印刷</h5>
                <p>大判印刷時に最も鮮明なモアレ効果が現れます</p>
              </div>
            </div>
            
            <div className="usage-method">
              <div className="method-icon">🔍</div>
              <div className="method-content">
                <h5>4K/8K表示</h5>
                <p>高解像度ディスプレイで縞模様の詳細を確認</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div className="optimization-info">
        <div className="info-badge">
          <span className="badge-icon">⚡</span>
          <span className="badge-text">メモリ最適化: プレビューを1つに集約し、2430×3240pxの高品質を維持</span>
        </div>
      </div>
    </div>
  );
};

export default Preview;
