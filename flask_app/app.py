"""
人生ガチャ Flask版

Reflex版のFigmaデザインを完全再現
"""

import sys
import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# プロジェクトルートをパスに追加
_project_root = Path(__file__).parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from core import GachaService, get_gacha_service

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'jinsei-gacha-secret-key-2026')

# ============================================
# 定数
# ============================================
RANK_INFO = {
    "SS": {"color": "#1a1a1a", "label": "超大当たり", "desc": "上位2-5%、高学歴・高収入・長寿"},
    "S": {"color": "#333333", "label": "大当たり", "desc": "上位10-20%、好条件の人生"},
    "A": {"color": "#4d4d4d", "label": "当たり", "desc": "平均以上の人生"},
    "B": {"color": "#666666", "label": "普通", "desc": "一般的な人生"},
    "C": {"color": "#808080", "label": "ハズレ", "desc": "平均以下の人生"},
    "D": {"color": "#999999", "label": "大ハズレ", "desc": "早逝など不運な人生"},
}

GACHA_RATES = {
    "hokkaido": {"SS": "1.43%", "S": "6.01%", "A": "18.26%", "B": "46.00%", "C": "14.88%", "D": "13.42%"},
    "tokyo": {"SS": "4.33%", "S": "12.62%", "A": "25.42%", "B": "39.46%", "C": "9.31%", "D": "8.86%"},
}

# ============================================
# ヘルパー関数
# ============================================
def get_service(region='hokkaido'):
    return get_gacha_service(region)

def format_education(education):
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

def init_session():
    if 'region' not in session:
        session['region'] = 'hokkaido'
    if 'num_people' not in session:
        session['num_people'] = 1
    if 'lives' not in session:
        session['lives'] = []
    if 'score_results' not in session:
        session['score_results'] = []
    if 'total_generated' not in session:
        session['total_generated'] = 0

# ============================================
# ルート
# ============================================
@app.route('/')
def index():
    init_session()
    return render_template('gacha.html', 
                         region=session['region'],
                         num_people=session['num_people'])

@app.route('/set_region/<region>')
def set_region(region):
    init_session()
    if region in ['hokkaido', 'tokyo']:
        session['region'] = region
    return redirect(url_for('index'))

@app.route('/set_num_people', methods=['POST'])
def set_num_people():
    init_session()
    num = int(request.form.get('num_people', 1))
    session['num_people'] = max(1, min(20, num))
    return redirect(url_for('index'))

@app.route('/pull_gacha')
def pull_gacha():
    init_session()
    service = get_service(session['region'])
    
    lives = []
    score_results = []
    
    for _ in range(session['num_people']):
        life = service.simulator.generate_life()
        score_result = service.simulator.calculate_life_score(life)
        lives.append(life)
        score_results.append(score_result)
    
    session['lives'] = lives
    session['score_results'] = score_results
    session['total_generated'] = session.get('total_generated', 0) + session['num_people']
    
    return redirect(url_for('result'))

@app.route('/result')
def result():
    init_session()
    if not session.get('score_results'):
        return redirect(url_for('index'))
    
    return render_template('result.html',
                         score_results=session['score_results'],
                         total_generated=session['total_generated'])

@app.route('/detail/<int:index>')
def detail(index):
    init_session()
    if not session.get('lives') or index >= len(session['lives']):
        return redirect(url_for('result'))
    
    service = get_service(session['region'])
    life = session['lives'][index]
    score_result = session['score_results'][index]
    
    # 人生ストーリー生成
    life_story = service._generate_life_story(life)
    
    # 親ガチャスコア
    parent_result = service.simulator.calculate_parent_gacha_score(life)
    
    # 高校名・大学名の処理
    hs_name = life.get('high_school_name', '')
    if isinstance(hs_name, dict):
        hs_name = hs_name.get('name', '')
    
    uni_name = life.get('university_name', '')
    if isinstance(uni_name, dict):
        uni_name = uni_name.get('name', '')
    
    return render_template('detail.html',
                         life=life,
                         score_result=score_result,
                         parent_result=parent_result,
                         life_story=life_story,
                         hs_name=hs_name,
                         uni_name=uni_name,
                         format_education=format_education,
                         index=index)

@app.route('/api/rates')
def api_rates():
    init_session()
    region = session.get('region', 'hokkaido')
    region_name = "北海道" if region == "hokkaido" else "東京"
    return jsonify({
        'region': region,
        'region_name': region_name,
        'rates': GACHA_RATES[region],
        'rank_info': RANK_INFO
    })

# ============================================
# テンプレートフィルター
# ============================================
@app.template_filter('format_edu')
def format_edu_filter(s):
    return format_education(s)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
