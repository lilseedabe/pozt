import React from 'react';
import { useAppContext } from '../../context/AppContext';
import './styles.css';

const Result = () => {
  const { state } = useAppContext();
  const { result } = state;
  
  if (!result) {
    return null;
  }
  
  const { urls } = result;
  const downloadUrl = urls.result;
  
  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `pozt_high_quality_${new Date().getTime()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  return (
    <div className="result">
      <h3>高品質モアレ画像 - 完成</h3>
      <div className="result-content">
        <div className="result-image">
          <img src={urls.result} alt="生成結果" />
          <div className="image-info-overlay">
            <span className="size-badge">2430×3240px</span>
          </div>
        </div>
        
        <div className="result-info">
          <h4>✨ 生成完了</h4>
          <p>高品質なモアレ効果画像が生成されました！</p>
          
          <div className="quality-features">
            <div className="feature-item">
              <span className="feature-icon">🎯</span>
              <div className="feature-content">
                <strong>高解像度出力</strong>
                <p>2430×3240ピクセルの印刷品質</p>
              </div>
            </div>
            
            <div className="feature-item">
              <span className="feature-icon">🔄</span>
              <div className="feature-content">
                <strong>多段階効果</strong>
                <p>表示条件により異なる見え方を実現</p>
              </div>
            </div>
            
            <div className="feature-item">
              <span className="feature-icon">⚡</span>
              <div className="feature-content">
                <strong>メモリ最適化</strong>
                <p>高品質を保ちつつ効率的な処理を実現</p>
              </div>
            </div>
          </div>
          
          <h4>📋 使用方法</h4>
          <ol>
            <li><strong>ダウンロード:</strong> 下記ボタンから高品質画像を保存</li>
            <li><strong>印刷:</strong> 大判印刷で最も鮮明な効果を確認</li>
            <li><strong>デジタル表示:</strong> 拡大縮小でモアレ効果を体験</li>
            <li><strong>SNS共有:</strong> 圧縮により隠し画像が目立たなくなる効果</li>
          </ol>
          
          <h4>🔍 効果の特徴</h4>
          <ul>
            <li><strong>通常表示:</strong> 明確な白黒の1ピクセル幅縞模様</li>
            <li><strong>画像圧縮時:</strong> 縞が潰れて均一なグレーに</li>
            <li><strong>4K/8K表示:</strong> 縞模様が復活し、隠し画像の輪郭が見える</li>
            <li><strong>最大拡大:</strong> モアレ効果により隠し画像が鮮明に現れる</li>
          </ul>
          
          <button className="download-btn" onClick={handleDownload}>
            <span className="download-icon">📥</span>
            高品質画像をダウンロード (2430×3240px)
          </button>
          
          <div className="technical-info">
            <small>
              💡 <strong>ヒント:</strong> ダウンロード後、様々な表示倍率や印刷サイズで効果をお楽しみください。
              特に、スマートフォンでの表示とPC画面での表示で異なる見え方を体験できます。
            </small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Result;
