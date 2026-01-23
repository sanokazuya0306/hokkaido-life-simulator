"""
詳細カードコンポーネント

Figmaデザイン準拠 (MacBook Air - 3):
- カード: 1040x720, 角丸48px, 背景#D9D9D9
- ストーリーテキスト: Zen Old Mincho, 24px, lineHeight 2em
- ランク表示: 360x128, グラデーション背景
"""

import reflex as rx
from ..state import GachaState


def life_story_text() -> rx.Component:
    """
    人生ストーリーテキスト
    
    Figma: Zen Old Mincho, 24px, lineHeight 2em, color #323232
    """
    return rx.text(
        GachaState.selected_life_story,
        style={
            "font_family": "'Zen Old Mincho', serif",
            "font_weight": "700",
            "font_size": "24px",
            "line_height": "2em",
            "color": "#323232",
            "text_align": "center",
            "white_space": "pre-wrap",
            "max_width": "720px",
        },
    )


def rank_display_dynamic() -> rx.Component:
    """
    人生ランク表示（動的）
    
    Figma: 360x128, 角丸8px, グラデーション背景
    """
    # 共通スタイル
    container_style = {
        "width": "360px",
        "height": "128px",
        "border_radius": "8px",
        "display": "flex",
        "align_items": "center",
        "justify_content": "center",
        "gap": "20px",
    }
    
    label_style = {
        "font_family": "'Zen Old Mincho', serif",
        "font_weight": "700",
        "font_size": "36px",
    }
    
    rank_style = {
        "font_family": "'Roboto', sans-serif",
        "font_weight": "600",
        "font_size": "64px",
    }
    
    return rx.cond(
        GachaState.selected_life_rank == "SS",
        rx.box(
            rx.text("人生ランク", style={**label_style, "color": "#D8D8D8"}),
            rx.text("SS", style={**rank_style, "color": "#D8D8D8"}),
            style={
                **container_style,
                "background": "linear-gradient(135deg, #080808 0%, #6E6E6E 100%)",
            },
        ),
        rx.cond(
            GachaState.selected_life_rank == "S",
            rx.box(
                rx.text("人生ランク", style={**label_style, "color": "#000", "text_shadow": "0 0 2px #FFF"}),
                rx.text("S", style={**rank_style, "color": "#000", "text_shadow": "0 0 2px #FFF"}),
                style={
                    **container_style,
                    "background": "linear-gradient(135deg, #292929 0%, #8F8F8F 100%)",
                },
            ),
            rx.box(
                rx.text("人生ランク", style={**label_style, "color": "#000", "text_shadow": "0 0 2px #FFF"}),
                rx.text(GachaState.selected_life_rank, style={**rank_style, "color": "#000", "text_shadow": "0 0 2px #FFF"}),
                style={
                    **container_style,
                    "background": "#C0C0C0",
                },
            ),
        ),
    )


def parent_rank_display_dynamic() -> rx.Component:
    """
    親ガチャランク表示（動的）
    
    Figma: Zen Old Mincho 24px + Roboto 40px
    """
    return rx.hstack(
        rx.text(
            "親ガチャランク",
            style={
                "font_family": "'Zen Old Mincho', serif",
                "font_weight": "700",
                "font_size": "24px",
                "color": "#323232",
            },
        ),
        rx.text(
            GachaState.selected_parent_rank,
            style={
                "font_family": "'Roboto', sans-serif",
                "font_weight": "600",
                "font_size": "40px",
                "color": "#000000",
            },
        ),
        spacing="4",
        align="center",
        justify="center",
    )


def detail_item(label: str, value) -> rx.Component:
    """詳細項目（ラベル: 値）"""
    return rx.hstack(
        rx.text(label, style={"font_weight": "600", "min_width": "80px", "color": "#323232", "font_size": "14px"}),
        rx.text(value, style={"color": "#666", "font_size": "14px"}),
        justify="between",
        width="100%",
    )


