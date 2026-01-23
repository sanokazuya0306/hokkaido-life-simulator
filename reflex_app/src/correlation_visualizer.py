"""
統計相関関係可視化モジュール

人生シミュレーターで使用されている統計データ間の因果関係を
Sankey図で可視化する
"""

import plotly.graph_objects as go
from typing import Dict, List, Any


# ノード定義（各要素）
# layer: "input"（入力/親ガチャ要素）, "middle"（中間計算）, "output"（最終出力）
CORRELATION_NODES = [
    # === 入力層（親ガチャ要素）===
    {
        "id": 0,
        "name": "出生地",
        "layer": "input",
        "description": "市区町村別の出生数データに基づいて決定",
        "source": "北海道庁・東京都「人口動態統計」",
        "effect": "世帯年収・高校選択・地域補正に影響",
    },
    {
        "id": 1,
        "name": "世帯年収",
        "layer": "input",
        "description": "出生地の世帯年収分布から決定（児童世帯向け補正済み）",
        "source": "総務省「住宅・土地統計調査」",
        "effect": "個人偏差値・高校/大学進学率に影響",
    },
    {
        "id": 2,
        "name": "父親の学歴",
        "layer": "input",
        "description": "性別別の最終学歴分布から決定",
        "source": "総務省「国勢調査」2020年",
        "effect": "個人偏差値・高校/大学進学率に影響",
    },
    {
        "id": 3,
        "name": "母親の学歴",
        "layer": "input",
        "description": "性別別の最終学歴分布から決定",
        "source": "総務省「国勢調査」2020年",
        "effect": "個人偏差値・高校/大学進学率に影響",
    },
    {
        "id": 4,
        "name": "性別",
        "layer": "input",
        "description": "労働者数の男女比に基づいて決定",
        "source": "総務省「労働力調査」",
        "effect": "雇用形態・生涯年収・寿命に影響",
    },
    
    # === 中間層（計算要素）===
    {
        "id": 5,
        "name": "個人偏差値",
        "layer": "middle",
        "description": "環境要因から算出される学力指標（平均50、標準偏差8）",
        "source": "文部科学省「全国学力調査」相関研究",
        "effect": "高校選択・大学選択に影響",
    },
    {
        "id": 6,
        "name": "高校進学",
        "layer": "middle",
        "description": "市区町村別進学率×親学歴補正×世帯年収補正",
        "source": "文部科学省「学校基本調査」",
        "effect": "高校偏差値・大学進学可否に影響",
    },
    {
        "id": 7,
        "name": "高校偏差値",
        "layer": "middle",
        "description": "個人偏差値に基づいて近接高校から選択",
        "source": "各種高校偏差値データ",
        "effect": "卒業時偏差値に影響",
    },
    {
        "id": 8,
        "name": "大学進学",
        "layer": "middle",
        "description": "市区町村別進学率×親学歴補正×世帯年収補正",
        "source": "文部科学省「学校基本調査」",
        "effect": "大学ランク・最終学歴に影響",
    },
    {
        "id": 9,
        "name": "大学ランク",
        "layer": "middle",
        "description": "卒業時偏差値に基づいてS/A/B/C/Dランクを決定",
        "source": "各種大学偏差値データ",
        "effect": "最終学歴スコア・企業規模・生涯年収に影響",
    },
    {
        "id": 10,
        "name": "企業規模",
        "layer": "middle",
        "description": "最終学歴と大学ランクに基づいて大/中/小企業を決定",
        "source": "文部科学省「学校基本調査」就職先統計",
        "effect": "生涯年収に影響（大企業1.0、中0.82、小0.72倍）",
    },
    {
        "id": 11,
        "name": "雇用形態",
        "layer": "middle",
        "description": "最終学歴と性別に基づいて正社員/非正規を決定",
        "source": "総務省「労働力調査」",
        "effect": "生涯年収に影響（正社員1.0、非正規0.65倍）",
    },
    {
        "id": 12,
        "name": "産業",
        "layer": "middle",
        "description": "性別に基づいて産業別労働者分布から選択",
        "source": "総務省「労働力調査」",
        "effect": "生涯年収に影響（産業別賃金格差）",
    },
    
    # === 出力層（最終スコア）===
    {
        "id": 13,
        "name": "最終学歴",
        "layer": "output",
        "description": "中卒/高卒/短大専門/大卒/大学院卒（人生スコアの30%）",
        "source": "総務省「国勢調査」パーセンタイル",
        "effect": "人生スコアに30%寄与",
    },
    {
        "id": 14,
        "name": "生涯年収",
        "layer": "output",
        "description": "学歴×性別×企業規模×雇用形態×産業×大学ランク（人生スコアの40%）",
        "source": "労働政策研究・研修機構「ユースフル労働統計」",
        "effect": "人生スコアに40%寄与",
    },
    {
        "id": 15,
        "name": "寿命",
        "layer": "output",
        "description": "年齢別死亡率に基づいて決定（人生スコアの30%）",
        "source": "厚生労働省「簡易生命表」",
        "effect": "人生スコアに30%寄与",
    },
]

