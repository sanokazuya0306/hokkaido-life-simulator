"""
地域選択コンポーネント

Figmaデザイン準拠: 300x87px、角丸10px（セグメントコントロール）
"""

import reflex as rx
from ..state import GachaState


# 共通スタイル (Figma: 300x87px)
BUTTON_BASE_STYLE = {
    "height": "87px",
    "min_height": "87px",
    "width": "300px",
    "min_width": "300px",
    "font_family": "'Zen Kaku Gothic New', sans-serif",
    "font_size": "24px",
    "color": "#000000",
    "cursor": "pointer",
    "transition": "all 0.2s ease",
    "padding": "0 24px",
}


def region_selector() -> rx.Component:
    """
    地域選択セグメントコントロール
    
    Figmaデザイン: 幅600px（2ボタン合計）、高さ87px
    rx.condを使用して選択状態に応じたスタイルを動的に切り替え
    """
    return rx.hstack(
        # 北海道ボタン
        rx.button(
            "北海道",
            on_click=GachaState.select_hokkaido,
            style={
                **BUTTON_BASE_STYLE,
                "border_radius": "10px 0 0 10px",
                "background": rx.cond(
                    GachaState.is_hokkaido,
                    "#D9D9D9",
                    "rgba(0, 0, 0, 0.08)",
                ),
                "border": rx.cond(
                    GachaState.is_hokkaido,
                    "4px solid rgba(0, 0, 0, 0.2)",
                    "1px solid rgba(0, 0, 0, 0.15)",
                ),
                "font_weight": rx.cond(
                    GachaState.is_hokkaido,
                    "700",
                    "400",
                ),
            },
        ),
        # 東京ボタン
        rx.button(
            "東京",
            on_click=GachaState.select_tokyo,
            style={
                **BUTTON_BASE_STYLE,
                "border_radius": "0 10px 10px 0",
                "background": rx.cond(
                    GachaState.is_tokyo,
                    "#D9D9D9",
                    "rgba(0, 0, 0, 0.08)",
                ),
                "border": rx.cond(
                    GachaState.is_tokyo,
                    "4px solid rgba(0, 0, 0, 0.2)",
                    "1px solid rgba(0, 0, 0, 0.15)",
                ),
                "font_weight": rx.cond(
                    GachaState.is_tokyo,
                    "700",
                    "400",
                ),
            },
        ),
        spacing="0",
        justify="center",
        style={
            "max_width": "600px",
            "margin": "0 auto 20px auto",
        },
    )
