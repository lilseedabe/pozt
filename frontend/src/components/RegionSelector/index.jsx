import React, { useEffect } from 'react';
import { useAppContext } from '../../context/AppContext';
import { useCanvas } from '../../hooks/useCanvas';
import { FiArrowUp, FiArrowDown, FiArrowLeft, FiArrowRight, FiSquare, FiCircle, FiStar, FiHeart } from 'react-icons/fi';
import { TbHexagon } from 'react-icons/tb';
import { GiFlowerEmblem, GiArabicDoor } from 'react-icons/gi';
import Canvas from './Canvas';
import './styles.css';

const RegionSelector = () => {
  const { state, actions } = useAppContext();
  const { imageUrl, settings } = state;
  const { shapeType, shapeParams } = settings;
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

  // 形状タイプの変更ハンドラー
  const handleShapeTypeChange = (newShapeType) => {
    actions.updateSettings({ shapeType: newShapeType });
  };

  // 形状パラメータの変更ハンドラー
  const handleShapeParamChange = (paramName, value) => {
    actions.updateSettings({
      shapeParams: {
        ...shapeParams,
        [paramName]: value
      }
    });
  };

  // 形状タイプの設定
  const shapeTypes = [
    { id: 'rectangle', label: '四角形', icon: FiSquare },
    { id: 'circle', label: '円形', icon: FiCircle },
    { id: 'star', label: '星形', icon: FiStar },
    { id: 'heart', label: 'ハート', icon: FiHeart },
    { id: 'hexagon', label: '六角形', icon: TbHexagon },
    { id: 'japanese', label: '和柄', icon: GiFlowerEmblem },
    { id: 'arabesque', label: 'アラベスク', icon: GiArabicDoor }
  ];

  // 和柄パターンの設定
  const japanesePatterns = [
    { id: 'sakura', label: '桜' },
    { id: 'seigaiha', label: '青海波' },
    { id: 'asanoha', label: '麻の葉' },
    { id: 'kumiko', label: '組子' }
  ];

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
            <div className="size-control-group">
              <label className="size-control-label">
                幅: {region.width}px
              </label>
              <input 
                type="range" 
                min="50" 
                max="800" 
                step="10"
                value={region.width} 
                onChange={(e) => {
                  const newWidth = parseInt(e.target.value);
                  setRegionSize(newWidth, region.height);
                }}
                className="size-slider"
              />
            </div>
            
            <div className="size-control-group">
              <label className="size-control-label">
                高さ: {region.height}px
              </label>
              <input 
                type="range" 
                min="50" 
                max="800" 
                step="10"
                value={region.height} 
                onChange={(e) => {
                  const newHeight = parseInt(e.target.value);
                  setRegionSize(region.width, newHeight);
                }}
                className="size-slider"
              />
            </div>
            
            <div className="region-info">
              <p>選択領域: X={region.x}, Y={region.y}, 幅={region.width}, 高さ={region.height}</p>
            </div>
          </div>
        </div>
        
        <div className="control-section">
          <h3>選択形状</h3>
          <div className="shape-controls">
            <div className="shape-types">
              {shapeTypes.map((shape) => {
                const IconComponent = shape.icon;
                return (
                  <button
                    key={shape.id}
                    className={`shape-btn ${shapeType === shape.id ? 'active' : ''}`}
                    onClick={() => handleShapeTypeChange(shape.id)}
                    title={shape.label}
                  >
                    <IconComponent />
                    <span>{shape.label}</span>
                  </button>
                );
              })}
            </div>

            {/* 形状固有のパラメータ設定 */}
            <div className="shape-params">
              {/* 基本パラメータ: サイズ */}
              {shapeType !== 'rectangle' && (
                <div className="param-group">
                  <label className="param-label">
                    サイズ: {Math.round(shapeParams.size * 100)}%
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.05"
                    value={shapeParams.size}
                    onChange={(e) => handleShapeParamChange('size', parseFloat(e.target.value))}
                    className="param-slider"
                  />
                </div>
              )}

              {/* 回転角度 */}
              {['star', 'heart', 'hexagon', 'japanese', 'arabesque'].includes(shapeType) && (
                <div className="param-group">
                  <label className="param-label">
                    回転: {shapeParams.rotation}°
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="360"
                    step="15"
                    value={shapeParams.rotation}
                    onChange={(e) => handleShapeParamChange('rotation', parseInt(e.target.value))}
                    className="param-slider"
                  />
                </div>
              )}

              {/* 星形固有パラメータ */}
              {shapeType === 'star' && (
                <>
                  <div className="param-group">
                    <label className="param-label">
                      頂点数: {shapeParams.points}
                    </label>
                    <input
                      type="range"
                      min="3"
                      max="12"
                      step="1"
                      value={shapeParams.points}
                      onChange={(e) => handleShapeParamChange('points', parseInt(e.target.value))}
                      className="param-slider"
                    />
                  </div>
                  <div className="param-group">
                    <label className="param-label">
                      内径比: {Math.round(shapeParams.innerRadius * 100)}%
                    </label>
                    <input
                      type="range"
                      min="0.1"
                      max="0.9"
                      step="0.05"
                      value={shapeParams.innerRadius}
                      onChange={(e) => handleShapeParamChange('innerRadius', parseFloat(e.target.value))}
                      className="param-slider"
                    />
                  </div>
                </>
              )}

              {/* 和柄固有パラメータ */}
              {shapeType === 'japanese' && (
                <>
                  <div className="param-group">
                    <label className="param-label">パターン</label>
                    <select
                      value={shapeParams.pattern}
                      onChange={(e) => handleShapeParamChange('pattern', e.target.value)}
                      className="param-select"
                    >
                      {japanesePatterns.map((pattern) => (
                        <option key={pattern.id} value={pattern.id}>
                          {pattern.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="param-group">
                    <label className="param-label">
                      複雑度: {Math.round(shapeParams.complexity * 100)}%
                    </label>
                    <input
                      type="range"
                      min="0.1"
                      max="1.0"
                      step="0.05"
                      value={shapeParams.complexity}
                      onChange={(e) => handleShapeParamChange('complexity', parseFloat(e.target.value))}
                      className="param-slider"
                    />
                  </div>
                </>
              )}

              {/* アラベスク固有パラメータ */}
              {shapeType === 'arabesque' && (
                <div className="param-group">
                  <label className="param-label">
                    複雑度: {Math.round(shapeParams.complexity * 100)}%
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.05"
                    value={shapeParams.complexity}
                    onChange={(e) => handleShapeParamChange('complexity', parseFloat(e.target.value))}
                    className="param-slider"
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RegionSelector;
