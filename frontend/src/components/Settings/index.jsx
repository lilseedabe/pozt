// Settings/index.jsx に追加する高速化表示機能

import React, { useState } from 'react';
import { useAppContext } from '../../context/AppContext';
import { processImage } from '../../services/api';
import './styles.css';

const Settings = ({ onComplete }) => {
  const { state, actions } = useAppContext();
  const { image, region, settings } = state;
  
  const [localSettings, setLocalSettings] = useState({
    patternType: settings.patternType,
    stripeMethod: settings.stripeMethod,
    resizeMethod: settings.resizeMethod,
    addBorder: settings.addBorder,
    borderWidth: settings.borderWidth,
    overlayRatio: settings.overlayRatio
  });
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState(null);
  const [processingTime, setProcessingTime] = useState(null);
  const [processingProgress, setProcessingProgress] = useState(0);
  
  // 処理時間の推定
  const estimateProcessingTime = () => {
    const complexityScores = {
      "overlay": 1,
      "high_frequency": 2,
      "adaptive": 1.5,
      "adaptive_subtle": 1.5,
      "adaptive_strong": 1.5,
      "moire_pattern": 3,
      "color_preserving": 4,
      "hue_preserving": 4,
      "blended": 3,
      "hybrid_overlay": 2.5
    };
    
    const baseTime = 8; // 基本処理時間（秒）
    const complexity = complexityScores[localSettings.stripeMethod] || 2;
    return Math.round(baseTime * complexity);
  };
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setLocalSettings({
      ...localSettings,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  const handleRangeChange = (e) => {
    const { name, value } = e.target;
    setLocalSettings({
      ...localSettings,
      [name]: parseFloat(value)
    });
  };
  
  const simulateProgress = (estimatedTime) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += (100 / estimatedTime) * 0.1; // 0.1秒ごとに更新
      setProcessingProgress(Math.min(progress, 95)); // 95%で停止
      
      if (progress >= 95) {
        clearInterval(interval);
      }
    }, 100);
    
    return interval;
  };
  
  const handle
