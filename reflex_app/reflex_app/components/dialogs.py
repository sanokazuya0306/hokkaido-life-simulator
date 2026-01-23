"""
ダイアログコンポーネント

確率、データセット、相関図の情報表示用
"""

import reflex as rx
from ..state import GachaState
import sys
from pathlib import Path

# 親ディレクトリのsrcモジュールを参照
_parent_dir = Path(__file__).parent.parent.parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

from src.correlation_visualizer import create_correlation_sankey, get_correlation_summary


# ランク情報（モノトーンカラー）
RANK_INFO = {
    "SS": {"color": "#1a1a1a", "bg": "rgba(26, 26, 26, 0.08)", "label": "超大当たり", "desc": "上位2-5%、高学歴・高収入・長寿"},
    "S": {"color": "#333333", "bg": "rgba(51, 51, 51, 0.08)", "label": "大当たり", "desc": "上位10-20%、好条件の人生"},
    "A": {"color": "#4d4d4d", "bg": "rgba(77, 77, 77, 0.08)", "label": "当たり", "desc": "平均以上の人生"},
    "B": {"color": "#666666", "bg": "rgba(102, 102, 102, 0.08)", "label": "普通", "desc": "一般的な人生"},
    "C": {"color": "#808080", "bg": "rgba(128, 128, 128, 0.08)", "label": "ハズレ", "desc": "平均以下の人生"},
    "D": {"color": "#999999", "bg": "rgba(153, 153, 153, 0.08)", "label": "大ハズレ", "desc": "早逝など不運な人生"},
}

# 地域ごとのガチャ確率（10,000サンプル実測値、新配分: 寿命40%、生涯年収35%、学歴25%）
# しきい値: SS≧85, S≧75, A≧62, B≧42, C≧35, D<35
GACHA_RATES = {
    "hokkaido": {"SS": "1.43%", "S": "6.01%", "A": "18.26%", "B": "46.00%", "C": "14.88%", "D": "13.42%"},
    "tokyo": {"SS": "4.33%", "S": "12.62%", "A": "25.42%", "B": "39.46%", "C": "9.31%", "D": "8.86%"},
}


def rate_item(rank: str, rate: str) -> rx.Component:
    """確率表示アイテム"""
    info = RANK_INFO.get(rank, {"color": "#666", "bg": "#f8f9fa", "label": "", "desc": ""})
    
    return rx.box(
        rx.hstack(
            # ランク表示
            rx.box(
                rx.text(
                    rank,
                    style={
                        "font_size": "1.8rem",
                        "font_weight": "700",
                        "color": info["color"],
                    },
                ),
                style={
                    "width": "60px",
                    "height": "60px",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "background": info["bg"],
                    "border_radius": "8px",
                    "border": f"2px solid {info['color']}",
                },
            ),
            # ラベルと説明
            rx.vstack(
                rx.text(
                    info["label"],
                    style={
                        "font_weight": "600",
                        "color": "#2c3e50",
                        "font_size": "1rem",
                    },
                ),
                rx.text(
                    info["desc"],
                    style={
                        "font_size": "0.85rem",
                        "color": "#666",
                    },
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            # 確率
            rx.text(
                rate,
                style={
                    "font_size": "1.5rem",
                    "font_weight": "700",
                    "color": info["color"],
                    "font_variant_numeric": "tabular-nums",
                },
            ),
            spacing="4",
            align="center",
            width="100%",
        ),
        style={
            "padding": "0.75rem 1rem",
            "margin": "0.5rem 0",
            "background": "#ffffff",
            "border": "1px solid #e0e0e0",
            "border_radius": "8px",
            "border_left": f"4px solid {info['color']}",
            "box_shadow": "0 1px 3px rgba(0, 0, 0, 0.05)",
            "transition": "all 0.2s ease",
            "_hover": {
                "box_shadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
                "transform": "translateX(2px)",
            },
        },
    )


def rates_content_hokkaido() -> rx.Component:
    """北海道の確率表示"""
    rates = GACHA_RATES["hokkaido"]
    return rx.vstack(
        *[rate_item(rank, rate) for rank, rate in rates.items()],
        spacing="1",
        width="100%",
    )


def rates_content_tokyo() -> rx.Component:
    """東京の確率表示"""
    rates = GACHA_RATES["tokyo"]
    return rx.vstack(
        *[rate_item(rank, rate) for rank, rate in rates.items()],
        spacing="1",
        width="100%",
    )


def rates_dialog() -> rx.Component:
    """確率ダイアログ (Figma: 100x28px)"""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "確率",
                style={
                    "width": "100px",
                    "height": "28px",
                    "background": "#D9D9D9",
                    "border": "none",
                    "border_radius": "0",
                    "padding": "0",
                    "font_family": "'Zen Kaku Gothic New', sans-serif",
                    "font_size": "12px",
                    "font_weight": "400",
                    "color": "#000000",
                    "cursor": "pointer",
                    "_hover": {"background": "#CCCCCC"},
                },
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("🎲 ガチャ確率"),
            rx.dialog.description(
                rx.vstack(
                    # 地域表示カード
                    rx.box(
                        rx.hstack(
                            rx.text(
                                rx.text.span(GachaState.region_name),
                                rx.text.span("のガチャ確率"),
                                style={"font_size": "1.1rem", "font_weight": "600"},
                            ),
                            rx.spacer(),
                            rx.text(
                                "10,000回シミュレーション",
                                style={"font_size": "0.8rem", "color": "#666"},
                            ),
                            width="100%",
                            align="center",
                        ),
                        style={
                            "padding": "0.75rem 1rem",
                            "background": "#f8f9fa",
                            "border_radius": "8px",
                            "border": "1px solid #e0e0e0",
                            "margin_bottom": "1rem",
                        },
                    ),
                    # 地域に応じた確率表示
                    rx.cond(
                        GachaState.is_hokkaido,
                        rates_content_hokkaido(),
                        rates_content_tokyo(),
                    ),
                    # 注釈
                    rx.box(
                        rx.text(
                            "確率は実際のシミュレーション結果（2026年1月計算、新配分: 寿命40%・生涯年収35%・学歴25%）に基づいています。",
                            style={"font_size": "0.85rem", "color": "#666"},
                        ),
                        style={
                            "margin_top": "1rem",
                            "padding": "0.75rem 1rem",
                            "background": "#f8f9fa",
                            "border_radius": "8px",
                            "border_left": "3px solid #666",
                        },
                    ),
                    spacing="2",
                    width="100%",
                ),
            ),
            rx.dialog.close(
                rx.button(
                    "閉じる",
                    style={
                        "margin_top": "1rem",
                        "background": "#D9D9D9",
                        "border": "none",
                        "border_radius": "4px",
                        "padding": "8px 24px",
                        "cursor": "pointer",
                        "_hover": {"background": "#CCCCCC"},
                    },
                ),
            ),
            style={
                "max_width": "600px",
                "max_height": "85vh",
                "overflow_y": "auto",
            },
        ),
    )


