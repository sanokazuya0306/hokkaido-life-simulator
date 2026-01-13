"""
死亡シミュレーター

死亡年齢と死因の決定を担当
"""

import random
from typing import Dict, List, Any


class DeathSimulator:
    """死亡に関するシミュレーションを担当するクラス"""
    
    def __init__(
        self,
        death_by_age: List[Dict[str, Any]],
        death_by_cause: List[Dict[str, Any]],
    ):
        """
        初期化
        
        Args:
            death_by_age: 年齢別死亡者数データ
            death_by_cause: 死因別死亡者数データ
        """
        self.death_by_age = death_by_age
        self.death_by_cause = death_by_cause
    
    def select_death_age(self) -> int:
        """
        死亡年齢をランダムに選択（年齢別死亡者数に基づく重み付き選択）
        
        Returns:
            死亡年齢
        """
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
    
    def select_death_cause(self) -> str:
        """
        死因をランダムに選択（死因別死亡者数に基づく重み付き選択）
        
        Returns:
            死因
        """
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
