"""
出生シミュレーター

出生地と性別の決定を担当
"""

import random
from typing import Dict, List, Any, Optional, Tuple


class BirthSimulator:
    """出生に関するシミュレーションを担当するクラス"""
    
    def __init__(
        self,
        birth_data: List[Dict[str, Any]],
        workers_by_gender: Dict[str, int],
        workers_by_industry_gender: Dict[str, Dict[str, int]],
        workers_by_industry: List[Dict[str, Any]],
        income_by_city: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        education_level_by_gender: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        region: str = "hokkaido",
    ):
        """
        初期化
        
        Args:
            birth_data: 市町村別出生数データ
            workers_by_gender: 性別別労働者数
            workers_by_industry_gender: 性別×産業別労働者数
            workers_by_industry: 産業別労働者数
            income_by_city: 市町村別世帯年収分布
            education_level_by_gender: 性別別最終学歴分布
            region: 地域識別子 ("hokkaido" または "tokyo")
        """
        self.birth_data = birth_data
        self.workers_by_gender = workers_by_gender
        self.workers_by_industry_gender = workers_by_industry_gender
        self.workers_by_industry = workers_by_industry
        self.income_by_city = income_by_city or {}
        self.education_level_by_gender = education_level_by_gender or {}
        self.region = region
    
    def select_birth_city(self) -> str:
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
                # 北海道の場合のみ、札幌市の区を「札幌市○○区」の形式に変換
                if self.region == "hokkaido" and city.endswith("区") and "市" not in city:
                    city = f"札幌市{city}"
                return city
        
        # 最後の要素も同様に処理
        city = self.birth_data[-1]["city"]
        if self.region == "hokkaido" and city.endswith("区") and "市" not in city:
            city = f"札幌市{city}"
        return city
    
    def select_gender(self) -> str:
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
    
    def select_parent_industry(self, gender: str) -> str:
        """
        親の職業（産業）を選択
        
        Args:
            gender: 親の性別（"男性" or "女性"）
            
        Returns:
            産業名
        """
        # 性別×産業データがある場合
        if self.workers_by_industry_gender:
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
        
        # 性別データがない場合は全体データを使用
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
    
    # 児童のいる世帯向け年収補正係数
    # 全世帯データには高齢者世帯（年金生活者）が含まれ低年収層が多くなる
    # 児童のいる世帯の平均所得は約812万円（全世帯536万円より高い）
    # 国民生活基礎調査（令和5年）の五分位階級分布を参考に補正
    # 
    # 補正の根拠:
    # - 児童のいる世帯の第1五分位（下位20%）は全世帯の約4%相当
    # - 児童のいる世帯の第5五分位（上位20%）は全世帯の約43%相当
    # - 低年収層を大幅に減らし、中〜高年収層を増やす
    CHILD_HOUSEHOLD_INCOME_ADJUSTMENT = {
        "100万円未満": 0.15,      # 大幅減（高齢単身世帯が多い層）
        "100〜200万円": 0.25,     # 大幅減
        "200〜300万円": 0.50,     # 減少
        "300〜400万円": 0.85,     # やや減少
        "400〜500万円": 1.10,     # やや増加
        "500〜600万円": 1.30,     # 増加
        "500〜700万円": 1.30,     # 増加（表記揺れ対応）
        "600〜800万円": 1.50,     # 増加
        "700〜1000万円": 1.60,    # 増加
        "800〜1000万円": 1.60,    # 増加（表記揺れ対応）
        "1000〜1500万円": 1.80,   # 大幅増加
        "1500万円以上": 2.00,     # 大幅増加
        # 東京都向けの追加レンジ
        "400〜600万円": 1.20,
    }
    
    def select_household_income(self, city: str) -> str:
        """
        世帯年収レンジを選択（児童のいる世帯向けに補正）
        
        住宅・土地統計調査の全世帯データを、国民生活基礎調査の
        「児童のいる世帯」分布に近づけるよう補正係数を適用。
        
        Args:
            city: 出生地の市町村名
            
        Returns:
            年収レンジの文字列（例: "300〜400万円"）
        """
        # 市町村名の正規化（「札幌市○○区」→「札幌市○○区」）
        normalized_city = city
        
        # 札幌市の区の場合、そのまま検索
        if "札幌市" in city:
            normalized_city = city
        
        # 該当市町村のデータを取得
        income_distribution = self.income_by_city.get(normalized_city)
        
        # 見つからない場合はデフォルト分布を使用
        if not income_distribution:
            default_key = "北海道（デフォルト）" if self.region == "hokkaido" else "東京都（デフォルト）"
            income_distribution = self.income_by_city.get(default_key)
        
        # それでも見つからない場合はデフォルト値を返す
        if not income_distribution:
            return "400〜500万円"  # 児童世帯の中央値付近
        
        # 児童のいる世帯向けに補正係数を適用
        adjusted_distribution = []
        for item in income_distribution:
            income_range = item["range"]
            original_count = item["count"]
            
            # 補正係数を取得（デフォルトは1.0）
            adjustment = self.CHILD_HOUSEHOLD_INCOME_ADJUSTMENT.get(income_range, 1.0)
            adjusted_count = original_count * adjustment
            
            adjusted_distribution.append({
                "range": income_range,
                "count": adjusted_count
            })
        
        # 重み付き選択
        total_count = sum(item["count"] for item in adjusted_distribution)
        if total_count == 0:
            return "400〜500万円"
        
        rand = random.uniform(0, total_count)
        cumulative = 0
        for item in adjusted_distribution:
            cumulative += item["count"]
            if rand <= cumulative:
                return item["range"]
        
        return adjusted_distribution[-1]["range"]
    
    def select_parent_education(self, gender: str) -> str:
        """
        親の最終学歴を選択
        
        Args:
            gender: 親の性別（"男性" or "女性"）
            
        Returns:
            最終学歴（例: "高校", "大学" など）
        """
        # 性別の学歴データを取得
        education_data = self.education_level_by_gender.get(gender)
        
        if not education_data:
            # データがない場合はデフォルト値を使用（education_level.csvの統計データに基づく）
            # 出典: 国勢調査2020年データ（全国平均、性別別）
            if gender == "女性":
                default_data = [
                    {"education": "中学校", "ratio": 7.0},
                    {"education": "高校", "ratio": 44.0},
                    {"education": "短大・専門学校", "ratio": 26.0},
                    {"education": "大学", "ratio": 21.5},
                    {"education": "大学院", "ratio": 1.5},
                ]
            else:  # 男性（デフォルト）
                default_data = [
                    {"education": "中学校", "ratio": 8.5},
                    {"education": "高校", "ratio": 42.0},
                    {"education": "短大・専門学校", "ratio": 12.0},
                    {"education": "大学", "ratio": 33.5},
                    {"education": "大学院", "ratio": 4.0},
                ]
            education_data = default_data
        
        # 重み付き選択
        total_ratio = sum(item["ratio"] for item in education_data)
        if total_ratio == 0:
            return "高校"
        
        rand = random.uniform(0, total_ratio)
        cumulative = 0
        for item in education_data:
            cumulative += item["ratio"]
            if rand <= cumulative:
                return item["education"]
        
        return education_data[-1]["education"]
