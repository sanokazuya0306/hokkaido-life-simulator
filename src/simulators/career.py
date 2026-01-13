"""
キャリアシミュレーター

就職先の産業と定年年齢の決定を担当
"""

import random
from typing import Dict, List, Any, Optional


class CareerSimulator:
    """キャリアに関するシミュレーションを担当するクラス"""
    
    def __init__(
        self,
        workers_by_industry: List[Dict[str, Any]],
        workers_by_industry_gender: Dict[str, Dict[str, int]],
        retirement_age_distribution: List[Dict[str, Any]],
    ):
        """
        初期化
        
        Args:
            workers_by_industry: 産業別労働者数データ
            workers_by_industry_gender: 性別×産業別労働者数
            retirement_age_distribution: 定年年齢分布
        """
        self.workers_by_industry = workers_by_industry
        self.workers_by_industry_gender = workers_by_industry_gender
        self.retirement_age_distribution = retirement_age_distribution
    
    def select_industry(self, gender: Optional[str] = None) -> str:
        """
        就職先の産業をランダムに選択（労働者数に基づく重み付き選択）
        
        Args:
            gender: 性別（指定された場合、性別に応じた産業分布を使用）
            
        Returns:
            産業名
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
    
    def select_retirement_age(self) -> Optional[int]:
        """
        定年年齢をランダムに選択（定年年齢分布に基づく重み付き選択）
        
        Returns:
            定年年齢（定年なしの場合はNone）
        """
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
