"""定数モジュール"""

from .scores import (
    LOCATION_SCORES,
    GENDER_SCORES,
    EDUCATION_SCORES,
    UNIVERSITY_DESTINATION_SCORES,
    UNIVERSITY_RANK_SCORES,
    UNIVERSITY_RANKS,
    INDUSTRY_SALARY_SCORES,
    DEATH_CAUSE_SCORES,
    SCORE_WEIGHTS,
    get_lifespan_score,
    get_university_rank,
    get_university_rank_score,
    # 親ガチャスコア用
    PARENT_EDUCATION_SCORES,
    HOUSEHOLD_INCOME_SCORES,
    BIRTHPLACE_SCORES,
    # ランク関連
    RANK_THRESHOLDS,
    RANK_LABELS,
    get_rank,
    get_rank_label,
    # 生涯年収関連
    LIFETIME_INCOME_BASE,
    LIFETIME_INCOME_PERCENTILES,
    get_lifetime_income_score,
    # 企業規模・雇用形態関連
    COMPANY_SIZE_SALARY_MULTIPLIER,
    COMPANY_SIZE_DISTRIBUTION_BY_EDUCATION,
    EMPLOYMENT_TYPE_SALARY_MULTIPLIER,
    EMPLOYMENT_TYPE_DISTRIBUTION,
    # 学歴別産業分布
    INDUSTRY_DISTRIBUTION_BY_EDUCATION,
    # 最終学歴スコアリング（新）
    get_education_score,
    # 起業家・経営者関連
    ENTREPRENEUR_PROBABILITY,
    ENTREPRENEUR_SUCCESS_TIERS,
    EXECUTIVE_PROMOTION_PROBABILITY,
    EXECUTIVE_INCOME_TIERS,
    SALARIED_EXECUTIVE_MULTIPLIER,
    # 年代別死因分布（新）
    AGE_BASED_DEATH_CAUSES,
    get_age_group_for_death_cause,
)
from .sns_reactions import SNS_REACTIONS

__all__ = [
    "LOCATION_SCORES",
    "GENDER_SCORES",
    "EDUCATION_SCORES",
    "UNIVERSITY_DESTINATION_SCORES",
    "UNIVERSITY_RANK_SCORES",
    "UNIVERSITY_RANKS",
    "INDUSTRY_SALARY_SCORES",
    "DEATH_CAUSE_SCORES",
    "SCORE_WEIGHTS",
    "get_lifespan_score",
    "get_university_rank",
    "get_university_rank_score",
    "SNS_REACTIONS",
    # 親ガチャスコア用
    "PARENT_EDUCATION_SCORES",
    "HOUSEHOLD_INCOME_SCORES",
    "BIRTHPLACE_SCORES",
    # ランク関連
    "RANK_THRESHOLDS",
    "RANK_LABELS",
    "get_rank",
    "get_rank_label",
    # 生涯年収関連
    "LIFETIME_INCOME_BASE",
    "LIFETIME_INCOME_PERCENTILES",
    "get_lifetime_income_score",
    # 企業規模・雇用形態関連
    "COMPANY_SIZE_SALARY_MULTIPLIER",
    "COMPANY_SIZE_DISTRIBUTION_BY_EDUCATION",
    "EMPLOYMENT_TYPE_SALARY_MULTIPLIER",
    "EMPLOYMENT_TYPE_DISTRIBUTION",
    # 学歴別産業分布
    "INDUSTRY_DISTRIBUTION_BY_EDUCATION",
    "get_education_score",
    # 起業家・経営者関連
    "ENTREPRENEUR_PROBABILITY",
    "ENTREPRENEUR_SUCCESS_TIERS",
    "EXECUTIVE_PROMOTION_PROBABILITY",
    "EXECUTIVE_INCOME_TIERS",
    "SALARIED_EXECUTIVE_MULTIPLIER",
    # 年代別死因分布
    "AGE_BASED_DEATH_CAUSES",
    "get_age_group_for_death_cause",
]
