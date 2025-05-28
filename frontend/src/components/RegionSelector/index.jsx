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

  // 領域が変更されたらアプリコンテキストを更新
  useEffect(() => {
    if (region) {
      actions.setRegion(region);
    }
  }, [region, actions]);

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
            <button className="direction-btn up" onClick={() => moveRegion('up')}>
              <FiArrowUp />
            </button>
            <div className="horizontal-controls">
              <button className="direction-btn left" onClick={() => moveRegion('left')}>
                <FiArrowLeft />
              </button>
              <button className="direction-btn right" onClick={() => moveRegion('right')}>
                <FiArrowRight />
              </button>
            </div>
            <button className="direction-btn down" onClick={() => moveRegion('down')}>
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
          <div className="size-controls">
            <div className="size-display">
              <span className="size-label">小</span>
              <span className="size-value">{region.width}×{region.height}</span>
              <span className="size-label">大</span>
            </div>
            <input 
              type="range" 
              min="50" 
              max="400" 
              step="10"
              value={region.width} 
              onChange={(e) => {
                const newSize = parseInt(e.target.value);
                setRegionSize(newSize, newSize);
              }}
              className="size-slider"
            />
            
            <div className="region-info">
              <p>選択領域: X={region.x}, Y={region.y}, 幅={region.width}, 高さ={region.height}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegionSelector;
