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
]
