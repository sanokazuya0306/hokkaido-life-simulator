"""Reflex configuration."""

import reflex as rx
import os


# Railway/Render用: 環境変数からポートを取得
port = int(os.getenv("PORT", "3000"))

config = rx.Config(
    app_name="reflex_app",
    title="人生ガチャ",
    description="北海道・東京の人生シミュレーター",
    show_built_with_reflex=False,
    # 単一ポートで動作させる
    frontend_port=port,
    backend_port=port,
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
