#!/usr/bin/env python3
"""
北海道人生シミュレーター - 拡張版Webアプリ
統計情報とグラフ表示機能付き
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
from hokkaido_life_simulator import HokkaidoLifeSimulator

# ページ設定
st.set_page_config(
    page_title="北海道人生シミュレーター - 拡張版",
    page_icon="🌏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# カスタムCSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .life-story {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .life-story p {
        font-size: 1.1rem;
        line-height: 1.8;
        margin: 0.5rem 0;
    }
    .dataset-info {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.2rem;
        padding: 0.75rem;
        border-radius: 10px;
    }
    .stButton>button:hover {
        background-color: #1557a0;
    }
    </style>
    """, unsafe_allow_html=True)

# タイトル
st.markdown('<div class="main-header">🌏 北海道人生シミュレーター - 拡張版</div>', unsafe_allow_html=True)
st.markdown("---")

# 説明
st.markdown("""
### 📊 このアプリについて

北海道庁が公開している公式統計データを使って、ランダムに人生の軌跡を生成するシミュレーターです。

**拡張版では統計分析とグラフ表示機能が追加されています。**
""")

# サイドバー設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 生成人数
    num_people = st.slider(
        "生成する人数",
        min_value=10,
        max_value=1000,
        value=100,
        step=10,
        help="一度に生成する人生の数を選択してください（拡張版では大量生成に対応）"
    )
    
    # シード値
    use_seed = st.checkbox("再現性のある結果を生成（シード値を使用）")
    if use_seed:
        seed_value = st.number_input(
            "シード値",
            min_value=0,
            max_value=9999,
            value=42,
            help="同じシード値を使用すると、同じ結果が再現されます"
        )
    else:
        seed_value = None
    
    st.markdown("---")
    
    # 表示オプション
    st.subheader("📈 表示オプション")
    show_individual_lives = st.checkbox("個別の人生を表示", value=True)
    show_statistics = st.checkbox("統計分析を表示", value=True)
    show_graphs = st.checkbox("グラフを表示", value=True)
    show_datasets = st.checkbox("データセット情報を表示", value=False)

# セッション状態の初期化
if 'lives' not in st.session_state:
    st.session_state.lives = []
if 'simulator' not in st.session_state:
    st.session_state.simulator = None

# シミュレーターの初期化
@st.cache_resource
def load_simulator():
    return HokkaidoLifeSimulator()

if st.session_state.simulator is None:
    with st.spinner('データを読み込み中...'):
        st.session_state.simulator = load_simulator()

simulator = st.session_state.simulator

# メインコンテンツ
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎲 人生を生成する", use_container_width=True):
        import random
        
        if seed_value is not None:
            random.seed(seed_value)
        
        st.session_state.lives = []
        with st.spinner('人生を生成中...'):
            progress_bar = st.progress(0)
            for i in range(num_people):
                life = simulator.generate_life()
                st.session_state.lives.append(life)
                progress_bar.progress((i + 1) / num_people)
            progress_bar.empty()

# 統計分析を実行
def analyze_lives(lives):
    """生成された人生を分析"""
    if not lives:
        return None
    
    df = pd.DataFrame(lives)
    
    analysis = {
        'total': len(lives),
        'high_school_rate': (df['high_school'].sum() / len(lives)) * 100,
        'university_rate': (df['university'].sum() / len(lives)) * 100,
        'avg_death_age': df['death_age'].mean(),
        'median_death_age': df['death_age'].median(),
        'birth_cities': Counter(df['birth_city']),
        'industries': Counter(df['industry']),
        'death_causes': Counter(df['death_cause']),
        'university_destinations': Counter(df['university_destination'].dropna()),
        'retirement_ages': df['retirement_age'].dropna().tolist(),
        'death_ages': df['death_age'].tolist(),
    }
    
    return analysis

