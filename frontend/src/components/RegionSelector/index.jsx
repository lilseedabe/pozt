import React, { useEffect, useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { useCanvas } from '../../hooks/useCanvas';
import { FiArrowUp, FiArrowDown, FiArrowLeft, FiArrowRight } from 'react-icons/fi';
import Canvas from './Canvas';
import './styles.css';

const RegionSelector = () => {
  const { state, actions } = useAppContext();
  const { imageUrl } = state;
  const {
    canvasRef,
    region,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
    moveToGridPosition,
    setRegionSize,
    moveRegion
  } = useCanvas(imageUrl);
  
  const [sizeBtnActive, setSizeBtnActive] = useState('medium');

  // 領域が変更されたらアプリコンテキストを更新
  useEffect(() => {
    if (region) {
      actions.setRegion(region);
    }
  }, [region, actions]);
  
  // サイズプリセットの設定
  const handleSizePreset = (size, width, height) => {
    setRegionSize(width, height);
    setSizeBtnActive(size);
  };

  if (!imageUrl) {
    return <div className="region-selector-empty">画像をアップロードしてください</div>;
  }

  return (
    <div className="region-selector">
      <div className="region-canvas-container">
        <Canvas
          canvasRef={canvasRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        />
      </div>
      
      <div className="region-controls">
        <div className="control-section">
          <h3>位置の調整</h3>
          <div className="direction-controls">
            <button className="direction-btn" onClick={() => moveRegion('up')}>
              <FiArrowUp />
            </button>
            <div className="horizontal-controls">
              <button className="direction-btn" onClick={() => moveRegion('left')}>
                <FiArrowLeft />
              </button>
              <button className="direction-btn" onClick={() => moveRegion('right')}>
                <FiArrowRight />
              </button>
            </div>
            <button className="direction-btn" onClick={() => moveRegion('down')}>
              <FiArrowDown />
            </button>
          </div>
        </div>
        
        <div className="control-section">
          <h3>グリッド位置</h3>
          <div className="grid-controls">
            <div className="grid-row">
              <button className="grid-btn" onClick={() => moveToGridPosition(1)}>左上</button>
              <button className="grid-btn" onClick={() => moveToGridPosition(2)}>上中央</button>
              <button className="grid-btn" onClick={() => moveToGridPosition(3)}>右上</button>
            </div>
            <div className="grid-row">
              <button className="grid-btn" onClick={() => moveToGridPosition(4)}>左中央</button>
              <button className="grid-btn" onClick={() => moveToGridPosition(5)}>中央</button>
              <button className="grid-btn" onClick={() => moveToGridPosition(6)}>右中央</button>
            </div>
            <div className="grid-row">
              <button className="grid-btn" onClick={() => moveToGridPosition(7)}>左下</button>
              <button className="grid-btn" onClick={() => moveToGridPosition(8)}>下中央</button>
              <button className="grid-btn" onClick={() => moveToGridPosition(9)}>右下</button>
            </div>
          </div>
        </div>
        
        <div className="control-section">
          <h3>サイズ調整</h3>
          <div className="size-presets">
            <button 
              className={`size-btn ${sizeBtnActive === 'small' ? 'active' : ''}`}
              onClick={() => handleSizePreset('small', 100, 100)}
            >
              小 (100x100)
            </button>
            <button 
              className={`size-btn ${sizeBtnActive === 'medium' ? 'active' : ''}`}
              onClick={() => handleSizePreset('medium', 150, 150)}
            >
              中 (150x150)
            </button>
            <button 
              className={`size-btn ${sizeBtnActive === 'large' ? 'active' : ''}`}
              onClick={() => handleSizePreset('large', 250, 250)}
            >
              大 (250x250)
            </button>
          </div>
          
          <div className="region-info">
            <p>選択領域: X={region.x}, Y={region.y}, 幅={region.width}, 高さ={region.height}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegionSelector;
