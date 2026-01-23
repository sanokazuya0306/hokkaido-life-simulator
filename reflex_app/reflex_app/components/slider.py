"""
スライダーコンポーネント

Figmaデザイン準拠: 600px幅、0-20の範囲
"""

import reflex as rx
from ..state import GachaState


def people_slider() -> rx.Component:
    """
    人数選択スライダー
    
    Figmaデザイン: 幅600px、0-20の範囲
    """
    return rx.box(
        rx.vstack(
            # 現在の値を表示
            rx.text(
                rx.text.span(GachaState.num_people),
                rx.text.span("人"),
                style={
                    "font_family": "'Roboto', sans-serif",
                    "font_weight": "600",
                    "font_size": "24px",
                    "color": "#323232",
                    "text_align": "center",
                },
            ),
            # スライダー
            rx.slider(
                default_value=[1],
                min=0,
                max=20,
                step=1,
                on_value_commit=GachaState.set_num_people,
                style={
                    "width": "100%",
                    "--slider-track-background": "#E0E0E0",
                    "--slider-range-background": "#141414",
                    "--slider-thumb-background": "#141414",
                },
            ),
            # 範囲ラベル
            rx.hstack(
                rx.text("0", style={"color": "#666", "font_size": "12px"}),
                rx.spacer(),
                rx.text("20", style={"color": "#666", "font_size": "12px"}),
                width="100%",
            ),
            spacing="2",
            align="center",
            width="100%",
        ),
        style={
            "max_width": "600px",
            "width": "600px",
        },
    )
