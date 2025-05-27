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
    link.download = `pozt_${new Date().getTime()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  return (
    <div className="result">
      <h3>最終出力</h3>
      <div className="result-content">
        <div className="result-image">
          <img src={urls.result} alt="生成結果" />
        </div>
        
        <div className="result-info">
          <h4>使用方法</h4>
          <ol>
            <li>下記のダウンロードボタンから画像を保存します</li>
            <li>印刷する場合は、高品質・高解像度設定を使用してください</li>
            <li>デジタル表示の場合、拡大縮小することでモアレ効果が現れます</li>
            <li>解像度が変わると異なる見え方になります</li>
          </ol>
          
          <h4>効果の特徴</h4>
          <ul>
            <li>通常表示: 明確な白黒の1ピクセル幅縞模様</li>
            <li>画像圧縮時: 縞が潰れて均一なグレーに</li>
            <li>4K読み込み: 縞模様が復活し、隠し画像の輪郭が見える</li>
            <li>最大拡大: モアレ効果により隠し画像が鮮明に現れる</li>
          </ul>
          
          <button className="download-btn" onClick={handleDownload}>
            画像をダウンロード
          </button>
        </div>
      </div>
    </div>
  );
};

export default Result;
