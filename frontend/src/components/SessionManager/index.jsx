import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './styles.css';

const SessionManager = () => {
  const [sessionInfo, setSessionInfo] = useState(null);
  const [showWarning, setShowWarning] = useState(false);
  const [remainingTime, setRemainingTime] = useState(null);
  const [isSessionExpired, setIsSessionExpired] = useState(false);

  // セッション状態を取得
  const fetchSessionStatus = async () => {
    try {
      const response = await axios.get('/api/session-status');
      const data = response.data;
      
      setSessionInfo(data);
      
      if (data.remaining_seconds && data.remaining_seconds !== 'Unknown') {
        const remaining = parseInt(data.remaining_seconds);
        setRemainingTime(remaining);
        
        // 5分以下で警告表示
        if (remaining <= 300 && remaining > 0) {
          setShowWarning(true);
        } else if (remaining <= 0) {
          setIsSessionExpired(true);
        } else {
          setShowWarning(false);
        }
      }
    } catch (error) {
      console.error('セッション状態の取得に失敗:', error);
      if (error.response && error.response.status === 403) {
        setIsSessionExpired(true);
      }
    }
  };

  // カウントダウンタイマー
  useEffect(() => {
    const interval = setInterval(() => {
      if (remainingTime !== null && remainingTime > 0) {
        setRemainingTime(prev => {
          const newTime = prev - 1;
          if (newTime <= 300 && newTime > 0) {
            setShowWarning(true);
          } else if (newTime <= 0) {
            setIsSessionExpired(true);
            setShowWarning(false);
          }
          return newTime;
        });
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [remainingTime]);

  // 定期的にセッション状態をチェック
  useEffect(() => {
    // 初回取得
    fetchSessionStatus();
    
    // 5分毎に状態確認
    const interval = setInterval(fetchSessionStatus, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  // 時間をフォーマット
  const formatTime = (seconds) => {
    if (!seconds || seconds < 0) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  // セッション延長（正規サイトへリダイレクト）
  const extendSession = () => {
    window.location.href = 'https://pozt.iodo.co.jp';
  };

  // セッション期限切れダイアログ
  if (isSessionExpired) {
    return (
      <div className="session-expired-overlay">
        <div className="session-expired-dialog">
          <div className="session-expired-icon">⏰</div>
          <h2>セッションが期限切れです</h2>
          <p>アプリケーションを継続利用するには、正規サイトから再度アクセスしてください。</p>
          <button 
            className="redirect-button"
            onClick={extendSession}
          >
            正規サイトへ移動
          </button>
          <div className="session-info">
            <small>このページは5秒後に自動的にリダイレクトされます...</small>
          </div>
        </div>
      </div>
    );
  }

  // 警告表示
  if (showWarning && remainingTime) {
    return (
      <div className="session-warning">
        <div className="warning-content">
          <div className="warning-icon">⚠️</div>
          <div className="warning-text">
            <strong>セッション期限が近づいています</strong>
            <p>残り時間: <span className="time-remaining">{formatTime(remainingTime)}</span></p>
          </div>
          <button 
            className="extend-button"
            onClick={extendSession}
          >
            セッション延長
          </button>
          <button 
            className="dismiss-button"
            onClick={() => setShowWarning(false)}
          >
            ×
          </button>
        </div>
      </div>
    );
  }

  // 通常時のセッション情報表示（オプション）
  if (sessionInfo && remainingTime > 300) {
    return (
      <div className="session-info-bar">
        <div className="session-status">
          <span className="status-icon">🔒</span>
          <span className="status-text">
            セッション有効 (残り: {formatTime(remainingTime)})
          </span>
        </div>
      </div>
    );
  }

  return null;
};

export default SessionManager;
