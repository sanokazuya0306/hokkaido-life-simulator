"""
データローダー

CSVファイルからシミュレーションに必要なデータを読み込む
"""

import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any


class DataLoader:
    """シミュレーションデータの読み込みを担当するクラス"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        初期化
        
        Args:
            data_dir: データファイルが格納されているディレクトリ
                     Noneの場合はスクリプトと同じディレクトリのdataフォルダ
        """
        if data_dir is None:
            # このファイルの親ディレクトリ（src）の親（hokkaido_life_simulator）のdata
            self.data_dir = Path(__file__).parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        # データ格納用
        self.birth_data: List[Dict[str, Any]] = []
        self.high_school_rates: Dict[str, float] = {}
        self.high_schools_by_city: Dict[str, List[str]] = {}
        self.university_rates: Dict[str, float] = {}
        self.university_destinations: List[Dict[str, Any]] = []
        self.universities_by_prefecture: Dict[str, List[Dict[str, Any]]] = {}
        self.workers_by_industry: List[Dict[str, Any]] = []
        self.workers_by_gender: Dict[str, int] = {}
        self.workers_by_industry_gender: Dict[str, Dict[str, int]] = {}
        self.retirement_age_distribution: List[Dict[str, Any]] = []
        self.death_by_age: List[Dict[str, Any]] = []
        self.death_by_cause: List[Dict[str, Any]] = []
    
    def load_all(self) -> None:
        """すべてのデータファイルを読み込む"""
        self._load_birth_data()
        self._load_high_school_rates()
        self._load_high_schools()
        self._load_university_rates()
        self._load_university_destinations()
        self._load_universities_by_prefecture()
        self._load_workers_by_industry()
        self._load_workers_by_gender()
        self._load_workers_by_industry_gender()
        self._load_retirement_age()
        self._load_death_by_age()
        self._load_death_by_cause()
    
    def _load_birth_data(self) -> None:
        """出生数データを読み込む"""
        birth_file = self.data_dir / "birth_by_city.csv"
        if birth_file.exists():
            with open(birth_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    city = row.get("市町村", "").strip()
                    birth_count = int(row.get("出生数", 0))
                    # 「北海道」や「北　海　道」などの総計行、および「札幌市」全体をスキップ
                    if city and birth_count > 0 and city not in ["北海道", "北　海　道", "全道", "全道計", "札幌市"]:
                        self.birth_data.append({"city": city, "count": birth_count})
        else:
            print(f"警告: {birth_file} が見つかりません。サンプルデータを使用します。", file=sys.stderr)
            self.birth_data = [
                {"city": "札幌市", "count": 10000},
                {"city": "旭川市", "count": 2000},
                {"city": "函館市", "count": 1500},
            ]
    
    def _load_high_school_rates(self) -> None:
        """高校進学率データを読み込む"""
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
    
    def _load_high_schools(self) -> None:
        """市町村別高校データを読み込む"""
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
    
    def _load_university_rates(self) -> None:
        """大学進学率データを読み込む"""
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
    
    def _load_university_destinations(self) -> None:
        """大学進学先の都道府県データを読み込む"""
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
    
    def _load_universities_by_prefecture(self) -> None:
        """都道府県別大学データを読み込む"""
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
    
    def _load_workers_by_industry(self) -> None:
        """産業別労働者数データを読み込む"""
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
    
    def _load_workers_by_gender(self) -> None:
        """性別別労働者数データを読み込む"""
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
            self.workers_by_gender = {"男性": 1430000, "女性": 1210000}
    
    def _load_workers_by_industry_gender(self) -> None:
        """性別×産業別労働者数データを読み込む"""
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
            self.workers_by_industry_gender = {}
    
    def _load_retirement_age(self) -> None:
        """定年年齢データを読み込む"""
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
    
    def _load_death_by_age(self) -> None:
        """年齢別死亡者数データを読み込む"""
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
            self.death_by_age = []
            for age in range(0, 100):
                count = max(1, int(100 * (age / 100) ** 3))
                self.death_by_age.append({"age": age, "count": count})
    
    def _load_death_by_cause(self) -> None:
        """死因別死亡者数データを読み込む"""
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
    
    def get_dataset_info(self) -> List[Dict[str, str]]:
        """使用しているデータセットの情報を返す"""
        return [
            {
                "name": "1. 市町村別出生数",
                "official_name": "市区町村別人口、人口動態及び世帯数（令和6年）",
                "source": "北海道総合政策部地域行政局市町村課",
                "year": "2024年",
                "count": f"{len(self.birth_data)}市町村"
            },
            {
                "name": "2. 市町村別高校進学率",
                "official_name": "学校基本調査 中学校卒業後の進路別卒業者数（令和6年度）",
                "source": "北海道教育委員会",
                "year": "2024年度",
                "count": f"{len(self.high_school_rates)}市町村"
            },
            {
                "name": "3. 市町村別大学進学率",
                "official_name": "学校基本調査 高等学校卒業後の進路別卒業者数（令和6年度）",
                "source": "北海道教育委員会",
                "year": "2024年度",
                "count": f"{len(self.university_rates)}市町村"
            },
            {
                "name": "4. 大学進学先都道府県",
                "official_name": "学校基本調査 大学・短期大学への都道府県別入学者数（令和6年度）",
                "source": "北海道教育委員会",
                "year": "2024年度",
                "count": f"{len(self.university_destinations)}都道府県"
            },
            {
                "name": "5. 産業別労働者数",
                "official_name": "労働力調査 第2表 産業別就業者数・雇用者数（令和6年平均）",
                "source": "北海道総合政策部計画局統計課",
                "year": "2024年",
                "count": f"{len(self.workers_by_industry)}産業"
            },
            {
                "name": "6. 性別別労働者数",
                "official_name": "労働力調査（令和6年平均）",
                "source": "北海道総合政策部計画局統計課",
                "year": "2024年",
                "count": f"{len(self.workers_by_gender)}区分",
            },
            {
                "name": "7. 性別×産業別労働者数",
                "official_name": "労働力調査（令和6年平均）+ 全国傾向から推定",
                "source": "北海道総合政策部計画局統計課 / 総務省統計局",
                "year": "2024年",
                "count": f"{len(self.workers_by_industry_gender)}産業"
            },
            {
                "name": "8. 定年年齢分布",
                "official_name": "就労条件総合調査結果の概況（令和4年）",
                "source": "厚生労働省",
                "year": "2022年",
                "count": f"{len(self.retirement_age_distribution)}区分"
            },
            {
                "name": "9. 年齢別死亡者数",
                "official_name": "北海道保健統計年報 第24表 死亡数（令和4年）",
                "source": "北海道保健福祉部総務課",
                "year": "2022年",
                "count": f"{len(self.death_by_age)}年齢"
            },
            {
                "name": "10. 死因別死亡者数",
                "official_name": "北海道保健統計年報 表3 死亡数・死亡率（令和4年）",
                "source": "北海道保健福祉部総務課",
                "year": "2022年",
                "count": f"{len(self.death_by_cause)}種類"
            }
        ]
