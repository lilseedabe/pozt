// frontend/src/App.js - リバースモード統合版
import React, { useState, useEffect } from 'react';
import { useAppContext } from './context/AppContext';
import ImageUpload from './components/ImageUpload';
import RegionSelector from './components/RegionSelector';
import Settings from './components/Settings';
import Preview from './components/Preview';
import Result from './components/Result';
import SessionManager from './components/SessionManager';
import ReverseMode from './components/ReverseMode'; // 新しいコンポーネント
import { FiRefreshCw, FiArrowRight } from 'react-icons/fi';
import './styles/App.css';

function App() {
  const { state } = useAppContext();
  const { image, processingStatus, result } = state;
  const [activeStep, setActiveStep] = useState(1);
  const [isReverseMode, setIsReverseMode] = useState(false); // リバースモード状態

  // 画像がアップロードされたらステップ2に進む
  useEffect(() => {
    if (image && !isReverseMode) {
      setActiveStep(2);
    }
  }, [image, isReverseMode]);

  // 結果が生成されたらステップ5に進む  
  useEffect(() => {
    if (result && !isReverseMode) {
      setActiveStep(5);
    }
  }, [result, isReverseMode]);

  // モード切替
  const toggleMode = () => {
    setIsReverseMode(!isReverseMode);
    setActiveStep(1); // ステップをリセット
  };

  // リバースモードの場合
  if (isReverseMode) {
    return (
      <div className="app">
        <SessionManager />
        <ReverseMode onBack={() => setIsReverseMode(false)} />
      </div>
    );
  }

  return (
    <div className="app">
      {/* セッション管理コンポーネント */}
      <SessionManager />
      
      <header className="app-header">
        <div className="app-title-container">
          <h1 className="app-title">pozt</h1>
          <div className="app-title-bar"></div>
        </div>
        <p className="app-subtitle">Pattern Optical Zone Technology - 視覚の魔法を体験しよう</p>
        
        {/* モード切替ボタン */}
        <div className="mode-toggle-container">
          <button 
            className="mode-toggle-button"
            onClick={toggleMode}
            title="リバースモードに切り替え"
          >
            <FiRefreshCw className="mode-icon" />
            <span className="mode-text">リバースモード</span>
            <FiArrowRight className="mode-arrow" />
          </button>
          <div className="mode-description">
            <small>モアレ画像から隠し画像を抽出</small>
          </div>
        </div>
        
        {/* アクセス制御情報表示 */}
        <div className="access-control-info">
          <div className="access-info-badge">
            <span className="security-icon">🔒</span>
            <span className="security-text">セキュアアクセス - pozt.iodo.co.jp 認証済み</span>
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="app-description">
          <p>
            光学パターン技術を活用して、見る角度や表示環境によって変化する驚きの視覚アート作品を作成できる無料のウェブアプリケーションです。
          </p>
          <div className="mode-info">
            <div className="mode-card current-mode">
              <div className="mode-icon-large">🎨</div>
              <h3>通常モード（現在）</h3>
              <p>画像にモアレ効果を適用して隠し画像を作成</p>
            </div>
            <div className="mode-switch-arrow">⇄</div>
            <div className="mode-card other-mode" onClick={toggleMode}>
              <div className="mode-icon-large">🔍</div>
              <h3>リバースモード</h3>
              <p>モアレ画像から隠し画像を抽出・表示</p>
              <div className="mode-card-overlay">
                <span>クリックで切り替え</span>
              </div>
            </div>
          </div>
          <div className="security-notice">
            <small>
              🛡️ このアプリケーションは安全な接続で保護されています。セッションは30分間有効です。
            </small>
          </div>
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
        <div className="footer-modes">
          <small>
            💡 <strong>ヒント:</strong> 
            通常モードで隠し画像を作成した後、リバースモードでその画像から隠し画像を抽出してみましょう！
          </small>
        </div>
        <div className="footer-security">
          <small>🔐 Secured by domain access control | Session timeout: 30 minutes</small>
        </div>
      </footer>
    </div>
  );
}

export default App;
