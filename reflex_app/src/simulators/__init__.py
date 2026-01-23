"""シミュレーターモジュール"""

from .birth import BirthSimulator
from .education import EducationSimulator
from .career import CareerSimulator
from .death import DeathSimulator

__all__ = [
    "BirthSimulator",
    "EducationSimulator",
    "CareerSimulator",
    "DeathSimulator",
]
