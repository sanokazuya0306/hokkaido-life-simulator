"""Reflex configuration."""

import reflex as rx
import os


# API URL: ビルド時は localhost、実行時はCaddyがプロキシ
# 環境変数で上書き可能
api_url = os.getenv("API_URL", "http://localhost:8000")

config = rx.Config(
    app_name="reflex_app",
    title="人生ガチャ",
    description="北海道・東京の人生シミュレーター",
    show_built_with_reflex=False,  # セルフホスト時は常に非表示
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
