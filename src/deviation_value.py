"""
偏差値計算モジュール

個人の学力偏差値を計算し、高校・大学の選択に使用する
偏差値は環境要因（親学歴、世帯年収など）に基づいて生成される
"""

import random
import math
from typing import Dict, Any, Optional


# 偏差値ランク定義
DEVIATION_TIERS = {
    "top": {"min": 70, "label": "上位層（偏差値70+）", "percentile": 2.3},
    "high": {"min": 60, "label": "高位層（偏差値60-69）", "percentile": 15.9},
    "middle": {"min": 50, "label": "中位層（偏差値50-59）", "percentile": 50.0},
    "low": {"min": 40, "label": "低位層（偏差値40-49）", "percentile": 84.1},
    "bottom": {"min": 0, "label": "下位層（偏差値40未満）", "percentile": 100.0},
}

# 高校偏差値ランク
HIGH_SCHOOL_DEVIATION_TIERS = {
    "進学校": {"min": 65, "max": 80},
    "準進学校": {"min": 55, "max": 64},
    "標準校": {"min": 45, "max": 54},
    "その他": {"min": 35, "max": 44},
}

# 大学偏差値ランク（既存のUNIVERSITY_RANKSと連携）
# 大学入学者の偏差値分布に基づく
UNIVERSITY_DEVIATION_MAPPING = {
    "S": {"min": 70, "max": 80, "label": "難関（東大・京大・旧帝大・早慶）", "population_rate": 0.03},
    "A": {"min": 60, "max": 69, "label": "上位（上位国立・MARCH）", "population_rate": 0.12},
    "B": {"min": 52, "max": 59, "label": "中堅（中堅国立・日東駒専）", "population_rate": 0.25},
    "C": {"min": 45, "max": 51, "label": "標準（その他国立・中堅私立）", "population_rate": 0.35},
    "D": {"min": 35, "max": 44, "label": "その他私立", "population_rate": 0.25},
}

# 親学歴による偏差値補正
PARENT_EDUCATION_DEVIATION_MODIFIER = {
    "大学院": 8.0,
    "大学院卒": 8.0,
    "大学": 5.0,
    "大学卒": 5.0,
    "短大・専門学校": 1.0,
    "短大・専門卒": 1.0,
    "短大・専門": 1.0,
    "高校": -2.0,
    "高校卒": -2.0,
    "中学校": -5.0,
    "中学卒": -5.0,
    "中学": -5.0,
    "default": 0.0,
}

# 世帯年収による偏差値補正
HOUSEHOLD_INCOME_DEVIATION_MODIFIER = {
    "1500万円以上": 5.0,
    "1000〜1500万円": 4.0,
    "1000万円以上": 4.0,
    "700〜1000万円": 2.5,
    "500〜700万円": 1.0,
    "400〜500万円": 0.0,
    "300〜400万円": -1.0,
    "200〜300万円": -2.0,
    "100〜200万円": -3.0,
    "100万円未満": -4.0,
    "default": 0.0,
}

# 地域による偏差値補正（教育機会の差）
REGION_DEVIATION_MODIFIER = {
    "東京": 2.0,
    "北海道": -1.0,
    "default": 0.0,
}


