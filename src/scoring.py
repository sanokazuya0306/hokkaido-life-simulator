"""
スコア計算モジュール

人生データからスコアを計算する
"""

from typing import Dict, Any

from .constants import (
    LOCATION_SCORES,
    GENDER_SCORES,
    EDUCATION_SCORES,
    UNIVERSITY_DESTINATION_SCORES,
    INDUSTRY_SALARY_SCORES,
    DEATH_CAUSE_SCORES,
    SCORE_WEIGHTS,
    get_lifespan_score,
)


class LifeScorer:
    """人生スコアを計算するクラス"""
    
    def calculate_life_score(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        人生のスコアを計算する（0〜100点）
        東京で生まれ育って最大限に充実した人生を100点とする
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            dict: 総合スコアと各項目のスコア詳細
        """
        scores = {}
        
        # 1. 出生地スコア（北海道内なので一律）
        scores["location"] = {
            "score": LOCATION_SCORES["北海道"],
            "max_score": 100,
            "label": "出生地",
            "value": life["birth_city"],
            "reason": f"北海道生まれ（東京比: 求人倍率0.93 vs 1.73）",
            "source": "厚生労働省「一般職業紹介状況」2025年11月"
        }
        
        # 2. 性別スコア
        gender = life["gender"]
        gender_score = GENDER_SCORES.get(gender, 75)
        scores["gender"] = {
            "score": gender_score,
            "max_score": 100,
            "label": "性別",
            "value": gender,
            "reason": f"{gender}（賃金格差: 男性100に対し女性75.8）" if gender == "女性" else f"{gender}（賃金基準）",
            "source": "厚生労働省「賃金構造基本統計調査」2024年"
        }
        
        # 3. 学歴スコア
        if life["university"]:
            education_level = "大学卒"
        elif life["high_school"]:
            education_level = "高校卒"
        else:
            education_level = "中学卒"
        
        education_score = EDUCATION_SCORES[education_level]
        scores["education"] = {
            "score": education_score,
            "max_score": 100,
            "label": "最終学歴",
            "value": education_level,
            "reason": f"{education_level}（生涯賃金比較に基づく）",
            "source": "労働政策研究・研修機構「ユースフル労働統計」"
        }
        
        # 4. 大学進学先スコア（大学進学者のみ）
        if life["university"] and life.get("university_destination"):
            dest = life["university_destination"]
            dest_score = UNIVERSITY_DESTINATION_SCORES.get(dest, UNIVERSITY_DESTINATION_SCORES["default"])
            scores["university_dest"] = {
                "score": dest_score,
                "max_score": 100,
                "label": "大学進学先",
                "value": dest,
                "reason": f"{dest}の大学（産業集積度・求人倍率に基づく）",
                "source": "文部科学省「学校基本調査」"
            }
        else:
            # 大学に行かなかった場合は0点（重みが低いので影響は限定的）
            scores["university_dest"] = {
                "score": 0,
                "max_score": 100,
                "label": "大学進学先",
                "value": "進学せず",
                "reason": "大学に進学しなかった",
                "source": "-"
            }
        
        # 5. 就職産業スコア
        industry = life["industry"]
        # 産業名の部分一致でスコアを取得
        industry_score = INDUSTRY_SALARY_SCORES.get("default")
        for ind_name, ind_score in INDUSTRY_SALARY_SCORES.items():
            if ind_name in industry or industry in ind_name:
                industry_score = ind_score
                break
        
        scores["industry"] = {
            "score": industry_score,
            "max_score": 100,
            "label": "就職産業",
            "value": industry,
            "reason": f"{industry}（産業別平均賃金に基づく）",
            "source": "厚生労働省「賃金構造基本統計調査」2024年"
        }
        
        # 6. 寿命スコア
        death_age = life["death_age"]
        lifespan_score = get_lifespan_score(death_age, life["gender"])
        
        # 理想的な寿命の基準
        avg_lifespan = 81.09 if life["gender"] == "男性" else 87.13
        scores["lifespan"] = {
            "score": lifespan_score,
            "max_score": 100,
            "label": "寿命",
            "value": f"{death_age}歳",
            "reason": f"{death_age}歳で死亡（平均寿命: {life['gender']}{avg_lifespan}歳）",
            "source": "厚生労働省「簡易生命表」2024年"
        }
        
        # 7. 死因スコア
        death_cause = life["death_cause"]
        # 死因の分類
        if "老衰" in death_cause:
            cause_category = "老衰"
        elif "自殺" in death_cause or "自傷" in death_cause:
            cause_category = "自殺"
        elif "不慮" in death_cause or "事故" in death_cause:
            cause_category = "不慮の事故"
        else:
            cause_category = "default"
        
        death_cause_score = DEATH_CAUSE_SCORES.get(cause_category, DEATH_CAUSE_SCORES["default"])
        
        # 悪性新生物（ガン）などの病気は70点
        if "悪性新生物" in death_cause or "腫瘍" in death_cause:
            death_cause_score = 70
            cause_display = "ガン"
        elif "心疾患" in death_cause:
            death_cause_score = 65
            cause_display = death_cause
        elif "脳血管" in death_cause:
            death_cause_score = 65
            cause_display = death_cause
        else:
            cause_display = death_cause
        
        scores["death_cause"] = {
            "score": death_cause_score,
            "max_score": 100,
            "label": "死因",
            "value": cause_display,
            "reason": f"{cause_display}で死亡（老衰が最高評価）",
            "source": "厚生労働省「人口動態統計」"
        }
        
        # 総合スコアの計算（重み付き平均）
        total_score = 0
        for key, weight in SCORE_WEIGHTS.items():
            total_score += scores[key]["score"] * weight
        
        return {
            "total_score": round(total_score, 1),
            "breakdown": scores,
            "weights": SCORE_WEIGHTS,
        }
    
    def get_score_interpretation(self, total_score: float) -> str:
        """
        スコアの解釈を返す
        
        Args:
            total_score: 総合スコア
            
        Returns:
            解釈文字列
        """
        if total_score >= 80:
            return "非常に恵まれた人生（上位10%相当）"
        elif total_score >= 65:
            return "平均以上の充実した人生"
        elif total_score >= 50:
            return "平均的な人生"
        elif total_score >= 35:
            return "やや困難の多い人生"
        else:
            return "多くの困難に直面した人生"
