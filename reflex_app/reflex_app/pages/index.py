"""
メインページ

view_modeに応じて以下の画面を切り替え:
- gacha: ガチャ画面
- result: 結果一覧画面
- detail: 詳細画面
"""

import reflex as rx
from ..state import GachaState
from ..components.gacha_button import gacha_button, back_button, refresh_button, secondary_button
from ..components.region_selector import region_selector
from ..components.slider import people_slider
from ..components.rank_card import rank_card_grid
from ..components.detail_card import detail_card
from ..components.dialogs import about_gacha_dialog


def gacha_view() -> rx.Component:
    """
    ガチャ画面
    Figma準拠: 1280x832フレーム、絶対配置
    """
    return rx.box(
        # 中央揃え用コンテナ
        rx.el.div(
            # 地域選択 (x=340, y=107)
            rx.el.div(
                region_selector(),
                style={
                    "position": "absolute",
                    "top": "107px",
                    "left": "50%",
                    "transform": "translateX(-50%)",
                },
            ),
            
            # スライダー (x=340, y=271)
            rx.el.div(
                people_slider(),
                style={
                    "position": "absolute",
                    "top": "271px",
                    "left": "50%",
                    "transform": "translateX(-50%)",
                    "width": "600px",
                },
            ),
            
            # ガチャボタン (x=340, y=407)
            rx.el.div(
                gacha_button(),
                style={
                    "position": "absolute",
                    "top": "407px",
                    "left": "50%",
                    "transform": "translateX(-50%)",
                },
            ),
            
            # 下部ボタン (y=645) - 統合ダイアログ
            rx.el.div(
                about_gacha_dialog(),
                style={
                    "position": "absolute",
                    "top": "645px",
                    "left": "50%",
                    "transform": "translateX(-50%)",
                },
            ),
            
            style={
                "position": "relative",
                "width": "100%",
                "max_width": "1280px",
                "height": "832px",
                "margin": "0 auto",
            },
        ),
        width="100%",
        style={
            "height": "100vh",
            "display": "flex",
            "align_items": "center",
            "justify_content": "center",
            "overflow": "hidden",
        },
    )


def result_view() -> rx.Component:
    """
    結果一覧画面
    Figma準拠: ← 左上、↺ 右上、カウンター右下
    """
    # アイコンボタンスタイル (Figma: 48px font)
    icon_style = {
        "font_family": "'Roboto', sans-serif",
        "font_weight": "600",
        "font_size": "48px",
        "color": "#000000",
        "cursor": "pointer",
        "background": "transparent",
        "border": "none",
        "padding": "0",
        "line_height": "1",
        "_hover": {
            "opacity": "0.7",
        },
    }
    
    # カウンタースタイル (Figma: 20px font)
    counter_style = {
        "font_family": "'Roboto', sans-serif",
        "font_weight": "600",
        "font_size": "20px",
        "color": "#000000",
    }
    
    return rx.box(
        # 全体のコンテナ - 相対位置指定
        rx.box(
            # 左上: 戻るボタン
            rx.button(
                "←",
                on_click=GachaState.go_to_gacha,
                style={
                    **icon_style,
                    "position": "absolute",
                    "top": "76px",
                    "left": "126px",
                },
            ),
            
            # 右上: 再生成ボタン
            rx.button(
                "↺",
                on_click=GachaState.regenerate,
                style={
                    **icon_style,
                    "position": "absolute",
                    "top": "76px",
                    "right": "126px",
                },
            ),
            
            # 中央: カードグリッド
            rx.box(
                rank_card_grid(),
                style={
                    "position": "absolute",
                    "top": "50%",
                    "left": "50%",
                    "transform": "translate(-50%, -50%)",
                },
            ),
            
            # 右下: カウンター
            rx.text(
                GachaState.total_generated,
                style={
                    **counter_style,
                    "position": "absolute",
                    "bottom": "112px",
                    "right": "117px",
                },
            ),
            
            style={
                "position": "relative",
                "width": "100%",
                "height": "100vh",
                "max_width": "1280px",
                "margin": "0 auto",
            },
        ),
        width="100%",
    )


def detail_view() -> rx.Component:
    """
    詳細画面
    Figma準拠: フルスクリーンカード、右下に展開ボタン
    """
    # アイコンボタンスタイル
    icon_style = {
        "font_family": "'Roboto', sans-serif",
        "font_weight": "600",
        "font_size": "48px",
        "color": "#000000",
        "cursor": "pointer",
        "background": "transparent",
        "border": "none",
        "padding": "0",
        "line_height": "1",
        "_hover": {
            "opacity": "0.7",
        },
    }
    
    return rx.box(
        # 全体コンテナ
        rx.box(
            # 左上: 閉じるボタン
            rx.button(
                "×",
                on_click=GachaState.go_to_result,
                style={
                    **icon_style,
                    "position": "absolute",
                    "top": "44px",
                    "left": "40px",
                    "z_index": "10",
                },
            ),
            
            # 中央: 詳細カード（展開ボタン内包）
            detail_card(),
            
            style={
                "position": "relative",
                "width": "100%",
                "min_height": "100vh",
                "display": "flex",
                "flex_direction": "column",
                "align_items": "center",
                "padding": "44px 20px",
            },
        ),
        width="100%",
        style={
            "overflow_y": "auto",
        },
    )


def index() -> rx.Component:
    """
    メインページ
    
    view_modeに応じて画面を切り替え
    """
    return rx.box(
        rx.cond(
            GachaState.view_mode == "gacha",
            gacha_view(),
            rx.cond(
                GachaState.view_mode == "result",
                result_view(),
                detail_view(),
            ),
        ),
        style={
            "min_height": "100vh",
            "background_color": "#FFFFFF",
            "font_family": "'Zen Kaku Gothic New', sans-serif",
        },
    )
