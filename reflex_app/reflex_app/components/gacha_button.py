"""
ガチャボタンコンポーネント

Figmaデザイン準拠: 600x200px、角丸100px、枠線10px
"""

import reflex as rx
from ..state import GachaState


def gacha_button() -> rx.Component:
    """
    メインのガチャボタン
    
    Figmaデザイン:
    - サイズ: 600x160px
    - 背景: #D9D9D9
    - 枠線: 5px solid #575757
    - 角丸: 100px
    - フォント: 36px, bold
    """
    return rx.button(
        "ガチャを引く",
        on_click=GachaState.pull_gacha,
        disabled=GachaState.num_people <= 0,
        style={
            "width": "600px",
            "height": "160px",
            "background": "#D9D9D9",
            "border": "5px solid #575757",
            "border_radius": "100px",
            "font_family": "'Zen Kaku Gothic New', sans-serif",
            "font_weight": "700",
            "font_size": "36px",
            "color": "#323232",
            "letter_spacing": "0.05em",
            "cursor": "pointer",
            "transition": "all 0.2s ease",
            "_hover": {
                "background": "#CCCCCC",
                "border_color": "#454545",
            },
            "_active": {
                "background": "#BEBEBE",
                "transform": "scale(0.98)",
            },
            "_disabled": {
                "opacity": "0.5",
                "cursor": "not-allowed",
            },
        },
    )


def secondary_button(text: str, on_click) -> rx.Component:
    """
    セカンダリボタン（情報ボタン、戻るボタン等）
    """
    return rx.button(
        text,
        on_click=on_click,
        style={
            "background": "#D9D9D9",
            "border": "none",
            "border_radius": "4px",
            "font_family": "'Zen Kaku Gothic New', sans-serif",
            "font_weight": "400",
            "font_size": "14px",
            "color": "#000000",
            "padding": "8px 16px",
            "cursor": "pointer",
            "transition": "background 0.2s ease",
            "_hover": {
                "background": "#CCCCCC",
            },
        },
    )


def back_button(text: str = "← 戻る", on_click=None) -> rx.Component:
    """戻るボタン"""
    return secondary_button(text, on_click or GachaState.go_to_gacha)


def refresh_button(on_click=None) -> rx.Component:
    """再生成ボタン"""
    return secondary_button("↺ 再生成", on_click or GachaState.regenerate)
