"""
コアロジック層

UI非依存のビジネスロジックを提供する
"""

from .gacha_service import GachaService, LifeResult, get_gacha_service, clear_service_cache

__all__ = [
    "GachaService",
    "LifeResult",
    "get_gacha_service",
    "clear_service_cache",
]
