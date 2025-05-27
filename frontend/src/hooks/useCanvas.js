import { useRef, useEffect, useState, useCallback } from 'react';

export const useCanvas = (imageUrl) => {
  const canvasRef = useRef(null);
  const [region, setRegion] = useState({ x: 100, y: 100, width: 150, height: 150 });
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
  
  // 領域描画関数をuseCallbackでメモ化
  const drawRegion = useCallback((ctx, regionData, img) => {
    const { x, y, width, height } = regionData;
    
    // 画像を再描画
    ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    ctx.drawImage(img, 0, 0);
    
    // 半透明のオーバーレイを描画
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
    ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
    
    // 選択領域を切り抜く
    ctx.globalCompositeOperation = 'destination-out';
    ctx.fillStyle = 'rgba(255, 255, 255, 1)';
    ctx.fillRect(x, y, width, height);
    ctx.globalCompositeOperation = 'source-over';
    
    // 領域の境界線を描画
    ctx.strokeStyle = '#00a8ff';
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, width, height);
    
    // リサイズハンドルを描画
    const handleSize = 8;
    ctx.fillStyle = '#00a8ff';
    ctx.fillRect(x + width - handleSize/2, y + height - handleSize/2, handleSize, handleSize);
    
    // ラベルを表示
    ctx.fillStyle = 'rgba(0, 168, 255, 0.8)';
    ctx.fillRect(x, y - 20, 100, 20);
    ctx.fillStyle = 'white';
    ctx.font = '12px Arial';
    ctx.fillText(`${width}x${height}`, x + 5, y - 6);
  }, []);
  
  // キャンバス初期化処理
  useEffect(() => {
    if (!imageUrl || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    const img = new Image();
    img.src = imageUrl;
    img.onload = () => {
      // キャンバスサイズを画像に合わせる
      canvas.width = img.width;
      canvas.height = img.height;
      setImageSize({ width: img.width, height: img.height });
      
      // 画像描画
      ctx.drawImage(img, 0, 0);
      
      // 初期領域を描画
      drawRegion(ctx, region, img);
    };
  }, [imageUrl, region, drawRegion]); // 依存配列に region と drawRegion を追加
  
  // 領域が変更されたら再描画
  useEffect(() => {
    if (!canvasRef.current || !imageUrl) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    const img = new Image();
    img.src = imageUrl;
    img.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      drawRegion(ctx, region, img);
    };
  }, [region, imageUrl, drawRegion]); // drawRegion を依存配列に追加
  
  // マウスダウンイベントハンドラ
  const handleMouseDown = (e) => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // リサイズハンドルをクリックしたかチェック
    const handleSize = 8;
    if (
      x >= region.x + region.width - handleSize &&
      x <= region.x + region.width + handleSize &&
      y >= region.y + region.height - handleSize &&
      y <= region.y + region.height + handleSize
    ) {
      setIsResizing(true);
      setDragStart({ x, y });
      return;
    }
    
    // 領域内をクリックしたかチェック
    if (
      x >= region.x && 
      x <= region.x + region.width && 
      y >= region.y && 
      y <= region.y + region.height
    ) {
      setIsDragging(true);
      setDragStart({ x, y });
    } else {
      // 新しい領域の開始点
      const newRegion = {
        x: x,
        y: y,
        width: 0,
        height: 0
      };
      setRegion(newRegion);
      setIsDragging(true);
      setDragStart({ x, y });
    }
  };
  
  // マウス移動イベントハンドラ
  const handleMouseMove = (e) => {
    if (!canvasRef.current || (!isDragging && !isResizing)) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    if (isResizing) {
      // リサイズ処理
      const newWidth = Math.max(50, x - region.x);
      const newHeight = Math.max(50, y - region.y);
      
      // 画像の境界チェック
      const boundedWidth = Math.min(newWidth, imageSize.width - region.x);
      const boundedHeight = Math.min(newHeight, imageSize.height - region.y);
      
      setRegion({
        ...region,
        width: boundedWidth,
        height: boundedHeight
      });
    } else if (isDragging) {
      // ドラッグ処理
      const dx = x - dragStart.x;
      const dy = y - dragStart.y;
      
      if (region.width === 0 && region.height === 0) {
        // 新規選択の場合
        const newWidth = Math.abs(x - region.x);
        const newHeight = Math.abs(y - region.y);
        const newX = Math.min(x, region.x);
        const newY = Math.min(y, region.y);
        
        setRegion({
          x: newX,
          y: newY,
          width: newWidth,
          height: newHeight
        });
      } else {
        // 既存領域の移動
        let newX = region.x + dx;
        let newY = region.y + dy;
        
        // 画像の境界チェック
        newX = Math.max(0, Math.min(newX, imageSize.width - region.width));
        newY = Math.max(0, Math.min(newY, imageSize.height - region.height));
        
        setRegion({
          ...region,
          x: newX,
          y: newY
        });
        
        setDragStart({ x, y });
      }
    }
  };
  
  // マウスアップイベントハンドラ
  const handleMouseUp = () => {
    setIsDragging(false);
    setIsResizing(false);
  };
  
  // グリッド位置に領域を配置する関数
  const moveToGridPosition = (gridPosition) => {
    if (!imageSize.width || !imageSize.height) return;
    
    const gridRow = Math.floor((gridPosition - 1) / 3);
    const gridCol = (gridPosition - 1) % 3;
    
    const cellWidth = imageSize.width / 3;
    const cellHeight = imageSize.height / 3;
    
    const newX = Math.floor(gridCol * cellWidth + (cellWidth - region.width) / 2);
    const newY = Math.floor(gridRow * cellHeight + (cellHeight - region.height) / 2);
    
    // 境界チェック
    const boundedX = Math.max(0, Math.min(newX, imageSize.width - region.width));
    const boundedY = Math.max(0, Math.min(newY, imageSize.height - region.height));
    
    setRegion({
      ...region,
      x: boundedX,
      y: boundedY
    });
  };
  
  // 領域サイズを設定
  const setRegionSize = (width, height) => {
    // 境界チェック
    const boundedWidth = Math.min(width, imageSize.width - region.x);
    const boundedHeight = Math.min(height, imageSize.height - region.y);
    
    setRegion({
      ...region,
      width: boundedWidth,
      height: boundedHeight
    });
  };
  
  // 領域を指定方向に移動
  const moveRegion = (direction, step = 20) => {
    let newX = region.x;
    let newY = region.y;
    
    switch (direction) {
      case 'up':
        newY = Math.max(0, region.y - step);
        break;
      case 'down':
        newY = Math.min(imageSize.height - region.height, region.y + step);
        break;
      case 'left':
        newX = Math.max(0, region.x - step);
        break;
      case 'right':
        newX = Math.min(imageSize.width - region.width, region.x + step);
        break;
      default:
        break;
    }
    
    setRegion({
      ...region,
      x: newX,
      y: newY
    });
  };
  
  return {
    canvasRef,
    region,
    setRegion,
    handleMouseDown,
    handleMouseMove,
    handleMouseUp,
    moveToGridPosition,
    setRegionSize,
    moveRegion
  };
};
