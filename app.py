#!/usr/bin/env python3
"""
人生シミュレーター - Webアプリ版
北海道・東京の公開データに基づいて人生をシミュレーション
"""

import streamlit as st
import pandas as pd
from src import RegionalLifeSimulator, REGION_CONFIG

# 地域別の設定
REGION_DISPLAY = {
    "hokkaido": {"name": "北海道", "icon": "🏔️", "color": "#1f77b4", "data_source": "北海道庁・厚生労働省"},
    "tokyo": {"name": "東京", "icon": "🗼", "color": "#e63946", "data_source": "東京都・厚生労働省"},
}

# 地域ごとのガチャ確率（統計的な分布に基づく推定）
REGION_GACHA_RATES = {
    "hokkaido": {"SS": "0.5%", "S": "3%", "A": "12%", "B": "35%", "C": "35%", "D": "14.5%"},
    "tokyo": {"SS": "2%", "S": "8%", "A": "20%", "B": "40%", "C": "22%", "D": "8%"},
}

# ページ設定
st.set_page_config(
    page_title="人生ガチャ",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# セッション状態の初期化
if 'lives' not in st.session_state:
    st.session_state.lives = []
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = "hokkaido"
if 'show_dataset_dialog' not in st.session_state:
    st.session_state.show_dataset_dialog = False

# カスタムCSS（動的に地域カラーを適用）
def get_custom_css(region_color):
    return f"""
    <style>
    .main-header {{
        font-size: 3rem;
        font-weight: bold;
        color: {region_color};
        text-align: center;
        padding: 1rem 0;
    }}
    .life-story {{
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid {region_color};
    }}
    .life-story p {{
        font-size: 1.1rem;
        line-height: 1.8;
        margin: 0.5rem 0;
    }}
    .dataset-info {{
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }}
    .gacha-btn {{
        width: 100%;
        background-color: {region_color};
        color: white;
        font-size: 1.2rem;
        padding: 0.75rem;
        border-radius: 10px;
    }}
    </style>
    """

# 地域選択
current_region = st.session_state.selected_region
region_info = REGION_DISPLAY[current_region]

# CSSを適用
st.markdown(get_custom_css(region_info["color"]), unsafe_allow_html=True)

# タイトル
st.markdown(f'<div class="main-header">🎰 {region_info["icon"]} {region_info["name"]}人生ガチャ</div>', unsafe_allow_html=True)

# 地域選択トグル
st.markdown("---")

col_toggle1, col_toggle2, col_toggle3 = st.columns([1, 2, 1])
with col_toggle2:
    st.markdown("##### 🗺️ 地域を選択")
    
    # シンプルなボタンを作成
    col_hk, col_tk = st.columns(2)
    
    with col_hk:
        hk_selected = current_region == "hokkaido"
        if st.button("🏔️ 北海道", key="select_hokkaido", use_container_width=True, type="primary" if hk_selected else "secondary"):
            if not hk_selected:
                st.session_state.selected_region = "hokkaido"
                st.session_state.lives = []
                st.cache_resource.clear()
                st.rerun()
    
    with col_tk:
        tk_selected = current_region == "tokyo"
        if st.button("🗼 東京", key="select_tokyo", use_container_width=True, type="primary" if tk_selected else "secondary"):
            if not tk_selected:
                st.session_state.selected_region = "tokyo"
                st.session_state.lives = []
                st.cache_resource.clear()
                st.rerun()
    
    # ガチャ確率を表形式で表示
    st.markdown("##### 🎲 ガチャ確率")
    
    hk_rates = REGION_GACHA_RATES["hokkaido"]
    tk_rates = REGION_GACHA_RATES["tokyo"]
    
    # 表形式のHTML
    st.markdown(f"""
    <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 0.5rem;">
        <thead>
            <tr style="background-color: #f0f2f6;">
                <th style="padding: 8px; border: 1px solid #ddd; text-align: center;">ランク</th>
                <th style="padding: 8px; border: 1px solid #ddd; text-align: center; background: linear-gradient(135deg, #FFD700, #FFA500); color: #333;">SS</th>
                <th style="padding: 8px; border: 1px solid #ddd; text-align: center; background: #C0C0C0; color: #333;">S</th>
                <th style="padding: 8px; border: 1px solid #ddd; text-align: center; background: #CD7F32; color: #fff;">A</th>
                <th style="padding: 8px; border: 1px solid #ddd; text-align: center; background: #4CAF50; color: #fff;">B</th>
                <th style="padding: 8px; border: 1px solid #ddd; text-align: center; background: #FF9800; color: #fff;">C</th>
                <th style="padding: 8px; border: 1px solid #ddd; text-align: center; background: #f44336; color: #fff;">D</th>
            </tr>
        </thead>
        <tbody>
            <tr style="{'background-color: #e6f2ff; font-weight: bold;' if current_region == 'hokkaido' else ''}">
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">🏔️ 北海道</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{hk_rates['SS']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{hk_rates['S']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{hk_rates['A']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{hk_rates['B']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{hk_rates['C']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{hk_rates['D']}</td>
            </tr>
            <tr style="{'background-color: #ffe6e8; font-weight: bold;' if current_region == 'tokyo' else ''}">
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">🗼 東京</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{tk_rates['SS']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{tk_rates['S']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{tk_rates['A']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{tk_rates['B']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{tk_rates['C']}</td>
                <td style="padding: 8px; border: 1px solid #ddd; text-align: center;">{tk_rates['D']}</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)

st.markdown("---")

# 設定エリア（2列）
col_settings1, col_settings2 = st.columns(2)

with col_settings1:
    st.subheader("⚙️ 設定")
    # 生成人数（横幅を狭くするためにcolumns使用）
    col_slider, col_empty = st.columns([2, 1])
    with col_slider:
        num_people = st.slider(
            "生成する人数",
            min_value=1,
            max_value=20,
            value=1,
            help="一度に生成する人生の数を選択してください"
        )

with col_settings2:
    st.subheader("📊 表示オプション")
    show_score = st.checkbox("人生スコアを表示", value=True, help="最終学歴・生涯年収・寿命による人生スコアを表示")
    show_parent_gacha = st.checkbox("親ガチャスコアを表示", value=False, help="親の学歴・世帯年収・出生地による親ガチャスコアを表示")
    verbose_score = st.checkbox("スコアの詳細な根拠を表示", value=False, help="各項目の出典を表示")

# サイドバー（非表示だが互換性のため残す）
with st.sidebar:
    st.header("⚙️ 設定")
    st.info("設定はメイン画面に移動しました")
    if st.button("🔄 データ再読み込み", help="シミュレーターのデータを再読み込みします"):
        st.cache_resource.clear()
        st.session_state.lives = []
        st.rerun()

# シミュレーターの初期化（地域別にキャッシュ）
@st.cache_resource
def load_simulator(region: str):
    return RegionalLifeSimulator(region=region)

simulator = load_simulator(st.session_state.selected_region)

# メインコンテンツ
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button(f"🎰 {region_info['name']}ガチャを引く", use_container_width=True, type="primary"):
        import random
        
        st.session_state.lives = []
        with st.spinner('人生を生成中...'):
            for i in range(num_people):
                life = simulator.generate_life()
                st.session_state.lives.append(life)
    
    # データセット情報ボタン
    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    if st.button("📚 データセット情報を見る", use_container_width=True):
        st.session_state.show_dataset_dialog = True

# データセット情報のダイアログ
@st.dialog(f"📚 使用しているデータセット（{region_info['name']}）", width="large")
def show_dataset_info():
    # データローダーからデータセット情報を取得
    datasets = simulator.data_loader.get_dataset_info()
    
    for dataset in datasets:
        st.markdown(f"""
        <div class="dataset-info">
            <strong>{dataset['name']}</strong> ({dataset['count']})<br>
            📄 正式名称: {dataset['official_name']}<br>
            🏢 提供元: {dataset['source']}<br>
            📅 データ年: {dataset['year']}
        </div>
        """, unsafe_allow_html=True)
        
        # 詳細情報がある場合は展開表示
        if 'details' in dataset and dataset['details']:
            details = dataset['details']
            with st.expander(f"📊 {dataset['name']} の詳細・根拠データ"):
                st.markdown(f"**概要**: {details.get('description', '')}")
                st.markdown(f"**計算方法**: {details.get('methodology', '')}")
                if details.get('formula'):
                    st.code(details['formula'], language=None)
                
                # 補正係数テーブル
                if details.get('coefficients'):
                    st.markdown("**補正係数一覧**:")
                    coef_data = []
                    for key, values in details['coefficients'].items():
                        coef_data.append({
                            "区分": key,
                            "高校進学補正": values.get('high_school_modifier', 1.0),
                            "大学進学補正": values.get('university_modifier', 1.0)
                        })
                    st.dataframe(coef_data, use_container_width=True)
                
                # 参照データ
                if details.get('references'):
                    st.markdown("**参照した研究・統計データ**:")
                    for i, ref in enumerate(details['references'], 1):
                        st.markdown(f"**{i}. {ref['name']}**")
                        st.markdown(f"   - 主な知見: {ref['finding']}")
                        if ref.get('data'):
                            st.json(ref['data'])
                        if ref.get('url'):
                            st.markdown(f"   - URL: {ref['url']}")
                
                # 注意事項
                if details.get('notes'):
                    st.markdown("**注意事項**:")
                    for note in details['notes']:
                        st.markdown(f"- {note}")
                
                # READMEファイルへのリンク
                if dataset.get('readme'):
                    st.info(f"詳細なドキュメントは data/{dataset['readme']} を参照してください。")
    
    st.info(f"すべて{region_info['data_source']}が公開している公式統計データを使用しています。")

# ダイアログ表示
if st.session_state.show_dataset_dialog:
    show_dataset_info()
    st.session_state.show_dataset_dialog = False

# 生成された人生を表示
if st.session_state.lives:
    st.markdown("---")
    
    for i, life in enumerate(st.session_state.lives):
        with st.container():
            st.markdown(f"### 人生 #{i+1}")
            
            # 人生のストーリーを表示（基本情報のみ、スコアとSNS反応は青枠外で個別に表示）
            life_story = simulator.format_life(life, show_score=False, show_sns=False)
            
            # HTMLで整形して表示（改行を<br>に変換）
            story_lines = life_story.split("\n")
            story_html = f"""
            <div class="life-story">
                {"<br>".join(story_lines)}
            </div>
            """
            st.markdown(story_html, unsafe_allow_html=True)
            
            # 親ガチャスコアを表示
            if show_parent_gacha:
                parent_gacha_result = simulator.calculate_parent_gacha_score(life)
                pg_score = int(parent_gacha_result['total_score'])
                pg_rank = parent_gacha_result.get('rank', 'B')
                pg_rank_label = parent_gacha_result.get('rank_label', '普通')
                
                # ランクに応じた色を設定
                rank_colors = {
                    "SS": "#FFD700",  # 金色
                    "S": "#C0C0C0",   # 銀色
                    "A": "#CD7F32",   # 銅色
                    "B": "#4CAF50",   # 緑
                    "C": "#FF9800",   # オレンジ
                    "D": "#f44336",   # 赤
                }
                pg_color = rank_colors.get(pg_rank, "#666")
                
                st.markdown(f"""
                <div style="background-color: #fff3e0; padding: 1rem; border-radius: 10px; margin: 1rem 0; border-left: 5px solid {pg_color};">
                    <h4 style="margin: 0;">🎰 親ガチャスコア: {pg_score}点　<span style="color: {pg_color}; font-weight: bold;">{pg_rank}ランク</span>　{pg_rank_label}</h4>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">親の学歴・世帯年収・出生地の3要素で算定</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 詳細なスコア内訳を表示
                if verbose_score:
                    with st.expander("📈 親ガチャスコア内訳を見る"):
                        breakdown = parent_gacha_result["breakdown"]
                        
                        for key in ["parent_education", "household_income", "birthplace"]:
                            item = breakdown[key]
                            score = item["score"]
                            
                            st.markdown(f"""
                            **{item['label']}**: {score:.1f}点  
                            → {item['value']}  
                            理由: {item['reason']}  
                            出典: {item['source']}
                            """)
                            st.markdown("---")
            
            # 人生スコアを表示
            if show_score:
                score_result = simulator.calculate_life_score(life)
                total_score = int(score_result['total_score'])
                life_rank = score_result.get('rank', 'B')
                life_rank_label = score_result.get('rank_label', '普通')
                
                # ランクに応じた色を設定
                rank_colors = {
                    "SS": "#FFD700",  # 金色
                    "S": "#C0C0C0",   # 銀色
                    "A": "#CD7F32",   # 銅色
                    "B": "#4CAF50",   # 緑
                    "C": "#FF9800",   # オレンジ
                    "D": "#f44336",   # 赤
                }
                life_color = rank_colors.get(life_rank, "#666")
                
                st.markdown(f"""
                <div style="background-color: #e8f4f8; padding: 1rem; border-radius: 10px; margin: 1rem 0; border-left: 5px solid {life_color};">
                    <h4 style="margin: 0;">📊 人生スコア: {total_score}点　<span style="color: {life_color}; font-weight: bold;">{life_rank}ランク</span>　{life_rank_label}</h4>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">最終学歴・生涯年収・寿命の3要素で算定</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 詳細なスコア内訳を表示
                if verbose_score:
                    with st.expander("📈 人生スコア内訳を見る"):
                        breakdown = score_result["breakdown"]
                        
                        for key in ["education", "lifetime_income", "lifespan"]:
                            item = breakdown[key]
                            score = item["score"]
                            
                            st.markdown(f"""
                            **{item['label']}**: {score:.1f}点  
                            → {item['value']}  
                            理由: {item['reason']}  
                            出典: {item['source']}
                            """)
                            st.markdown("---")
            
            # 詳細情報をエクスパンダーで表示
            with st.expander("📋 詳細データを見る"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**👶 出生情報**")
                    st.metric("性別", life.get('gender', '不明'))
                    st.metric("出生地", life['birth_city'])
                    st.metric("世帯年収", life.get('household_income', '不明'))
                    st.metric("父親の職業", life.get('father_industry', '不明'))
                    st.metric("父親の学歴", life.get('father_education', '不明'))
                    st.metric("母親の職業", life.get('mother_industry', '不明'))
                    st.metric("母親の学歴", life.get('mother_education', '不明'))
                
                with col2:
                    st.markdown("**📚 学歴**")
                    st.metric("高校進学", "あり" if life['high_school'] else "なし")
                    if life['high_school'] and life.get('high_school_name'):
                        st.metric("高校名", life['high_school_name'])
                    st.metric("大学進学", "あり" if life['university'] else "なし")
                    if life['university_destination']:
                        st.metric("進学先", life['university_destination'])
                    if life.get('university_name'):
                        st.metric("大学名", life['university_name'])
                
                with col3:
                    st.markdown("**💼 キャリア・最期**")
                    # 企業規模と雇用形態
                    st.metric("企業規模", life.get('company_size', '不明'))
                    st.metric("雇用形態", life.get('employment_type', '不明'))
                    # キャリアサマリーがある場合
                    career_summary = life.get('career_summary', {})
                    if career_summary:
                        st.metric("勤務社数", f"{career_summary.get('total_companies', 1)}社")
                        st.metric("転職回数", f"{career_summary.get('total_job_changes', 0)}回")
                    st.metric("最終産業", life.get('industry', '不明'))
                    retirement_text = f"{life['retirement_age']}歳" if life.get('retirement_age') else "定年なし"
                    st.metric("定年年齢", retirement_text)
                    st.metric("死亡年齢", f"{life['death_age']}歳")
                    st.metric("死因", life['death_cause'])
            
            st.markdown("---")

# フッター
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🎰 {region_info['icon']} {region_info['name']}人生ガチャ | データ提供: {region_info['data_source']}</p>
</div>
""", unsafe_allow_html=True)
