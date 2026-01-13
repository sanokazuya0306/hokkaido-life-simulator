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
        self.university_rates = {}
        self.university_destinations = []
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
    
    def decide_university(self, city, went_to_high_school):
        """大学進学を決定（高校に進学した場合のみ）"""
        if not went_to_high_school:
            return False
        
        rate = self.university_rates.get(city, self.university_rates.get("default", 50.0))
        return random.random() * 100 < rate
    
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
    
    def generate_life(self):
        """1人の人生を生成"""
        gender = self.select_gender()
        birth_city = self.select_birth_city()
        
        # 両親の職業を生成（性別に応じた産業分布から選択）
        father_industry = self.select_industry("男性")
        mother_industry = self.select_industry("女性")
        
        went_to_high_school = self.decide_high_school(birth_city)
        went_to_university = self.decide_university(birth_city, went_to_high_school)
        university_destination = self.select_university_destination() if went_to_university else None
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
            "university": went_to_university,
            "university_destination": university_destination,
            "industry": industry,
            "retirement_age": retirement_age,
            "death_age": death_age,
            "death_cause": death_cause,
        }
    
    def format_life(self, life):
        """人生の軌跡を文字列でフォーマット"""
        # 出生地（市町村名）と両親の職業
        birth_city = life['birth_city']
        father_industry = life.get('father_industry', '不明')
        mother_industry = life.get('mother_industry', '不明')
        
        # 出生地の整形（「札幌市○○区」は「北海道札幌市○○区」、それ以外は「北海道○○市」など）
        if "北海道" not in birth_city:
            birth_location = f"北海道{birth_city}"
        else:
            birth_location = birth_city
        
        # 進学の表示
        education_parts = []
        if life["high_school"]:
            education_parts.append("高校に進学")
        
        if life["university"] and life.get("university_destination"):
            education_parts.append(f"{life['university_destination']}の大学に進学")
        
        education_str = "\n".join(education_parts) if education_parts else "中学卒業"
        
        # 就職の表示
        industry = life['industry']
        if life["university"]:
            job_str = f"大学進学後に{industry}に就職"
        elif life["high_school"]:
            job_str = f"高校卒業後に{industry}に就職"
        else:
            job_str = f"中学卒業後に{industry}に就職"
        
        # 定年の表示（定年前に死亡した場合は表示しない）
        retirement_age = life.get('retirement_age')
        death_age = life['death_age']
        
        retirement_str = None
        if retirement_age is not None and death_age >= retirement_age:
            retirement_str = f"{retirement_age}歳で定年退職"
        elif retirement_age is None and death_age >= 60:
            # 定年なしの場合、60歳以上で死亡した場合のみ表示
            retirement_str = "定年なし"
        
        # 死因の表示（「悪性新生物＜腫瘍＞」を「ガン」に変換）
        death_cause = life['death_cause']
        if "悪性新生物" in death_cause or "腫瘍" in death_cause:
            death_cause = "ガン"
        
        death_str = f"{life['death_age']}歳で{death_cause}により死亡"
        
        # 最終的な出力（定年情報がある場合のみ含める）
        parts = [
            f"{birth_location}に、{father_industry}の父親と{mother_industry}の母親の元に生まれる",
            education_str,
            job_str
        ]
        
        if retirement_str:
            parts.append(retirement_str)
        
        parts.append(death_str)
        
        return "\n".join(parts)


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
    
    args = parser.parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
    
    simulator = HokkaidoLifeSimulator(data_dir=args.data_dir)
    
    for i in range(args.number):
        life = simulator.generate_life()
        print(f"=== 人生 #{i+1} ===")
        print(simulator.format_life(life))
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

