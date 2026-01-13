"""
SNS反応生成モジュール

人生データとスコアに基づいてSNS上での予想される反応を生成する
"""

import random
from typing import Dict, List, Any

from .constants import SNS_REACTIONS


class SNSReactionGenerator:
    """SNS反応を生成するクラス"""
    
    def generate_reactions(
        self,
        life: Dict[str, Any],
        score_result: Dict[str, Any],
        num_reactions: int = 3,
    ) -> List[str]:
        """
        人生データとスコアに基づいてSNS上での予想される反応を生成
        
        Args:
            life: 人生データ
            score_result: calculate_life_score()の戻り値
            num_reactions: 生成する反応数（デフォルト: 3）
            
        Returns:
            list: SNS反応のリスト
        """
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
        
        # 指定数を選択
        return candidates[:num_reactions]
