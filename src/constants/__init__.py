"""定数モジュール"""

from .scores import (
    LOCATION_SCORES,
    GENDER_SCORES,
    EDUCATION_SCORES,
    UNIVERSITY_DESTINATION_SCORES,
    INDUSTRY_SALARY_SCORES,
    DEATH_CAUSE_SCORES,
    SCORE_WEIGHTS,
    get_lifespan_score,
)
from .sns_reactions import SNS_REACTIONS

__all__ = [
    "LOCATION_SCORES",
    "GENDER_SCORES",
    "EDUCATION_SCORES",
    "UNIVERSITY_DESTINATION_SCORES",
    "INDUSTRY_SALARY_SCORES",
    "DEATH_CAUSE_SCORES",
    "SCORE_WEIGHTS",
    "get_lifespan_score",
    "SNS_REACTIONS",
]