# データセット情報（詳細な原典名とリンク付き）
DATASET_INFO = [
    {
        "name": "市区町村別出生数",
        "official_name": "人口動態調査 出生数，市区町村別",
        "source": "厚生労働省",
        "year": "2024年",
        "icon": "📍",
        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00450011&tstat=000001028897",
        "note": "小規模自治体は人口比で按分した推計値を使用",
    },
    {
        "name": "世帯年収分布",
        "official_name": "住宅・土地統計調査 世帯の年間収入階級別",
        "source": "総務省統計局",
        "year": "2023年",
        "icon": "💰",
        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200522&tstat=000001127155",
    },
    {
        "name": "高校・大学進学率",
        "official_name": "学校基本調査 都道府県別進学率（令和6年度確定値）",
        "source": "文部科学省",
        "year": "2024年度",
        "icon": "🎓",
        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00400001&tstat=000001011528",
        "note": "市区町村別は都市規模に応じた推計値を使用",
    },
    {
        "name": "大学進学先都道府県",
        "official_name": "学校基本調査 出身高校の所在地県別入学者数（令和6年度確定値）",
        "source": "文部科学省 / 旺文社教育情報センター",
        "year": "2024年度",
        "icon": "🏫",
        "url": "https://eic.obunsha.co.jp/file/educational_info/202501/02.pdf",
        "note": "東京都: 地元進学率68.8%、北海道: 地元進学率65.3%（実データに基づく）",
    },
    {
        "name": "最終学歴分布",
        "official_name": "国勢調査 在学か否かの別・最終卒業学校の種類別人口",
        "source": "総務省統計局",
        "year": "2020年",
        "icon": "📊",
        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200521&tstat=000001136464",
    },
    {
        "name": "産業別就業者数",
        "official_name": "労働力調査 産業，従業上の地位別就業者数（令和6年平均）",
        "source": "総務省統計局",
        "year": "2024年",
        "icon": "🏭",
        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200531&tstat=000000110001",
    },
    {
        "name": "年齢別死亡率",
        "official_name": "令和5年簡易生命表 死亡率",
        "source": "厚生労働省",
        "year": "2023年",
        "icon": "📈",
        "url": "https://www.mhlw.go.jp/toukei/saikin/hw/life/life23/index.html",
    },
    {
        "name": "死因統計",
        "official_name": "人口動態統計 死因簡単分類別にみた性別死亡数・死亡率",
        "source": "厚生労働省",
        "year": "2022年",
        "icon": "🏥",
        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00450011&tstat=000001028897",
    },
    {
        "name": "親学歴と子の進学率",
        "official_name": "OECD Education at a Glance 2025 / 21世紀出生児縦断調査",
        "source": "OECD / 文部科学省 / 厚生労働省",
        "year": "2024-2025年",
        "icon": "👪",
        "url": "https://www.oecd.org/education/education-at-a-glance/",
        "note": "親学歴による補正係数: 中卒-5, 高卒0, 大卒+5, 院卒+8",
    },
    {
        "name": "世帯年収と子の進学率",
        "official_name": "21世紀出生児縦断調査 / 東京大学学生生活実態調査",
        "source": "文部科学省 / 東京大学 / 厚生労働省",
        "year": "2023-2024年",
        "icon": "💵",
        "url": "https://www.mext.go.jp/b_menu/toukei/chousa08/21seiki/mext_02723.html",
        "note": "貧困持続群35.4% vs 非貧困持続群63.4%の進学率差に基づく",
    },
    {
        "name": "学歴別産業分布（大卒）",
        "official_name": "雇用動向調査 産業別入職者・離職者状況",
        "source": "厚生労働省",
        "year": "2024年",
        "icon": "🎓",
        "url": "https://www.mhlw.go.jp/toukei/itiran/roudou/koyou/doukou/25-2/index.html",
        "note": "大卒: 情報通信12%, 製造13%, 卸売小売12%, 学術研究10%, 医療福祉9%",
    },
    {
        "name": "学歴別産業分布（高卒）",
        "official_name": "高卒採用の市場データ / 学校基本調査",
        "source": "株式会社ジンジブ / 文部科学省",
        "year": "2024年",
        "icon": "🏭",
        "url": "https://jinjib.co.jp/business/market",
        "note": "高卒: 製造業39.9%, 卸売小売10.6%, 建設8.6%, 公務7.3%, 運輸6.1%",
    },
    {
        "name": "学歴別雇用形態（正社員率）",
        "official_name": "労働力調査（詳細集計）雇用形態別雇用者数",
        "source": "総務省統計局",
        "year": "2024年",
        "icon": "💼",
        "url": "https://www.stat.go.jp/data/roudou/sokuhou/nen/dt/index.html",
        "note": "大卒男90%・女75%, 高卒男75%・女55%, 中卒男55%・女35%",
    },
    {
        "name": "転職・離職率（年齢別）",
        "official_name": "雇用動向調査 年齢階級別転職入職率・離職率",
        "source": "厚生労働省",
        "year": "2024年",
        "icon": "🔄",
        "url": "https://www.mhlw.go.jp/toukei/itiran/roudou/koyou/doukou/25-2/dl/kekka_gaiyo-03.pdf",
        "note": "20-24歳: 転職14.6%(男), 25-29歳: 13.4%, 年齢とともに低下",
    },
    {
        "name": "新卒3年以内離職率",
        "official_name": "新規学卒就職者の離職状況",
        "source": "厚生労働省",
        "year": "2024年（令和4年3月卒業者）",
        "icon": "📉",
        "url": "https://www.mhlw.go.jp/stf/houdou/0000177553_00010.html",
        "note": "大卒33.8%, 高卒37.9%, 中卒約55%（七五三現象）",
    },
]


