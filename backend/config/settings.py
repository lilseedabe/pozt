"""
特殊視覚効果による隠し画像ジェネレーターの設定（高品質維持・プレビュー削減版）
"""

# 画像サイズ設定（高品質維持）
TARGET_WIDTH = 2430   # 元のサイズを維持
TARGET_HEIGHT = 3240  # 元のサイズを維持

# モード設定
PATTERN_TYPES = {
    "horizontal": "横パターン（水平）",
    "vertical": "縦パターン（垂直）"
}

# パターンタイプ定義（全て維持）
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

# 強度マッピング（全て維持）
STRENGTH_MAP = {
    "high_frequency": 0.015,
    "adaptive": 0.02,
    "adaptive_subtle": 0.015,
    "adaptive_strong": 0.03,
    "adaptive_minimal": 0.01,
    "perfect_subtle": 0.025,
    "ultra_subtle": 0.02,
    "near_perfect": 0.018,
    "color_preserving": 0.025,
    "hue_preserving": 0.02,
    "blended": 0.022
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

# メモリ最適化設定（プレビュー削減のみ）
ENABLE_SINGLE_PREVIEW_MODE = True  # プレビューを1つのみ生成
