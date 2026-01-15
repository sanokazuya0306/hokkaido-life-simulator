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
        
        # スコアベースの反応（ランク基準）
        # ★★★★★★ (60点以上): 非常に恵まれた人生
        # ★★★★★ (45-60点): 平均以上
        # ★★★★ (35-45点): 平均的
        # ★★★ (25-35点): やや困難
        # ★★ (15-25点): 多くの困難
        # ★ (15点未満): 極めて厳しい
        if total_score >= 60:
            candidates.extend(SNS_REACTIONS["rank_6star"])  # ★★★★★★
        elif total_score >= 45:
            candidates.extend(SNS_REACTIONS["rank_5star"])  # ★★★★★
        elif total_score >= 35:
            candidates.extend(SNS_REACTIONS["rank_4star"])  # ★★★★
        elif total_score >= 25:
            candidates.extend(SNS_REACTIONS["rank_3star"])  # ★★★
        elif total_score >= 15:
            candidates.extend(SNS_REACTIONS["rank_2star"])  # ★★
        else:
            candidates.extend(SNS_REACTIONS["rank_1star"])  # ★
        
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
        
        # 転職回数ベースの反応（新規）
        job_change_count = life.get("job_change_count", 0)
        if job_change_count >= 4:
            candidates.extend(SNS_REACTIONS["many_job_changes"])
        elif job_change_count == 0:
            candidates.extend(SNS_REACTIONS["no_job_change"])
        elif job_change_count <= 2:
            candidates.extend(SNS_REACTIONS["few_job_changes"])
        
        # 死因ベースの反応
        death_cause = life["death_cause"]
        if "悪性新生物" in death_cause or "腫瘍" in death_cause or "ガン" in death_cause:
            candidates.extend(SNS_REACTIONS["death_cancer"])
        elif "老衰" in death_cause:
            candidates.extend(SNS_REACTIONS["death_old_age"])
        elif "不慮" in death_cause or "事故" in death_cause:
            candidates.extend(SNS_REACTIONS["death_accident"])
        elif "自殺" in death_cause or "自死" in death_cause:
            candidates.extend(SNS_REACTIONS["death_suicide"])
        
        # 若くして亡くなった場合
        death_age = life["death_age"]
        if death_age < 50:
            candidates.extend(SNS_REACTIONS["death_young"])
        
        # 長寿関連（新規）
        if death_age >= 90:
            candidates.extend(SNS_REACTIONS["long_life"])
        elif death_age < 65:
            candidates.extend(SNS_REACTIONS["short_life"])
        
        # 出生地ベースの反応
        if "札幌" in life["birth_city"]:
            candidates.extend(SNS_REACTIONS["birth_sapporo"])
        elif "市" not in life["birth_city"]:
            candidates.extend(SNS_REACTIONS["birth_rural"])
        
        # 結婚関連（新規）- lifeデータに含まれている場合
        if "married" in life:
            if life["married"]:
                candidates.extend(SNS_REACTIONS["married"])
            else:
                candidates.extend(SNS_REACTIONS["unmarried"])
        
        # 汎用的な反応をランダムに追加（複数カテゴリからバランスよく）
        general_categories = ["general_cynical", "general_self_responsibility", "general_detached"]
        selected_general = random.choice(general_categories)
        candidates.extend(SNS_REACTIONS[selected_general])
        
        # 重複を除去してシャッフル
        candidates = list(set(candidates))
        random.shuffle(candidates)
        
        # 指定数を選択
        return candidates[:num_reactions]
