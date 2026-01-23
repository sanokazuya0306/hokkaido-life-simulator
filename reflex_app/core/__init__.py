"""
コアロジック層

UI非依存のビジネスロジックを提供する
"""

from .gacha_service import GachaService, LifeResult

__all__ = [
    "GachaService",
    "LifeResult",
]
