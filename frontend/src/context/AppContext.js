import React, { createContext, useContext, useReducer } from 'react';

// 初期状態（パラメータ拡張版・最適化済み）
const initialState = {
  image: null,
  imageUrl: null,
  region: null,
  settings: {
    patternType: 'horizontal',
    stripeMethod: 'overlay',
    resizeMethod: 'contain',
    addBorder: true,
    borderWidth: 3,
    overlayRatio: 0.4,
    // 最適化されたデフォルト値
    strength: 0.02,
    opacity: 0.0,           // 0.6 → 0.0 に変更（最適化）
    enhancementFactor: 1.2,
    frequency: 1,
    blurRadius: 0,          // 5 → 0 に変更（最適化）
    contrastBoost: 1.0,
    colorShift: 0.0,
    sharpnessBoost: 0.0     // 新しいパラメータを追加
  },
  processingStatus: 'idle', // idle, processing, success, error
  result: null,
  error: null
};

// アクションタイプ
const actionTypes = {
  SET_IMAGE: 'SET_IMAGE',
  SET_REGION: 'SET_REGION',
  UPDATE_SETTINGS: 'UPDATE_SETTINGS',
  START_PROCESSING: 'START_PROCESSING',
  PROCESSING_SUCCESS: 'PROCESSING_SUCCESS',
  PROCESSING_ERROR: 'PROCESSING_ERROR',
  RESET: 'RESET'
};

// リデューサー（パラメータ拡張対応）
function appReducer(state, action) {
  switch (action.type) {
    case actionTypes.SET_IMAGE:
      return {
        ...state,
        image: action.payload.image,
        imageUrl: action.payload.imageUrl,
        region: null, // 新しい画像がセットされたら領域をリセット
        result: null // 結果もリセット
      };
    case actionTypes.SET_REGION:
      return {
        ...state,
        region: action.payload
      };
    case actionTypes.UPDATE_SETTINGS:
      return {
        ...state,
        settings: {
          ...state.settings,
          ...action.payload
        }
      };
    case actionTypes.START_PROCESSING:
      return {
        ...state,
        processingStatus: 'processing',
        error: null
      };
    case actionTypes.PROCESSING_SUCCESS:
      return {
        ...state,
        processingStatus: 'success',
        result: action.payload
      };
    case actionTypes.PROCESSING_ERROR:
      return {
        ...state,
        processingStatus: 'error',
        error: action.payload
      };
    case actionTypes.RESET:
      return initialState;
    default:
      return state;
  }
}

// コンテキストの作成
const AppContext = createContext();

// プロバイダーコンポーネント（パラメータ拡張対応）
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // アクション作成関数
  const actions = {
    setImage: (image, imageUrl) => dispatch({ 
      type: actionTypes.SET_IMAGE, 
      payload: { image, imageUrl } 
    }),
    setRegion: (region) => dispatch({ 
      type: actionTypes.SET_REGION, 
      payload: region 
    }),
    updateSettings: (settings) => {
      console.log('🔧 Updating settings with enhanced parameters:', settings);
      dispatch({ 
        type: actionTypes.UPDATE_SETTINGS, 
        payload: settings 
      });
    },
    startProcessing: () => {
      console.log('🚀 Starting enhanced processing...');
      dispatch({ 
        type: actionTypes.START_PROCESSING 
      });
    },
    processingSuccess: (result) => {
      console.log('✅ Enhanced processing succeeded:', result);
      dispatch({ 
        type: actionTypes.PROCESSING_SUCCESS, 
        payload: result 
      });
    },
    processingError: (error) => {
      console.error('❌ Enhanced processing failed:', error);
      dispatch({ 
        type: actionTypes.PROCESSING_ERROR, 
        payload: error 
      });
    },
    reset: () => {
      console.log('🔄 Resetting app state');
      dispatch({ 
        type: actionTypes.RESET 
      });
    }
  };

  // デバッグ用: 状態変更をログ出力
  React.useEffect(() => {
    console.log('📊 Enhanced App State Updated:', {
      hasImage: !!state.image,
      hasRegion: !!state.region,
      processingStatus: state.processingStatus,
      settings: state.settings,
      hasResult: !!state.result
    });
  }, [state]);

  return (
    <AppContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </AppContext.Provider>
  );
}

// カスタムフック
export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}
