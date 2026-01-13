#!/usr/bin/env python3
"""
北海道人生シミュレーター - Webアプリ版
"""

import streamlit as st
import pandas as pd
from src import HokkaidoLifeSimulator
from career_simulation import CareerSimulator

# ページ設定
st.set_page_config(
    page_title="北海道人生シミュレーター",
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
st.markdown('<div class="main-header">🌏 北海道人生シミュレーター</div>', unsafe_allow_html=True)
st.markdown("---")

# 説明
st.markdown("""
### 📊 このアプリについて

北海道庁が公開している公式統計データを使って、ランダムに人生の軌跡を生成するシミュレーターです。

出生地、進学、就職、退職、そして死亡まで、統計データに基づいたリアルな人生を体験できます。
""")

# サイドバー設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    # 生成人数
    num_people = st.slider(
        "生成する人数",
        min_value=1,
        max_value=20,
        value=1,
        help="一度に生成する人生の数を選択してください"
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
    st.subheader("📊 表示オプション")
    show_score = st.checkbox("人生スコアを表示", value=True, help="東京基準100点の人生スコアを表示")
    verbose_score = st.checkbox("スコアの詳細な根拠を表示", value=False, help="各項目の出典を表示")
    show_sns = st.checkbox("SNS反応を表示", value=True, help="予想されるSNS上の反応を表示")
    
    st.markdown("---")
    
    # データセット情報の表示
    show_datasets = st.checkbox("データセット情報を表示", value=False)

# セッション状態の初期化
if 'lives' not in st.session_state:
    st.session_state.lives = []

# シミュレーターの初期化（キャッシュをクリアして新しいインスタンスを使用）
# 起動時に一度キャッシュをクリア
if 'simulator_initialized' not in st.session_state:
    st.cache_resource.clear()
    st.session_state.simulator_initialized = True

@st.cache_resource
def load_simulator():
    return HokkaidoLifeSimulator()

# キャッシュクリア機能
with st.sidebar:
    if st.button("🔄 データ再読み込み", help="シミュレーターのデータを再読み込みします"):
        st.cache_resource.clear()
        st.session_state.simulator_initialized = False
        st.rerun()

simulator = load_simulator()

# メインコンテンツ
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🎲 人生を生成する", use_container_width=True):
        import random
        
        if seed_value is not None:
            random.seed(seed_value)
        
        st.session_state.lives = []
        with st.spinner('人生を生成中...'):
            for i in range(num_people):
                life = simulator.generate_life()
                st.session_state.lives.append(life)

# 生成された人生を表示
if st.session_state.lives:
    st.markdown("---")
    st.header("✨ 生成された人生")
    
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
            
            # スコアを表示
            if show_score:
                score_result = simulator.calculate_life_score(life)
                total_score = score_result['total_score']
                
                # スコアの解釈（掛け算方式用）
                if total_score >= 75:
                    interpretation = "非常に恵まれた人生（上位5%相当）"
                    score_color = "🟢"
                elif total_score >= 60:
                    interpretation = "平均以上の充実した人生"
                    score_color = "🔵"
                elif total_score >= 45:
                    interpretation = "平均的な人生"
                    score_color = "🟡"
                elif total_score >= 30:
                    interpretation = "やや困難の多い人生"
                    score_color = "🟠"
                elif total_score >= 15:
                    interpretation = "多くの困難に直面した人生"
                    score_color = "🔴"
                else:
                    interpretation = "極めて厳しい人生"
                    score_color = "⚫"
                
                st.markdown(f"""
                <div style="background-color: #e8f4f8; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                    <h4 style="margin: 0;">📊 人生スコア: {score_color} {total_score:.1f} / 100点</h4>
                    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; color: #666;">
                        ※ 東京で生まれ育ち最大限に充実した人生を100点として算出<br>
                        【評価】{interpretation}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # 詳細なスコア内訳を表示
                if verbose_score:
                    with st.expander("📈 スコア内訳を見る"):
                        breakdown = score_result["breakdown"]
                        weights = score_result["weights"]
                        
                        for key in ["location", "gender", "education", "university_dest", "industry", "lifespan", "death_cause"]:
                            item = breakdown[key]
                            weight = weights[key]
                            weighted_score = item["score"] * weight
                            
                            st.markdown(f"""
                            **{item['label']}**: {item['score']}点 × {weight*100:.0f}% = {weighted_score:.1f}点  
                            → {item['value']}  
                            理由: {item['reason']}  
                            出典: {item['source']}
                            """)
                            st.markdown("---")
            
            # SNS反応を表示
            if show_sns:
                score_result = simulator.calculate_life_score(life) if not show_score else score_result
                sns_reactions = simulator.generate_sns_reactions(life, score_result)
                
                st.markdown("""
                <div style="background-color: #f5f5f5; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                    <h4 style="margin: 0 0 0.5rem 0;">💬 SNSでの予想される反応</h4>
                </div>
                """, unsafe_allow_html=True)
                
                for reaction in sns_reactions:
                    st.markdown(f"""
                    <div style="background-color: white; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #1f77b4;">
                        💬 {reaction}
                    </div>
                    """, unsafe_allow_html=True)
            
            # 詳細情報をエクスパンダーで表示
            with st.expander("📋 詳細データを見る"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**👶 出生情報**")
                    st.metric("性別", life.get('gender', '不明'))
                    st.metric("出生地", life['birth_city'])
                    st.metric("父親の職業", life.get('father_industry', '不明'))
                    st.metric("母親の職業", life.get('mother_industry', '不明'))
                
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
            "name": "6. 性別別労働者数",
            "official_name": "労働力調査（令和6年平均）",
            "source": "北海道総合政策部計画局統計課",
            "year": "2024年",
            "count": f"{len(simulator.workers_by_gender)}区分"
        },
        {
            "name": "7. 性別×産業別労働者数",
            "official_name": "労働力調査（令和6年平均）+ 全国傾向から推定",
            "source": "北海道総合政策部計画局統計課 / 総務省統計局",
            "year": "2024年",
            "count": f"{len(simulator.workers_by_industry_gender)}産業"
        },
        {
            "name": "8. 定年年齢分布",
            "official_name": "就労条件総合調査結果の概況（令和4年）",
            "source": "厚生労働省",
            "year": "2022年",
            "count": f"{len(simulator.retirement_age_distribution)}区分"
        },
        {
            "name": "9. 年齢別死亡者数",
            "official_name": "北海道保健統計年報 第24表 死亡数（令和4年）",
            "source": "北海道保健福祉部総務課",
            "year": "2022年",
            "count": f"{len(simulator.death_by_age)}年齢"
        },
        {
            "name": "10. 死因別死亡者数",
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

# キャリアシミュレーション機能
st.markdown("---")
st.header("💼 キャリアシミュレーション")
st.markdown("""
大卒（22歳就業開始）から定年（60歳）までの間に、転職・離職・再就職がどのように発生するかをシミュレーションします。

厚生労働省「令和6年雇用動向調査」のデータに基づいています。
""")

# キャリアシミュレーターの初期化
@st.cache_resource
def load_career_simulator():
    return CareerSimulator()

career_simulator = load_career_simulator()

# キャリアシミュレーション設定
col1, col2 = st.columns(2)

with col1:
    career_gender = st.selectbox(
        "性別を選択",
        ["男性", "女性"],
        help="男女で転職・離職率が異なります"
    )

with col2:
    career_count = st.slider(
        "シミュレーション回数",
        min_value=1,
        max_value=5,
        value=3,
        help="同性別で複数パターンを生成"
    )

# 転職率データを表示
with st.expander("📊 使用データ（年齢別転職入職率・離職率）"):
    rate_data = []
    for data in career_simulator.job_mobility_data:
        rate_data.append({
            "年齢階級": f"{data['age_min']}-{data['age_max']}歳",
            "男性_転職率": f"{data['male_job_change_rate']:.1f}%",
            "男性_離職率": f"{data['male_separation_rate']:.1f}%",
            "女性_転職率": f"{data['female_job_change_rate']:.1f}%",
            "女性_離職率": f"{data['female_separation_rate']:.1f}%",
        })
    st.dataframe(pd.DataFrame(rate_data), use_container_width=True)
    st.caption("出典: 厚生労働省「令和6年雇用動向調査」")

# セッション状態でキャリア結果を保持
if 'career_results' not in st.session_state:
    st.session_state.career_results = []

if st.button("🎲 キャリアをシミュレーション", use_container_width=True):
    st.session_state.career_results = []
    for i in range(career_count):
        result = career_simulator.simulate_career(career_gender, start_age=22, retirement_age=60)
        st.session_state.career_results.append(result)

# キャリアシミュレーション結果を表示
if st.session_state.career_results:
    st.markdown("### 📋 シミュレーション結果")
    
    for i, result in enumerate(st.session_state.career_results):
        with st.container():
            st.markdown(f"#### シミュレーション #{i+1} ({result['gender']})")
            
            # サマリー
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("転職回数", f"{result['total_job_changes']}回")
            with col2:
                st.metric("離職回数", f"{result['total_separations']}回")
            with col3:
                st.metric("勤務社数", f"{result['total_companies']}社")
            with col4:
                st.metric("無職期間", f"{result['total_unemployment_years']}年")
            
            # イベント履歴
            if result['events']:
                st.markdown("**キャリア履歴:**")
                events_html = "<div style='background-color: #f0f2f6; padding: 1rem; border-radius: 10px;'>"
                for event in result['events']:
                    if event['type'] == "転職":
                        icon = "🔄"
                        text = f"{event['age']}歳で転職（{event['company_number']}社目へ）"
                    elif event['type'] == "離職":
                        icon = "📤"
                        text = f"{event['age']}歳で離職（退職）"
                    elif event['type'] == "再就職":
                        icon = "📥"
                        text = f"{event['age']}歳で再就職（{event['company_number']}社目、無職期間{event['unemployment_duration']}年）"
                    else:
                        icon = "•"
                        text = event.get('description', '')
                    events_html += f"<p style='margin: 0.3rem 0;'>{icon} {text}</p>"
                events_html += "</div>"
                st.markdown(events_html, unsafe_allow_html=True)
            else:
                st.info("🏢 同一企業で定年まで勤務（終身雇用パターン）")
            
            # 定年時の状態
            status_color = "🟢" if result['final_status'] == "就業中" else "🔴"
            st.markdown(f"**定年時の状態:** {status_color} {result['final_status']}")
            
            st.markdown("---")
    
    # 統計的な補足
    st.markdown("### 💡 シミュレーションのロジック")
    st.markdown("""
    **就業中の場合（毎年）:**
    1. 転職入職率の確率 → 🔄 転職（別の会社へ直接移動）
    2. (離職率 - 転職率)の確率 → 📤 離職（無職になる）
    3. それ以外 → 現職継続
    
    **無職の場合（毎年）:**
    1. 再就職率の確率 → 📥 再就職
    2. それ以外 → 無職継続
    
    **特徴:**
    - 女性は離職率が高く、特に30代で顕著（結婚・出産・育児）
    - 女性50代は再就職率が高い（子育て後の復帰）
    - 男性は相対的に離職せず転職する傾向
    """)

# フッター
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🌟 北海道人生シミュレーター | データ提供: 北海道庁・厚生労働省</p>
</div>
""", unsafe_allow_html=True)

