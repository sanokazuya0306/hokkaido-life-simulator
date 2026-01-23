"""Reflex configuration."""

import reflex as rx
import os


# Railway/Render/Heroku用: 環境変数からAPIエンドポイントを取得
api_url = os.getenv("API_URL", None)

config = rx.Config(
    app_name="reflex_app",
    title="人生ガチャ",
    description="北海道・東京の人生シミュレーター",
    show_built_with_reflex=False,  # セルフホスト時は常に非表示
    # デプロイ時のAPI URL（環境変数から取得）
    api_url=api_url,
    # Tailwind CSS有効化
    tailwind={
        "theme": {
            "extend": {
                "fontFamily": {
                    "zen": ["Zen Kaku Gothic New", "sans-serif"],
                    "mincho": ["Zen Old Mincho", "serif"],
                },
                "colors": {
                    "gacha": {
                        "bg": "#D9D9D9",
                        "border": "#575757",
                        "text": "#323232",
                    }
                }
            }
        }
    },
)
