"""
出生シミュレーター

出生地と性別の決定を担当
"""

import random
from typing import Dict, List, Any, Optional


class BirthSimulator:
    """出生に関するシミュレーションを担当するクラス"""
    
    def __init__(
        self,
        birth_data: List[Dict[str, Any]],
        workers_by_gender: Dict[str, int],
        workers_by_industry_gender: Dict[str, Dict[str, int]],
        workers_by_industry: List[Dict[str, Any]],
    ):
        """
        初期化
        
        Args:
            birth_data: 市町村別出生数データ
            workers_by_gender: 性別別労働者数
            workers_by_industry_gender: 性別×産業別労働者数
            workers_by_industry: 産業別労働者数
        """
        self.birth_data = birth_data
        self.workers_by_gender = workers_by_gender
        self.workers_by_industry_gender = workers_by_industry_gender
        self.workers_by_industry = workers_by_industry
    
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
                # 札幌市の区を「札幌市○○区」の形式に変換
                if city.endswith("区") and "市" not in city:
                    city = f"札幌市{city}"
                return city
        
        # 最後の要素も同様に処理
        city = self.birth_data[-1]["city"]
        if city.endswith("区") and "市" not in city:
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
