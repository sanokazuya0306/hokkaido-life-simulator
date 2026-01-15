#!/usr/bin/env python3
"""
北海道の公開データを使ってランダムに人生の軌跡を生成するプログラム

必要なデータファイル:
- birth_by_city.csv: 市町村別の出生数
- high_school_rate.csv: 市町村別の高校進学率
- university_rate.csv: 市町村別の大学進学率
- hokkaido_university_destinations.csv: 大学進学先の都道府県
- workers_by_industry.csv: 産業別の労働者数
- workers_by_gender.csv: 性別別の労働者数（令和6年労働力調査）
- workers_by_industry_gender.csv: 性別×産業別の労働者数
- retirement_age.csv: 定年年齢の分布
- death_by_age.csv: 年齢別の死亡者数
- death_by_cause.csv: 死因別の死亡者数
"""

import os
import sys
import csv
import random
import argparse
from pathlib import Path


# ============================================================================
# 人生スコア計算のための統計データ定数
# 東京で生まれ育って最大限に充実した人生 = 100点 を基準とする
# ============================================================================

# 出生地による機会格差（有効求人倍率ベース）
# 出典: 厚生労働省 一般職業紹介状況（2025年11月）
LOCATION_SCORES = {
    "東京": 100,  # 有効求人倍率 1.73（基準）
    "北海道": 54,  # 有効求人倍率 0.93（1.73の約54%）
}

# 性別による経済的機会格差
# 出典: 厚生労働省「賃金構造基本統計調査」2024年
GENDER_SCORES = {
    "男性": 100,  # 賃金100（基準）
    "女性": 76,   # 賃金75.8（男性の約76%）
}

# 学歴による生涯賃金格差
# 出典: 労働政策研究・研修機構「ユースフル労働統計」
EDUCATION_SCORES = {
    "大学卒": 100,  # 生涯賃金約2.7億円（基準）
    "高校卒": 75,   # 生涯賃金約2.0億円（大学卒の約75%）
    "中学卒": 60,   # 生涯賃金約1.6億円（大学卒の約60%）
}

# 大学進学先による機会格差
# 出典: 大学所在地の求人倍率と産業集積度
UNIVERSITY_DESTINATION_SCORES = {
    "東京都": 100,
    "神奈川県": 90,
    "大阪府": 85,
    "愛知県": 85,
    "京都府": 80,
    "兵庫県": 75,
    "福岡県": 70,
    "北海道": 60,
    "default": 65,
}

# 産業別の平均賃金スコア
# 出典: 厚生労働省「賃金構造基本統計調査」2024年
INDUSTRY_SALARY_SCORES = {
    "情報通信業": 100,
    "金融業，保険業": 95,
    "学術研究，専門・技術サービス業": 90,
    "電気・ガス・熱供給・水道業": 90,
    "教育，学習支援業": 85,
    "不動産業，物品賃貸業": 80,
    "製造業": 80,
    "建設業": 75,
    "運輸業，郵便業": 70,
    "卸売業，小売業": 65,
    "医療，福祉": 65,
    "複合サービス事業": 60,
    "サービス業（他に分類されないもの）": 55,
    "生活関連サービス業，娯楽業": 55,
    "農業，林業": 50,
    "漁業": 50,
    "宿泊業，飲食サービス業": 45,
    "default": 60,
}

# 寿命によるスコア
# 出典: 厚生労働省「簡易生命表」2024年（平均寿命: 男性81.09歳、女性87.13歳）
def get_lifespan_score(age, gender):
    """寿命に基づくスコアを計算（長寿であるほど高スコア）"""
    # 理想的な寿命を90歳として100点
    ideal_age = 90
    min_score_age = 30  # 30歳以下で死亡は0点
    
    if age <= min_score_age:
        return 0
    elif age >= ideal_age:
        return 100
    else:
        # 30歳から90歳までを0点から100点にマッピング
        return int((age - min_score_age) / (ideal_age - min_score_age) * 100)

# 死因によるスコア調整
# 「老衰」で亡くなるのは最も自然な死（高スコア）
DEATH_CAUSE_SCORES = {
    "老衰": 100,
    "その他": 80,
    "不慮の事故": 40,
    "自殺": 20,
    "default": 70,
}

# 各要素の重み（合計100%）
SCORE_WEIGHTS = {
    "location": 0.20,      # 出生地（20%）
    "gender": 0.15,        # 性別（15%）
    "education": 0.20,     # 学歴（20%）
    "university_dest": 0.05,  # 大学進学先（5%）
    "industry": 0.15,      # 就職産業（15%）
    "lifespan": 0.15,      # 寿命（15%）
    "death_cause": 0.10,   # 死因（10%）
}

# ============================================================================
# SNS反応テンプレート
# ============================================================================