def dataset_item(data: dict) -> rx.Component:
    """データセット表示アイテム"""
    # noteがある場合の表示コンポーネント
    note_component = rx.cond(
        data.get("note", "") != "",
        rx.text(
            f"※ {data.get('note', '')}",
            style={"font_size": "0.75rem", "color": "#d35400", "font_style": "italic", "margin_top": "4px"},
        ),
        rx.box(),
    ) if data.get("note") else rx.box()
    
    return rx.box(
        rx.vstack(
            # ヘッダー（名前とアイコン）
            rx.hstack(
                rx.box(
                    rx.text(data["icon"], style={"font_size": "1.2rem"}),
                    style={
                        "width": "36px",
                        "height": "36px",
                        "display": "flex",
                        "align_items": "center",
                        "justify_content": "center",
                        "background": "#f8f9fa",
                        "border_radius": "6px",
                        "border": "1px solid #e0e0e0",
                    },
                ),
                rx.text(
                    data["name"],
                    style={"font_weight": "600", "color": "#2c3e50", "font_size": "0.95rem"},
                ),
                rx.spacer(),
                rx.text(
                    data["year"],
                    style={"font_size": "0.75rem", "color": "#888", "background": "#f0f0f0", "padding": "2px 8px", "border_radius": "4px"},
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            # 正式名称
            rx.text(
                data["official_name"],
                style={"font_size": "0.85rem", "color": "#666", "line_height": "1.4"},
            ),
            # 出典とリンク
            rx.hstack(
                rx.text(
                    f"出典: {data['source']}",
                    style={"font_size": "0.8rem", "color": "#888"},
                ),
                rx.spacer(),
                rx.link(
                    rx.hstack(
                        rx.text("🔗", style={"font_size": "0.75rem"}),
                        rx.text("原典を見る", style={"font_size": "0.75rem"}),
                        spacing="1",
                        align="center",
                    ),
                    href=data["url"],
                    is_external=True,
                    style={
                        "color": "#1976d2",
                        "text_decoration": "none",
                        "_hover": {"text_decoration": "underline"},
                    },
                ),
                width="100%",
                align="center",
            ),
            # 注釈（noteがある場合のみ表示）
            note_component,
            spacing="2",
            align="start",
            width="100%",
        ),
        style={
            "padding": "0.75rem 1rem",
            "background": "#ffffff",
            "border": "1px solid #e0e0e0",
            "border_radius": "8px",
            "width": "100%",
            "transition": "all 0.2s ease",
            "_hover": {
                "box_shadow": "0 2px 8px rgba(0, 0, 0, 0.08)",
                "border_color": "#ccc",
            },
        },
    )


def source_item(source: dict) -> rx.Component:
    """データソースアイテム（リンク付き）"""
    return rx.hstack(
        rx.text("•", style={"font_size": "0.75rem", "color": "#333"}),
        rx.vstack(
            rx.hstack(
                rx.text(
                    f"{source['org']}「{source['name']}」{source['year']}",
                    style={"font_size": "0.75rem", "color": "#333"},
                ),
                rx.link(
                    rx.text("🔗", style={"font_size": "0.7rem"}),
                    href=source.get("url", "#"),
                    is_external=True,
                    style={"margin_left": "4px"},
                ) if source.get("url") else rx.fragment(),
                spacing="1",
                align="center",
            ),
            rx.text(
                source.get("note", ""),
                style={"font_size": "0.7rem", "color": "#555"},
            ) if source.get("note") else rx.fragment(),
            spacing="0",
            align="start",
        ),
        spacing="1",
        align="start",
        width="100%",
    )


def logic_section(title: str, formula: str, details: list, sources: list) -> rx.Component:
    """
    計算ロジックセクション
    
    sources: 辞書形式のリスト
        - org: 機関名（例: "厚生労働省"）
        - name: データセット名（例: "賃金構造基本統計調査"）
        - year: 年度（例: "2023年"）
        - url: リンクURL
        - note: 補足説明（オプション）
    """
    return rx.box(
        rx.vstack(
            # 計算式
            rx.box(
                rx.text(formula, style={"font_family": "monospace", "font_size": "0.85rem", "color": "#2c3e50"}),
                style={
                    "padding": "0.5rem 0.75rem",
                    "background": "#f0f0f0",
                    "border_radius": "4px",
                    "width": "100%",
                    "overflow_x": "auto",
                },
            ),
            # 詳細
            rx.vstack(
                *[rx.text(d, style={"font_size": "0.8rem", "color": "#666", "line_height": "1.5"}) for d in details],
                spacing="1",
                align="start",
                width="100%",
            ),
            # 出典（リンク付き）
            rx.box(
                rx.vstack(
                    rx.text("📚 根拠データ", style={"font_weight": "600", "font_size": "0.75rem", "color": "#333"}),
                    *[source_item(s) for s in sources],
                    spacing="1",
                    align="start",
                ),
                style={"margin_top": "0.5rem", "padding_top": "0.5rem", "border_top": "1px solid #e0e0e0", "width": "100%"},
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        style={"padding": "0.75rem", "width": "100%"},
    )


def dataset_dialog() -> rx.Component:
    """データセットダイアログ (Figma: 100x28px)"""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "データ",
                style={
                    "width": "100px",
                    "height": "28px",
                    "background": "#D9D9D9",
                    "border": "none",
                    "border_radius": "0",
                    "padding": "0",
                    "font_family": "'Zen Kaku Gothic New', sans-serif",
                    "font_size": "12px",
                    "font_weight": "400",
                    "color": "#000000",
                    "cursor": "pointer",
                    "_hover": {"background": "#CCCCCC"},
                },
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("📚 データセット・計算ロジック"),
            rx.dialog.description(
                rx.vstack(
                    # ヘッダー
                    rx.box(
                        rx.text(
                            "このシミュレーターで使用している公式統計データと計算ロジックの詳細です。",
                            style={"color": "#666", "font_size": "0.9rem"},
                        ),
                        style={
                            "padding": "0.75rem 1rem",
                            "background": "#f8f9fa",
                            "border_radius": "8px",
                            "border": "1px solid #e0e0e0",
                            "margin_bottom": "1rem",
                            "width": "100%",
                        },
                    ),
                    # データセット一覧
                    rx.text("📊 使用データセット", style={"font_weight": "700", "color": "#2c3e50", "font_size": "1rem", "margin_bottom": "0.5rem"}),
                    rx.vstack(
                        *[dataset_item(data) for data in DATASET_INFO],
                        spacing="2",
                        width="100%",
                    ),
                    # 計算ロジック（折りたたみ）
                    rx.text("🔧 計算ロジック詳細", style={"font_weight": "700", "color": "#2c3e50", "font_size": "1rem", "margin_top": "1.5rem", "margin_bottom": "0.5rem"}),
                    rx.accordion.root(
                        # 1. 偏差値の計算
                        rx.accordion.item(
                            header=rx.text("📐 個人偏差値の計算", style={"font_weight": "600", "color": "#2c3e50"}),
                            content=logic_section(
                                "偏差値",
                                "偏差値 = 50 + 親学歴補正 + 世帯年収補正 + 地域補正 + ランダム項",
                                [
                                    "【親学歴による補正】（両親の平均）",
                                    "　大学院卒: +8.0 / 大学卒: +5.0 / 短大専門: +1.0 / 高校卒: -2.0 / 中学卒: -5.0",
                                    "【世帯年収による補正】",
                                    "　1500万以上: +5.0 / 1000-1500万: +4.0 / 700-1000万: +2.5 / 500-700万: +1.0",
                                    "　400-500万: 0.0 / 300-400万: -1.0 / 200-300万: -2.0 / 100-200万: -3.0 / 100万未満: -4.0",
                                    "【地域による補正】東京: +2.0 / 北海道: -1.0",
                                    "【ランダム項】標準偏差8.0の正規分布（個人差）",
                                    "【範囲】30.0〜80.0にクリップ",
                                ],
                                [
                                    {
                                        "org": "文部科学省・国立教育政策研究所",
                                        "name": "全国学力・学習状況調査",
                                        "year": "2024年",
                                        "url": "https://www.nier.go.jp/24chousakekkahoukoku/index.html",
                                        "note": "家庭環境と学力の相関分析",
                                    },
                                    {
                                        "org": "OECD",
                                        "name": "Education at a Glance",
                                        "year": "2024年",
                                        "url": "https://www.oecd.org/education/education-at-a-glance/",
                                        "note": "国際的な教育格差データ",
                                    },
                                    {
                                        "org": "ベネッセ教育総合研究所",
                                        "name": "子どもの生活と学びに関する親子調査",
                                        "year": "2023年",
                                        "url": "https://berd.benesse.jp/shotouchutou/research/detail1.php?id=5781",
                                        "note": "親の所得・学歴と子どもの学力の関係",
                                    },
                                ],
                            ),
                            value="deviation",
                        ),
                        # 2. 進学率の計算
                        rx.accordion.item(
                            header=rx.text("🎓 高校・大学進学率の計算", style={"font_weight": "600", "color": "#2c3e50"}),
                            content=logic_section(
                                "進学率",
                                "調整後進学率 = 地域別基準進学率 × 家庭環境補正 × 偏差値補正",
                                [
                                    "【家庭環境補正】= (親学歴補正 + 世帯年収補正) / 2",
                                    "　（親学歴と世帯年収は相関が高いため平均を取る）",
                                    "【親学歴による大学進学率補正】",
                                    "　大学院: ×1.50 / 大学: ×1.30 / 短大専門: ×1.00 / 高校: ×0.80 / 中学: ×0.40",
                                    "【世帯年収による大学進学率補正】",
                                    "　1500万以上: ×1.30 / 1000-1500万: ×1.20 / 700-1000万: ×1.10",
                                    "　500-700万: ×1.00（基準）/ 400-500万: ×0.90 / 300-400万: ×0.80",
                                    "　200-300万: ×0.70 / 100-200万: ×0.60 / 100万未満: ×0.55",
                                    "【高校偏差値による大学進学率補正】※2024年追加",
                                    "　偏差値70+: ×1.30 / 65-69: ×1.20 / 60-64: ×1.10 / 55-59: ×1.05",
                                    "　50-54: ×1.00（基準）/ 45-49: ×0.70 / 40-44: ×0.46 / 35未満: ×0.25",
                                    "　（根拠: 学科別進学率 普通科71.3%、商業科33.0%、工業科17.9%）",
                                    "【地域別基準進学率】市区町村別データを使用（文部科学省）",
                                    "　東京都全体: 74.2% / 北海道全体: 52.8%（2024年度）",
                                ],
                                [
                                    {
                                        "org": "文部科学省",
                                        "name": "学校基本調査（令和6年度確定値）",
                                        "year": "2024年",
                                        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00400001&tstat=000001011528",
                                        "note": "都道府県別・学科別進学率",
                                    },
                                    {
                                        "org": "文部科学省",
                                        "name": "21世紀出生児縦断調査",
                                        "year": "2022年",
                                        "url": "https://www.mext.go.jp/b_menu/toukei/chousa08/21seiki/kekka/1268591.htm",
                                        "note": "親の学歴・年収と子の進学の関係",
                                    },
                                    {
                                        "org": "東京大学",
                                        "name": "学生生活実態調査",
                                        "year": "2022年",
                                        "url": "https://www.u-tokyo.ac.jp/ja/students/welfare/h01_01.html",
                                        "note": "東大生の家庭の世帯年収分布",
                                    },
                                    {
                                        "org": "SSM調査研究会",
                                        "name": "社会階層と社会移動全国調査",
                                        "year": "2015年",
                                        "url": "https://www.l.u-tokyo.ac.jp/2015SSM-PJ/",
                                        "note": "社会的地位の世代間移動",
                                    },
                                ],
                            ),
                            value="enrollment",
                        ),
                        # 3. 生涯年収の計算
                        rx.accordion.item(
                            header=rx.text("💰 生涯年収の計算", style={"font_weight": "600", "color": "#2c3e50"}),
                            content=logic_section(
                                "生涯年収",
                                "生涯年収 = 基準年収 × 勤務年数比 × 産業補正 × 性別補正 × 企業規模補正 × 雇用形態補正 × 大学ランク補正",
                                [
                                    "【学歴別基準生涯年収】",
                                    "　大学院卒: 3.2億円 / 大学卒: 2.7億円 / 短大専門: 2.3億円 / 高校卒: 2.0億円 / 中学卒: 1.6億円",
                                    "【性別補正】男性: ×1.00 / 女性: ×0.76（男女賃金格差）",
                                    "【企業規模補正】大企業: ×1.00 / 中企業: ×0.82 / 小企業: ×0.72",
                                    "【雇用形態補正】正社員: ×1.00 / 非正規: ×0.65",
                                    "【大学ランク補正】Sランク: ×1.15 / Aランク: ×1.08 / Bランク: ×1.00 / Cランク: ×0.95 / Dランク: ×0.92",
                                    "【産業補正】産業スコア(0-100)を0.7〜1.3の係数に変換",
                                ],
                                [
                                    {
                                        "org": "労働政策研究・研修機構",
                                        "name": "ユースフル労働統計2024",
                                        "year": "2024年",
                                        "url": "https://www.jil.go.jp/kokunai/statistics/kako/2024/index.html",
                                        "note": "学歴別生涯賃金推計",
                                    },
                                    {
                                        "org": "厚生労働省",
                                        "name": "賃金構造基本統計調査",
                                        "year": "2023年",
                                        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00450091&tstat=000001011429",
                                        "note": "企業規模・産業・雇用形態別賃金",
                                    },
                                    {
                                        "org": "厚生労働省",
                                        "name": "賃金構造基本統計調査 雇用形態別",
                                        "year": "2023年",
                                        "url": "https://www.mhlw.go.jp/toukei/itiran/roudou/chingin/kouzou/z2023/index.html",
                                        "note": "正社員・非正規の賃金格差データ",
                                    },
                                    {
                                        "org": "厚生労働省",
                                        "name": "男女間賃金格差",
                                        "year": "2024年",
                                        "url": "https://www.mhlw.go.jp/stf/newpage_28077.html",
                                        "note": "女性賃金は男性の75.8%（0.76倍の根拠）",
                                    },
                                ],
                            ),
                            value="income",
                        ),
                        # 4. 寿命・死因の計算
                        rx.accordion.item(
                            header=rx.text("⏳ 寿命・死因の計算", style={"font_weight": "600", "color": "#2c3e50"}),
                            content=logic_section(
                                "寿命・死因",
                                "死亡年齢 = 年齢別死亡者数データに基づく重み付きランダム選択",
                                [
                                    "【死亡年齢の決定】",
                                    "　年齢別死亡者数の分布に基づいて確率的に決定",
                                    "　性別・地域別のデータを使用",
                                    "【死因の決定】",
                                    "　死因別死亡者数データに基づく重み付きランダム選択",
                                    "　80歳未満の場合は「老衰」を除外",
                                    "【平均寿命】男性: 81.09歳 / 女性: 87.13歳（2023年簡易生命表）",
                                ],
                                [
                                    {
                                        "org": "厚生労働省",
                                        "name": "簡易生命表",
                                        "year": "2023年",
                                        "url": "https://www.mhlw.go.jp/toukei/saikin/hw/life/life23/index.html",
                                        "note": "年齢別死亡率・平均寿命",
                                    },
                                    {
                                        "org": "厚生労働省",
                                        "name": "人口動態統計",
                                        "year": "2022年",
                                        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00450011&tstat=000001028897",
                                        "note": "死因別死亡数",
                                    },
                                ],
                            ),
                            value="death",
                        ),
                        # 5. 人生スコアの計算
                        rx.accordion.item(
                            header=rx.text("🏆 人生スコア・ランクの計算", style={"font_weight": "600", "color": "#2c3e50"}),
                            content=logic_section(
                                "人生スコア",
                                "人生スコア = 寿命スコア × 0.40 + 生涯年収スコア × 0.35 + 学歴スコア × 0.25",
                                [
                                    "【配分根拠】幸福度・人生満足度研究に基づく（2025年改訂）",
                                    "　・内閣府「満足度・生活の質に関する調査2025」",
                                    "　・World Happiness Report 2024",
                                    "",
                                    "【寿命スコア: 40%】平均寿命を60点として換算（0-100点）",
                                    "　健康は幸福の基盤。早逝は人生の質に最大の影響",
                                    "　健康状態の生活満足度への影響は高い（回帰係数0.104）",
                                    "",
                                    "【生涯年収スコア: 35%】生涯年収パーセンタイルに基づく（0-100点）",
                                    "　1%: 5,000万円→0点 / 50%: 2.2億円→60点 / 99%: 5.5億円→100点",
                                    "　経済的要因は重要だが、一定水準以上では影響が減少（収穫逓減）",
                                    "",
                                    "【学歴スコア: 25%】国勢調査の学歴分布パーセンタイルに基づく（0-100点）",
                                    "　例: 大学院卒Sランク 95.1点 / 大学卒Bランク 84.0点 / 高校卒 36.2点",
                                    "　「人生選択の自由度」との強い相関（幸福度変動の82%を説明）",
                                    "",
                                    "【ランク判定】SS: 85点以上 / S: 75点以上 / A: 62点以上 / B: 42点以上 / C: 35点以上 / D: 35点未満",
                                ],
                                [
                                    {
                                        "org": "内閣府",
                                        "name": "満足度・生活の質に関する調査報告書2025",
                                        "year": "2025年",
                                        "url": "https://www5.cao.go.jp/keizai2/wellbeing/manzoku/index.html",
                                        "note": "生活満足度への分野別影響度分析",
                                    },
                                    {
                                        "org": "World Happiness Report",
                                        "name": "World Happiness Report 2024",
                                        "year": "2024年",
                                        "url": "https://worldhappiness.report/ed/2024/",
                                        "note": "幸福度の決定要因（収入、健康、社会的支援、自由度）",
                                    },
                                    {
                                        "org": "総務省統計局",
                                        "name": "国勢調査 学歴別人口",
                                        "year": "2020年",
                                        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200521&tstat=000001136464",
                                        "note": "15歳以上卒業者の最終学歴分布",
                                    },
                                    {
                                        "org": "労働政策研究・研修機構",
                                        "name": "ユースフル労働統計2024",
                                        "year": "2024年",
                                        "url": "https://www.jil.go.jp/kokunai/statistics/kako/2024/index.html",
                                        "note": "生涯年収パーセンタイル分布",
                                    },
                                    {
                                        "org": "厚生労働省",
                                        "name": "簡易生命表",
                                        "year": "2023年",
                                        "url": "https://www.mhlw.go.jp/toukei/saikin/hw/life/life23/index.html",
                                        "note": "平均寿命（男性81.09歳、女性87.13歳）",
                                    },
                                ],
                            ),
                            value="life_score",
                        ),
                        # 6. 親ガチャスコアの計算
                        rx.accordion.item(
                            header=rx.text("🎰 親ガチャスコアの計算", style={"font_weight": "600", "color": "#2c3e50"}),
                            content=logic_section(
                                "親ガチャスコア",
                                "親ガチャスコア = 世帯年収スコア × 0.35 + 出生地スコア × 0.35 + 親の学歴スコア × 0.30",
                                [
                                    "【配分根拠】子どもの発達・幸福度研究に基づく（2025年改訂）",
                                    "　・東京大学・ベネッセ親子調査「子どもの幸福度と家庭環境」",
                                    "　・厚生労働省「国民生活基礎調査」ひとり親世帯の貧困率44.5%",
                                    "",
                                    "【世帯年収スコア: 35%】（国民生活基礎調査パーセンタイル）",
                                    "　1500万以上: 98点 / 1000-1500万: 90点 / 700-1000万: 78点 / 500-700万: 60点",
                                    "　400-500万: 38点 / 300-400万: 22点 / 200-300万: 12点 / 100-200万: 5点 / 100万未満: 2点",
                                    "　※研究では「世帯年収と子どもの幸福度の関連は想像より小さい」",
                                    "",
                                    "【出生地スコア: 35%】市区町村別の複合指標（年収・進学率・就職率）",
                                    "　地域による機会格差（進学率、求人倍率、医療アクセス）を重視",
                                    "　東京の大学進学率は約68%、北海道は約45%",
                                    "",
                                    "【親の学歴スコア: 30%】（両親の平均、国勢調査パーセンタイル）",
                                    "　大学院卒: 94.3点 / 大学卒: 84.0点 / 短大専門: 68.3点 / 高校卒: 36.2点 / 中学卒: 0点",
                                    "　教育機会・文化資本に影響するが、直接的な幸福度への影響は限定的",
                                    "",
                                    "【重み調整】極端に高い/低い値（85点以上/15点以下）がある場合、その要素の重みを45%に増加",
                                ],
                                [
                                    {
                                        "org": "東京大学・ベネッセ教育総合研究所",
                                        "name": "子どもの生活と学びに関する親子調査",
                                        "year": "2023年",
                                        "url": "https://berd.benesse.jp/shotouchutou/research/detail1.php?id=5781",
                                        "note": "親子の幸福度の相互影響、収入と幸福度の関係",
                                    },
                                    {
                                        "org": "内閣府",
                                        "name": "満足度・生活の質に関する調査報告書2025",
                                        "year": "2025年",
                                        "url": "https://www5.cao.go.jp/keizai2/wellbeing/manzoku/index.html",
                                        "note": "社会とのつながりと幸福度の関係",
                                    },
                                    {
                                        "org": "総務省統計局",
                                        "name": "国勢調査 学歴別人口",
                                        "year": "2020年",
                                        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200521&tstat=000001136464",
                                        "note": "親世代の学歴分布パーセンタイル",
                                    },
                                    {
                                        "org": "厚生労働省",
                                        "name": "国民生活基礎調査",
                                        "year": "2022年",
                                        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00450061&tstat=000001114975",
                                        "note": "児童のいる世帯の年収分布、ひとり親世帯貧困率",
                                    },
                                    {
                                        "org": "総務省統計局",
                                        "name": "住宅・土地統計調査",
                                        "year": "2018年",
                                        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200522&tstat=000001127155",
                                        "note": "市区町村別の世帯年収分布",
                                    },
                                ],
                            ),
                            value="parent_score",
                        ),
                        # 7. 大学ランクによる就職への影響
                        rx.accordion.item(
                            header=rx.text("🏢 大学ランクと就職の関係", style={"font_weight": "600", "color": "#2c3e50"}),
                            content=logic_section(
                                "大学ランク→就職",
                                "大企業率 = 基準率(35%) + ランク別補正 / 正社員率 = 基準率 × ランク別補正係数",
                                [
                                    "【大学ランク別の大企業就職率】",
                                    "　Sランク（旧帝大・早慶）: 55%（+20pt）",
                                    "　Aランク（MARCH・関関同立）: 45%（+10pt）",
                                    "　Bランク（日東駒専・中堅国立）: 35%（基準）",
                                    "　Cランク（中堅私立）: 25%（-10pt）",
                                    "　Dランク（その他私立）: 18%（-17pt）",
                                    "",
                                    "【大学ランク別の正社員率補正】",
                                    "　Sランク: ×1.06（+6%）",
                                    "　Aランク: ×1.03（+3%）",
                                    "　Bランク: ×1.00（基準）",
                                    "　Cランク: ×0.97（-3%）",
                                    "　Dランク: ×0.92（-8%）",
                                    "",
                                    "【企業規模別の賃金補正】",
                                    "　大企業: ×1.00 / 中企業: ×0.82 / 小企業: ×0.72",
                                    "【雇用形態別の賃金補正】",
                                    "　正社員: ×1.00 / 非正規: ×0.65",
                                ],
                                [
                                    {
                                        "org": "大学通信",
                                        "name": "有名企業400社実就職率ランキング",
                                        "year": "2025年",
                                        "url": "https://univ-online.com/article/career/32503/",
                                        "note": "大学ランク別大企業就職率の推定根拠",
                                    },
                                    {
                                        "org": "内閣府経済社会総合研究所",
                                        "name": "大学4年生の正社員内定要因に関する実証分析",
                                        "year": "2020年",
                                        "url": "https://www.esri.cao.go.jp/jp/esri/archive/bun/bun190/bun190a.pdf",
                                        "note": "大学ランクと正社員内定率の相関分析",
                                    },
                                    {
                                        "org": "厚生労働省",
                                        "name": "賃金構造基本統計調査",
                                        "year": "2023年",
                                        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00450091&tstat=000001011429",
                                        "note": "企業規模別の賃金格差データ",
                                    },
                                    {
                                        "org": "総務省統計局",
                                        "name": "労働力調査 詳細集計",
                                        "year": "2024年",
                                        "url": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200531&tstat=000000110001",
                                        "note": "学歴・性別別正社員・非正規比率",
                                    },
                                ],
                            ),
                            value="university_career",
                        ),
                        type="multiple",
                        collapsible=True,
                        style={"width": "100%"},
                    ),
                    # 注釈
                    rx.box(
                        rx.vstack(
                            rx.text(
                                "📋 データの信頼性について",
                                style={"font_weight": "600", "color": "#2c3e50", "font_size": "0.9rem"},
                            ),
                            rx.text(
                                "すべて政府機関（厚生労働省・総務省統計局・文部科学省・労働政策研究機構）が公開している公式統計データを使用しています。",
                                style={"font_size": "0.85rem", "color": "#666", "line_height": "1.6"},
                            ),
                            rx.text(
                                "各データの「🔗 原典を見る」リンクから、e-Stat（政府統計ポータル）や各省庁の公式サイトで原データを確認できます。",
                                style={"font_size": "0.85rem", "color": "#666", "line_height": "1.6"},
                            ),
                            rx.text(
                                "補正係数の一部は複数の研究から推定した値です。シミュレーション結果は統計的な傾向を示すものであり、個人の人生を予測するものではありません。",
                                style={"font_size": "0.8rem", "color": "#888", "line_height": "1.6", "margin_top": "0.5rem"},
                            ),
                            spacing="2",
                            align="start",
                        ),
                        style={
                            "margin_top": "1rem",
                            "padding": "1rem",
                            "background": "#f8f9fa",
                            "border_radius": "8px",
                            "border_left": "3px solid #666",
                            "width": "100%",
                        },
                    ),
                    spacing="2",
                    width="100%",
                ),
            ),
            rx.dialog.close(
                rx.button(
                    "閉じる",
                    style={
                        "margin_top": "1rem",
                        "background": "#D9D9D9",
                        "border": "none",
                        "border_radius": "4px",
                        "padding": "8px 24px",
                        "cursor": "pointer",
                        "_hover": {"background": "#CCCCCC"},
                    },
                ),
            ),
            style={
                "max_width": "800px",
                "max_height": "90vh",
                "overflow_y": "auto",
            },
        ),
    )


def correlation_dialog() -> rx.Component:
    """相関図ダイアログ (Figma: 100x28px)"""
    # サマリー情報を取得
    summary = get_correlation_summary()
    # Sankey図を生成
    fig = create_correlation_sankey()
    
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "相関図",
                style={
                    "width": "100px",
                    "height": "28px",
                    "background": "#D9D9D9",
                    "border": "none",
                    "border_radius": "0",
                    "padding": "0",
                    "font_family": "'Zen Kaku Gothic New', sans-serif",
                    "font_size": "12px",
                    "font_weight": "400",
                    "color": "#000000",
                    "cursor": "pointer",
                    "_hover": {"background": "#CCCCCC"},
                },
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("📊 統計データ相関図"),
            rx.dialog.description(
                rx.vstack(
                    # ヘッダー
                    rx.box(
                        rx.vstack(
                            rx.text(
                                "このシミュレーターでは、様々な統計データが互いに影響し合って最終的な「人生スコア」を算出しています。",
                                style={"color": "#666", "font_size": "0.9rem"},
                            ),
                            rx.text(
                                "💡 ノードをホバーすると詳細が表示されます",
                                style={"font_weight": "600", "color": "#2c3e50", "font_size": "0.85rem"},
                            ),
                            spacing="2",
                            align="start",
                        ),
                        style={
                            "padding": "0.75rem 1rem",
                            "background": "#f8f9fa",
                            "border_radius": "8px",
                            "border": "1px solid #e0e0e0",
                            "margin_bottom": "1rem",
                        },
                    ),
                    # 要素カウント（モノトーンベースにアクセントカラー）
                    rx.hstack(
                        rx.box(
                            rx.vstack(
                                rx.text("入力要素", style={"font_weight": "600", "font_size": "0.85rem", "color": "#2c3e50"}),
                                rx.text(f"{summary['input_count']}個", style={"font_size": "1.5rem", "font_weight": "700", "color": "#1a1a1a"}),
                                rx.text("親ガチャ要素", style={"font_size": "0.75rem", "color": "#666"}),
                                spacing="1",
                                align="center",
                            ),
                            style={
                                "padding": "0.75rem",
                                "background": "#ffffff",
                                "border_radius": "8px",
                                "border": "1px solid #e0e0e0",
                                "border_left": "4px solid rgba(31, 119, 180, 1)",
                                "flex": "1",
                                "text_align": "center",
                            },
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("中間計算", style={"font_weight": "600", "font_size": "0.85rem", "color": "#2c3e50"}),
                                rx.text(f"{summary['middle_count']}個", style={"font_size": "1.5rem", "font_weight": "700", "color": "#1a1a1a"}),
                                rx.text("偏差値・進学率等", style={"font_size": "0.75rem", "color": "#666"}),
                                spacing="1",
                                align="center",
                            ),
                            style={
                                "padding": "0.75rem",
                                "background": "#ffffff",
                                "border_radius": "8px",
                                "border": "1px solid #e0e0e0",
                                "border_left": "4px solid rgba(255, 127, 14, 1)",
                                "flex": "1",
                                "text_align": "center",
                            },
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text("最終出力", style={"font_weight": "600", "font_size": "0.85rem", "color": "#2c3e50"}),
                                rx.text(f"{summary['output_count']}個", style={"font_size": "1.5rem", "font_weight": "700", "color": "#1a1a1a"}),
                                rx.text("学歴・年収・寿命", style={"font_size": "0.75rem", "color": "#666"}),
                                spacing="1",
                                align="center",
                            ),
                            style={
                                "padding": "0.75rem",
                                "background": "#ffffff",
                                "border_radius": "8px",
                                "border": "1px solid #e0e0e0",
                                "border_left": "4px solid rgba(44, 160, 44, 1)",
                                "flex": "1",
                                "text_align": "center",
                            },
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    # Sankey図（Plotly）
                    rx.box(
                        rx.plotly(data=fig, style={"width": "100%", "height": "500px"}),
                        style={
                            "width": "100%",
                            "margin_top": "1rem",
                            "border": "1px solid #e0e0e0",
                            "border_radius": "8px",
                            "overflow": "hidden",
                            "background": "#ffffff",
                        },
                    ),
                    # 図の見方（折りたたみ）
                    rx.accordion.root(
                        rx.accordion.item(
                            header=rx.text("📖 図の見方", style={"font_weight": "600", "color": "#2c3e50"}),
                            content=rx.vstack(
                                rx.box(
                                    rx.vstack(
                                        rx.text("レイヤー（層）の説明", style={"font_weight": "700", "margin_bottom": "0.5rem", "color": "#2c3e50"}),
                                        rx.hstack(
                                            rx.box(style={"width": "12px", "height": "12px", "background": "rgba(31, 119, 180, 1)", "border_radius": "2px"}),
                                            rx.text("入力層", style={"font_weight": "600", "color": "#2c3e50"}),
                                            rx.text("シミュレーション開始時に決まる要素（親ガチャ）", style={"color": "#666", "font_size": "0.9rem"}),
                                            spacing="2",
                                            align="center",
                                        ),
                                        rx.hstack(
                                            rx.box(style={"width": "12px", "height": "12px", "background": "rgba(255, 127, 14, 1)", "border_radius": "2px"}),
                                            rx.text("中間層", style={"font_weight": "600", "color": "#2c3e50"}),
                                            rx.text("入力から計算される要素（進学、偏差値など）", style={"color": "#666", "font_size": "0.9rem"}),
                                            spacing="2",
                                            align="center",
                                        ),
                                        rx.hstack(
                                            rx.box(style={"width": "12px", "height": "12px", "background": "rgba(44, 160, 44, 1)", "border_radius": "2px"}),
                                            rx.text("出力層", style={"font_weight": "600", "color": "#2c3e50"}),
                                            rx.text("最終的なスコアに寄与する要素", style={"color": "#666", "font_size": "0.9rem"}),
                                            spacing="2",
                                            align="center",
                                        ),
                                        spacing="2",
                                        align="start",
                                    ),
                                    style={"padding": "1rem", "background": "#f8f9fa", "border_radius": "8px", "width": "100%", "border": "1px solid #e0e0e0"},
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.text("線（リンク）の意味", style={"font_weight": "700", "margin_bottom": "0.5rem", "color": "#2c3e50"}),
                                        rx.text("• 線の太さは影響の強さを表します", style={"color": "#666"}),
                                        rx.text("• 線をホバーすると、具体的な影響内容が表示されます", style={"color": "#666"}),
                                        spacing="2",
                                        align="start",
                                    ),
                                    style={"padding": "1rem", "background": "#f8f9fa", "border_radius": "8px", "width": "100%", "margin_top": "0.5rem", "border": "1px solid #e0e0e0"},
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.text("人生スコアの構成", style={"font_weight": "700", "margin_bottom": "0.5rem", "color": "#2c3e50"}),
                                        rx.hstack(
                                            rx.text("最終学歴", style={"font_weight": "600", "color": "#2c3e50"}),
                                            rx.text("30%", style={"color": "#666"}),
                                            rx.text("•", style={"color": "#ccc"}),
                                            rx.text("生涯年収", style={"font_weight": "600", "color": "#2c3e50"}),
                                            rx.text("40%", style={"color": "#666"}),
                                            rx.text("•", style={"color": "#ccc"}),
                                            rx.text("寿命", style={"font_weight": "600", "color": "#2c3e50"}),
                                            rx.text("30%", style={"color": "#666"}),
                                            spacing="2",
                                            wrap="wrap",
                                        ),
                                        spacing="2",
                                        align="start",
                                    ),
                                    style={"padding": "1rem", "background": "#f8f9fa", "border_radius": "8px", "width": "100%", "margin_top": "0.5rem", "border": "1px solid #e0e0e0"},
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            value="how_to_read",
                        ),
                        rx.accordion.item(
                            header=rx.text("🔗 主要な因果関係", style={"font_weight": "600", "color": "#2c3e50"}),
                            content=rx.vstack(
                                rx.box(
                                    rx.vstack(
                                        rx.text("親の学歴 → 子の学歴", style={"font_weight": "700", "margin_bottom": "0.5rem", "color": "#2c3e50"}),
                                        rx.text("• 親の学歴が高いほど、子の偏差値が高くなる傾向（補正: -5〜+8）", style={"color": "#666", "font_size": "0.9rem"}),
                                        rx.text("• 親の学歴が高いほど、高校・大学進学率が上昇", style={"color": "#666", "font_size": "0.9rem"}),
                                        spacing="1",
                                        align="start",
                                    ),
                                    style={"padding": "0.75rem", "background": "#ffffff", "border_radius": "8px", "width": "100%", "border": "1px solid #e0e0e0", "border_left": "3px solid #333"},
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.text("世帯年収 → 進学率", style={"font_weight": "700", "margin_bottom": "0.5rem", "color": "#2c3e50"}),
                                        rx.text("• 高年収世帯ほど進学率が高い", style={"color": "#666", "font_size": "0.9rem"}),
                                        rx.text("• 大学進学には特に大きな影響", style={"color": "#666", "font_size": "0.9rem"}),
                                        spacing="1",
                                        align="start",
                                    ),
                                    style={"padding": "0.75rem", "background": "#ffffff", "border_radius": "8px", "width": "100%", "margin_top": "0.5rem", "border": "1px solid #e0e0e0", "border_left": "3px solid #555"},
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.text("性別 → 生涯年収", style={"font_weight": "700", "margin_bottom": "0.5rem", "color": "#2c3e50"}),
                                        rx.text("• 女性は男性の約76%の賃金（男女賃金格差）", style={"color": "#666", "font_size": "0.9rem"}),
                                        rx.text("• 女性は非正規雇用率が高い傾向", style={"color": "#666", "font_size": "0.9rem"}),
                                        spacing="1",
                                        align="start",
                                    ),
                                    style={"padding": "0.75rem", "background": "#ffffff", "border_radius": "8px", "width": "100%", "margin_top": "0.5rem", "border": "1px solid #e0e0e0", "border_left": "3px solid #777"},
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.text("大学ランク → 企業規模・雇用形態", style={"font_weight": "700", "margin_bottom": "0.5rem", "color": "#2c3e50"}),
                                        rx.text("• 大企業就職率: S +20pt / A +10pt / B 基準 / C -10pt / D -17pt", style={"color": "#666", "font_size": "0.9rem"}),
                                        rx.text("• 正社員率補正: S ×1.06 / A ×1.03 / B 基準 / C ×0.97 / D ×0.92", style={"color": "#666", "font_size": "0.9rem"}),
                                        rx.text("• 生涯年収補正: S ×1.15 / A ×1.08 / B 基準 / C ×0.95 / D ×0.92", style={"color": "#666", "font_size": "0.9rem"}),
                                        spacing="1",
                                        align="start",
                                    ),
                                    style={"padding": "0.75rem", "background": "#ffffff", "border_radius": "8px", "width": "100%", "margin_top": "0.5rem", "border": "1px solid #e0e0e0", "border_left": "3px solid #999"},
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            value="causality",
                        ),
                        type="multiple",
                        collapsible=True,
                        style={"width": "100%", "margin_top": "1rem"},
                    ),
                    spacing="3",
                    width="100%",
                ),
            ),
            rx.dialog.close(
                rx.button(
                    "閉じる",
                    style={
                        "margin_top": "1rem",
                        "background": "#D9D9D9",
                        "border": "none",
                        "border_radius": "4px",
                        "padding": "8px 24px",
                        "cursor": "pointer",
                        "_hover": {"background": "#CCCCCC"},
                    },
                ),
            ),
            style={
                "max_width": "900px",
                "max_height": "90vh",
                "overflow_y": "auto",
            },
        ),
    )