class DeviationValueCalculator:
    """偏差値を計算するクラス"""
    
    @staticmethod
    def calculate_individual_deviation(
        father_education: Optional[str] = None,
        mother_education: Optional[str] = None,
        household_income: Optional[str] = None,
        birth_city: Optional[str] = None,
    ) -> float:
        """
        個人の学力偏差値を計算する
        
        偏差値は平均50、標準偏差10の正規分布に従う
        環境要因により期待値が上下する
        
        Args:
            father_education: 父親の最終学歴
            mother_education: 母親の最終学歴
            household_income: 世帯年収
            birth_city: 出生地
            
        Returns:
            偏差値（30-80程度の範囲）
        """
        # 基準値: 平均50
        base_deviation = 50.0
        
        # 親学歴による補正（両親の平均）
        father_mod = PARENT_EDUCATION_DEVIATION_MODIFIER.get(
            father_education, 
            PARENT_EDUCATION_DEVIATION_MODIFIER["default"]
        )
        mother_mod = PARENT_EDUCATION_DEVIATION_MODIFIER.get(
            mother_education, 
            PARENT_EDUCATION_DEVIATION_MODIFIER["default"]
        )
        parent_education_modifier = (father_mod + mother_mod) / 2
        
        # 世帯年収による補正
        income_modifier = HOUSEHOLD_INCOME_DEVIATION_MODIFIER.get(
            household_income,
            HOUSEHOLD_INCOME_DEVIATION_MODIFIER["default"]
        )
        
        # 地域による補正
        region_modifier = 0.0
        if birth_city:
            if "東京" in birth_city or "区" in birth_city:
                region_modifier = REGION_DEVIATION_MODIFIER["東京"]
            else:
                region_modifier = REGION_DEVIATION_MODIFIER["北海道"]
        
        # 期待値を計算
        expected_deviation = base_deviation + parent_education_modifier + income_modifier + region_modifier
        
        # 標準正規分布に従う乱数を生成（Box-Muller法）
        u1 = random.random()
        u2 = random.random()
        z = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        
        # 標準偏差8の正規分布（環境要因で多少圧縮）
        std_dev = 8.0
        deviation_value = expected_deviation + z * std_dev
        
        # 30-80の範囲にクリップ
        deviation_value = max(30.0, min(80.0, deviation_value))
        
        return round(deviation_value, 1)
    
    @staticmethod
    def get_deviation_tier(deviation_value: float) -> str:
        """
        偏差値からティアを取得
        
        Args:
            deviation_value: 偏差値
            
        Returns:
            ティア名（"top", "high", "middle", "low", "bottom"）
        """
        if deviation_value >= 70:
            return "top"
        elif deviation_value >= 60:
            return "high"
        elif deviation_value >= 50:
            return "middle"
        elif deviation_value >= 40:
            return "low"
        else:
            return "bottom"
    
    @staticmethod
    def get_expected_university_rank(deviation_value: float) -> str:
        """
        偏差値から期待される大学ランクを取得
        
        Args:
            deviation_value: 偏差値
            
        Returns:
            大学ランク（"S", "A", "B", "C", "D"）
        """
        # 確率的に決定（偏差値に応じてランクが上下する可能性）
        if deviation_value >= 70:
            # 偏差値70+: Sランク70%, Aランク30%
            return "S" if random.random() < 0.7 else "A"
        elif deviation_value >= 60:
            # 偏差値60-69: Sランク10%, Aランク60%, Bランク30%
            rand = random.random()
            if rand < 0.10:
                return "S"
            elif rand < 0.70:
                return "A"
            else:
                return "B"
        elif deviation_value >= 52:
            # 偏差値52-59: Aランク10%, Bランク60%, Cランク30%
            rand = random.random()
            if rand < 0.10:
                return "A"
            elif rand < 0.70:
                return "B"
            else:
                return "C"
        elif deviation_value >= 45:
            # 偏差値45-51: Bランク10%, Cランク60%, Dランク30%
            rand = random.random()
            if rand < 0.10:
                return "B"
            elif rand < 0.70:
                return "C"
            else:
                return "D"
        else:
            # 偏差値45未満: Cランク10%, Dランク90%
            return "C" if random.random() < 0.1 else "D"
    
    @staticmethod
    def get_high_school_deviation_range(individual_deviation: float) -> tuple:
        """
        個人偏差値に基づいて進学可能な高校の偏差値範囲を取得
        
        Args:
            individual_deviation: 個人の偏差値
            
        Returns:
            (min_deviation, max_deviation) のタプル
        """
        # 個人偏差値の±7程度の範囲の高校に進学可能
        min_dev = max(35, individual_deviation - 7)
        max_dev = min(80, individual_deviation + 5)
        return (min_dev, max_dev)
    
    @staticmethod
    def simulate_academic_growth(
        initial_deviation: float,
        high_school_deviation: float,
    ) -> float:
        """
        高校での学力成長をシミュレート
        
        進学校に入ると偏差値が上昇しやすい
        
        Args:
            initial_deviation: 入学時の偏差値
            high_school_deviation: 高校の偏差値
            
        Returns:
            高校卒業時の偏差値
        """
        # 高校環境による成長
        high_school_effect = (high_school_deviation - 50) * 0.15
        
        # ランダムな成長（-3〜+5）
        growth = random.uniform(-3, 5)
        
        # 最終偏差値
        final_deviation = initial_deviation + high_school_effect + growth
        
        # 30-80の範囲にクリップ
        final_deviation = max(30.0, min(80.0, final_deviation))
        
        return round(final_deviation, 1)


# 統計的リアリズム検証用関数
def verify_distribution(n_samples: int = 10000) -> Dict[str, float]:
    """
    偏差値分布が正規分布に従っているか検証
    
    Args:
        n_samples: サンプル数
        
    Returns:
        各ティアの出現率
    """
    calc = DeviationValueCalculator()
    tier_counts = {"top": 0, "high": 0, "middle": 0, "low": 0, "bottom": 0}
    
    for _ in range(n_samples):
        dev = calc.calculate_individual_deviation()
        tier = calc.get_deviation_tier(dev)
        tier_counts[tier] += 1
    
    return {tier: count / n_samples * 100 for tier, count in tier_counts.items()}