def score_breakdown_section() -> rx.Component:
    """
    スコア内訳セクション（展開時に表示）
    """
    section_title_style = {
        "font_family": "'Zen Kaku Gothic New', sans-serif",
        "font_weight": "700",
        "font_size": "16px",
        "color": "#323232",
        "margin_bottom": "12px",
        "margin_top": "16px",
    }
    
    card_style = {
        "padding": "16px",
        "background": "rgba(255,255,255,0.5)",
        "border_radius": "8px",
        "width": "100%",
        "max_width": "720px",
    }
    
    score_card_style = {
        "padding": "16px",
        "background": "rgba(255,255,255,0.5)",
        "border_radius": "8px",
        "width": "100%",
        "max_width": "720px",
    }
    
    return rx.box(
        rx.vstack(
            rx.divider(style={"margin": "24px 0", "border_color": "rgba(0,0,0,0.2)"}),
            
            # 総合スコア表示
            rx.hstack(
                rx.text(
                    GachaState.total_score,
                    style={"font_size": "24px", "font_weight": "700"},
                ),
                rx.text(
                    "点",
                    style={"font_size": "24px", "font_weight": "700"},
                ),
                rx.text(
                    "「",
                    style={"font_size": "16px", "color": "#666"},
                ),
                rx.text(
                    GachaState.rank_label,
                    style={"font_size": "16px", "color": "#666"},
                ),
                rx.text(
                    "」",
                    style={"font_size": "16px", "color": "#666"},
                ),
                spacing="1",
                align="center",
                justify="center",
                style={"margin_bottom": "16px"},
            ),
            
            # === 詳細データ ===
            rx.text("📋 詳細データ", style=section_title_style),
            
            rx.hstack(
                # 出生情報
                rx.vstack(
                    rx.text("👶 出生情報", style={"font_weight": "700", "font_size": "14px", "margin_bottom": "8px"}),
                    detail_item("性別", GachaState.detail_gender),
                    detail_item("出生地", GachaState.detail_birth_city),
                    detail_item("世帯年収", GachaState.detail_household_income),
                    detail_item("父学歴", GachaState.detail_father_education_display),
                    detail_item("母学歴", GachaState.detail_mother_education_display),
                    spacing="1",
                    style=card_style,
                ),
                
                # 学歴・偏差値
                rx.vstack(
                    rx.text("📚 学歴・偏差値", style={"font_weight": "700", "font_size": "14px", "margin_bottom": "8px"}),
                    # 個人偏差値（初期）
                    rx.cond(
                        GachaState.detail_deviation_value > 0,
                        rx.hstack(
                            rx.text("個人偏差値", style={"font_weight": "600", "min_width": "80px", "color": "#323232", "font_size": "14px"}),
                            rx.text(
                                GachaState.detail_deviation_value.to(str),
                                style={"color": "#666", "font_size": "14px"}
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.box(),
                    ),
                    # 高校（偏差値付き）
                    rx.cond(
                        GachaState.detail_high_school,
                        rx.cond(
                            GachaState.detail_high_school_deviation > 0,
                            rx.hstack(
                                rx.text("高校", style={"font_weight": "600", "min_width": "80px", "color": "#323232", "font_size": "14px"}),
                                rx.text(
                                    rx.cond(
                                        GachaState.detail_high_school_name != "",
                                        GachaState.detail_high_school_name + " (偏差値" + GachaState.detail_high_school_deviation.to(str) + ")",
                                        "進学"
                                    ),
                                    style={"color": "#666", "font_size": "14px"}
                                ),
                                justify="between",
                                width="100%",
                            ),
                            detail_item("高校", GachaState.detail_high_school_name),
                        ),
                        detail_item("高校", "進学せず"),
                    ),
                    # 卒業時偏差値（高校進学者のみ）
                    rx.cond(
                        GachaState.detail_high_school,
                        rx.cond(
                            GachaState.detail_graduation_deviation > 0,
                            rx.hstack(
                                rx.text("卒業時偏差値", style={"font_weight": "600", "min_width": "80px", "color": "#323232", "font_size": "14px"}),
                                rx.hstack(
                                    rx.text(
                                        GachaState.detail_graduation_deviation.to(str),
                                        style={"color": "#666", "font_size": "14px"}
                                    ),
                                    rx.cond(
                                        GachaState.detail_deviation_growth != "",
                                        rx.text(
                                            " (" + GachaState.detail_deviation_growth + ")",
                                            style={"color": "#888", "font_size": "12px"}
                                        ),
                                        rx.box(),
                                    ),
                                    spacing="0",
                                ),
                                justify="between",
                                width="100%",
                            ),
                            rx.box(),
                        ),
                        rx.box(),
                    ),
                    # 大学
                    rx.cond(
                        GachaState.detail_university,
                        rx.fragment(
                            detail_item("大学", GachaState.detail_university_name),
                            detail_item("ランク", GachaState.detail_university_rank),
                        ),
                        detail_item("大学", "進学せず"),
                    ),
                    spacing="1",
                    style=card_style,
                ),
                
                # キャリア
                rx.vstack(
                    rx.text("💼 キャリア", style={"font_weight": "700", "font_size": "14px", "margin_bottom": "8px"}),
                    detail_item("企業規模", GachaState.detail_company_size),
                    detail_item("雇用形態", GachaState.detail_employment_type),
                    rx.hstack(
                        rx.text("転職回数", style={"font_weight": "600", "min_width": "80px", "color": "#323232", "font_size": "14px"}),
                        rx.text(GachaState.detail_job_changes, style={"color": "#666", "font_size": "14px"}),
                        rx.text("回", style={"color": "#666", "font_size": "14px"}),
                        justify="between",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("死亡年齢", style={"font_weight": "600", "min_width": "80px", "color": "#323232", "font_size": "14px"}),
                        rx.text(GachaState.detail_death_age, style={"color": "#666", "font_size": "14px"}),
                        rx.text("歳", style={"color": "#666", "font_size": "14px"}),
                        justify="between",
                        width="100%",
                    ),
                    detail_item("死因", GachaState.detail_death_cause),
                    spacing="1",
                    style=card_style,
                ),
                
                spacing="4",
                align="start",
                justify="center",
                wrap="wrap",
                style={"max_width": "720px"},
            ),
            
            # === 人生スコア内訳 ===
            rx.text("📈 人生スコア内訳", style=section_title_style),
            
            rx.hstack(
                rx.text("人生:", style={"font_weight": "600", "color": "#000000"}),
                rx.text(GachaState.total_score, style={"font_weight": "700", "color": "#000000"}),
                rx.text("点", style={"font_weight": "700", "color": "#000000"}),
                rx.text("「", style={"color": "#666"}),
                rx.text(GachaState.rank_label, style={"color": "#666"}),
                rx.text("」", style={"color": "#666"}),
                spacing="1",
                align="center",
                style={"margin_bottom": "12px"},
            ),
            
            rx.hstack(
                # 寿命スコア（40%）
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("寿命 (40%)", style={"font_weight": "700", "color": "#323232"}),
                            rx.hstack(
                                rx.text(GachaState.lifespan_score, style={"font_weight": "600"}),
                                rx.text("点", style={"font_weight": "600"}),
                                spacing="0",
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.text("→ ", style={"font_size": "14px", "color": "#666"}),
                            rx.text(GachaState.lifespan_value, style={"font_size": "14px", "color": "#666"}),
                            spacing="0",
                        ),
                        rx.hstack(
                            rx.text("計算: 寿命スコア", style={"font_size": "12px", "color": "#999"}),
                            rx.text(GachaState.lifespan_score, style={"font_size": "12px", "color": "#999"}),
                            rx.text("点 × 40% = ", style={"font_size": "12px", "color": "#999"}),
                            rx.text(
                                rx.cond(
                                    GachaState.lifespan_score != 0.0,
                                    (GachaState.lifespan_score * 0.4).to(str),
                                    "0.0"
                                ),
                                style={"font_size": "12px", "color": "#999"},
                            ),
                            rx.text("点", style={"font_size": "12px", "color": "#999"}),
                            spacing="0",
                            style={"margin_top": "4px"},
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    style=score_card_style,
                ),
                # 生涯年収スコア（35%）
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("生涯年収 (35%)", style={"font_weight": "700", "color": "#323232"}),
                            rx.hstack(
                                rx.text(GachaState.income_score, style={"font_weight": "600"}),
                                rx.text("点", style={"font_weight": "600"}),
                                spacing="0",
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.text("→ ", style={"font_size": "14px", "color": "#666"}),
                            rx.text(GachaState.income_value, style={"font_size": "14px", "color": "#666"}),
                            spacing="0",
                        ),
                        rx.hstack(
                            rx.text("計算: 生涯年収スコア", style={"font_size": "12px", "color": "#999"}),
                            rx.text(GachaState.income_score, style={"font_size": "12px", "color": "#999"}),
                            rx.text("点 × 35% = ", style={"font_size": "12px", "color": "#999"}),
                            rx.text(
                                rx.cond(
                                    GachaState.income_score != 0.0,
                                    (GachaState.income_score * 0.35).to(str),
                                    "0.0"
                                ),
                                style={"font_size": "12px", "color": "#999"},
                            ),
                            rx.text("点", style={"font_size": "12px", "color": "#999"}),
                            spacing="0",
                            style={"margin_top": "4px"},
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    style=score_card_style,
                ),
                # 学歴スコア（25%）
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("学歴 (25%)", style={"font_weight": "700", "color": "#323232"}),
                            rx.hstack(
                                rx.text(GachaState.edu_score, style={"font_weight": "600"}),
                                rx.text("点", style={"font_weight": "600"}),
                                spacing="0",
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.text("→ ", style={"font_size": "14px", "color": "#666"}),
                            rx.text(GachaState.edu_value, style={"font_size": "14px", "color": "#666"}),
                            spacing="0",
                        ),
                        rx.hstack(
                            rx.text("計算: 学歴スコア", style={"font_size": "12px", "color": "#999"}),
                            rx.text(GachaState.edu_score, style={"font_size": "12px", "color": "#999"}),
                            rx.text("点 × 25% = ", style={"font_size": "12px", "color": "#999"}),
                            rx.text(
                                rx.cond(
                                    GachaState.edu_score != 0.0,
                                    (GachaState.edu_score * 0.25).to(str),
                                    "0.0"
                                ),
                                style={"font_size": "12px", "color": "#999"},
                            ),
                            rx.text("点", style={"font_size": "12px", "color": "#999"}),
                            spacing="0",
                            style={"margin_top": "4px"},
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    style=score_card_style,
                ),
                spacing="4",
                align="start",
                justify="center",
                wrap="wrap",
                style={"max_width": "720px"},
            ),
            
            # === 親ガチャスコア内訳 ===
            rx.text("📈 親ガチャスコア内訳", style=section_title_style),
            
            rx.hstack(
                rx.text("親ガチャ:", style={"font_weight": "600", "color": "#000000"}),
                rx.text(GachaState.parent_total_score, style={"font_weight": "700", "color": "#000000"}),
                rx.text("点", style={"font_weight": "700", "color": "#000000"}),
                rx.text("「", style={"color": "#666"}),
                rx.text(GachaState.parent_rank_label, style={"color": "#666"}),
                rx.text("」", style={"color": "#666"}),
                spacing="1",
                align="center",
                style={"margin_bottom": "12px"},
            ),
            
            rx.hstack(
                # 世帯年収（35%）
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("世帯年収 (35%)", style={"font_weight": "700", "color": "#323232"}),
                            rx.hstack(
                                rx.text(GachaState.parent_income_score, style={"font_weight": "600"}),
                                rx.text("点", style={"font_weight": "600"}),
                                spacing="0",
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.text("→ ", style={"font_size": "14px", "color": "#666"}),
                            rx.text(GachaState.parent_income_value, style={"font_size": "14px", "color": "#666"}),
                            spacing="0",
                        ),
                        rx.hstack(
                            rx.text("計算: 世帯年収スコア", style={"font_size": "12px", "color": "#999"}),
                            rx.text(GachaState.parent_income_score, style={"font_size": "12px", "color": "#999"}),
                            rx.text("点 × 35% = ", style={"font_size": "12px", "color": "#999"}),
                            rx.text(
                                rx.cond(
                                    GachaState.parent_income_score != 0.0,
                                    (GachaState.parent_income_score * 0.35).to(str),
                                    "0.0"
                                ),
                                style={"font_size": "12px", "color": "#999"},
                            ),
                            rx.text("点", style={"font_size": "12px", "color": "#999"}),
                            spacing="0",
                            style={"margin_top": "4px"},
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    style=score_card_style,
                ),
                # 出生地（35%）
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("出生地 (35%)", style={"font_weight": "700", "color": "#323232"}),
                            rx.hstack(
                                rx.text(GachaState.parent_birthplace_score, style={"font_weight": "600"}),
                                rx.text("点", style={"font_weight": "600"}),
                                spacing="0",
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.text("→ ", style={"font_size": "14px", "color": "#666"}),
                            rx.text(GachaState.parent_birthplace_value, style={"font_size": "14px", "color": "#666"}),
                            spacing="0",
                        ),
                        rx.hstack(
                            rx.text("計算: 出生地スコア", style={"font_size": "12px", "color": "#999"}),
                            rx.text(GachaState.parent_birthplace_score, style={"font_size": "12px", "color": "#999"}),
                            rx.text("点 × 35% = ", style={"font_size": "12px", "color": "#999"}),
                            rx.text(
                                rx.cond(
                                    GachaState.parent_birthplace_score != 0.0,
                                    (GachaState.parent_birthplace_score * 0.35).to(str),
                                    "0.0"
                                ),
                                style={"font_size": "12px", "color": "#999"},
                            ),
                            rx.text("点", style={"font_size": "12px", "color": "#999"}),
                            spacing="0",
                            style={"margin_top": "4px"},
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    style=score_card_style,
                ),
                # 親の学歴（30%）
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.text("親の学歴 (30%)", style={"font_weight": "700", "color": "#323232"}),
                            rx.hstack(
                                rx.text(GachaState.parent_edu_score, style={"font_weight": "600"}),
                                rx.text("点", style={"font_weight": "600"}),
                                spacing="0",
                            ),
                            justify="between",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.text("→ ", style={"font_size": "14px", "color": "#666"}),
                            rx.text(GachaState.parent_edu_value, style={"font_size": "14px", "color": "#666"}),
                            spacing="0",
                        ),
                        rx.hstack(
                            rx.text("計算: 親の学歴スコア", style={"font_size": "12px", "color": "#999"}),
                            rx.text(GachaState.parent_edu_score, style={"font_size": "12px", "color": "#999"}),
                            rx.text("点 × 30% = ", style={"font_size": "12px", "color": "#999"}),
                            rx.text(
                                rx.cond(
                                    GachaState.parent_edu_score != 0.0,
                                    (GachaState.parent_edu_score * 0.3).to(str),
                                    "0.0"
                                ),
                                style={"font_size": "12px", "color": "#999"},
                            ),
                            rx.text("点", style={"font_size": "12px", "color": "#999"}),
                            spacing="0",
                            style={"margin_top": "4px"},
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    style=score_card_style,
                ),
                spacing="4",
                align="start",
                justify="center",
                wrap="wrap",
                style={"max_width": "720px"},
            ),
            
            rx.box(height="40px"),
            
            spacing="2",
            align="center",
            width="100%",
        ),
        style={
            "width": "100%",
            "padding_top": "20px",
        },
    )


def detail_card() -> rx.Component:
    """
    詳細カード（人生ストーリー + ランク表示）
    
    Figma準拠:
    - 背景: #D9D9D9
    - 角丸: 48px
    - サイズ: 最大1040px
    """
    return rx.el.div(
        rx.el.div(
            # 人生ストーリー
            life_story_text(),
            
            rx.box(height="40px"),
            
            # 人生ランク表示
            rank_display_dynamic(),
            
            rx.box(height="30px"),
            
            # 親ガチャランク表示
            parent_rank_display_dynamic(),
            
            # 展開可能なスコア内訳
            rx.cond(
                GachaState.show_detail_breakdown,
                score_breakdown_section(),
                rx.box(),
            ),
            
            style={
                "display": "flex",
                "flex_direction": "column",
                "align_items": "center",
                "width": "100%",
                "padding_bottom": "60px",  # 展開ボタン用のスペース
            },
        ),
        # 右下: 展開ボタン（カード内に配置）
        rx.button(
            rx.cond(
                GachaState.show_detail_breakdown,
                "↑",
                "↓",
            ),
            on_click=GachaState.toggle_detail_breakdown,
            style={
                "position": "absolute",
                "bottom": "24px",
                "right": "40px",
                "background": "transparent",
                "border": "none",
                "font_size": "32px",
                "cursor": "pointer",
                "color": "#323232",
                "padding": "8px",
                "_hover": {
                    "opacity": "0.7",
                },
            },
        ),
        style={
            "background": "#D9D9D9",
            "border_radius": "48px",
            "padding": "68px 50px 40px 50px",
            "width": "100%",
            "max_width": "1040px",
            "min_height": "720px",
            "position": "relative",
        },
    )


def expand_button() -> rx.Component:
    """
    展開ボタン（↓矢印）
    右下に配置
    """
    return rx.button(
        rx.cond(
            GachaState.show_detail_breakdown,
            "↑",
            "↓",
        ),
        on_click=GachaState.toggle_detail_breakdown,
        style={
            "position": "absolute",
            "bottom": "20px",
            "right": "40px",
            "background": "transparent",
            "border": "none",
            "font_size": "32px",
            "cursor": "pointer",
            "color": "#323232",
            "padding": "8px",
            "_hover": {
                "opacity": "0.7",
            },
        },
    )


def counter_display() -> rx.Component:
    """累計カウンター表示"""
    return rx.text(
        rx.text.span("累計: "),
        rx.text.span(GachaState.total_generated),
        rx.text.span("人"),
        style={
            "font_family": "'Roboto', sans-serif",
            "font_weight": "600",
            "font_size": "18px",
            "color": "#000000",
            "text_align": "right",
            "padding": "10px 20px",
        },
    )
