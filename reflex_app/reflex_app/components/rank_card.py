"""
ランクカードコンポーネント

Figmaデザイン準拠: 111x148px、角丸8px
"""

import reflex as rx
from ..state import GachaState


def get_rank_card_style(rank: str) -> dict:
    """ランクに応じたスタイルを取得"""
    base_style = {
        "width": "111px",
        "height": "148px",
        "border_radius": "8px",
        "display": "flex",
        "align_items": "center",
        "justify_content": "center",
        "font_family": "'Roboto', sans-serif",
        "font_weight": "600",
        "font_size": "48px",
        "cursor": "pointer",
        "transition": "transform 0.2s, box-shadow 0.2s",
        "margin": "8px auto",
        "_hover": {
            "transform": "translateY(-4px)",
            "box_shadow": "0 8px 20px rgba(0, 0, 0, 0.15)",
        },
    }
    
    if rank == "SS":
        base_style.update({
            "background": "linear-gradient(135deg, #080808 0%, #6E6E6E 100%)",
            "color": "#D8D8D8",
        })
    elif rank == "S":
        base_style.update({
            "background": "linear-gradient(135deg, #292929 0%, #8F8F8F 100%)",
            "color": "#000000",
        })
    else:
        base_style.update({
            "background": "#D9D9D9",
            "color": "#000000",
        })
    
    return base_style


def rank_card_with_style(rank_text, index: int, bg_style: str, text_color: str) -> rx.Component:
    """スタイル付きランクカード"""
    return rx.box(
        rx.vstack(
            rx.box(
                rank_text,
                style={
                    "width": "111px",
                    "height": "148px",
                    "border_radius": "8px",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "font_family": "'Roboto', sans-serif",
                    "font_weight": "600",
                    "font_size": "48px",
                    "cursor": "pointer",
                    "transition": "transform 0.2s, box-shadow 0.2s",
                    "margin": "8px auto",
                    "background": bg_style,
                    "color": text_color,
                    "_hover": {
                        "transform": "translateY(-4px)",
                        "box_shadow": "0 8px 20px rgba(0, 0, 0, 0.15)",
                    },
                },
            ),
            rx.button(
                "詳細",
                on_click=lambda: GachaState.select_life(index),
                style={
                    "width": "100%",
                    "background": "#D9D9D9",
                    "border": "none",
                    "border_radius": "4px",
                    "font_size": "12px",
                    "padding": "4px 8px",
                    "cursor": "pointer",
                    "_hover": {
                        "background": "#CCCCCC",
                    },
                },
            ),
            spacing="2",
            align="center",
        ),
    )


def rank_card_item(result, index: int) -> rx.Component:
    """
    ランクカード（結果一覧用、Reflex Var対応）
    
    Figma準拠: 111x148px、角丸8px
    カード全体がクリック可能で詳細画面へ遷移
    """
    rank = result["rank"]
    
    # Figma準拠のカードスタイル
    card_style = {
        "width": "111px",
        "height": "148px",
        "border_radius": "8px",
        "display": "flex",
        "align_items": "center",
        "justify_content": "center",
        "font_family": "'Roboto', sans-serif",
        "font_weight": "600",
        "font_size": "48px",
        "cursor": "pointer",
        "transition": "transform 0.2s, box-shadow 0.2s",
        "_hover": {
            "transform": "translateY(-4px)",
            "box_shadow": "0 8px 20px rgba(0, 0, 0, 0.15)",
        },
    }
    
    return rx.cond(
        rank == "SS",
        rx.box(
            rank,
            on_click=lambda: GachaState.select_life(index),
            style={
                **card_style,
                "background": "linear-gradient(135deg, #080808 0%, #6E6E6E 100%)",
                "color": "#D8D8D8",
            },
        ),
        rx.cond(
            rank == "S",
            rx.box(
                rank,
                on_click=lambda: GachaState.select_life(index),
                style={
                    **card_style,
                    "background": "linear-gradient(135deg, #292929 0%, #8F8F8F 100%)",
                    "color": "#000000",
                },
            ),
            rx.box(
                rank,
                on_click=lambda: GachaState.select_life(index),
                style={
                    **card_style,
                    "background": "#D9D9D9",
                    "color": "#000000",
                },
            ),
        ),
    )


def rank_card(rank: str, index: int) -> rx.Component:
    """
    ランクカード（静的なランク文字列用）
    """
    return rx.box(
        rx.vstack(
            rx.box(
                rank,
                style=get_rank_card_style(rank),
            ),
            rx.button(
                "詳細",
                on_click=lambda: GachaState.select_life(index),
                style={
                    "width": "100%",
                    "background": "#D9D9D9",
                    "border": "none",
                    "border_radius": "4px",
                    "font_size": "12px",
                    "padding": "4px 8px",
                    "cursor": "pointer",
                    "_hover": {
                        "background": "#CCCCCC",
                    },
                },
            ),
            spacing="2",
            align="center",
        ),
    )


def rank_card_grid() -> rx.Component:
    """
    ランクカードのグリッド表示（5列）
    Figma準拠: gap 40px、カード111x148px
    """
    return rx.box(
        rx.foreach(
            GachaState.score_results,
            lambda result, idx: rank_card_item(result, idx),
        ),
        style={
            "display": "grid",
            "grid_template_columns": "repeat(5, 111px)",
            "gap": "40px",
            "justify_content": "center",
        },
    )


def rank_display(rank: str) -> rx.Component:
    """
    詳細画面用のランク表示
    
    Figmaデザイン: 340x120px、角丸8px
    """
    # ランクに応じた背景色
    if rank == "SS":
        bg = "linear-gradient(135deg, #080808 0%, #6E6E6E 100%)"
        text_color = "#D8D8D8"
    elif rank == "S":
        bg = "linear-gradient(135deg, #292929 0%, #8F8F8F 100%)"
        text_color = "#000000"
    else:
        bg = "#C0C0C0"
        text_color = "#000000"
    
    return rx.box(
        rx.hstack(
            rx.text(
                "人生ランク",
                style={
                    "font_family": "'Zen Old Mincho', serif",
                    "font_weight": "700",
                    "font_size": "32px",
                    "color": text_color,
                    "text_shadow": "0 0 2px #FFFFFF" if rank != "SS" else "none",
                },
            ),
            rx.text(
                rank,
                style={
                    "font_family": "'Roboto', sans-serif",
                    "font_weight": "600",
                    "font_size": "56px",
                    "color": text_color,
                    "text_shadow": "0 0 2px #FFFFFF" if rank != "SS" else "none",
                },
            ),
            spacing="5",
            align="center",
            justify="center",
        ),
        style={
            "width": "340px",
            "height": "120px",
            "border_radius": "8px",
            "display": "flex",
            "align_items": "center",
            "justify_content": "center",
            "background": bg,
            "margin": "0 auto 20px auto",
        },
    )


def parent_rank_display(rank: str) -> rx.Component:
    """親ガチャランク表示"""
    return rx.hstack(
        rx.text(
            "親ガチャランク",
            style={
                "font_family": "'Zen Old Mincho', serif",
                "font_weight": "700",
                "font_size": "22px",
                "color": "#323232",
            },
        ),
        rx.text(
            rank,
            style={
                "font_family": "'Roboto', sans-serif",
                "font_weight": "600",
                "font_size": "36px",
                "color": "#000000",
            },
        ),
        spacing="4",
        align="center",
        justify="center",
    )