# リンク定義（因果関係）
# source/target: ノードのid
# value: 影響の強さ（表示の太さ）
# label: ホバー時に表示される説明
CORRELATION_LINKS = [
    # 出生地からの影響
    {"source": 0, "target": 1, "value": 3, "label": "市区町村別年収分布を参照"},
    {"source": 0, "target": 6, "value": 2, "label": "市区町村別進学率（基準値）"},
    {"source": 0, "target": 7, "value": 2, "label": "近接高校から選択"},
    {"source": 0, "target": 5, "value": 1, "label": "地域補正（東京+2、北海道-1）"},
    
    # 世帯年収からの影響
    {"source": 1, "target": 5, "value": 2, "label": "年収補正（-4〜+5）"},
    {"source": 1, "target": 6, "value": 2, "label": "高校進学率補正"},
    {"source": 1, "target": 8, "value": 2, "label": "大学進学率補正"},
    
    # 父親学歴からの影響
    {"source": 2, "target": 5, "value": 2, "label": "学歴補正（-5〜+8）"},
    {"source": 2, "target": 6, "value": 2, "label": "高校進学率補正"},
    {"source": 2, "target": 8, "value": 2, "label": "大学進学率補正"},
    
    # 母親学歴からの影響
    {"source": 3, "target": 5, "value": 2, "label": "学歴補正（-5〜+8）"},
    {"source": 3, "target": 6, "value": 2, "label": "高校進学率補正"},
    {"source": 3, "target": 8, "value": 2, "label": "大学進学率補正"},
    
    # 性別からの影響
    {"source": 4, "target": 11, "value": 2, "label": "性別別正社員率"},
    {"source": 4, "target": 12, "value": 2, "label": "性別別産業分布"},
    {"source": 4, "target": 14, "value": 2, "label": "性別賃金格差（女性0.76倍）"},
    {"source": 4, "target": 15, "value": 2, "label": "性別平均寿命（男81歳、女87歳）"},
    
    # 個人偏差値からの影響
    {"source": 5, "target": 7, "value": 3, "label": "偏差値±7範囲の高校を選択"},
    {"source": 5, "target": 9, "value": 3, "label": "卒業時偏差値→大学ランク"},
    
    # 高校進学からの影響
    {"source": 6, "target": 7, "value": 3, "label": "進学した場合のみ高校選択"},
    {"source": 6, "target": 8, "value": 3, "label": "高卒のみ大学進学可能"},
    {"source": 6, "target": 13, "value": 2, "label": "非進学→中卒"},
    
    # 高校偏差値からの影響
    {"source": 7, "target": 5, "value": 2, "label": "高校環境による学力成長"},
    
    # 大学進学からの影響
    {"source": 8, "target": 9, "value": 3, "label": "進学した場合のみ大学選択"},
    {"source": 8, "target": 13, "value": 3, "label": "進学→大卒/院卒"},
    
    # 大学ランクからの影響
    {"source": 9, "target": 10, "value": 2, "label": "Sランク→大企業+20%"},
    {"source": 9, "target": 13, "value": 2, "label": "ランク別学歴スコア"},
    {"source": 9, "target": 14, "value": 2, "label": "Sランク→年収+15%"},
    
    # 企業規模からの影響
    {"source": 10, "target": 14, "value": 2, "label": "大1.0/中0.82/小0.72倍"},
    
    # 雇用形態からの影響
    {"source": 11, "target": 14, "value": 2, "label": "正社員1.0/非正規0.65倍"},
    
    # 産業からの影響
    {"source": 12, "target": 14, "value": 2, "label": "産業別賃金補正（0.7〜1.3倍）"},
    
    # 最終学歴からの影響
    {"source": 13, "target": 10, "value": 2, "label": "学歴別企業規模分布"},
    {"source": 13, "target": 11, "value": 2, "label": "学歴別正社員率"},
    {"source": 13, "target": 14, "value": 3, "label": "基準生涯年収（1.6〜3.2億円）"},
]


def get_layer_color(layer: str) -> str:
    """レイヤー別の色を取得"""
    colors = {
        "input": "rgba(31, 119, 180, 0.8)",    # 青（入力層）
        "middle": "rgba(255, 127, 14, 0.8)",   # オレンジ（中間層）
        "output": "rgba(44, 160, 44, 0.8)",    # 緑（出力層）
    }
    return colors.get(layer, "rgba(128, 128, 128, 0.8)")


