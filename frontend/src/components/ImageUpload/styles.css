.image-upload {
  display: flex;
  flex-direction: column;
  gap: var(--space-lg);
  width: 100%;
  animation: fadeIn 0.8s ease-out;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 400px;
  border: 3px dashed var(--border-primary);
  border-radius: var(--radius-xl);
  padding: var(--space-2xl);
  cursor: pointer;
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.upload-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--gradient-card);
  opacity: 0;
  transition: opacity var(--transition-normal);
  z-index: 0;
}

.upload-area::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: conic-gradient(
    transparent,
    rgba(0, 212, 255, 0.3),
    transparent,
    rgba(99, 102, 241, 0.3),
    transparent
  );
  animation: rotate 4s linear infinite;
  opacity: 0;
  transition: opacity var(--transition-normal);
  z-index: 0;
}

.upload-area:hover {
  border-color: var(--accent-primary);
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl), var(--shadow-glow);
  background: var(--bg-card);
}

.upload-area:hover::before {
  opacity: 1;
}

.upload-area:hover::after {
  opacity: 0.5;
}

.upload-area.dragging {
  border-color: var(--accent-primary);
  background: var(--bg-card);
  transform: scale(1.05);
  box-shadow: 0 0 0 6px rgba(0, 212, 255, 0.2), var(--shadow-xl);
  animation: pulse 1s ease-in-out infinite;
}

.upload-area.dragging::before {
  opacity: 1;
}

.upload-area.dragging::after {
  opacity: 0.8;
}

.upload-area.uploading {
  pointer-events: none;
  border-color: var(--accent-success);
  background: rgba(16, 185, 129, 0.1);
}

.file-input {
  display: none;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  z-index: 2;
  position: relative;
}

.upload-icon {
  font-size: 4rem;
  color: var(--accent-primary);
  margin-bottom: var(--space-lg);
  animation: float 3s ease-in-out infinite;
  filter: drop-shadow(0 0 20px rgba(0, 212, 255, 0.3));
}

.upload-area:hover .upload-icon {
  animation: pulse 1s ease-in-out infinite;
  transform: scale(1.1);
  color: var(--text-primary);
}

.upload-content h3 {
  margin-bottom: var(--space-md);
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.upload-content p {
  margin-bottom: var(--space-xl);
  color: var(--text-secondary);
  font-size: 1.1rem;
  font-weight: 500;
}

.supported-formats {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md) var(--space-lg);
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
  font-size: 1rem;
  color: var(--text-secondary);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}

.upload-area:hover .supported-formats {
  background: var(--bg-secondary);
  border-color: var(--border-accent);
  box-shadow: var(--shadow-md);
}

.format-icon {
  color: var(--accent-primary);
  font-size: 1.25rem;
  animation: float 3s ease-in-out infinite 0.5s;
}

.upload-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-lg);
  z-index: 2;
  position: relative;
}

.upload-status .spinner {
  border: 6px solid rgba(0, 212, 255, 0.1);
  border-radius: 50%;
  border-top: 6px solid var(--accent-primary);
  width: 60px;
  height: 60px;
  animation: rotate 1s linear infinite;
  box-shadow: var(--shadow-glow);
}

.upload-status p {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--accent-primary);
  margin: 0;
  animation: pulse 2s infinite;
}

.upload-status small {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-top: var(--space-sm);
}

.upload-status.success .success-icon {
  font-size: 4rem;
  color: var(--accent-success);
  animation: bounce 0.6s ease-in-out;
  filter: drop-shadow(0 0 20px rgba(16, 185, 129, 0.5));
}

.upload-status.success p {
  color: var(--accent-success);
  animation: none;
}

.upload-specs {
  margin-top: var(--space-md);
  padding: var(--space-sm);
  background: rgba(0, 0, 0, 0.2);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--accent-primary);
}

.upload-specs small {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.upload-error {
  padding: var(--space-lg);
  background: rgba(239, 68, 68, 0.1);
  border-left: 6px solid var(--accent-danger);
  border-radius: var(--radius-lg);
  color: var(--accent-danger);
  font-weight: 500;
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow-md);
  animation: slideUp 0.3s ease-out;
}

.upload-error p {
  margin: 0;
  color: var(--accent-danger);
}

.retry-btn {
  margin-top: var(--space-md);
  padding: var(--space-sm) var(--space-md);
  background: var(--accent-danger);
  color: var(--text-primary);
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.retry-btn:hover {
  background: #dc2626;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* プログレスバー効果 */
.upload-area.uploading::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  height: 4px;
  background: var(--gradient-primary);
  animation: uploadProgress 2s ease-in-out;
  z-index: 3;
}

@keyframes uploadProgress {
  0% {
    width: 0%;
  }
  100% {
    width: 100%;
  }
}

/* ホバーグロー効果 */
.upload-area::after {
  border-radius: var(--radius-xl);
}

/* ドラッグ中のフィードバック */
.upload-area.dragging .upload-content {
  transform: scale(1.05);
}

.upload-area.dragging .upload-icon {
  color: var(--text-primary);
  transform: scale(1.2);
  animation: bounce 0.6s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% {
    transform: scale(1.2) translateY(0);
  }
  50% {
    transform: scale(1.2) translateY(-10px);
  }
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .upload-area {
    min-height: 320px;
    padding: var(--space-xl);
  }
  
  .upload-icon {
    font-size: 3rem;
  }
  
  .upload-content h3 {
    font-size: 1.5rem;
  }
  
  .upload-content p {
    font-size: 1rem;
  }
  
  .supported-formats {
    flex-direction: column;
    gap: var(--space-sm);
    text-align: center;
  }
}

@media (max-width: 480px) {
  .upload-area {
    min-height: 280px;
    padding: var(--space-lg);
  }
  
  .upload-icon {
    font-size: 2.5rem;
  }
  
  .upload-content h3 {
    font-size: 1.25rem;
  }
  
  .supported-formats {
    padding: var(--space-sm) var(--space-md);
    font-size: 0.9rem;
  }
}

/* アクセシビリティ */
@media (prefers-reduced-motion: reduce) {
  .upload-icon,
  .format-icon {
    animation: none;
  }
  
  .upload-area::after {
    animation: none;
  }
}

/* タッチデバイス用の調整 */
@media (hover: none) {
  .upload-area:hover {
    transform: none;
    box-shadow: var(--shadow-md);
  }
  
  .upload-area:active {
    transform: scale(0.98);
  }
}

/* 高DPI対応 */
@media (-webkit-min-device-pixel-ratio: 2) {
  .upload-area {
    border-width: 2px;
  }
  
  .upload-area.dragging {
    border-width: 3px;
  }
}
