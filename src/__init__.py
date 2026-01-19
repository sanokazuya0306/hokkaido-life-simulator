"""
地域別人生シミュレーター

北海道・東京などの公開データを使ってランダムに人生の軌跡を生成するプログラム
"""

from .simulator import RegionalLifeSimulator, HokkaidoLifeSimulator, TokyoLifeSimulator
from .data_loader import REGION_CONFIG

__all__ = [
    "RegionalLifeSimulator",
    "HokkaidoLifeSimulator",  # 後方互換性
    "TokyoLifeSimulator",
    "REGION_CONFIG",
]
__version__ = "2.1.0"
