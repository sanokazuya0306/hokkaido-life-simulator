"""
死亡シミュレーター

死亡年齢と死因の決定を担当

年代別死因分布（厚生労働省 人口動態統計 2024年に基づく）:
- 10-39歳: 自殺が死因第1位（G7で日本のみの特徴）
- 40歳以降: 悪性新生物（がん）が第1位
- 90歳以上: 老衰が第1位に上昇
"""

import random
from typing import Dict, List, Any

from ..constants.scores import AGE_BASED_DEATH_CAUSES, get_age_group_for_death_cause


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
            death_by_cause: 死因別死亡者数データ（フォールバック用）
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
    
    def select_death_cause(self, death_age: int = None) -> str:
        """
        年代別の死因分布に基づいて死因を選択
        
        厚生労働省「人口動態統計」2024年のデータに基づき、
        年代ごとに異なる死因分布から重み付きランダム選択を行う。
        
        主な特徴:
        - 10-39歳: 自殺が第1位（約40-50%）
        - 40歳以降: 悪性新生物が第1位（約35-45%）
        - 90歳以上: 老衰が第1位（約30%）
        
        Args:
            death_age: 死亡年齢
        
        Returns:
            死因
        """
        # 年代グループを決定
        if death_age is None:
            age_group = "70-79"  # デフォルトは高齢期
        else:
            age_group = get_age_group_for_death_cause(death_age)
        
        # 年代別死因分布を取得
        causes_distribution = AGE_BASED_DEATH_CAUSES.get(age_group)
        
        if not causes_distribution:
            # フォールバック: 旧方式（death_by_causeデータ）を使用
            return self._select_death_cause_fallback(death_age)
        
        # 重み付きランダム選択
        causes = list(causes_distribution.keys())
        weights = list(causes_distribution.values())
        
        selected_cause = random.choices(causes, weights=weights, k=1)[0]
        return selected_cause
    
    def _select_death_cause_fallback(self, death_age: int = None) -> str:
        """
        フォールバック: 旧方式の死因選択（death_by_causeデータ使用）
        
        Args:
            death_age: 死亡年齢（老衰は80歳以上のみ許可）
        
        Returns:
            死因
        """
        if not self.death_by_cause:
            return "不明"
        
        # 80歳未満の場合は老衰を除外
        available_causes = self.death_by_cause
        if death_age is not None and death_age < 80:
            available_causes = [item for item in self.death_by_cause if item["cause"] != "老衰"]
        
        if not available_causes:
            return "不明"
        
        total_deaths = sum(item["count"] for item in available_causes)
        if total_deaths == 0:
            return random.choice(available_causes)["cause"] if available_causes else "不明"
        
        rand = random.uniform(0, total_deaths)
        cumulative = 0
        for item in available_causes:
            cumulative += item["count"]
            if rand <= cumulative:
                return item["cause"]
        
        return available_causes[-1]["cause"]
