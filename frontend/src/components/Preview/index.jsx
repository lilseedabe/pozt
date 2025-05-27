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
      <h3>多段階プレビュー</h3>
      <div className="preview-grid">
        <div className="preview-card">
          <h4>画像圧縮時</h4>
          <p>画像圧縮により縞模様が潰れて均一なグレーに</p>
          <div className="preview-image">
            <img src={urls.x_post} alt="圧縮効果シミュレーション" />
          </div>
        </div>
        
        <div className="preview-card">
          <h4>4K読み込み時</h4>
          <p>縞模様が復活、わずかな変調が見える</p>
          <div className="preview-image">
            <img src={urls.view_4k} alt="4K表示" />
          </div>
        </div>
        
        <div className="preview-card">
          <h4>4K拡大時</h4>
          <p>モアレ効果で隠し画像が鮮明に現れる</p>
          <div className="preview-image">
            <img src={urls.zoom} alt="拡大表示" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Preview;