def get_link_color(source_layer: str, target_layer: str) -> str:
    """リンクの色を取得（ソースレイヤーに基づく）"""
    colors = {
        "input": "rgba(31, 119, 180, 0.3)",
        "middle": "rgba(255, 127, 14, 0.3)",
        "output": "rgba(44, 160, 44, 0.3)",
    }
    return colors.get(source_layer, "rgba(128, 128, 128, 0.3)")


def create_correlation_sankey() -> go.Figure:
    """
    統計相関関係のSankey図を生成
    
    Returns:
        Plotly Figure オブジェクト
    """
    # ノードのラベルと色を準備
    node_labels = [node["name"] for node in CORRELATION_NODES]
    node_colors = [get_layer_color(node["layer"]) for node in CORRELATION_NODES]
    
    # ノードのカスタムデータ（ホバー用）
    node_customdata = [
        f"<b>{node['name']}</b><br>"
        f"<br>{node['description']}<br>"
        f"<br>📊 出典: {node['source']}<br>"
        f"<br>➡️ {node['effect']}"
        for node in CORRELATION_NODES
    ]
    
    # リンクのソース、ターゲット、値を準備
    link_sources = [link["source"] for link in CORRELATION_LINKS]
    link_targets = [link["target"] for link in CORRELATION_LINKS]
    link_values = [link["value"] for link in CORRELATION_LINKS]
    link_labels = [link["label"] for link in CORRELATION_LINKS]
    
    # リンクの色（ソースノードのレイヤーに基づく）
    link_colors = []
    for link in CORRELATION_LINKS:
        source_node = CORRELATION_NODES[link["source"]]
        target_node = CORRELATION_NODES[link["target"]]
        link_colors.append(get_link_color(source_node["layer"], target_node["layer"]))
    
    # Sankey図を作成
    fig = go.Figure(data=[go.Sankey(
        arrangement="snap",
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors,
            customdata=node_customdata,
            hovertemplate="%{customdata}<extra></extra>",
        ),
        link=dict(
            source=link_sources,
            target=link_targets,
            value=link_values,
            label=link_labels,
            color=link_colors,
            hovertemplate="<b>%{label}</b><extra></extra>",
        ),
    )])
    
    # レイアウト設定
    fig.update_layout(
        title=dict(
            text="📊 人生シミュレーター 統計データ相関図",
            font=dict(size=20),
            x=0.5,
            xanchor="center",
        ),
        font=dict(size=12, family="Arial, sans-serif"),
        height=700,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    
    # 凡例用のアノテーション
    fig.add_annotation(
        x=0.0, y=-0.08,
        xref="paper", yref="paper",
        text="🔵 入力層（親ガチャ要素）",
        showarrow=False,
        font=dict(size=11, color="rgba(31, 119, 180, 1)"),
        xanchor="left",
    )
    fig.add_annotation(
        x=0.35, y=-0.08,
        xref="paper", yref="paper",
        text="🟠 中間層（計算要素）",
        showarrow=False,
        font=dict(size=11, color="rgba(255, 127, 14, 1)"),
        xanchor="left",
    )
    fig.add_annotation(
        x=0.65, y=-0.08,
        xref="paper", yref="paper",
        text="🟢 出力層（人生スコア）",
        showarrow=False,
        font=dict(size=11, color="rgba(44, 160, 44, 1)"),
        xanchor="left",
    )
    
    return fig


def get_correlation_summary() -> Dict[str, Any]:
    """
    相関関係のサマリー情報を取得
    
    Returns:
        サマリー情報の辞書
    """
    input_nodes = [n for n in CORRELATION_NODES if n["layer"] == "input"]
    middle_nodes = [n for n in CORRELATION_NODES if n["layer"] == "middle"]
    output_nodes = [n for n in CORRELATION_NODES if n["layer"] == "output"]
    
    return {
        "total_nodes": len(CORRELATION_NODES),
        "total_links": len(CORRELATION_LINKS),
        "input_count": len(input_nodes),
        "middle_count": len(middle_nodes),
        "output_count": len(output_nodes),
        "input_nodes": [n["name"] for n in input_nodes],
        "middle_nodes": [n["name"] for n in middle_nodes],
        "output_nodes": [n["name"] for n in output_nodes],
    }


def get_node_details(node_name: str) -> Dict[str, Any]:
    """
    特定ノードの詳細情報を取得
    
    Args:
        node_name: ノード名
        
    Returns:
        ノードの詳細情報（見つからない場合はNone）
    """
    for node in CORRELATION_NODES:
        if node["name"] == node_name:
            # このノードに接続するリンクを取得
            incoming_links = [
                CORRELATION_NODES[link["source"]]["name"]
                for link in CORRELATION_LINKS
                if link["target"] == node["id"]
            ]
            outgoing_links = [
                CORRELATION_NODES[link["target"]]["name"]
                for link in CORRELATION_LINKS
                if link["source"] == node["id"]
            ]
            
            return {
                **node,
                "incoming": incoming_links,
                "outgoing": outgoing_links,
            }
    return None
