"""
スコア計算モジュール

人生データからスコアを計算する
掛け算方式: 各要素を掛け合わせることで、地域格差が如実に反映される
"""

from typing import Dict, Any

from .constants import (
    LOCATION_SCORES,
    GENDER_SCORES,
    EDUCATION_SCORES,
    UNIVERSITY_DESTINATION_SCORES,
    INDUSTRY_SALARY_SCORES,
    DEATH_CAUSE_SCORES,
    get_lifespan_score,
    get_university_rank,
    get_university_rank_score,
)


class LifeScorer:
    """人生スコアを計算するクラス"""
    
    def calculate_life_score(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        人生のスコアを計算する（0〜100点）
        東京で生まれ育って最大限に充実した人生を100点とする
        
        掛け算方式: 各要素の割合を掛け合わせて最終スコアを算出
        これにより、どこか1つが低いと全体が大きく下がる
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            dict: 総合スコアと各項目のスコア詳細
        """
        scores = {}
        
        # 1. 出生地スコア（北海道内なので一律54%）
        location_score = LOCATION_SCORES["北海道"]
        scores["location"] = {
            "score": location_score,
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
        
        # 4. 大学進学先スコア（大学進学者のみ計算に含める）
        if life["university"] and life.get("university_destination"):
            dest = life["university_destination"]
            dest_score = UNIVERSITY_DESTINATION_SCORES.get(dest, UNIVERSITY_DESTINATION_SCORES["default"])
            scores["university_dest"] = {
                "score": dest_score,
                "max_score": 100,
                "label": "大学進学先",
                "value": dest,
                "reason": f"{dest}の大学（産業集積度・求人倍率に基づく）",
                "source": "文部科学省「学校基本調査」",
                "include_in_calc": True,
            }
        else:
            # 大学に行かなかった場合は計算から除外
            scores["university_dest"] = {
                "score": 0,
                "max_score": 100,
                "label": "大学進学先",
                "value": "進学せず",
                "reason": "大学に進学しなかった（スコア計算から除外）",
                "source": "-",
                "include_in_calc": False,
            }
        
        # 4.5. 大学ランクスコア（大学進学者のみ計算に含める）
        if life["university"] and life.get("university_name"):
            uni_name = life["university_name"]
            uni_rank = get_university_rank(uni_name)
            uni_rank_score = get_university_rank_score(uni_name)
            
            rank_labels = {"S": "難関", "A": "上位", "B": "中堅", "C": "標準", "D": "その他"}
            rank_label = rank_labels.get(uni_rank, "標準")
            
            scores["university_rank"] = {
                "score": uni_rank_score,
                "max_score": 100,
                "label": "大学ランク",
                "value": f"{uni_name}（{rank_label}）",
                "reason": f"偏差値ランク{uni_rank}（{rank_label}大学）",
                "source": "大学偏差値ランキング",
                "include_in_calc": True,
            }
        else:
            scores["university_rank"] = {
                "score": 0,
                "max_score": 100,
                "label": "大学ランク",
                "value": "進学せず",
                "reason": "大学に進学しなかった（スコア計算から除外）",
                "source": "-",
                "include_in_calc": False,
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
        
        # ============================================================
        # 加重平均方式でスコア計算（平均50〜60点になるよう調整）
        # 各要素の重みを考慮して合計
        # ============================================================
        
        # 基本要素のスコアと重み
        # 出生地（平均54）の重みを上げて全体平均を下げる
        # 産業（平均62）の重みも上げる
        base_scores = [
            (location_score, 0.25),      # 出生地（北海道は54点）- 最重要要素
            (gender_score, 0.05),        # 性別（女性は76点）- 影響を軽減
            (education_score, 0.10),     # 学歴（中卒60、高卒75、大卒100）
            (industry_score, 0.20),      # 産業（飲食45〜IT100）
            (lifespan_score, 0.20),      # 寿命（30歳以下0〜90歳以上100）
            (death_cause_score, 0.10),   # 死因（自殺20〜老衰100）
        ]
        
        # 大学関連スコア（大卒の場合のみ）
        if scores["university_dest"].get("include_in_calc", False):
            base_scores.append((scores["university_dest"]["score"], 0.05))
        if scores["university_rank"].get("include_in_calc", False):
            base_scores.append((scores["university_rank"]["score"], 0.05))
        
        # 重みを正規化（大卒でない場合、他の要素の重みを増やす）
        total_weight = sum(weight for _, weight in base_scores)
        
        # 加重平均でスコアを計算
        weighted_sum = sum(score * weight for score, weight in base_scores)
        base_score = weighted_sum / total_weight
        
        # スケーリング調整
        # 目標分布:
        # - 北海道の典型的なケース: 50〜60点
        # - 頑張れば: 70〜80点
        # - 最良ケース: 90点以上も稀に出る（0.5〜1%）
        # - 最悪ケース: 20〜30点
        #
        # base_scoreの実測分布: 平均70点、範囲50-85点程度
        # これを平均55点、範囲20-100点に変換
        # 変換式: (base_score - 70) * 3.0 + 55
        # base=50 → -5点→20点、base=70 → 55点、base=80 → 85点、base=85→100点
        if base_score <= 0:
            total_score = 0
        else:
            # 線形変換: 中央を55点に、分布を3倍に広げる
            adjusted = (base_score - 70) * 3.0 + 55
            # 最低20点、最高100点に制限
            total_score = max(20, min(100, adjusted))
        
        return {
            "total_score": round(total_score, 1),
            "breakdown": scores,
            "calculation_method": "weighted_average",  # 計算方式を記録
            "num_factors": len(base_scores),
        }
    
    def get_score_interpretation(self, total_score: float) -> str:
        """
        スコアの解釈を返す（app.pyのランク基準に合わせて調整）
        
        Args:
            total_score: 総合スコア
            
        Returns:
            解釈文字列
        """
        if total_score >= 90:
            return "素晴らしい人生！（上位1%相当）"
        elif total_score >= 80:
            return "とても充実した人生（上位5%相当）"
        elif total_score >= 70:
            return "平均以上の良い人生"
        elif total_score >= 60:
            return "平均的な人生"
        elif total_score >= 30:
            return "いろいろあった人生"
        else:
            return "波乱万丈の人生"