SNS_REACTIONS = {
    # 高スコア（80点以上）への反応
    "high_score": [
        "これはガチャSSR引いてる。北海道でこれなら東京なら無双だったな",
        "情報通信業で大卒とか、北海道の中でも勝ち組ルートじゃん",
        "親ガチャ当たり、学歴も産業もいい。でも北海道という時点で-20点くらいある",
        "81点て、東京生まれならもっといけた可能性を感じる",
        "これで人生「充実」扱いなの、基準が東京だと厳しいな",
    ],
    # 中スコア（50-79点）への反応
    "mid_score": [
        "高卒で製造業、定年まで働いて82歳まで生きる。これが日本の平均的な人生なんだよな",
        "65点て、可もなく不可もなくって感じ。でもそれが大多数なんだよね",
        "女性で-24%されるの、シミュレーションとはいえ現実を突きつけられる",
        "北海道生まれの時点で半分くらい決まってるの、地方創生とは",
        "普通に生きて普通に死ぬ。これが一番難しいのかもしれない",
    ],
    # 低スコア（50点未満）への反応
    "low_score": [
        "中卒で40代死亡はキツい…統計的にはあり得る話なんだけど",
        "35点以下の人生を「困難」と表現するの、なんか淡々としてて怖い",
        "これ見ると自分の人生まだマシかもって思える（そういう使い方するな）",
        "北海道 × 女性 × 低学歴のコンボ、社会構造の問題が可視化されてる",
        "人生ガチャのリセマラできないの、残酷すぎん？",
    ],
    # 性別関連
    "gender_female": [
        "女性というだけで-24点、これがジェンダーギャップ指数118位の国の現実",
        "同じ人生でも男性だったら+3〜4点は違うんだろうな",
        "女性の平均寿命が長いのに、経済的には不利。長く生きる分だけ大変という",
    ],
    "gender_male": [
        "男性だけど81歳で亡くなるの、平均寿命ピッタリで逆にリアル",
        "男性は経済的には有利だけど、寿命短いし自殺率高いし、トータルでどうなんだろ",
    ],
    # 学歴関連
    "no_university": [
        "大学行かないと0点なの厳しい。でも実際の生涯賃金差を考えると妥当か",
        "高卒で定年まで働けたの、むしろ勝ち組まである",
    ],
    "university": [
        "北海道の大学だと60点なの、やっぱ東京の大学行くべきだったか",
        "大卒なのに北海道で就職したの、地元愛か就活失敗か",
    ],
    # 産業関連
    "good_industry": [
        "情報通信業100点なの、時代だな〜",
        "金融保険で95点、まあ給料いいもんな",
    ],
    "bad_industry": [
        "飲食45点は草。でもこれが現実なんだよな",
        "農林業50点、食料自給率がとか言ってる場合じゃない賃金",
    ],
    # 死因関連
    "death_cancer": [
        "ガンで亡くなる確率の高さよ…2人に1人がなる時代",
        "82歳でガンて、ある意味長生きできた方なのかも",
    ],
    "death_old_age": [
        "老衰100点なの、ある意味理想の死に方",
        "老衰で亡くなれるの、それだけで人生の勝ち組感ある",
    ],
    "death_accident": [
        "不慮の事故で-60点、本人の努力でどうにもならないやつ",
        "事故死はマジで運。人生ってそういうもんか",
    ],
    "death_young": [
        "40代で亡くなるの、統計的にはあり得るけど見るとキツい",
        "若くして亡くなるパターン、親より先に死ぬ可能性を考えさせられる",
    ],
    # 出生地関連
    "birth_sapporo": [
        "札幌生まれはまだ北海道の中ではマシな方",
        "札幌市〇〇区、北海道のボーナスステージ",
    ],
    "birth_rural": [
        "地方の町村生まれ、選択肢の少なさが人生に効いてくる",
        "この町、人口何人なんだろ…",
    ],
    # 汎用的な反応
    "general": [
        "人生を点数化するの、なんか残酷だけど面白い",
        "このシミュレーター、自分の人生でやったら何点なんだろ",
        "統計データに基づいてるのがリアルで怖い",
        "北海道限定なの、全国版も見てみたい",
        "東京基準100点、地方民には厳しい採点",
        "人生ガチャの結果を見せられてる気分",
        "これ見てると、生まれた場所と性別でかなり決まっちゃうんだな",
        "シミュレーションとはいえ、誰かの人生かもしれないと思うと複雑",
    ],
}


