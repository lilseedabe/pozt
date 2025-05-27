"""
特殊視覚効果による隠し画像ジェネレーターの設定
"""

# 画像サイズ設定
TARGET_WIDTH = 2430   # 固定サイズの幅
TARGET_HEIGHT = 3240  # 固定サイズの高さ

# モード設定
PATTERN_TYPES = {
    "horizontal": "横パターン（水平）",
    "vertical": "縦パターン（垂直）"
}

# パターンタイプ定義
STRIPE_METHODS = {
    "overlay": "マスク重ね合わせモード",
    "high_frequency": "高周波パターン + 重ね合わせ融合",
    "moire_pattern": "完全パターン + 重ね合わせ融合",
    "adaptive": "標準視覚効果 + 重ね合わせ融合",
    "adaptive_subtle": "控えめ視覚効果 + 重ね合わせ融合",
    "adaptive_strong": "強め視覚効果 + 重ね合わせ融合",
    "adaptive_minimal": "最小視覚効果 + 重ね合わせ融合",
    "perfect_subtle": "やや強め視覚効果 + 重ね合わせ融合",
    "ultra_subtle": "中程度視覚効果 + 重ね合わせ融合", 
    "near_perfect": "やや控えめ視覚効果 + 重ね合わせ融合",
    "color_preserving": "色調保存モード + 重ね合わせ融合",
    "hue_preserving": "色相保存モード + 重ね合わせ融合",
    "blended": "ブレンドモード + 重ね合わせ融合",
    "hybrid": "混合モード（可変比率）"
}

# 強度マッピング
STRENGTH_MAP = {
    "high_frequency": 0.015,    # 高周波モード
    "adaptive": 0.02,           # 標準
    "adaptive_subtle": 0.015,   # 控えめ
    "adaptive_strong": 0.03,    # 強め
    "adaptive_minimal": 0.01,   # 最小
    "perfect_subtle": 0.025,    # 弱めに調整
    "ultra_subtle": 0.02,       # 弱めに調整
    "near_perfect": 0.018,      # 弱めに調整
    "color_preserving": 0.025,  # 色調保存モード
    "hue_preserving": 0.02,     # 色相保存モード
    "blended": 0.022           # ブレンドモード
}

# リサイズ方法
RESIZE_METHODS = {
    "contain": "アスペクト比保持（黒帯あり）", 
    "cover": "画面を埋める", 
    "stretch": "引き伸ばし"
}

# デフォルト値
DEFAULT_REGION_SIZE = 150
DEFAULT_BORDER_WIDTH = 3
