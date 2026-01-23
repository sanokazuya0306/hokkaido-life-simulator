"""
人生ガチャ - Reflex版

メインアプリケーションエントリーポイント
"""

import reflex as rx
from .pages.index import index
from .state import GachaState


# Google Fontsの読み込み
STYLESHEETS = [
    "https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;700&family=Zen+Old+Mincho:wght@700&family=Roboto:wght@400;600;900&display=swap",
]


# グローバルスタイル
GLOBAL_STYLE = {
    "html, body": {
        "margin": "0",
        "padding": "0",
        "font_family": "'Zen Kaku Gothic New', sans-serif",
        "background_color": "#FFFFFF",
    },
    "*": {
        "box_sizing": "border-box",
    },
    # Radixコンポーネントのデフォルト幅制限を解除
    ".rt-Flex": {
        "max_width": "none !important",
    },
    ".rt-Box": {
        "max_width": "none !important",
    },
}


# アプリケーション作成
app = rx.App(
    stylesheets=STYLESHEETS,
    style=GLOBAL_STYLE,
    theme=rx.theme(
        accent_color="gray",
        radius="medium",
    ),
)

# ルート設定
app.add_page(index, route="/", title="人生ガチャ")