# 生成された人生を表示
if st.session_state.lives:
    analysis = analyze_lives(st.session_state.lives)
    
    # 統計情報を表示
    if show_statistics and analysis:
        st.markdown("---")
        st.header("📊 統計分析")
        
        # 主要指標
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("生成人数", f"{analysis['total']:,}人")
        
        with col2:
            st.metric("高校進学率", f"{analysis['high_school_rate']:.1f}%")
        
        with col3:
            st.metric("大学進学率", f"{analysis['university_rate']:.1f}%")
        
        with col4:
            st.metric("平均寿命", f"{analysis['avg_death_age']:.1f}歳")
    
    # グラフを表示
    if show_graphs and analysis:
        st.markdown("---")
        st.header("📈 データ可視化")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🗺️ 出生地分布", 
            "💼 産業分布", 
            "💀 死因分布",
            "🎓 大学進学先",
            "📊 年齢分布"
        ])
        
        with tab1:
            # 出生地分布（上位20都市）
            top_cities = dict(analysis['birth_cities'].most_common(20))
            fig = px.bar(
                x=list(top_cities.keys()),
                y=list(top_cities.values()),
                title="出生地分布（上位20都市）",
                labels={'x': '市町村', 'y': '人数'},
                color=list(top_cities.values()),
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # 産業分布
            industries = dict(analysis['industries'])
            fig = px.pie(
                values=list(industries.values()),
                names=list(industries.keys()),
                title="就職先産業の割合"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # 死因分布
            death_causes = dict(analysis['death_causes'])
            fig = px.bar(
                x=list(death_causes.keys()),
                y=list(death_causes.values()),
                title="死因の分布",
                labels={'x': '死因', 'y': '人数'},
                color=list(death_causes.values()),
                color_continuous_scale='Reds'
            )
            fig.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            # 大学進学先分布
            if analysis['university_destinations']:
                destinations = dict(analysis['university_destinations'].most_common(15))
                fig = px.bar(
                    x=list(destinations.keys()),
                    y=list(destinations.values()),
                    title="大学進学先都道府県（上位15）",
                    labels={'x': '都道府県', 'y': '人数'},
                    color=list(destinations.values()),
                    color_continuous_scale='Greens'
                )
                fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("大学進学者がいません")
        
        with tab5:
            # 年齢分布
            col1, col2 = st.columns(2)
            
            with col1:
                # 死亡年齢のヒストグラム
                fig = px.histogram(
                    x=analysis['death_ages'],
                    title="死亡年齢の分布",
                    labels={'x': '年齢', 'y': '人数'},
                    nbins=30,
                    color_discrete_sequence=['#1f77b4']
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # 定年年齢のヒストグラム
                if analysis['retirement_ages']:
                    fig = px.histogram(
                        x=analysis['retirement_ages'],
                        title="定年年齢の分布",
                        labels={'x': '年齢', 'y': '人数'},
                        nbins=20,
                        color_discrete_sequence=['#ff7f0e']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("定年データがありません")
    
    # 個別の人生を表示
    if show_individual_lives:
        st.markdown("---")
        st.header("✨ 生成された人生")
        
        # 表示件数を制限
        display_count = min(20, len(st.session_state.lives))
        
        if len(st.session_state.lives) > 20:
            st.info(f"💡 {len(st.session_state.lives)}人中、最初の{display_count}人を表示しています")
        
        for i, life in enumerate(st.session_state.lives[:display_count]):
            with st.container():
                st.markdown(f"### 人生 #{i+1}")
                
                # 人生のストーリーを表示
                life_story = simulator.format_life(life)
                
                # HTMLで整形して表示（改行を<br>に変換）
                story_lines = life_story.split("\n")
                story_html = f"""
                <div class="life-story">
                    {"<br>".join(story_lines)}
                </div>
                """
                st.markdown(story_html, unsafe_allow_html=True)
                
                # 詳細情報をエクスパンダーで表示
                with st.expander("📋 詳細データを見る"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("出生地", life['birth_city'])
                        st.metric("高校進学", "あり" if life['high_school'] else "なし")
                        st.metric("大学進学", "あり" if life['university'] else "なし")
                        if life['university_destination']:
                            st.metric("進学先", life['university_destination'])
                    
                    with col2:
                        st.metric("就職先産業", life['industry'])
                        retirement_text = f"{life['retirement_age']}歳" if life['retirement_age'] else "定年なし"
                        st.metric("定年年齢", retirement_text)
                        st.metric("死亡年齢", f"{life['death_age']}歳")
                        st.metric("死因", life['death_cause'])
                
                st.markdown("---")

# データセット情報を表示
if show_datasets:
    st.markdown("---")
    st.header("📚 使用しているデータセット")
    
    datasets = [
        {
            "name": "1. 市町村別出生数",
            "official_name": "市区町村別人口、人口動態及び世帯数（令和6年）",
            "source": "北海道総合政策部地域行政局市町村課",
            "year": "2024年",
            "count": f"{len(simulator.birth_data)}市町村"
        },
        {
            "name": "2. 市町村別高校進学率",
            "official_name": "学校基本調査 中学校卒業後の進路別卒業者数（令和6年度）",
            "source": "北海道教育委員会",
            "year": "2024年度",
            "count": f"{len(simulator.high_school_rates)}市町村"
        },
        {
            "name": "3. 市町村別大学進学率",
            "official_name": "学校基本調査 高等学校卒業後の進路別卒業者数（令和6年度）",
            "source": "北海道教育委員会",
            "year": "2024年度",
            "count": f"{len(simulator.university_rates)}市町村"
        },
        {
            "name": "4. 大学進学先都道府県",
            "official_name": "学校基本調査 大学・短期大学への都道府県別入学者数（令和6年度）",
            "source": "北海道教育委員会",
            "year": "2024年度",
            "count": f"{len(simulator.university_destinations)}都道府県"
        },
        {
            "name": "5. 産業別労働者数",
            "official_name": "労働力調査 第2表 産業別就業者数・雇用者数（令和6年平均）",
            "source": "北海道総合政策部計画局統計課",
            "year": "2024年",
            "count": f"{len(simulator.workers_by_industry)}産業"
        },
        {
            "name": "6. 定年年齢分布",
            "official_name": "就労条件総合調査結果の概況（令和4年）",
            "source": "厚生労働省",
            "year": "2022年",
            "count": f"{len(simulator.retirement_age_distribution)}区分"
        },
        {
            "name": "7. 年齢別死亡者数",
            "official_name": "北海道保健統計年報 第24表 死亡数（令和4年）",
            "source": "北海道保健福祉部総務課",
            "year": "2022年",
            "count": f"{len(simulator.death_by_age)}年齢"
        },
        {
            "name": "8. 死因別死亡者数",
            "official_name": "北海道保健統計年報 表3 死亡数・死亡率（令和4年）",
            "source": "北海道保健福祉部総務課",
            "year": "2022年",
            "count": f"{len(simulator.death_by_cause)}種類"
        }
    ]
    
    for dataset in datasets:
        st.markdown(f"""
        <div class="dataset-info">
            <strong>{dataset['name']}</strong> ({dataset['count']})<br>
            📄 正式名称: {dataset['official_name']}<br>
            🏢 提供元: {dataset['source']}<br>
            📅 データ年: {dataset['year']}
        </div>
        """, unsafe_allow_html=True)
    
    st.info("すべて北海道庁が公開している公式統計データを使用しています。")

# フッター
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🌟 北海道人生シミュレーター - 拡張版 | データ提供: 北海道庁</p>
</div>
""", unsafe_allow_html=True)