def about_gacha_dialog() -> rx.Component:
    """このガチャについて - 統合ダイアログ"""
    # サマリー情報を取得
    summary = get_correlation_summary()
    # Sankey図を生成
    fig = create_correlation_sankey()
    
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "このガチャについて",
                style={
                    "width": "280px",
                    "height": "80px",
                    "background": "#D9D9D9",
                    "border": "none",
                    "border_radius": "10px",
                    "font_family": "'Zen Kaku Gothic New', sans-serif",
                    "font_size": "20px",
                    "font_weight": "400",
                    "color": "#000000",
                    "cursor": "pointer",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                    "_hover": {"background": "#CCCCCC"},
                },
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("📖 このガチャについて"),
            rx.dialog.description(
                rx.vstack(
                    # ============================================
                    # 0. 導入文
                    # ============================================
                    rx.box(
                        rx.vstack(
                            rx.text(
                                "このガチャでは、各地で収集されて公開されている統計データに徹底的に基づいた、ある地域に生きる人間の人生を、シミュレーションにより大量に生み出します。そしてその結果に対して、現在の社会的な価値基準により採点をおこない、それぞれの人生に点数をつけ、ランク付けをします。",
                                style={"color": "#333", "font_size": "0.95rem", "line_height": "1.8"},
                            ),
                            rx.text(
                                "できる限り恣意性を排除した、統計的な情報でつくられた存在しないはずの人間の経歴。それは私たちの視野にどんな気付きをもたらすでしょうか。また、「点数」のオルタナティブにはどのようなものがあるでしょうか。",
                                style={"color": "#333", "font_size": "0.95rem", "line_height": "1.8"},
                            ),
                            rx.box(
                                rx.vstack(
                                    rx.text(
                                        "⚠️ 注意",
                                        style={"font_weight": "700", "color": "#2c3e50", "font_size": "0.9rem"},
                                    ),
                                    rx.text(
                                        "このガチャで生成される人生は、可能な限り統計情報に基づいて作成した、「あり得る可能性のある人生」です。「実在する人間の人生」とはまったく関係ありません。",
                                        style={"color": "#555", "font_size": "0.85rem", "line_height": "1.7"},
                                    ),
                                    rx.text(
                                        "また自動で行われているランク付けは、特定の個人のことを指しているわけではありませんが、読み手にとって必ずしも心地よいものではないかもしれません。「実在の人物を指しているわけではないのに、何故これが心地よくないのか？」ということも含めて、一緒に考えられれば嬉しく思います。",
                                        style={"color": "#555", "font_size": "0.85rem", "line_height": "1.7"},
                                    ),
                                    spacing="2",
                                    align="start",
                                ),
                                style={
                                    "margin_top": "0.75rem",
                                    "padding": "0.75rem 1rem",
                                    "background": "#fff9e6",
                                    "border_radius": "8px",
                                    "border_left": "4px solid #e6a700",
                                },
                            ),
                            spacing="3",
                            align="start",
                            width="100%",
                        ),
                        style={
                            "padding": "1rem",
                            "background": "#ffffff",
                            "border_radius": "8px",
                            "border": "1px solid #e0e0e0",
                            "width": "100%",
                            "margin_bottom": "1rem",
                        },
                    ),
                    
                    # ============================================
                    # 1. 相関図セクション
                    # ============================================
                    rx.box(
                        rx.vstack(
                            rx.text("📊 統計データ相関図", style={"font_weight": "700", "font_size": "1.1rem", "color": "#2c3e50"}),
                            rx.text(
                                "このシミュレーターでは、様々な統計データが互いに影響し合って最終的な「人生スコア」を算出しています。",
                                style={"color": "#666", "font_size": "0.9rem", "margin_bottom": "0.5rem"},
                            ),
                            # 要素カウント
                            rx.hstack(
                                rx.box(
                                    rx.vstack(
                                        rx.text("入力要素", style={"font_weight": "600", "font_size": "0.8rem", "color": "#2c3e50"}),
                                        rx.text(f"{summary['input_count']}個", style={"font_size": "1.2rem", "font_weight": "700", "color": "#1a1a1a"}),
                                        spacing="0",
                                        align="center",
                                    ),
                                    style={
                                        "padding": "0.5rem",
                                        "background": "#ffffff",
                                        "border_radius": "6px",
                                        "border": "1px solid #e0e0e0",
                                        "border_left": "3px solid rgba(31, 119, 180, 1)",
                                        "flex": "1",
                                        "text_align": "center",
                                    },
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.text("中間計算", style={"font_weight": "600", "font_size": "0.8rem", "color": "#2c3e50"}),
                                        rx.text(f"{summary['middle_count']}個", style={"font_size": "1.2rem", "font_weight": "700", "color": "#1a1a1a"}),
                                        spacing="0",
                                        align="center",
                                    ),
                                    style={
                                        "padding": "0.5rem",
                                        "background": "#ffffff",
                                        "border_radius": "6px",
                                        "border": "1px solid #e0e0e0",
                                        "border_left": "3px solid rgba(255, 127, 14, 1)",
                                        "flex": "1",
                                        "text_align": "center",
                                    },
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.text("最終出力", style={"font_weight": "600", "font_size": "0.8rem", "color": "#2c3e50"}),
                                        rx.text(f"{summary['output_count']}個", style={"font_size": "1.2rem", "font_weight": "700", "color": "#1a1a1a"}),
                                        spacing="0",
                                        align="center",
                                    ),
                                    style={
                                        "padding": "0.5rem",
                                        "background": "#ffffff",
                                        "border_radius": "6px",
                                        "border": "1px solid #e0e0e0",
                                        "border_left": "3px solid rgba(44, 160, 44, 1)",
                                        "flex": "1",
                                        "text_align": "center",
                                    },
                                ),
                                spacing="2",
                                width="100%",
                            ),
                            # Sankey図
                            rx.box(
                                rx.plotly(data=fig, style={"width": "100%", "height": "400px"}),
                                style={
                                    "width": "100%",
                                    "margin_top": "0.5rem",
                                    "border": "1px solid #e0e0e0",
                                    "border_radius": "8px",
                                    "overflow": "hidden",
                                    "background": "#ffffff",
                                },
                            ),
                            rx.text(
                                "💡 ノードをホバーすると詳細が表示されます",
                                style={"font_size": "0.8rem", "color": "#888", "margin_top": "0.25rem"},
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        style={
                            "padding": "1rem",
                            "background": "#f8f9fa",
                            "border_radius": "8px",
                            "border": "1px solid #e0e0e0",
                            "width": "100%",
                        },
                    ),
                    
                    # ============================================
                    # 2. 確率セクション（北海道・東京両方）
                    # ============================================
                    rx.box(
                        rx.vstack(
                            rx.text("🎲 ガチャ確率", style={"font_weight": "700", "font_size": "1.1rem", "color": "#2c3e50"}),
                            rx.text(
                                "10,000回のシミュレーション結果に基づく確率です（2026年1月計算、新配分: 寿命40%・生涯年収35%・学歴25%）",
                                style={"color": "#666", "font_size": "0.85rem", "margin_bottom": "0.5rem"},
                            ),
                            # 北海道と東京を横並び
                            rx.hstack(
                                # 北海道
                                rx.box(
                                    rx.vstack(
                                        rx.text("🏔️ 北海道", style={"font_weight": "700", "font_size": "1rem", "color": "#2c3e50", "margin_bottom": "0.5rem"}),
                                        *[
                                            rx.hstack(
                                                rx.box(
                                                    rx.text(rank, style={"font_size": "1rem", "font_weight": "700", "color": RANK_INFO[rank]["color"]}),
                                                    style={
                                                        "width": "32px",
                                                        "height": "32px",
                                                        "display": "flex",
                                                        "align_items": "center",
                                                        "justify_content": "center",
                                                        "background": RANK_INFO[rank]["bg"],
                                                        "border_radius": "4px",
                                                        "border": f"1px solid {RANK_INFO[rank]['color']}",
                                                    },
                                                ),
                                                rx.text(RANK_INFO[rank]["label"], style={"font_size": "0.8rem", "color": "#666", "flex": "1"}),
                                                rx.text(rate, style={"font_size": "0.9rem", "font_weight": "600", "color": RANK_INFO[rank]["color"]}),
                                                spacing="2",
                                                align="center",
                                                width="100%",
                                            )
                                            for rank, rate in GACHA_RATES["hokkaido"].items()
                                        ],
                                        spacing="1",
                                        align="start",
                                        width="100%",
                                    ),
                                    style={
                                        "padding": "0.75rem",
                                        "background": "#ffffff",
                                        "border_radius": "8px",
                                        "border": "1px solid #e0e0e0",
                                        "flex": "1",
                                    },
                                ),
                                # 東京
                                rx.box(
                                    rx.vstack(
                                        rx.text("🗼 東京", style={"font_weight": "700", "font_size": "1rem", "color": "#2c3e50", "margin_bottom": "0.5rem"}),
                                        *[
                                            rx.hstack(
                                                rx.box(
                                                    rx.text(rank, style={"font_size": "1rem", "font_weight": "700", "color": RANK_INFO[rank]["color"]}),
                                                    style={
                                                        "width": "32px",
                                                        "height": "32px",
                                                        "display": "flex",
                                                        "align_items": "center",
                                                        "justify_content": "center",
                                                        "background": RANK_INFO[rank]["bg"],
                                                        "border_radius": "4px",
                                                        "border": f"1px solid {RANK_INFO[rank]['color']}",
                                                    },
                                                ),
                                                rx.text(RANK_INFO[rank]["label"], style={"font_size": "0.8rem", "color": "#666", "flex": "1"}),
                                                rx.text(rate, style={"font_size": "0.9rem", "font_weight": "600", "color": RANK_INFO[rank]["color"]}),
                                                spacing="2",
                                                align="center",
                                                width="100%",
                                            )
                                            for rank, rate in GACHA_RATES["tokyo"].items()
                                        ],
                                        spacing="1",
                                        align="start",
                                        width="100%",
                                    ),
                                    style={
                                        "padding": "0.75rem",
                                        "background": "#ffffff",
                                        "border_radius": "8px",
                                        "border": "1px solid #e0e0e0",
                                        "flex": "1",
                                    },
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        style={
                            "padding": "1rem",
                            "background": "#f8f9fa",
                            "border_radius": "8px",
                            "border": "1px solid #e0e0e0",
                            "width": "100%",
                            "margin_top": "1rem",
                        },
                    ),
                    
                    # ============================================
                    # 3. データセクション
                    # ============================================
                    rx.box(
                        rx.vstack(
                            rx.text("📚 データセット・計算ロジック", style={"font_weight": "700", "font_size": "1.1rem", "color": "#2c3e50"}),
                            rx.text(
                                "公式統計データと計算ロジックの詳細です。",
                                style={"color": "#666", "font_size": "0.85rem", "margin_bottom": "0.5rem"},
                            ),
                            # データセット一覧（コンパクト）
                            rx.accordion.root(
                                rx.accordion.item(
                                    header=rx.text("📊 使用データセット一覧", style={"font_weight": "600", "color": "#2c3e50"}),
                                    content=rx.vstack(
                                        *[
                                            rx.hstack(
                                                rx.text(data["icon"], style={"font_size": "1rem"}),
                                                rx.vstack(
                                                    rx.text(data["name"], style={"font_weight": "600", "font_size": "0.85rem", "color": "#2c3e50"}),
                                                    rx.text(data["official_name"], style={"font_size": "0.75rem", "color": "#666"}),
                                                    spacing="0",
                                                    align="start",
                                                ),
                                                rx.spacer(),
                                                rx.link(
                                                    rx.text("🔗", style={"font_size": "0.8rem"}),
                                                    href=data["url"],
                                                    is_external=True,
                                                ),
                                                spacing="2",
                                                align="center",
                                                width="100%",
                                                style={"padding": "0.5rem", "background": "#ffffff", "border_radius": "4px", "border": "1px solid #e0e0e0"},
                                            )
                                            for data in DATASET_INFO
                                        ],
                                        spacing="1",
                                        width="100%",
                                    ),
                                    value="datasets",
                                ),
                                rx.accordion.item(
                                    header=rx.text("📐 偏差値の計算ロジック", style={"font_weight": "600", "color": "#2c3e50"}),
                                    content=rx.vstack(
                                        rx.box(
                                            rx.text("偏差値 = 50 + 親学歴補正 + 世帯年収補正 + 地域補正 + ランダム項", style={"font_family": "monospace", "font_size": "0.8rem", "color": "#080808"}),
                                            style={"padding": "0.5rem", "background": "#f0f0f0", "border_radius": "4px", "width": "100%"},
                                        ),
                                        rx.text("親学歴補正: 大学院+8 / 大学+5 / 短大専門+1 / 高校-2 / 中学-5", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.text("世帯年収補正: 1500万以上+5 〜 100万未満-4", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.text("地域補正: 東京+2 / 北海道-1", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.box(
                                            rx.vstack(
                                                rx.text("📚 根拠データ", style={"font_weight": "600", "font_size": "0.75rem", "color": "#333"}),
                                                rx.hstack(
                                                    rx.text("• 文部科学省・国立教育政策研究所「全国学力・学習状況調査」2024年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.nier.go.jp/24chousakekkahoukoku/index.html", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• OECD「Education at a Glance」2024年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.oecd.org/education/education-at-a-glance/", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• ベネッセ教育総合研究所「子どもの生活と学びに関する親子調査」2023年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://berd.benesse.jp/shotouchutou/research/detail1.php?id=5781", is_external=True),
                                                    spacing="1",
                                                ),
                                                spacing="1",
                                                align="start",
                                            ),
                                            style={"margin_top": "0.5rem", "padding_top": "0.5rem", "border_top": "1px solid #e0e0e0", "width": "100%"},
                                        ),
                                        spacing="1",
                                        width="100%",
                                    ),
                                    value="deviation",
                                ),
                                rx.accordion.item(
                                    header=rx.text("🎓 進学率の計算ロジック", style={"font_weight": "600", "color": "#2c3e50"}),
                                    content=rx.vstack(
                                        rx.box(
                                            rx.text("進学率 = 地域別基準進学率 × (親学歴補正 + 世帯年収補正) / 2", style={"font_family": "monospace", "font_size": "0.8rem", "color": "#080808"}),
                                            style={"padding": "0.5rem", "background": "#f0f0f0", "border_radius": "4px", "width": "100%"},
                                        ),
                                        rx.text("大学進学・親学歴補正: 大学院×1.5 / 大学×1.3 / 高校×0.8 / 中学×0.4", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.text("大学進学・世帯年収補正: 1500万以上×1.3 〜 100万未満×0.55", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.box(
                                            rx.vstack(
                                                rx.text("📚 根拠データ", style={"font_weight": "600", "font_size": "0.75rem", "color": "#333"}),
                                                rx.hstack(
                                                    rx.text("• 文部科学省「学校基本調査」2024年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00400001&tstat=000001011528", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• 文部科学省「21世紀出生児縦断調査」2022年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.mext.go.jp/b_menu/toukei/chousa08/21seiki/kekka/1268591.htm", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• 東京大学「学生生活実態調査」2022年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.u-tokyo.ac.jp/ja/students/welfare/h01_01.html", is_external=True),
                                                    spacing="1",
                                                ),
                                                spacing="1",
                                                align="start",
                                            ),
                                            style={"margin_top": "0.5rem", "padding_top": "0.5rem", "border_top": "1px solid #e0e0e0", "width": "100%"},
                                        ),
                                        spacing="1",
                                        width="100%",
                                    ),
                                    value="enrollment",
                                ),
                                rx.accordion.item(
                                    header=rx.text("💰 生涯年収の計算ロジック", style={"font_weight": "600", "color": "#2c3e50"}),
                                    content=rx.vstack(
                                        rx.box(
                                            rx.text("生涯年収 = 基準年収 × 性別 × 企業規模 × 雇用形態 × 大学ランク", style={"font_family": "monospace", "font_size": "0.8rem", "color": "#080808"}),
                                            style={"padding": "0.5rem", "background": "#f0f0f0", "border_radius": "4px", "width": "100%"},
                                        ),
                                        rx.text("基準年収: 大学院3.2億 / 大学2.7億 / 短大専門2.3億 / 高校2.0億 / 中学1.6億", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.text("性別補正: 男性×1.0 / 女性×0.76（男女賃金格差）", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.text("企業規模: 大×1.0 / 中×0.82 / 小×0.72", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.box(
                                            rx.vstack(
                                                rx.text("📚 根拠データ", style={"font_weight": "600", "font_size": "0.75rem", "color": "#333"}),
                                                rx.hstack(
                                                    rx.text("• 労働政策研究・研修機構「ユースフル労働統計2024」2024年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.jil.go.jp/kokunai/statistics/kako/2024/index.html", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• 厚生労働省「賃金構造基本統計調査」2023年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00450091&tstat=000001011429", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• 厚生労働省「男女間賃金格差」2024年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.mhlw.go.jp/stf/newpage_28077.html", is_external=True),
                                                    spacing="1",
                                                ),
                                                spacing="1",
                                                align="start",
                                            ),
                                            style={"margin_top": "0.5rem", "padding_top": "0.5rem", "border_top": "1px solid #e0e0e0", "width": "100%"},
                                        ),
                                        spacing="1",
                                        width="100%",
                                    ),
                                    value="income",
                                ),
                                rx.accordion.item(
                                    header=rx.text("🏆 人生スコアの計算ロジック", style={"font_weight": "600", "color": "#2c3e50"}),
                                    content=rx.vstack(
                                        rx.box(
                                            rx.text("人生スコア = 学歴×0.30 + 年収×0.40 + 寿命×0.30", style={"font_family": "monospace", "font_size": "0.8rem", "color": "#080808"}),
                                            style={"padding": "0.5rem", "background": "#f0f0f0", "border_radius": "4px", "width": "100%"},
                                        ),
                                        rx.text("各要素は国勢調査・統計データのパーセンタイルに基づき0-100点に換算", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.text("ランク: SS≧85 / S≧75 / A≧62 / B≧42 / C≧35 / D<35", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.box(
                                            rx.vstack(
                                                rx.text("📚 根拠データ", style={"font_weight": "600", "font_size": "0.75rem", "color": "#333"}),
                                                rx.hstack(
                                                    rx.text("• 総務省統計局「国勢調査 学歴別人口」2020年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200521&tstat=000001136464", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• 労働政策研究・研修機構「ユースフル労働統計2024」2024年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.jil.go.jp/kokunai/statistics/kako/2024/index.html", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• 厚生労働省「簡易生命表」2023年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.mhlw.go.jp/toukei/saikin/hw/life/life23/index.html", is_external=True),
                                                    spacing="1",
                                                ),
                                                spacing="1",
                                                align="start",
                                            ),
                                            style={"margin_top": "0.5rem", "padding_top": "0.5rem", "border_top": "1px solid #e0e0e0", "width": "100%"},
                                        ),
                                        spacing="1",
                                        width="100%",
                                    ),
                                    value="score",
                                ),
                                rx.accordion.item(
                                    header=rx.text("🎰 親ガチャスコアの計算ロジック", style={"font_weight": "600", "color": "#2c3e50"}),
                                    content=rx.vstack(
                                        rx.box(
                                            rx.text("親ガチャ = 親学歴×0.40 + 世帯年収×0.40 + 出生地×0.20", style={"font_family": "monospace", "font_size": "0.8rem", "color": "#080808"}),
                                            style={"padding": "0.5rem", "background": "#f0f0f0", "border_radius": "4px", "width": "100%"},
                                        ),
                                        rx.text("親学歴: 大学院94点 / 大学84点 / 短大専門68点 / 高校36点 / 中学0点", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.text("世帯年収: 1500万以上98点 / 500-700万60点 / 100万未満2点", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.box(
                                            rx.vstack(
                                                rx.text("📚 根拠データ", style={"font_weight": "600", "font_size": "0.75rem", "color": "#333"}),
                                                rx.hstack(
                                                    rx.text("• 総務省統計局「国勢調査 学歴別人口」2020年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200521&tstat=000001136464", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• 厚生労働省「国民生活基礎調査」2022年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00450061&tstat=000001114975", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• 総務省統計局「住宅・土地統計調査」2018年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200522&tstat=000001127155", is_external=True),
                                                    spacing="1",
                                                ),
                                                spacing="1",
                                                align="start",
                                            ),
                                            style={"margin_top": "0.5rem", "padding_top": "0.5rem", "border_top": "1px solid #e0e0e0", "width": "100%"},
                                        ),
                                        spacing="1",
                                        width="100%",
                                    ),
                                    value="parent",
                                ),
                                rx.accordion.item(
                                    header=rx.text("🏢 大学ランクと就職の関係", style={"font_weight": "600", "color": "#2c3e50"}),
                                    content=rx.vstack(
                                        rx.box(
                                            rx.text("大企業率 = 基準35% + ランク補正 / 正社員率 = 基準 × ランク係数", style={"font_family": "monospace", "font_size": "0.8rem", "color": "#080808"}),
                                            style={"padding": "0.5rem", "background": "#f0f0f0", "border_radius": "4px", "width": "100%"},
                                        ),
                                        rx.text("大企業率: S 55%(+20) / A 45%(+10) / B 35%(基準) / C 25%(-10) / D 18%(-17)", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.text("正社員率補正: S ×1.06 / A ×1.03 / B ×1.00 / C ×0.97 / D ×0.92", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.text("企業規模賃金: 大×1.0 / 中×0.82 / 小×0.72", style={"font_size": "0.8rem", "color": "#080808"}),
                                        rx.box(
                                            rx.vstack(
                                                rx.text("📚 根拠データ", style={"font_weight": "600", "font_size": "0.75rem", "color": "#333"}),
                                                rx.hstack(
                                                    rx.text("• 大学通信「有名企業400社実就職率ランキング」2025年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://univ-online.com/article/career/32503/", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• 内閣府経済社会総合研究所「大学4年生の正社員内定要因に関する実証分析」2020年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.esri.cao.go.jp/jp/esri/archive/bun/bun190/bun190a.pdf", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• 厚生労働省「賃金構造基本統計調査」2023年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00450091&tstat=000001011429", is_external=True),
                                                    spacing="1",
                                                ),
                                                rx.hstack(
                                                    rx.text("• 総務省統計局「労働力調査 詳細集計」2024年", style={"font_size": "0.75rem", "color": "#333"}),
                                                    rx.link("🔗", href="https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00200531&tstat=000000110001", is_external=True),
                                                    spacing="1",
                                                ),
                                                spacing="1",
                                                align="start",
                                            ),
                                            style={"margin_top": "0.5rem", "padding_top": "0.5rem", "border_top": "1px solid #e0e0e0", "width": "100%"},
                                        ),
                                        spacing="1",
                                        width="100%",
                                    ),
                                    value="university_career",
                                ),
                                type="multiple",
                                collapsible=True,
                                style={"width": "100%"},
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        style={
                            "padding": "1rem",
                            "background": "#f8f9fa",
                            "border_radius": "8px",
                            "border": "1px solid #e0e0e0",
                            "width": "100%",
                            "margin_top": "1rem",
                        },
                    ),
                    
                    # 注釈
                    rx.box(
                        rx.text(
                            "※ すべて政府機関の公式統計データを使用。シミュレーション結果は統計的傾向を示すものであり、個人の人生を予測するものではありません。",
                            style={"font_size": "0.8rem", "color": "#888", "line_height": "1.5"},
                        ),
                        style={
                            "margin_top": "1rem",
                            "padding": "0.75rem 1rem",
                            "background": "#f8f9fa",
                            "border_radius": "8px",
                            "border_left": "3px solid #666",
                            "width": "100%",
                        },
                    ),
                    spacing="2",
                    width="100%",
                ),
            ),
            rx.dialog.close(
                rx.button(
                    "閉じる",
                    style={
                        "margin_top": "1rem",
                        "background": "#D9D9D9",
                        "border": "none",
                        "border_radius": "4px",
                        "padding": "8px 24px",
                        "cursor": "pointer",
                        "_hover": {"background": "#CCCCCC"},
                    },
                ),
            ),
            style={
                "max_width": "900px",
                "max_height": "90vh",
                "overflow_y": "auto",
            },
        ),
    )
