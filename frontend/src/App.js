import React, { useState, useEffect } from 'react';
import { useAppContext } from './context/AppContext';
import ImageUpload from './components/ImageUpload';
import RegionSelector from './components/RegionSelector';
import Settings from './components/Settings';
import Preview from './components/Preview';
import Result from './components/Result';
import './styles/App.css';

function App() {
  const { state } = useAppContext();
  const { image, processingStatus, result } = state;
  const [activeStep, setActiveStep] = useState(1);

  // 画像がアップロードされたらステップ2に進む
  useEffect(() => {
    if (image) {
      setActiveStep(2);
    }
  }, [image]);

  // 結果が生成されたらステップ5に進む
  useEffect(() => {
    if (result) {
      setActiveStep(5);
    }
  }, [result]);

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-title-container">
          <h1 className="app-title">pozt</h1>
          <div className="app-title-bar"></div>
        </div>
        <p className="app-subtitle">Pattern Optical Zone Technology - 視覚の魔法を体験しよう</p>
      </header>

      <main className="app-main">
        <div className="app-description">
          <p>
            独自の光学パターン技術を活用して、見る角度や表示環境によって変化する驚きの視覚アート作品を作成できる無料のウェブアプリケーションです。
          </p>
        </div>

        <div className="app-steps">
          <div className={`step ${activeStep === 1 ? 'active' : ''}`}>
            <div className="step-number">1</div>
            <div className="step-content">
              <h2>画像をアップロード</h2>
              <ImageUpload />
            </div>
          </div>

          {image && (
            <div className={`step ${activeStep === 2 ? 'active' : ''}`}>
              <div className="step-number">2</div>
              <div className="step-content">
                <h2>隠したい領域を選択</h2>
                <RegionSelector />
              </div>
            </div>
          )}

          {image && state.region && (
            <div className={`step ${activeStep === 3 ? 'active' : ''}`}>
              <div className="step-number">3</div>
              <div className="step-content">
                <h2>生成設定</h2>
                <Settings onComplete={() => setActiveStep(4)} />
              </div>
            </div>
          )}

          {processingStatus === 'processing' && (
            <div className={`step ${activeStep === 4 ? 'active' : ''}`}>
              <div className="step-number">4</div>
              <div className="step-content">
                <h2>処理中...</h2>
                <div className="loading-spinner"></div>
              </div>
            </div>
          )}

          {result && (
            <div className={`step ${activeStep === 5 ? 'active' : ''}`}>
              <div className="step-number">5</div>
              <div className="step-content">
                <h2>結果</h2>
                <Preview />
                <Result />
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>&copy; 2025 pozt - Pattern Optical Zone Technology</p>
      </footer>
    </div>
  );
}

export default App;
