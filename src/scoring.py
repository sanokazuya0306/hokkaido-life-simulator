"""
スコア計算モジュール

人生データからスコアを計算する
- 親ガチャスコア: 親の学歴、世帯年収、出生地（北海道か東京か）
- 人生スコア: 最終学歴、生涯年収、寿命
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
    # 親ガチャスコア用
    PARENT_EDUCATION_SCORES,
    HOUSEHOLD_INCOME_SCORES,
    BIRTHPLACE_SCORES,
    # ランク関連
    get_rank,
    get_rank_label,
    # 生涯年収関連
    LIFETIME_INCOME_BASE,
    get_lifetime_income_score,
    # 企業規模・雇用形態関連
    COMPANY_SIZE_SALARY_MULTIPLIER,
    EMPLOYMENT_TYPE_SALARY_MULTIPLIER,
)


class LifeScorer:
    """人生スコアを計算するクラス"""
    
    def calculate_parent_gacha_score(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        親ガチャスコアを計算する（0〜100点）
        親の学歴、世帯年収、出生地（北海道か東京か）の3要素で算定
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            dict: 総合スコアとランク、各項目のスコア詳細
        """
        scores = {}
        
        # 1. 親の学歴スコア（父母の平均）
        father_edu = life.get("father_education", "高校卒")
        mother_edu = life.get("mother_education", "高校卒")
        
        father_edu_score = PARENT_EDUCATION_SCORES.get(father_edu, PARENT_EDUCATION_SCORES["default"])
        mother_edu_score = PARENT_EDUCATION_SCORES.get(mother_edu, PARENT_EDUCATION_SCORES["default"])
        parent_edu_score = (father_edu_score + mother_edu_score) / 2
        
        scores["parent_education"] = {
            "score": parent_edu_score,
            "max_score": 100,
            "label": "親の学歴",
            "value": f"父:{father_edu} / 母:{mother_edu}",
            "reason": f"父親{father_edu_score}点 + 母親{mother_edu_score}点 の平均",
            "source": "文部科学省「学校基本調査」"
        }
        
        # 2. 世帯年収スコア
        household_income = life.get("household_income", "400〜600万円")
        income_score = HOUSEHOLD_INCOME_SCORES.get(household_income, HOUSEHOLD_INCOME_SCORES["default"])
        
        scores["household_income"] = {
            "score": income_score,
            "max_score": 100,
            "label": "世帯年収",
            "value": household_income,
            "reason": f"世帯年収{household_income}",
            "source": "厚生労働省「国民生活基礎調査」"
        }
        
        # 3. 出生地スコア（北海道か東京か）
        birth_city = life.get("birth_city", "")
        # 地域判定（東京都内か北海道か）
        if "東京" in birth_city or "区" in birth_city:
            birthplace_score = BIRTHPLACE_SCORES["東京"]
            region_name = "東京"
        else:
            birthplace_score = BIRTHPLACE_SCORES["北海道"]
            region_name = "北海道"
        
        scores["birthplace"] = {
            "score": birthplace_score,
            "max_score": 100,
            "label": "出生地",
            "value": f"{birth_city}（{region_name}）",
            "reason": f"{region_name}生まれ（教育・就職機会の地域格差）",
            "source": "厚生労働省「一般職業紹介状況」"
        }
        
        # 総合スコア計算（3要素の加重平均）
        # 親の学歴40%、世帯年収40%、出生地20%
        total_score = (
            parent_edu_score * 0.40 +
            income_score * 0.40 +
            birthplace_score * 0.20
        )
        
        # ランク判定
        rank = get_rank(total_score)
        rank_label = get_rank_label(rank)
        
        return {
            "total_score": round(total_score, 1),
            "rank": rank,
            "rank_label": rank_label,
            "breakdown": scores,
            "calculation_method": "親ガチャ（親の学歴40%、世帯年収40%、出生地20%）",
        }
    
    def calculate_lifetime_income(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        生涯年収を計算する（万円）
        定年前に死亡した場合は、按分計算を行う
        
        計算式:
        生涯年収 = 基準生涯年収 × 勤務年数比率 × 産業補正 × 性別補正 × 企業規模補正 × 雇用形態補正
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            dict: 生涯年収（万円）と各補正係数の詳細
        """
        # 最終学歴を判定
        if life.get("university"):
            education_level = "大学卒"
            start_work_age = 22
        elif life.get("vocational_school"):
            education_level = "短大・専門卒"
            start_work_age = 20
        elif life.get("high_school"):
            education_level = "高校卒"
            start_work_age = 18
        else:
            education_level = "中学卒"
            start_work_age = 15
        
        # 基準生涯年収を取得
        base_income = LIFETIME_INCOME_BASE.get(education_level, LIFETIME_INCOME_BASE["高校卒"])
        
        # 定年年齢（なければ65歳を仮定）
        retirement_age = life.get("retirement_age") or 65
        death_age = life.get("death_age", 80)
        
        # 定年まで働けた場合の勤務年数
        full_working_years = retirement_age - start_work_age
        
        # 実際の勤務年数（死亡年齢と定年年齢の早い方まで）
        actual_end_age = min(death_age, retirement_age)
        actual_working_years = max(0, actual_end_age - start_work_age)
        
        # 勤務年数比率を計算
        if actual_working_years < full_working_years and full_working_years > 0:
            working_years_ratio = actual_working_years / full_working_years
        else:
            working_years_ratio = 1.0
        
        lifetime_income = base_income * working_years_ratio
        
        # 産業による補正（産業スコアを年収に反映）
        industry = life.get("industry", "")
        industry_score = INDUSTRY_SALARY_SCORES.get("default")
        for ind_name, ind_score in INDUSTRY_SALARY_SCORES.items():
            if ind_name in industry or industry in ind_name:
                industry_score = ind_score
                break
        
        # 産業スコア（0-100）を補正係数（0.7-1.3）に変換
        industry_multiplier = 0.7 + (industry_score / 100) * 0.6
        lifetime_income *= industry_multiplier
        
        # 性別による補正
        gender = life.get("gender", "男性")
        gender_multiplier = 0.76 if gender == "女性" else 1.0
        lifetime_income *= gender_multiplier
        
        # 企業規模による補正（大企業1.00、中企業0.82、小企業0.72）
        company_size = life.get("company_size", "中企業")
        company_size_multiplier = COMPANY_SIZE_SALARY_MULTIPLIER.get(
            company_size,
            COMPANY_SIZE_SALARY_MULTIPLIER["default"]
        )
        lifetime_income *= company_size_multiplier
        
        # 雇用形態による補正（正社員1.00、非正規0.65）
        employment_type = life.get("employment_type", "正社員")
        employment_type_multiplier = EMPLOYMENT_TYPE_SALARY_MULTIPLIER.get(
            employment_type,
            EMPLOYMENT_TYPE_SALARY_MULTIPLIER["default"]
        )
        lifetime_income *= employment_type_multiplier
        
        return {
            "total": round(lifetime_income, 0),
            "base_income": base_income,
            "education_level": education_level,
            "working_years_ratio": working_years_ratio,
            "industry_multiplier": industry_multiplier,
            "gender_multiplier": gender_multiplier,
            "company_size": company_size,
            "company_size_multiplier": company_size_multiplier,
            "employment_type": employment_type,
            "employment_type_multiplier": employment_type_multiplier,
        }
    
    def calculate_life_score(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        人生スコアを計算する（0〜100点）
        最終学歴、生涯年収、寿命の3要素で算定
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            dict: 総合スコアとランク、各項目のスコア詳細
        """
        scores = {}
        
        # 1. 最終学歴スコア
        if life.get("university"):
            education_level = "大学卒"
        elif life.get("vocational_school"):
            education_level = "短大・専門卒"
        elif life.get("high_school"):
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
        
        # 2. 生涯年収スコア
        income_result = self.calculate_lifetime_income(life)
        lifetime_income = income_result["total"]
        lifetime_income_score = get_lifetime_income_score(lifetime_income)
        
        # 定年前死亡の場合の注記
        death_age = life.get("death_age", 80)
        retirement_age = life.get("retirement_age") or 65
        if death_age < retirement_age:
            income_note = f"（{death_age}歳で死亡のため按分）"
        else:
            income_note = ""
        
        # 補正係数の説明文を生成
        multiplier_details = []
        if income_result["company_size_multiplier"] != 1.0:
            multiplier_details.append(f"{income_result['company_size']}×{income_result['company_size_multiplier']:.2f}")
        if income_result["employment_type_multiplier"] != 1.0:
            multiplier_details.append(f"{income_result['employment_type']}×{income_result['employment_type_multiplier']:.2f}")
        multiplier_note = f"（{', '.join(multiplier_details)}）" if multiplier_details else ""
        
        scores["lifetime_income"] = {
            "score": lifetime_income_score,
            "max_score": 100,
            "label": "生涯年収",
            "value": f"約{lifetime_income/10000:.1f}億円{income_note}",
            "reason": f"推定生涯年収{lifetime_income:.0f}万円{multiplier_note}",
            "source": "労働政策研究・研修機構「ユースフル労働統計」",
            "raw_value": lifetime_income,
            "income_details": income_result,
        }
        
        # 3. 寿命スコア
        lifespan_score = get_lifespan_score(death_age, life.get("gender", "男性"))
        avg_lifespan = 81.09 if life.get("gender") == "男性" else 87.13
        
        scores["lifespan"] = {
            "score": lifespan_score,
            "max_score": 100,
            "label": "寿命",
            "value": f"{death_age}歳",
            "reason": f"{death_age}歳で死亡（平均寿命: {life.get('gender', '男性')}{avg_lifespan}歳）",
            "source": "厚生労働省「簡易生命表」2024年"
        }
        
        # 総合スコア計算（3要素の加重平均）
        # 最終学歴30%、生涯年収40%、寿命30%
        total_score = (
            education_score * 0.30 +
            lifetime_income_score * 0.40 +
            lifespan_score * 0.30
        )
        
        # ランク判定
        rank = get_rank(total_score)
        rank_label = get_rank_label(rank)
        
        return {
            "total_score": round(total_score, 1),
            "rank": rank,
            "rank_label": rank_label,
            "breakdown": scores,
            "calculation_method": "人生スコア（最終学歴30%、生涯年収40%、寿命30%）",
        }
    
    def calculate_all_scores(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        親ガチャスコアと人生スコアの両方を計算する
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            dict: 両方のスコア結果
        """
        parent_gacha = self.calculate_parent_gacha_score(life)
        life_score = self.calculate_life_score(life)
        
        return {
            "parent_gacha": parent_gacha,
            "life_score": life_score,
        }
    
    def get_score_interpretation(self, total_score: float) -> str:
        """
        スコアの解釈を返す
        
        統計的スケール: 平均60点を基準
        
        Args:
            total_score: 総合スコア
            
        Returns:
            解釈文字列
        """
        rank = get_rank(total_score)
        if rank == "SS":
            return "神レベル！（上位1%相当）"
        elif rank == "S":
            return "大当たり！（上位5%相当）"
        elif rank == "A":
            return "当たり（上位20%相当）"
        elif rank == "B":
            return "普通（平均付近）"
        elif rank == "C":
            return "ハズレ（下位20%相当）"
        else:
            return "大ハズレ（下位5%相当）"
