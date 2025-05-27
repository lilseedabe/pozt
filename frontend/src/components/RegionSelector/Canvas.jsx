import React from 'react';

const Canvas = ({ canvasRef, onMouseDown, onMouseMove, onMouseUp }) => {
  return (
    <canvas
      ref={canvasRef}
      onMouseDown={onMouseDown}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      onMouseLeave={onMouseUp}
      className="region-canvas"
    />
  );
};

export default Canvas;