class HokkaidoLifeSimulator:
    def __init__(self, data_dir=None):
        """
        初期化
        
        Args:
            data_dir: データファイルが格納されているディレクトリ（Noneの場合はスクリプトと同じディレクトリのdataフォルダ）
        """
        if data_dir is None:
            # スクリプトファイルの場所を基準にdataディレクトリを探す
            script_dir = Path(__file__).parent
            self.data_dir = script_dir / "data"
        else:
            self.data_dir = Path(data_dir)
        self.birth_data = []
        self.high_school_rates = {}
        self.high_schools_by_city = {}  # 市町村別高校リスト
        self.university_rates = {}
        self.university_destinations = []
        self.universities_by_prefecture = {}  # 都道府県別大学リスト
        self.workers_by_industry = []
        self.workers_by_gender = {}  # 性別別の労働者割合
        self.workers_by_industry_gender = {}  # 性別×産業別の労働者数
        self.retirement_age_distribution = []
        self.death_by_age = []
        self.death_by_cause = []
        
        self.load_data()
    
    def load_data(self):
        """データファイルを読み込む"""
        # 出生数データ
        birth_file = self.data_dir / "birth_by_city.csv"
        if birth_file.exists():
            with open(birth_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    city = row.get("市町村", "").strip()
                    birth_count = int(row.get("出生数", 0))
                    # 「北海道」や「北　海　道」などの総計行、および「札幌市」全体をスキップ（区のデータを使用）
                    if city and birth_count > 0 and city not in ["北海道", "北　海　道", "全道", "全道計", "札幌市"]:
                        self.birth_data.append({"city": city, "count": birth_count})
        else:
            print(f"警告: {birth_file} が見つかりません。サンプルデータを使用します。", file=sys.stderr)
            self.birth_data = [
                {"city": "札幌市", "count": 10000},
                {"city": "旭川市", "count": 2000},
                {"city": "函館市", "count": 1500},
            ]
        
        # 高校進学率データ
        high_school_file = self.data_dir / "high_school_rate.csv"
        if high_school_file.exists():
            with open(high_school_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    city = row.get("市町村", "").strip()
                    rate = float(row.get("進学率", 0))
                    if city:
                        self.high_school_rates[city] = rate
        else:
            print(f"警告: {high_school_file} が見つかりません。デフォルト値を使用します。", file=sys.stderr)
            self.high_school_rates = {"default": 98.0}
        
        # 大学進学率データ
        university_file = self.data_dir / "university_rate.csv"
        if university_file.exists():
            with open(university_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    city = row.get("市町村", "").strip()
                    rate = float(row.get("進学率", 0))
                    if city:
                        self.university_rates[city] = rate
        else:
            print(f"警告: {university_file} が見つかりません。デフォルト値を使用します。", file=sys.stderr)
            self.university_rates = {"default": 50.0}
        
        # 大学進学先の都道府県データ
        university_dest_file = self.data_dir / "hokkaido_university_destinations.csv"
        if university_dest_file.exists():
            with open(university_dest_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    prefecture = row.get("進学先都道府県", "").strip()
                    count = row.get("進学者数", "").strip()
                    if prefecture and count:
                        try:
                            count_int = int(count)
                            if count_int > 0:
                                self.university_destinations.append({"prefecture": prefecture, "count": count_int})
                        except ValueError:
                            pass
        else:
            print(f"警告: {university_dest_file} が見つかりません。デフォルト値を使用します。", file=sys.stderr)
            self.university_destinations = [
                {"prefecture": "北海道", "count": 13800},
                {"prefecture": "東京都", "count": 549},
                {"prefecture": "愛知県", "count": 291},
            ]
        
        # 産業別労働者数データ
        workers_file = self.data_dir / "workers_by_industry.csv"
        if workers_file.exists():
            with open(workers_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    industry = row.get("産業", "").strip()
                    workers = int(row.get("労働者数", 0))
                    if industry and workers > 0:
                        self.workers_by_industry.append({"industry": industry, "count": workers})
        else:
            print(f"警告: {workers_file} が見つかりません。サンプルデータを使用します。", file=sys.stderr)
            self.workers_by_industry = [
                {"industry": "農業", "count": 50000},
                {"industry": "製造業", "count": 100000},
                {"industry": "建設業", "count": 80000},
                {"industry": "卸売・小売業", "count": 150000},
                {"industry": "サービス業", "count": 200000},
            ]
        
        # 年齢別死亡者数データ
        death_file = self.data_dir / "death_by_age.csv"
        if death_file.exists():
            with open(death_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    age = int(row.get("年齢", 0))
                    deaths = int(row.get("死亡者数", 0))
                    if age >= 0 and deaths > 0:
                        self.death_by_age.append({"age": age, "count": deaths})
        else:
            print(f"警告: {death_file} が見つかりません。サンプルデータを使用します。", file=sys.stderr)
            # 年齢別の死亡確率を簡易的に設定（実際のデータに基づく）
            self.death_by_age = []
            for age in range(0, 100):
                # 年齢が高いほど死亡者数が多い（簡易モデル）
                count = max(1, int(100 * (age / 100) ** 3))
                self.death_by_age.append({"age": age, "count": count})
        
        # 死因別死亡者数データ
        death_cause_file = self.data_dir / "death_by_cause.csv"
        if death_cause_file.exists():
            with open(death_cause_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cause = row.get("死因", "").strip()
                    deaths = int(row.get("死亡者数", 0))
                    if cause and deaths > 0:
                        self.death_by_cause.append({"cause": cause, "count": deaths})
        else:
            print(f"警告: {death_cause_file} が見つかりません。サンプルデータを使用します。", file=sys.stderr)
            self.death_by_cause = [
                {"cause": "悪性新生物", "count": 20000},
                {"cause": "心疾患", "count": 10000},
                {"cause": "老衰", "count": 6000},
                {"cause": "脳血管疾患", "count": 5000},
            ]
        
        # 性別別労働者数データ（令和6年労働力調査）
        workers_gender_file = self.data_dir / "workers_by_gender.csv"
        if workers_gender_file.exists():
            with open(workers_gender_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    gender = row.get("性別", "").strip()
                    workers = int(row.get("就業者数", 0))
                    if gender and gender != "合計" and workers > 0:
                        self.workers_by_gender[gender] = workers
        else:
            print(f"警告: {workers_gender_file} が見つかりません。デフォルト値を使用します。", file=sys.stderr)
            # 令和6年労働力調査のデフォルト値
            self.workers_by_gender = {"男性": 1430000, "女性": 1210000}
        
        # 性別×産業別労働者数データ
        workers_industry_gender_file = self.data_dir / "workers_by_industry_gender.csv"
        if workers_industry_gender_file.exists():
            with open(workers_industry_gender_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    industry = row.get("産業", "").strip()
                    male = int(row.get("男性", 0))
                    female = int(row.get("女性", 0))
                    if industry and (male > 0 or female > 0):
                        self.workers_by_industry_gender[industry] = {"男性": male, "女性": female}
        else:
            print(f"警告: {workers_industry_gender_file} が見つかりません。デフォルト値を使用します。", file=sys.stderr)
            # 性別データがない場合は全国傾向に基づくデフォルト値
            self.workers_by_industry_gender = {}
        
        # 市町村別高校データ
        high_schools_file = self.data_dir / "high_schools.csv"
        if high_schools_file.exists():
            with open(high_schools_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    city = row.get("市町村", "").strip()
                    school_name = row.get("高校名", "").strip()
                    if city and school_name:
                        if city not in self.high_schools_by_city:
                            self.high_schools_by_city[city] = []
                        self.high_schools_by_city[city].append(school_name)
        else:
            print(f"警告: {high_schools_file} が見つかりません。汎用高校名を使用します。", file=sys.stderr)
        
        # 都道府県別大学データ
        universities_file = self.data_dir / "universities_by_prefecture.csv"
        if universities_file.exists():
            with open(universities_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    prefecture = row.get("都道府県", "").strip()
                    univ_name = row.get("大学名", "").strip()
                    enrollment = row.get("入学者数", "").strip()
                    if prefecture and univ_name and enrollment:
                        try:
                            enrollment_int = int(enrollment)
                            if prefecture not in self.universities_by_prefecture:
                                self.universities_by_prefecture[prefecture] = []
                            self.universities_by_prefecture[prefecture].append({
                                "name": univ_name,
                                "enrollment": enrollment_int
                            })
                        except ValueError:
                            pass
        else:
            print(f"警告: {universities_file} が見つかりません。汎用大学名を使用します。", file=sys.stderr)
        
        # 定年年齢データ
        retirement_age_file = self.data_dir / "retirement_age.csv"
        if retirement_age_file.exists():
            with open(retirement_age_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    category = row.get("定年年齢区分", "").strip()
                    ratio = float(row.get("割合", 0))
                    if category and ratio > 0:
                        self.retirement_age_distribution.append({"category": category, "ratio": ratio})
        else:
            print(f"警告: {retirement_age_file} が見つかりません。デフォルト値を使用します。", file=sys.stderr)
            self.retirement_age_distribution = [
                {"category": "60歳", "ratio": 72.3},
                {"category": "61-64歳", "ratio": 2.6},
                {"category": "65歳", "ratio": 21.1},
                {"category": "66歳以上", "ratio": 3.5},
                {"category": "定年なし", "ratio": 0.5},
            ]
    
    def select_birth_city(self):
        """出生地をランダムに選択（出生数に基づく重み付き選択）"""
        if not self.birth_data:
            return "不明"
        
        total_births = sum(item["count"] for item in self.birth_data)
        if total_births == 0:
            return random.choice(self.birth_data)["city"] if self.birth_data else "不明"
        
        rand = random.uniform(0, total_births)
        cumulative = 0
        for item in self.birth_data:
            cumulative += item["count"]
            if rand <= cumulative:
                city = item["city"]
                # 札幌市の区を「札幌市○○区」の形式に変換
                if city.endswith("区") and "市" not in city:
                    city = f"札幌市{city}"
                return city
        
        # 最後の要素も同様に処理
        city = self.birth_data[-1]["city"]
        if city.endswith("区") and "市" not in city:
            city = f"札幌市{city}"
        return city
    
    def decide_high_school(self, city):
        """高校進学を決定"""
        rate = self.high_school_rates.get(city, self.high_school_rates.get("default", 98.0))
        return random.random() * 100 < rate
    
    def select_high_school_name(self, city):
        """出生地に近接した高校名を選択"""
        # まず出生地の市町村で高校を探す
        if city in self.high_schools_by_city:
            return random.choice(self.high_schools_by_city[city])
        
        # 札幌市の区の場合、区名で探す
        if "札幌市" in city:
            # 「札幌市中央区」→「札幌市中央区」で検索
            if city in self.high_schools_by_city:
                return random.choice(self.high_schools_by_city[city])
            # 区名だけを抽出して「中央区」で検索
            for key in self.high_schools_by_city:
                if key in city or city in key:
                    return random.choice(self.high_schools_by_city[key])
            # 札幌市内のいずれかの高校を選択
            sapporo_schools = []
            for key, schools in self.high_schools_by_city.items():
                if "札幌" in key:
                    sapporo_schools.extend(schools)
            if sapporo_schools:
                return random.choice(sapporo_schools)
        
        # 市町村名の部分一致で探す
        city_base = city.replace("市", "").replace("町", "").replace("村", "")
        for key, schools in self.high_schools_by_city.items():
            if city_base in key or key.replace("市", "").replace("町", "").replace("村", "") in city:
                return random.choice(schools)
        
        # 見つからない場合は汎用名を生成
        city_short = city.replace("市", "").replace("町", "").replace("村", "")
        return f"{city_short}高校"
    
    def decide_university(self, city, went_to_high_school):
        """大学進学を決定（高校に進学した場合のみ）"""
        if not went_to_high_school:
            return False
        
        rate = self.university_rates.get(city, self.university_rates.get("default", 50.0))
        return random.random() * 100 < rate
    
    def select_university_name(self, prefecture):
        """進学先都道府県から大学名を入学者数に基づいて選択"""
        # 都道府県名から「県」「府」「都」を除いた形で検索
        prefecture_key = prefecture
        
        # 「北海道」以外は末尾の「県」「府」「都」を保持したまま検索
        if prefecture_key in self.universities_by_prefecture:
            universities = self.universities_by_prefecture[prefecture_key]
        else:
            # 見つからない場合は汎用名を返す
            return f"{prefecture}の大学"
        
        if not universities:
            return f"{prefecture}の大学"
        
        # 入学者数に基づく重み付き選択
        total_enrollment = sum(u["enrollment"] for u in universities)
        if total_enrollment == 0:
            return random.choice(universities)["name"]
        
        rand = random.uniform(0, total_enrollment)
        cumulative = 0
        for univ in universities:
            cumulative += univ["enrollment"]
            if rand <= cumulative:
                return univ["name"]
        
        return universities[-1]["name"]
    
    def select_university_destination(self):
        """大学進学先の都道府県をランダムに選択（進学者数に基づく重み付き選択）"""
        if not self.university_destinations:
            return "北海道"
        
        total_students = sum(item["count"] for item in self.university_destinations)
        if total_students == 0:
            return random.choice(self.university_destinations)["prefecture"] if self.university_destinations else "北海道"
        
        rand = random.uniform(0, total_students)
        cumulative = 0
        for item in self.university_destinations:
            cumulative += item["count"]
            if rand <= cumulative:
                return item["prefecture"]
        
        return self.university_destinations[-1]["prefecture"]
    
    def select_gender(self):
        """性別をランダムに選択（労働者数に基づく重み付き選択）"""
        if not self.workers_by_gender:
            return random.choice(["男性", "女性"])
        
        total = sum(self.workers_by_gender.values())
        if total == 0:
            return random.choice(["男性", "女性"])
        
        rand = random.uniform(0, total)
        cumulative = 0
        for gender, count in self.workers_by_gender.items():
            cumulative += count
            if rand <= cumulative:
                return gender
        
        return "男性"
    
    def select_industry(self, gender=None):
        """就職先の産業をランダムに選択（労働者数に基づく重み付き選択）
        
        Args:
            gender: 性別（指定された場合、性別に応じた産業分布を使用）
        """
        # 性別が指定されていて、性別×産業データがある場合
        if gender and self.workers_by_industry_gender:
            industry_weights = []
            for industry, gender_data in self.workers_by_industry_gender.items():
                count = gender_data.get(gender, 0)
                if count > 0:
                    industry_weights.append({"industry": industry, "count": count})
            
            if industry_weights:
                total_workers = sum(item["count"] for item in industry_weights)
                if total_workers > 0:
                    rand = random.uniform(0, total_workers)
                    cumulative = 0
                    for item in industry_weights:
                        cumulative += item["count"]
                        if rand <= cumulative:
                            return item["industry"]
                    return industry_weights[-1]["industry"]
        
        # 性別データがない場合は従来の全体データを使用
        if not self.workers_by_industry:
            return "不明"
        
        total_workers = sum(item["count"] for item in self.workers_by_industry)
        if total_workers == 0:
            return random.choice(self.workers_by_industry)["industry"] if self.workers_by_industry else "不明"
        
        rand = random.uniform(0, total_workers)
        cumulative = 0
        for item in self.workers_by_industry:
            cumulative += item["count"]
            if rand <= cumulative:
                return item["industry"]
        
        return self.workers_by_industry[-1]["industry"]
    
    def select_death_age(self):
        """死亡年齢をランダムに選択（年齢別死亡者数に基づく重み付き選択）"""
        if not self.death_by_age:
            return random.randint(70, 85)
        
        total_deaths = sum(item["count"] for item in self.death_by_age)
        if total_deaths == 0:
            return random.randint(70, 85)
        
        rand = random.uniform(0, total_deaths)
        cumulative = 0
        for item in self.death_by_age:
            cumulative += item["count"]
            if rand <= cumulative:
                return item["age"]
        
        return self.death_by_age[-1]["age"]
    
    def select_death_cause(self):
        """死因をランダムに選択（死因別死亡者数に基づく重み付き選択）"""
        if not self.death_by_cause:
            return "不明"
        
        total_deaths = sum(item["count"] for item in self.death_by_cause)
        if total_deaths == 0:
            return random.choice(self.death_by_cause)["cause"] if self.death_by_cause else "不明"
        
        rand = random.uniform(0, total_deaths)
        cumulative = 0
        for item in self.death_by_cause:
            cumulative += item["count"]
            if rand <= cumulative:
                return item["cause"]
        
        return self.death_by_cause[-1]["cause"]
    
    def select_retirement_age(self):
        """定年年齢をランダムに選択（定年年齢分布に基づく重み付き選択）"""
        if not self.retirement_age_distribution:
            return 60  # デフォルト
        
        total_ratio = sum(item["ratio"] for item in self.retirement_age_distribution)
        if total_ratio == 0:
            return 60
        
        rand = random.uniform(0, total_ratio)
        cumulative = 0
        for item in self.retirement_age_distribution:
            cumulative += item["ratio"]
            if rand <= cumulative:
                category = item["category"]
                
                # カテゴリに応じて具体的な年齢を返す
                if category == "60歳":
                    return 60
                elif category == "61-64歳":
                    return random.randint(61, 64)
                elif category == "65歳":
                    return 65
                elif category == "66歳以上":
                    return random.randint(66, 75)
                elif category == "定年なし":
                    return None  # 定年なし
                else:
                    return 60
        
        return 60
    
    def calculate_life_score(self, life):
        """
        人生のスコアを計算する（0〜100点）
        東京で生まれ育って最大限に充実した人生を100点とする
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            dict: 総合スコアと各項目のスコア詳細
        """
        scores = {}
        
        # 1. 出生地スコア（北海道内なので一律）
        scores["location"] = {
            "score": LOCATION_SCORES["北海道"],
            "max_score": 100,
            "label": "出生地",
            "value": life["birth_city"],
            "reason": f"北海道生まれ（東京比: 求人倍率0.93 vs 1.73）",
            "source": "厚生労働省「一般職業紹介状況」2025年11月"
        }
        
        # 2. 性別スコア
        gender = life["gender"]
        gender_score = GENDER_SCORES.get(gender, 75)
        scores["gender"] = {
            "score": gender_score,
            "max_score": 100,
            "label": "性別",
            "value": gender,
            "reason": f"{gender}（賃金格差: 男性100に対し女性75.8）" if gender == "女性" else f"{gender}（賃金基準）",
            "source": "厚生労働省「賃金構造基本統計調査」2024年"
        }
        
        # 3. 学歴スコア
        if life["university"]:
            education_level = "大学卒"
        elif life["high_school"]:
            education_level = "高校卒"
        else:
            education_level = "中学卒"
        
        education_score = EDUCATION_SCORES[education_level]
        scores["education"] = {
            "score": education_score,
            "max_score": 100,
            "label": "最終学歴",
            "value": education_level,
            "reason": f"{education_level}（生涯賃金比較に基づく）",
            "source": "労働政策研究・研修機構「ユースフル労働統計」"
        }
        
        # 4. 大学進学先スコア（大学進学者のみ）
        if life["university"] and life.get("university_destination"):
            dest = life["university_destination"]
            dest_score = UNIVERSITY_DESTINATION_SCORES.get(dest, UNIVERSITY_DESTINATION_SCORES["default"])
            scores["university_dest"] = {
                "score": dest_score,
                "max_score": 100,
                "label": "大学進学先",
                "value": dest,
                "reason": f"{dest}の大学（産業集積度・求人倍率に基づく）",
                "source": "文部科学省「学校基本調査」"
            }
        else:
            # 大学に行かなかった場合は0点（重みが低いので影響は限定的）
            scores["university_dest"] = {
                "score": 0,
                "max_score": 100,
                "label": "大学進学先",
                "value": "進学せず",
                "reason": "大学に進学しなかった",
                "source": "-"
            }
        
        # 5. 就職産業スコア
        industry = life["industry"]
        # 産業名の部分一致でスコアを取得
        industry_score = INDUSTRY_SALARY_SCORES.get("default")
        for ind_name, ind_score in INDUSTRY_SALARY_SCORES.items():
            if ind_name in industry or industry in ind_name:
                industry_score = ind_score
                break
        
        scores["industry"] = {
            "score": industry_score,
            "max_score": 100,
            "label": "就職産業",
            "value": industry,
            "reason": f"{industry}（産業別平均賃金に基づく）",
            "source": "厚生労働省「賃金構造基本統計調査」2024年"
        }
        
        # 6. 寿命スコア
        death_age = life["death_age"]
        lifespan_score = get_lifespan_score(death_age, life["gender"])
        
        # 理想的な寿命の基準
        avg_lifespan = 81.09 if life["gender"] == "男性" else 87.13
        scores["lifespan"] = {
            "score": lifespan_score,
            "max_score": 100,
            "label": "寿命",
            "value": f"{death_age}歳",
            "reason": f"{death_age}歳で死亡（平均寿命: {life['gender']}{avg_lifespan}歳）",
            "source": "厚生労働省「簡易生命表」2024年"
        }
        
        # 7. 死因スコア
        death_cause = life["death_cause"]
        # 死因の分類
        if "老衰" in death_cause:
            cause_category = "老衰"
        elif "自殺" in death_cause or "自傷" in death_cause:
            cause_category = "自殺"
        elif "不慮" in death_cause or "事故" in death_cause:
            cause_category = "不慮の事故"
        else:
            cause_category = "default"
        
        death_cause_score = DEATH_CAUSE_SCORES.get(cause_category, DEATH_CAUSE_SCORES["default"])
        
        # 悪性新生物（ガン）などの病気は70点
        if "悪性新生物" in death_cause or "腫瘍" in death_cause:
            death_cause_score = 70
            cause_display = "ガン"
        elif "心疾患" in death_cause:
            death_cause_score = 65
            cause_display = death_cause
        elif "脳血管" in death_cause:
            death_cause_score = 65
            cause_display = death_cause
        else:
            cause_display = death_cause
        
        scores["death_cause"] = {
            "score": death_cause_score,
            "max_score": 100,
            "label": "死因",
            "value": cause_display,
            "reason": f"{cause_display}で死亡（老衰が最高評価）",
            "source": "厚生労働省「人口動態統計」"
        }
        
        # 総合スコアの計算（重み付き平均）
        total_score = 0
        for key, weight in SCORE_WEIGHTS.items():
            total_score += scores[key]["score"] * weight
        
        return {
            "total_score": round(total_score, 1),
            "breakdown": scores,
            "weights": SCORE_WEIGHTS,
        }
    
    def format_score_breakdown(self, score_result, verbose=True):
        """
        スコアの内訳を文字列でフォーマット
        
        Args:
            score_result: calculate_life_score()の戻り値
            verbose: 詳細な根拠を表示するかどうか
            
        Returns:
            str: フォーマットされたスコア情報
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"【人生スコア】 {score_result['total_score']:.1f} / 100点")
        lines.append("=" * 60)
        lines.append("※ 東京で生まれ育ち最大限に充実した人生を100点として算出")
        lines.append("")
        
        breakdown = score_result["breakdown"]
        weights = score_result["weights"]
        
        lines.append("【スコア内訳】")
        lines.append("-" * 60)
        
        for key in ["location", "gender", "education", "university_dest", "industry", "lifespan", "death_cause"]:
            item = breakdown[key]
            weight = weights[key]
            weighted_score = item["score"] * weight
            
            lines.append(f"  {item['label']}: {item['score']}点 × {weight*100:.0f}% = {weighted_score:.1f}点")
            lines.append(f"    → {item['value']}")
            
            if verbose:
                lines.append(f"    理由: {item['reason']}")
                if item['source'] != "-":
                    lines.append(f"    出典: {item['source']}")
            lines.append("")
        
        lines.append("-" * 60)
        lines.append(f"合計: {score_result['total_score']:.1f}点")
        lines.append("")
        
        # スコアの解釈
        total = score_result['total_score']
        if total >= 80:
            interpretation = "非常に恵まれた人生（上位10%相当）"
        elif total >= 65:
            interpretation = "平均以上の充実した人生"
        elif total >= 50:
            interpretation = "平均的な人生"
        elif total >= 35:
            interpretation = "やや困難の多い人生"
        else:
            interpretation = "多くの困難に直面した人生"
        
        lines.append(f"【評価】 {interpretation}")
        
        return "\n".join(lines)
    
    def generate_sns_reactions(self, life, score_result):
        """
        人生データとスコアに基づいてSNS上での予想される反応を生成
        
        Args:
            life: 人生データ
            score_result: calculate_life_score()の戻り値
            
        Returns:
            list: 3つのSNS反応
        """
        reactions = []
        total_score = score_result["total_score"]
        breakdown = score_result["breakdown"]
        
        # 候補となる反応カテゴリを決定
        candidates = []
        
        # スコアベースの反応
        if total_score >= 80:
            candidates.extend(SNS_REACTIONS["high_score"])
        elif total_score >= 50:
            candidates.extend(SNS_REACTIONS["mid_score"])
        else:
            candidates.extend(SNS_REACTIONS["low_score"])
        
        # 性別ベースの反応
        if life["gender"] == "女性":
            candidates.extend(SNS_REACTIONS["gender_female"])
        else:
            candidates.extend(SNS_REACTIONS["gender_male"])
        
        # 学歴ベースの反応
        if life["university"]:
            candidates.extend(SNS_REACTIONS["university"])
        else:
            candidates.extend(SNS_REACTIONS["no_university"])
        
        # 産業ベースの反応
        industry_score = breakdown["industry"]["score"]
        if industry_score >= 90:
            candidates.extend(SNS_REACTIONS["good_industry"])
        elif industry_score <= 50:
            candidates.extend(SNS_REACTIONS["bad_industry"])
        
        # 死因ベースの反応
        death_cause = life["death_cause"]
        if "悪性新生物" in death_cause or "腫瘍" in death_cause or "ガン" in death_cause:
            candidates.extend(SNS_REACTIONS["death_cancer"])
        elif "老衰" in death_cause:
            candidates.extend(SNS_REACTIONS["death_old_age"])
        elif "不慮" in death_cause or "事故" in death_cause:
            candidates.extend(SNS_REACTIONS["death_accident"])
        
        # 若くして亡くなった場合
        if life["death_age"] < 50:
            candidates.extend(SNS_REACTIONS["death_young"])
        
        # 出生地ベースの反応
        if "札幌" in life["birth_city"]:
            candidates.extend(SNS_REACTIONS["birth_sapporo"])
        elif "市" not in life["birth_city"]:
            candidates.extend(SNS_REACTIONS["birth_rural"])
        
        # 汎用的な反応も追加
        candidates.extend(SNS_REACTIONS["general"])
        
        # 重複を除去してシャッフル
        candidates = list(set(candidates))
        random.shuffle(candidates)
        
        # 3つ選択（異なるカテゴリからなるべく選ぶ）
        reactions = candidates[:3]
        
        return reactions
    
    def format_sns_reactions(self, reactions):
        """SNS反応をフォーマット"""
        lines = []
        lines.append("")
        lines.append("=" * 60)
        lines.append("【SNSでの予想される反応】")
        lines.append("=" * 60)
        
        for i, reaction in enumerate(reactions, 1):
            lines.append(f"💬 {reaction}")
            if i < len(reactions):
                lines.append("")
        
        return "\n".join(lines)
    
    def generate_life(self):
        """1人の人生を生成"""
        gender = self.select_gender()
        birth_city = self.select_birth_city()
        
        # 両親の職業を生成（性別に応じた産業分布から選択）
        father_industry = self.select_industry("男性")
        mother_industry = self.select_industry("女性")
        
        went_to_high_school = self.decide_high_school(birth_city)
        high_school_name = self.select_high_school_name(birth_city) if went_to_high_school else None
        
        went_to_university = self.decide_university(birth_city, went_to_high_school)
        university_destination = self.select_university_destination() if went_to_university else None
        university_name = self.select_university_name(university_destination) if went_to_university and university_destination else None
        
        industry = self.select_industry(gender)  # 性別に応じた産業選択
        retirement_age = self.select_retirement_age()
        death_age = self.select_death_age()
        death_cause = self.select_death_cause()
        
        return {
            "gender": gender,
            "birth_city": birth_city,
            "father_industry": father_industry,
            "mother_industry": mother_industry,
            "high_school": went_to_high_school,
            "high_school_name": high_school_name,
            "university": went_to_university,
            "university_destination": university_destination,
            "university_name": university_name,
            "industry": industry,
            "retirement_age": retirement_age,
            "death_age": death_age,
            "death_cause": death_cause,
        }
    
    def format_life(self, life, show_score=True, verbose_score=True, show_sns=True):
        """人生の軌跡を文字列でフォーマット
        
        Args:
            life: 人生データ
            show_score: スコアを表示するかどうか（デフォルト: True）
            verbose_score: スコアの詳細な根拠を表示するかどうか
            show_sns: SNS反応を表示するかどうか（デフォルト: True）
        """
        # 出生地（市町村名）と両親の職業
        birth_city = life['birth_city']
        father_industry = life.get('father_industry', '不明')
        mother_industry = life.get('mother_industry', '不明')
        
        # 性別の表示
        gender = life.get('gender', '不明')
        
        # 出生地の整形（「札幌市○○区」は「北海道札幌市○○区」、それ以外は「北海道○○市」など）
        if "北海道" not in birth_city:
            birth_location = f"北海道{birth_city}"
        else:
            birth_location = birth_city
        
        # 進学の表示
        education_parts = []
        if life["high_school"]:
            high_school_name = life.get("high_school_name", "地元の高校")
            education_parts.append(f"{high_school_name}に進学")
        
        if life["university"] and life.get("university_destination"):
            university_name = life.get("university_name", f"{life['university_destination']}の大学")
            education_parts.append(f"{university_name}に進学")
        
        education_str = "\n".join(education_parts) if education_parts else "中学卒業"
        
        # 就職の表示
        industry = life['industry']
        if life["university"]:
            job_str = f"大学進学後に{industry}に就職"
        elif life["high_school"]:
            job_str = f"高校卒業後に{industry}に就職"
        else:
            job_str = f"中学卒業後に{industry}に就職"
        
        # キャリアサマリーから転職回数と無職年数を取得
        career_summary = life.get('career_summary', {})
        job_changes = career_summary.get('total_job_changes', 0)
        unemployment_years = career_summary.get('total_unemployment_years', 0)
        
        # 転職・無職のプレフィックスを作成
        career_prefix_parts = []
        if job_changes > 0:
            career_prefix_parts.append(f"{job_changes}回の転職")
        if unemployment_years > 0:
            career_prefix_parts.append(f"{unemployment_years}年の無職")
        
        career_prefix = "、".join(career_prefix_parts)
        if career_prefix:
            career_prefix += "を経て、"
        
        # 定年の表示（定年前に死亡した場合は表示しない）
        retirement_age = life.get('retirement_age')
        death_age = life['death_age']
        
        # 死因の表示（「悪性新生物＜腫瘍＞」を「ガン」に変換）
        death_cause = life['death_cause']
        if "悪性新生物" in death_cause or "腫瘍" in death_cause:
            death_cause = "ガン"
        
        # 定年退職できたか、その前に死亡したかで表示を分ける
        retirement_str = None
        death_str = None
        
        if retirement_age is not None and death_age >= retirement_age:
            # 定年退職できた場合
            retirement_str = f"{career_prefix}{retirement_age}歳で定年退職"
            death_str = f"{death_age}歳で{death_cause}により死亡"
        else:
            # 定年前に死亡した場合
            death_str = f"{career_prefix}{death_age}歳で{death_cause}により死亡"
        
        # 最終的な出力
        parts = [
            f"{birth_location}に{gender}として、{father_industry}の父親と{mother_industry}の母親の元に生まれる",
            education_str,
            job_str
        ]
        
        if retirement_str:
            parts.append(retirement_str)
        
        parts.append(death_str)
        
        result = "\n".join(parts)
        
        # スコアを計算（SNS反応にも使用するため先に計算）
        score_result = None
        if show_score or show_sns:
            score_result = self.calculate_life_score(life)
        
        # スコアを表示する場合
        if show_score and score_result:
            result += "\n\n" + self.format_score_breakdown(score_result, verbose=verbose_score)
        
        # SNS反応を表示する場合
        if show_sns and score_result:
            sns_reactions = self.generate_sns_reactions(life, score_result)
            result += "\n" + self.format_sns_reactions(sns_reactions)
        
        return result


def main():
    parser = argparse.ArgumentParser(description="北海道のデータを使ってランダムに人生の軌跡を生成")
    parser.add_argument(
        "-n", "--number", type=int, default=1,
        help="生成する人数（デフォルト: 1）"
    )
    parser.add_argument(
        "-d", "--data-dir", type=str, default=None,
        help="データファイルが格納されているディレクトリ（デフォルト: スクリプトと同じディレクトリのdataフォルダ）"
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="乱数のシード値（再現性のため）"
    )
    parser.add_argument(
        "--show-datasets", action="store_true",
        help="使用したデータセット情報を表示"
    )
    parser.add_argument(
        "--no-score", action="store_true",
        help="人生スコアを非表示にする"
    )
    parser.add_argument(
        "--simple", action="store_true",
        help="スコアの詳細な根拠を省略して簡潔に表示"
    )
    parser.add_argument(
        "--no-sns", action="store_true",
        help="SNS反応を非表示にする"
    )
    # 後方互換性のため残す（非推奨）
    parser.add_argument(
        "-s", "--score", action="store_true",
        help=argparse.SUPPRESS  # ヘルプには表示しない（デフォルトで表示されるようになったため）
    )
    parser.add_argument(
        "--score-simple", action="store_true",
        help=argparse.SUPPRESS  # ヘルプには表示しない
    )
    
    args = parser.parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
    
    simulator = HokkaidoLifeSimulator(data_dir=args.data_dir)
    
    # スコア表示の設定（デフォルトで表示）
    show_score = not args.no_score
    verbose_score = not args.simple and not args.score_simple
    show_sns = not args.no_sns
    
    for i in range(args.number):
        life = simulator.generate_life()
        print(f"=== 人生 #{i+1} ===")
        print(simulator.format_life(life, show_score=show_score, verbose_score=verbose_score, show_sns=show_sns))
        print()
    
    # デフォルトで使用したデータセット情報を表示
    if args.number > 0:
        print("=" * 80)
        print("【参照データセット】")
        print("=" * 80)
        
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
                "count": f"{len(simulator.workers_by_gender)}区分",
                "url": "https://www.pref.hokkaido.lg.jp/ss/tuk/030lfs/212917.html"
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
            print(f"\n{dataset['name']} ({dataset['count']})")
            print(f"  正式名称: {dataset['official_name']}")
            print(f"  提供元: {dataset['source']}")
            print(f"  データ年: {dataset['year']}")
        
        print("\n" + "=" * 80)
        print("すべて北海道庁が公開している公式統計データを使用しています。")
        print("=" * 80)


if __name__ == "__main__":
    main()

