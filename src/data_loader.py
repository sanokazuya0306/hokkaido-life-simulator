"""
データローダー

CSVファイルからシミュレーションに必要なデータを読み込む
"""

import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any


# 地域設定
REGION_CONFIG = {
    "hokkaido": {
        "name": "北海道",
        "data_subdir": None,  # data/ 直下（後方互換性のため）
        "university_destinations_file": "hokkaido_university_destinations.csv",
    },
    "tokyo": {
        "name": "東京",
        "data_subdir": "tokyo",  # data/tokyo/
        "university_destinations_file": "tokyo_university_destinations.csv",
    },
}


class DataLoader:
    """シミュレーションデータの読み込みを担当するクラス"""
    
    def __init__(self, data_dir: Optional[Path] = None, region: str = "hokkaido"):
        """
        初期化
        
        Args:
            data_dir: データファイルが格納されているディレクトリ
                     Noneの場合はスクリプトと同じディレクトリのdataフォルダ
            region: 地域識別子 ("hokkaido" または "tokyo")
        """
        self.region = region
        if region not in REGION_CONFIG:
            raise ValueError(f"未対応の地域: {region}。対応地域: {list(REGION_CONFIG.keys())}")
        
        self.region_config = REGION_CONFIG[region]
        self.region_name = self.region_config["name"]
        
        # ベースデータディレクトリ
        if data_dir is None:
            base_data_dir = Path(__file__).parent.parent / "data"
        else:
            base_data_dir = Path(data_dir)
        
        # 地域別サブディレクトリの設定
        if self.region_config["data_subdir"]:
            self.data_dir = base_data_dir / self.region_config["data_subdir"]
        else:
            self.data_dir = base_data_dir
        
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
        self.income_by_city: Dict[str, List[Dict[str, Any]]] = {}
        self.income_ranges: List[str] = []
        self.education_level_by_gender: Dict[str, List[Dict[str, Any]]] = {}
        self.parent_education_effect: Dict[str, Dict[str, float]] = {}
        self.parent_income_effect: Dict[str, Dict[str, float]] = {}
    
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
        self._load_income_by_city()
        self._load_education_level()
        self._load_parent_education_effect()
        self._load_parent_income_effect()
    
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
        university_dest_file = self.data_dir / self.region_config["university_destinations_file"]
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
    
    def _load_income_by_city(self) -> None:
        """市区町村別世帯年収データを読み込む"""
        income_file = self.data_dir / "income_by_city.csv"
        if income_file.exists():
            with open(income_file, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                # ヘッダーから年収階級を取得（最初の列は「市町村」）
                self.income_ranges = header[1:]
                
                for row in reader:
                    if len(row) > 1:
                        city = row[0].strip()
                        # 各年収階級の世帯数を読み込む
                        income_distribution = []
                        for i, income_range in enumerate(self.income_ranges):
                            try:
                                count = int(row[i + 1]) if row[i + 1] else 0
                            except (ValueError, IndexError):
                                count = 0
                            income_distribution.append({
                                "range": income_range,
                                "count": count
                            })
                        if city:
                            self.income_by_city[city] = income_distribution
        else:
            print(f"警告: {income_file} が見つかりません。デフォルトの年収分布を使用します。", file=sys.stderr)
            # デフォルトの年収階級
            self.income_ranges = [
                "100万円未満", "100〜200万円", "200〜300万円", "300〜400万円",
                "400〜500万円", "500〜700万円", "700〜1000万円", "1000〜1500万円", "1500万円以上"
            ]
            # 北海道全体の分布をデフォルトとして設定
            default_counts = [160600, 196800, 268400, 285200, 228600, 340800, 248200, 95400, 26800]
            self.income_by_city["北海道（デフォルト）"] = [
                {"range": r, "count": c} for r, c in zip(self.income_ranges, default_counts)
            ]
    
    def _load_education_level(self) -> None:
        """性別別最終学歴データを読み込む"""
        education_file = self.data_dir / "education_level.csv"
        if education_file.exists():
            with open(education_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    gender = row.get("性別", "").strip()
                    education = row.get("最終学歴", "").strip()
                    ratio = float(row.get("割合", 0))
                    if gender and education and ratio > 0:
                        if gender not in self.education_level_by_gender:
                            self.education_level_by_gender[gender] = []
                        self.education_level_by_gender[gender].append({
                            "education": education,
                            "ratio": ratio
                        })
        else:
            print(f"警告: {education_file} が見つかりません。デフォルト値を使用します。", file=sys.stderr)
            # 北海道の推定データ（国勢調査2020年全国データ + 北海道補正）
            self.education_level_by_gender = {
                "男性": [
                    {"education": "中学校", "ratio": 8.5},
                    {"education": "高校", "ratio": 42.0},
                    {"education": "短大・専門学校", "ratio": 12.0},
                    {"education": "大学", "ratio": 33.5},
                    {"education": "大学院", "ratio": 4.0},
                ],
                "女性": [
                    {"education": "中学校", "ratio": 7.0},
                    {"education": "高校", "ratio": 44.0},
                    {"education": "短大・専門学校", "ratio": 26.0},
                    {"education": "大学", "ratio": 21.5},
                    {"education": "大学院", "ratio": 1.5},
                ],
            }
    
    def _load_parent_education_effect(self) -> None:
        """親学歴が子学歴に与える影響データを読み込む"""
        effect_file = self.data_dir / "parent_education_effect.csv"
        if effect_file.exists():
            with open(effect_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    parent_edu = row.get("親学歴", "").strip()
                    hs_modifier = float(row.get("高校進学補正", 1.0))
                    univ_modifier = float(row.get("大学進学補正", 1.0))
                    if parent_edu:
                        self.parent_education_effect[parent_edu] = {
                            "high_school_modifier": hs_modifier,
                            "university_modifier": univ_modifier
                        }
        else:
            print(f"警告: {effect_file} が見つかりません。デフォルト値を使用します。", file=sys.stderr)
            # デフォルト: 統計に基づく親学歴の影響係数
            self.parent_education_effect = {
                "中学校": {"high_school_modifier": 0.95, "university_modifier": 0.40},
                "高校": {"high_school_modifier": 1.00, "university_modifier": 0.70},
                "短大・専門学校": {"high_school_modifier": 1.00, "university_modifier": 0.90},
                "大学": {"high_school_modifier": 1.00, "university_modifier": 1.30},
                "大学院": {"high_school_modifier": 1.00, "university_modifier": 1.50},
            }
    
    def _load_parent_income_effect(self) -> None:
        """親の世帯年収が子学歴に与える影響データを読み込む"""
        effect_file = self.data_dir / "parent_income_effect.csv"
        if effect_file.exists():
            with open(effect_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    income_range = row.get("年収階級", "").strip()
                    hs_modifier = float(row.get("高校進学補正", 1.0))
                    univ_modifier = float(row.get("大学進学補正", 1.0))
                    if income_range:
                        self.parent_income_effect[income_range] = {
                            "high_school_modifier": hs_modifier,
                            "university_modifier": univ_modifier
                        }
        else:
            print(f"警告: {effect_file} が見つかりません。デフォルト値を使用します。", file=sys.stderr)
            # デフォルト: 21世紀出生児縦断調査等に基づく世帯年収の影響係数
            self.parent_income_effect = {
                "100万円未満": {"high_school_modifier": 0.92, "university_modifier": 0.55},
                "100〜200万円": {"high_school_modifier": 0.94, "university_modifier": 0.60},
                "200〜300万円": {"high_school_modifier": 0.96, "university_modifier": 0.70},
                "300〜400万円": {"high_school_modifier": 0.98, "university_modifier": 0.80},
                "400〜500万円": {"high_school_modifier": 1.00, "university_modifier": 0.90},
                "500〜700万円": {"high_school_modifier": 1.00, "university_modifier": 1.00},
                "700〜1000万円": {"high_school_modifier": 1.00, "university_modifier": 1.10},
                "1000〜1500万円": {"high_school_modifier": 1.00, "university_modifier": 1.20},
                "1500万円以上": {"high_school_modifier": 1.00, "university_modifier": 1.30},
            }
    
    def get_dataset_info(self) -> List[Dict[str, str]]:
        """使用しているデータセットの情報を返す"""
        # 地域によってデータソースの説明を切り替え
        if self.region == "hokkaido":
            birth_source = "北海道総合政策部地域行政局市町村課"
            education_source = "北海道教育委員会"
            labor_source = "北海道総合政策部計画局統計課"
            health_source = "北海道保健福祉部総務課"
            region_note = "北海道"
        else:  # tokyo
            birth_source = "東京都総務局統計部"
            education_source = "東京都教育委員会"
            labor_source = "東京都産業労働局"
            health_source = "東京都福祉保健局"
            region_note = "東京都"
        
        return [
            {
                "name": "1. 市区町村別出生数",
                "official_name": f"市区町村別人口、人口動態及び世帯数（令和6年）",
                "source": birth_source,
                "year": "2024年",
                "count": f"{len(self.birth_data)}市区町村"
            },
            {
                "name": "2. 市区町村別高校進学率",
                "official_name": "学校基本調査 中学校卒業後の進路別卒業者数（令和6年度）",
                "source": education_source,
                "year": "2024年度",
                "count": f"{len(self.high_school_rates)}市区町村"
            },
            {
                "name": "3. 市区町村別大学進学率",
                "official_name": "学校基本調査 高等学校卒業後の進路別卒業者数（令和6年度）",
                "source": education_source,
                "year": "2024年度",
                "count": f"{len(self.university_rates)}市区町村"
            },
            {
                "name": "4. 大学進学先都道府県",
                "official_name": "学校基本調査 大学・短期大学への都道府県別入学者数（令和6年度）",
                "source": education_source,
                "year": "2024年度",
                "count": f"{len(self.university_destinations)}都道府県"
            },
            {
                "name": "5. 産業別労働者数",
                "official_name": "労働力調査 第2表 産業別就業者数・雇用者数（令和6年平均）",
                "source": labor_source,
                "year": "2024年",
                "count": f"{len(self.workers_by_industry)}産業"
            },
            {
                "name": "6. 性別別労働者数",
                "official_name": "労働力調査（令和6年平均）",
                "source": labor_source,
                "year": "2024年",
                "count": f"{len(self.workers_by_gender)}区分",
            },
            {
                "name": "7. 性別×産業別労働者数",
                "official_name": "労働力調査（令和6年平均）+ 全国傾向から推定",
                "source": f"{labor_source} / 総務省統計局",
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
                "official_name": f"{region_note}保健統計年報 第24表 死亡数（令和4年）",
                "source": health_source,
                "year": "2022年",
                "count": f"{len(self.death_by_age)}年齢"
            },
            {
                "name": "10. 死因別死亡者数",
                "official_name": f"{region_note}保健統計年報 表3 死亡数・死亡率（令和4年）",
                "source": health_source,
                "year": "2022年",
                "count": f"{len(self.death_by_cause)}種類"
            },
            {
                "name": "11. 市区町村別世帯年収分布",
                "official_name": "住宅・土地統計調査 表44-4 世帯の年間収入階級別普通世帯数",
                "source": "総務省統計局",
                "year": "2018年（平成30年）",
                "count": f"{len(self.income_by_city)}市区町村"
            },
            {
                "name": "12. 性別別最終学歴分布",
                "official_name": "令和2年国勢調査 最終卒業学校の種類",
                "source": f"総務省統計局（{region_note}推定値）",
                "year": "2020年",
                "count": f"{len(self.education_level_by_gender)}区分"
            },
            {
                "name": "13. 親学歴が子学歴に与える影響",
                "official_name": "OECD Education at a Glance 2025等に基づく推定値",
                "source": "OECD / 文部科学省 / SSM調査等より推定",
                "year": "2025年",
                "count": f"{len(self.parent_education_effect)}区分",
                "details": self._get_parent_education_effect_details(),
                "readme": "README_parent_education_effect.md"
            },
            {
                "name": "14. 親の世帯年収が子学歴に与える影響",
                "official_name": "21世紀出生児縦断調査・東大学生生活実態調査等に基づく推定値",
                "source": "文部科学省 / 東京大学 / 厚生労働省等より推定",
                "year": "2024年",
                "count": f"{len(self.parent_income_effect)}区分",
                "details": self._get_parent_income_effect_details(),
                "readme": "README_parent_income_effect.md"
            }
        ]
    
    def _get_parent_education_effect_details(self) -> Dict[str, Any]:
        """親学歴効果の詳細情報を返す"""
        return {
            "description": "親の最終学歴が子の進学率に与える影響を補正係数として定義",
            "methodology": "両親の学歴から補正係数の平均を取り、地域別基準進学率に乗じる",
            "formula": "調整後進学率 = 地域別基準進学率 × (父親補正係数 + 母親補正係数) / 2 × 世帯年収補正係数",
            "coefficients": self.parent_education_effect,
            "references": [
                {
                    "name": "OECD Education at a Glance 2025（日本）",
                    "finding": "親が高等教育修了の場合、子の高等教育修了率は約72%（親が高卒の場合は約43%）",
                    "url": "https://www.oecd.org/en/publications/education-at-a-glance-2025_1a3543e2-en/japan_8f0a8541-en.html"
                },
                {
                    "name": "ベネッセ教育総合研究所「子どもの生活と学びに関する親子調査」",
                    "finding": "父母ともに大学卒の家庭では高1夏までに大学進学希望を形成する割合が約52%（非大学卒は約25%）",
                    "url": "https://benesse.jp/berd/special/childedu_researcher/yamaguchi.html"
                },
                {
                    "name": "SSM調査（社会階層と社会移動全国調査）",
                    "finding": "親の学歴が子の教育達成に影響を与える傾向は一貫して確認されている",
                    "url": "https://www.jstage.jst.go.jp/article/jsr/59/4/59_4_682/_article/-char/ja"
                }
            ],
            "notes": [
                "推定値であり、特定の論文から直接引用した数値ではない",
                "OECDデータでは親学歴による差は約1.7倍だが、保守的な補正係数を採用"
            ]
        }
    
    def _get_parent_income_effect_details(self) -> Dict[str, Any]:
        """世帯年収効果の詳細情報を返す"""
        return {
            "description": "親の世帯年収が子の進学率に与える影響を補正係数として定義",
            "methodology": "世帯年収と親学歴の補正係数の平均を取り、過度な補正を避ける",
            "formula": "調整後進学率 = 地域別基準進学率 × (親学歴補正 + 世帯年収補正) / 2",
            "coefficients": self.parent_income_effect,
            "references": [
                {
                    "name": "文部科学省「21世紀出生児縦断調査」分析",
                    "finding": "貧困持続群の大学進学率35.4% vs 非貧困持続群63.4%（約1.8倍の差）",
                    "url": "https://www.mext.go.jp/b_menu/toukei/chousa08/21seiki/mext_02723.html",
                    "data": {
                        "非貧困持続群": "63.4%",
                        "貧困脱出群": "43.0%",
                        "貧困突入群": "39.1%",
                        "貧困持続群": "35.4%"
                    }
                },
                {
                    "name": "東京大学「学生生活実態調査」（2023年度・第72回）",
                    "finding": "東大生の42.2%が世帯年収950万円以上の家庭出身（全国平均は約536万円）",
                    "url": "https://www.u-tokyo.ac.jp/ja/students/welfare/h02.html",
                    "data": {
                        "450万円未満": "9.4%",
                        "750万円〜950万円未満": "12.3%",
                        "950万円〜1050万円未満": "9.3%",
                        "1050万円〜1250万円未満": "12.5%",
                        "1250万円以上": "20.4%",
                        "分からない": "26.4%"
                    }
                },
                {
                    "name": "高等教育の修学支援新制度の効果分析",
                    "finding": "準対象世帯（年収210-370万円）で進学率が約61.5%から約70.7%に向上",
                    "url": "https://univ-journal.jp/215904/"
                },
                {
                    "name": "厚生労働省「国民生活基礎調査」（2024年）",
                    "finding": "全国平均世帯年収は約536万円（基準値として設定）",
                    "url": "https://www.mhlw.go.jp/toukei/list/20-21.html"
                },
                {
                    "name": "高校ランクの媒介効果に関する研究（2024年）",
                    "finding": "家族所得が大学進学に与える影響の約25%が高校の選抜性を経由",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/39542611/"
                }
            ],
            "notes": [
                "「世帯年収別の大学進学率」の直接的な公的統計は日本では限定的であり、関連研究から推定",
                "親学歴と世帯年収には相関があるため、両方の補正係数の平均を取る",
                "高等教育の修学支援新制度（2020年〜）により、低所得層の進学率は改善傾向"
            ]
        }
