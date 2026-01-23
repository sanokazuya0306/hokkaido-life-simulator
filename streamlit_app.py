"""
人生ガチャ Streamlit版

Reflex版からの移植: 既存のcore/とsrc/のロジックを再利用
"""

import streamlit as st
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加（Streamlit Cloud対応）
_project_root = Path(__file__).parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# 環境変数でも設定（念のため）
os.environ['PYTHONPATH'] = str(_project_root) + os.pathsep + os.environ.get('PYTHONPATH', '')

from core import GachaService, get_gacha_service
from src.correlation_visualizer import create_correlation_sankey, get_correlation_summary

# ============================================
# ページ設定
# ============================================
st.set_page_config(
    page_title="人生ガチャ",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# カスタムCSS
# ============================================
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;700&family=Zen+Old+Mincho:wght@400;700&family=Roboto:wght@400;600;700&display=swap');
    
    /* 全体スタイル */
    .stApp {
        background-color: #FFFFFF;
        font-family: 'Zen Kaku Gothic New', sans-serif;
    }
    
    /* ヘッダー非表示 */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    /* メインコンテンツ */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1280px;
    }
    
    /* ガチャボタンスタイル */
    .gacha-button {
        background-color: #D9D9D9;
        border: 5px solid #575757;
        border-radius: 100px;
        padding: 40px 80px;
        font-size: 36px;
        font-weight: 700;
        color: #323232;
        cursor: pointer;
        transition: all 0.2s;
        font-family: 'Zen Kaku Gothic New', sans-serif;
    }
    .gacha-button:hover {
        background-color: #CCCCCC;
        transform: scale(1.02);
    }
    
    /* 地域セレクタボタン */
    .region-button {
        height: 87px;
        font-size: 24px;
        font-weight: 400;
        font-family: 'Zen Kaku Gothic New', sans-serif;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
    }
    .region-button.active {
        background: rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.2);
    }
    .region-button.inactive {
        background: #D9D9D9;
        border: 5px solid rgba(0, 0, 0, 0.2);
    }
    
    /* ランクカードスタイル */
    .rank-card {
        width: 111px;
        height: 148px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Roboto', sans-serif;
        font-weight: 600;
        font-size: 48px;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
        margin: 8px;
    }
    .rank-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    }
    .rank-card-ss {
        background: linear-gradient(135deg, #080808 0%, #6E6E6E 100%);
        color: #D8D8D8;
    }
    .rank-card-s {
        background: linear-gradient(135deg, #292929 0%, #8F8F8F 100%);
        color: #000000;
    }
    .rank-card-normal {
        background: #D9D9D9;
        color: #000000;
    }
    
    /* 詳細カード */
    .detail-card {
        background: #D9D9D9;
        border-radius: 48px;
        padding: 68px 50px 40px 50px;
        max-width: 1040px;
        min-height: 720px;
        margin: 0 auto;
    }
    
    /* 人生ランク表示 */
    .rank-display {
        width: 360px;
        height: 128px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin: 20px auto;
    }
    .rank-display-ss {
        background: linear-gradient(135deg, #080808 0%, #6E6E6E 100%);
    }
    .rank-display-s {
        background: linear-gradient(135deg, #292929 0%, #8F8F8F 100%);
    }
    .rank-display-other {
        background: #C0C0C0;
    }
    
    /* 人生ストーリーテキスト */
    .life-story {
        font-family: 'Zen Old Mincho', serif;
        font-weight: 700;
        font-size: 24px;
        line-height: 2em;
        color: #323232;
        text-align: center;
        white-space: pre-wrap;
        max-width: 720px;
        margin: 0 auto;
    }
    
    /* カウンター */
    .counter {
        position: fixed;
        bottom: 20px;
        right: 40px;
        font-family: 'Roboto', sans-serif;
        font-weight: 600;
        font-size: 20px;
        color: #000000;
    }
    
    /* 情報ボタン */
    .info-button {
        background: #D9D9D9;
        border: none;
        padding: 8px 16px;
        font-size: 12px;
        cursor: pointer;
        transition: background 0.2s;
    }
    .info-button:hover {
        background: #CCCCCC;
    }
    
    /* スコアカード */
    .score-card {
        padding: 16px;
        background: rgba(255,255,255,0.5);
        border-radius: 8px;
        margin: 8px;
    }
    
    /* ダイアログスタイル */
    .rate-item {
        padding: 12px 16px;
        margin: 8px 0;
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    /* Streamlitのデフォルトスタイルを上書き */
    .stButton > button {
        font-family: 'Zen Kaku Gothic New', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# セッション状態の初期化
# ============================================
if 'region' not in st.session_state:
    st.session_state.region = 'hokkaido'
if 'num_people' not in st.session_state:
    st.session_state.num_people = 1
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'gacha'
if 'lives' not in st.session_state:
    st.session_state.lives = []
if 'score_results' not in st.session_state:
    st.session_state.score_results = []
if 'selected_life_index' not in st.session_state:
    st.session_state.selected_life_index = -1
if 'total_generated' not in st.session_state:
    st.session_state.total_generated = 0
if 'show_detail_breakdown' not in st.session_state:
    st.session_state.show_detail_breakdown = False

# ============================================
# ランク情報
# ============================================
RANK_INFO = {
    "SS": {"color": "#1a1a1a", "bg": "rgba(26, 26, 26, 0.08)", "label": "超大当たり", "desc": "上位2-5%、高学歴・高収入・長寿"},
    "S": {"color": "#333333", "bg": "rgba(51, 51, 51, 0.08)", "label": "大当たり", "desc": "上位10-20%、好条件の人生"},
    "A": {"color": "#4d4d4d", "bg": "rgba(77, 77, 77, 0.08)", "label": "当たり", "desc": "平均以上の人生"},
    "B": {"color": "#666666", "bg": "rgba(102, 102, 102, 0.08)", "label": "普通", "desc": "一般的な人生"},
    "C": {"color": "#808080", "bg": "rgba(128, 128, 128, 0.08)", "label": "ハズレ", "desc": "平均以下の人生"},
    "D": {"color": "#999999", "bg": "rgba(153, 153, 153, 0.08)", "label": "大ハズレ", "desc": "早逝など不運な人生"},
}

GACHA_RATES = {
    "hokkaido": {"SS": "1.43%", "S": "6.01%", "A": "18.26%", "B": "46.00%", "C": "14.88%", "D": "13.42%"},
    "tokyo": {"SS": "4.33%", "S": "12.62%", "A": "25.42%", "B": "39.46%", "C": "9.31%", "D": "8.86%"},
}

# ============================================
# ヘルパー関数
# ============================================
def get_service():
    """GachaServiceのインスタンスを取得"""
    return get_gacha_service(st.session_state.region)

def generate_life_story(life: dict, service: GachaService) -> str:
    """人生ストーリーを生成"""
    return service._generate_life_story(life)

def get_rank_card_html(rank: str, index: int) -> str:
    """ランクカードのHTMLを生成"""
    if rank == "SS":
        css_class = "rank-card rank-card-ss"
    elif rank == "S":
        css_class = "rank-card rank-card-s"
    else:
        css_class = "rank-card rank-card-normal"
    
    return f'<div class="{css_class}">{rank}</div>'

def format_education_display(education: str) -> str:
    """学歴を表示用にフォーマット"""
    if not education or education == "不明":
        return "不明"
    education = str(education).strip()
    if "大学院" in education or "院卒" in education:
        return "院卒"
    elif "大学" in education or "大卒" in education:
        return "大卒"
    elif "短大" in education or "専門" in education:
        return "短大・専門卒"
    elif "高校" in education or "高卒" in education:
        return "高卒"
    elif "中学" in education or "中卒" in education:
        return "中学卒"
    return education

# ============================================
# ガチャ画面
# ============================================
def gacha_view():
    """ガチャ画面"""
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    
    # 地域選択
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        region_col1, region_col2 = st.columns(2)
        with region_col1:
            hokkaido_style = "background: rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.2);" if st.session_state.region == "hokkaido" else "background: #D9D9D9; border: 5px solid rgba(0,0,0,0.2);"
            if st.button("北海道", key="hokkaido_btn", use_container_width=True):
                st.session_state.region = "hokkaido"
                st.rerun()
        with region_col2:
            tokyo_style = "background: rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.2);" if st.session_state.region == "tokyo" else "background: #D9D9D9; border: 5px solid rgba(0,0,0,0.2);"
            if st.button("東京", key="tokyo_btn", use_container_width=True):
                st.session_state.region = "tokyo"
                st.rerun()
    
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    
    # スライダー
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.session_state.num_people = st.slider(
            "人数",
            min_value=1,
            max_value=20,
            value=st.session_state.num_people,
            key="people_slider"
        )
    
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    
    # ガチャボタン
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("ガチャを引く", key="gacha_btn", use_container_width=True, type="primary"):
            pull_gacha()
    
    st.markdown("<br>" * 4, unsafe_allow_html=True)
    
    # 情報ボタン
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col2:
        if st.button("確率", key="rates_btn"):
            show_rates_dialog()
    with col3:
        if st.button("相関図", key="correlation_btn"):
            show_correlation_dialog()
    with col4:
        if st.button("データ", key="dataset_btn"):
            show_dataset_dialog()

def pull_gacha():
    """ガチャを引く"""
    service = get_service()
    
    st.session_state.lives = []
    st.session_state.score_results = []
    
    for _ in range(st.session_state.num_people):
        life = service.simulator.generate_life()
        score_result = service.simulator.calculate_life_score(life)
        st.session_state.lives.append(life)
        st.session_state.score_results.append(score_result)
    
    st.session_state.total_generated += st.session_state.num_people
    st.session_state.view_mode = "result"
    st.rerun()

# ============================================
# 結果一覧画面
# ============================================
def result_view():
    """結果一覧画面"""
    # ヘッダー
    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("←", key="back_btn"):
            st.session_state.view_mode = "gacha"
            st.rerun()
    with col3:
        if st.button("↺", key="refresh_btn"):
            pull_gacha()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # カードグリッド（5列）
    if st.session_state.score_results:
        num_results = len(st.session_state.score_results)
        rows = (num_results + 4) // 5  # 5列で割って行数を計算
        
        for row in range(rows):
            cols = st.columns(5)
            for col_idx in range(5):
                card_idx = row * 5 + col_idx
                if card_idx < num_results:
                    rank = st.session_state.score_results[card_idx].get("rank", "B")
                    with cols[col_idx]:
                        # ランクカード表示
                        if rank == "SS":
                            bg_style = "background: linear-gradient(135deg, #080808 0%, #6E6E6E 100%); color: #D8D8D8;"
                        elif rank == "S":
                            bg_style = "background: linear-gradient(135deg, #292929 0%, #8F8F8F 100%); color: #000000;"
                        else:
                            bg_style = "background: #D9D9D9; color: #000000;"
                        
                        st.markdown(f"""
                        <div style="
                            width: 111px;
                            height: 148px;
                            border-radius: 8px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-family: 'Roboto', sans-serif;
                            font-weight: 600;
                            font-size: 48px;
                            margin: 8px auto;
                            {bg_style}
                        ">{rank}</div>
                        """, unsafe_allow_html=True)
                        
                        # 詳細ボタン
                        if st.button("詳細", key=f"detail_btn_{card_idx}", use_container_width=True):
                            st.session_state.selected_life_index = card_idx
                            st.session_state.view_mode = "detail"
                            st.session_state.show_detail_breakdown = False
                            st.rerun()
    
    # カウンター
    st.markdown(f"""
    <div class="counter">{st.session_state.total_generated}</div>
    """, unsafe_allow_html=True)

# ============================================
# 詳細画面
# ============================================
def detail_view():
    """詳細画面"""
    if st.session_state.selected_life_index < 0:
        st.session_state.view_mode = "result"
        st.rerun()
        return
    
    service = get_service()
    life = st.session_state.lives[st.session_state.selected_life_index]
    score_result = st.session_state.score_results[st.session_state.selected_life_index]
    
    # 閉じるボタン
    col1, col2 = st.columns([1, 11])
    with col1:
        if st.button("×", key="close_btn"):
            st.session_state.view_mode = "result"
            st.rerun()
    
    # 詳細カード
    st.markdown('<div class="detail-card">', unsafe_allow_html=True)
    
    # 人生ストーリー
    life_story = generate_life_story(life, service)
    st.markdown(f'<div class="life-story">{life_story}</div>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 人生ランク表示
    rank = score_result.get("rank", "B")
    total_score = int(score_result.get("total_score", 0))
    rank_label = score_result.get("rank_label", "")
    
    if rank == "SS":
        rank_bg = "linear-gradient(135deg, #080808 0%, #6E6E6E 100%)"
        rank_color = "#D8D8D8"
    elif rank == "S":
        rank_bg = "linear-gradient(135deg, #292929 0%, #8F8F8F 100%)"
        rank_color = "#000000"
    else:
        rank_bg = "#C0C0C0"
        rank_color = "#000000"
    
    st.markdown(f"""
    <div style="
        width: 360px;
        height: 128px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin: 20px auto;
        background: {rank_bg};
    ">
        <span style="font-family: 'Zen Old Mincho', serif; font-weight: 700; font-size: 36px; color: {rank_color};">人生ランク</span>
        <span style="font-family: 'Roboto', sans-serif; font-weight: 600; font-size: 64px; color: {rank_color};">{rank}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 親ガチャランク
    parent_result = service.simulator.calculate_parent_gacha_score(life)
    parent_rank = parent_result.get("rank", "B")
    
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0;">
        <span style="font-family: 'Zen Old Mincho', serif; font-weight: 700; font-size: 24px; color: #323232;">親ガチャランク</span>
        <span style="font-family: 'Roboto', sans-serif; font-weight: 600; font-size: 40px; color: #000000; margin-left: 16px;">{parent_rank}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 展開ボタン
    if st.button("↓ 詳細を展開" if not st.session_state.show_detail_breakdown else "↑ 閉じる", key="expand_btn"):
        st.session_state.show_detail_breakdown = not st.session_state.show_detail_breakdown
        st.rerun()
    
    # 詳細展開時
    if st.session_state.show_detail_breakdown:
        show_detail_breakdown(life, score_result, parent_result, service)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_detail_breakdown(life: dict, score_result: dict, parent_result: dict, service):
    """詳細データの展開表示"""
    st.markdown("---")
    
    # 総合スコア
    total_score = int(score_result.get("total_score", 0))
    rank_label = score_result.get("rank_label", "")
    st.markdown(f"### {total_score}点「{rank_label}」")
    
    # 詳細データ
    st.markdown("#### 📋 詳細データ")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**👶 出生情報**")
        gender = "男性" if life.get('gender') == 'male' else "女性"
        st.write(f"性別: {gender}")
        st.write(f"出生地: {life.get('birth_city', '不明')}")
        st.write(f"世帯年収: {life.get('household_income', '不明')}")
        st.write(f"父学歴: {format_education_display(life.get('father_education', '不明'))}")
        st.write(f"母学歴: {format_education_display(life.get('mother_education', '不明'))}")
    
    with col2:
        st.markdown("**📚 学歴・偏差値**")
        deviation_value = life.get('deviation_value', 0)
        if deviation_value:
            st.write(f"個人偏差値: {deviation_value:.1f}")
        
        if life.get('high_school'):
            hs_name = life.get('high_school_name', '')
            if isinstance(hs_name, dict):
                hs_name = hs_name.get('name', '')
            hs_deviation = life.get('high_school_deviation', 0)
            if hs_deviation:
                st.write(f"高校: {hs_name} (偏差値{hs_deviation:.1f})")
            else:
                st.write(f"高校: {hs_name or '進学'}")
        else:
            st.write("高校: 進学せず")
        
        graduation_deviation = life.get('graduation_deviation', 0)
        if graduation_deviation:
            growth = graduation_deviation - deviation_value if deviation_value else 0
            growth_str = f"+{growth:.1f}" if growth >= 0 else f"{growth:.1f}"
            st.write(f"卒業時偏差値: {graduation_deviation:.1f} ({growth_str})")
        
        if life.get('university'):
            uni_name = life.get('university_name', '')
            if isinstance(uni_name, dict):
                uni_name = uni_name.get('name', '')
            uni_rank = life.get('university_rank', '')
            st.write(f"大学: {uni_name}")
            st.write(f"大学ランク: {uni_rank}")
        else:
            st.write("大学: 進学せず")
    
    with col3:
        st.markdown("**💼 キャリア**")
        st.write(f"企業規模: {life.get('company_size', '不明')}")
        st.write(f"雇用形態: {life.get('employment_type', '不明')}")
        career_summary = life.get('career_summary', {})
        job_changes = career_summary.get('total_job_changes', 0)
        st.write(f"転職回数: {job_changes}回")
        st.write(f"死亡年齢: {life.get('death_age', 0)}歳")
        st.write(f"死因: {life.get('death_cause', '不明')}")
    
    # 人生スコア内訳
    st.markdown("#### 📈 人生スコア内訳")
    breakdown = score_result.get('breakdown', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        lifespan = breakdown.get('lifespan', {})
        st.markdown("**寿命 (40%)**")
        st.write(f"スコア: {lifespan.get('score', 0):.1f}点")
        st.write(f"→ {lifespan.get('value', '')}")
    
    with col2:
        income = breakdown.get('lifetime_income', {})
        st.markdown("**生涯年収 (35%)**")
        st.write(f"スコア: {income.get('score', 0):.1f}点")
        st.write(f"→ {income.get('value', '')}")
    
    with col3:
        edu = breakdown.get('education', {})
        st.markdown("**学歴 (25%)**")
        st.write(f"スコア: {edu.get('score', 0):.1f}点")
        st.write(f"→ {edu.get('value', '')}")
    
    # 親ガチャスコア内訳
    st.markdown("#### 📈 親ガチャスコア内訳")
    parent_total = int(parent_result.get('total_score', 0))
    parent_rank_label = parent_result.get('rank_label', '')
    st.markdown(f"**親ガチャ: {parent_total}点「{parent_rank_label}」**")
    
    p_breakdown = parent_result.get('breakdown', {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        p_income = p_breakdown.get('household_income', {})
        st.markdown("**世帯年収 (35%)**")
        st.write(f"スコア: {p_income.get('score', 0):.1f}点")
        st.write(f"→ {p_income.get('value', '')}")
    
    with col2:
        p_birth = p_breakdown.get('birthplace', {})
        st.markdown("**出生地 (35%)**")
        st.write(f"スコア: {p_birth.get('score', 0):.1f}点")
        st.write(f"→ {p_birth.get('value', '')}")
    
    with col3:
        p_edu = p_breakdown.get('parent_education', {})
        st.markdown("**親の学歴 (30%)**")
        st.write(f"スコア: {p_edu.get('score', 0):.1f}点")
        st.write(f"→ {p_edu.get('value', '')}")

# ============================================
# ダイアログ
# ============================================
@st.dialog("🎲 ガチャ確率")
def show_rates_dialog():
    """確率ダイアログ"""
    region_name = "北海道" if st.session_state.region == "hokkaido" else "東京"
    rates = GACHA_RATES[st.session_state.region]
    
    st.markdown(f"**{region_name}のガチャ確率**（10,000回シミュレーション）")
    st.markdown("---")
    
    for rank, rate in rates.items():
        info = RANK_INFO[rank]
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown(f"**{rank}**")
        with col2:
            st.write(f"{info['label']} - {info['desc']}")
        with col3:
            st.write(f"**{rate}**")
    
    st.markdown("---")
    st.caption("確率は実際のシミュレーション結果（2026年1月計算、新配分: 寿命40%・生涯年収35%・学歴25%）に基づいています。")

@st.dialog("📊 相関図", width="large")
def show_correlation_dialog():
    """相関図ダイアログ"""
    try:
        fig = create_correlation_sankey()
        st.plotly_chart(fig, use_container_width=True)
        
        summary = get_correlation_summary()
        st.markdown("### サマリー")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ノード数", summary.get('nodes', 0))
        with col2:
            st.metric("リンク数", summary.get('links', 0))
        with col3:
            st.metric("カテゴリ数", summary.get('categories', 0))
    except Exception as e:
        st.error(f"相関図の表示中にエラーが発生しました: {e}")

@st.dialog("📋 データセット", width="large")
def show_dataset_dialog():
    """データセットダイアログ"""
    service = get_service()
    
    st.markdown("### 使用しているデータセット")
    st.markdown("---")
    
    # データセット情報（簡略版）
    datasets = [
        {"name": "市区町村別出生数", "source": "厚生労働省", "year": "2024年", "icon": "📍"},
        {"name": "世帯年収分布", "source": "総務省統計局", "year": "2023年", "icon": "💰"},
        {"name": "高校・大学進学率", "source": "文部科学省", "year": "2024年度", "icon": "🎓"},
        {"name": "大学進学先都道府県", "source": "文部科学省", "year": "2024年度", "icon": "🏫"},
        {"name": "最終学歴分布", "source": "総務省統計局", "year": "2020年", "icon": "📊"},
        {"name": "産業別就業者数", "source": "総務省統計局", "year": "2024年", "icon": "🏭"},
        {"name": "年齢別死亡率", "source": "厚生労働省", "year": "2023年", "icon": "📈"},
        {"name": "死因統計", "source": "厚生労働省", "year": "2022年", "icon": "🏥"},
    ]
    
    for ds in datasets:
        col1, col2, col3 = st.columns([1, 4, 2])
        with col1:
            st.write(ds["icon"])
        with col2:
            st.write(f"**{ds['name']}**")
        with col3:
            st.write(f"{ds['source']} ({ds['year']})")

# ============================================
# メインルーティング
# ============================================
def main():
    """メインアプリケーション"""
    if st.session_state.view_mode == "gacha":
        gacha_view()
    elif st.session_state.view_mode == "result":
        result_view()
    elif st.session_state.view_mode == "detail":
        detail_view()

if __name__ == "__main__":
    main()
