"""Reflex configuration."""

import reflex as rx
import os


# Railway/Render用: 環境変数からポートを取得（デフォルト8000）
port = int(os.getenv("PORT", "8000"))

# API URL（環境変数で指定可能、未指定時はReflexが自動検出）
api_url = os.getenv("API_URL")

config = rx.Config(
    app_name="reflex_app",
    title="人生ガチャ",
    description="北海道・東京の人生シミュレーター",
    show_built_with_reflex=False,  # セルフホスト時は常に非表示
    # ポート設定（Railwayは環境変数PORTを使用）
    backend_port=port,
    frontend_port=port,
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
