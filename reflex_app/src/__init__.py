"""
地域別人生シミュレーター

北海道・東京などの公開データを使ってランダムに人生の軌跡を生成するプログラム
"""

from .simulator import RegionalLifeSimulator, HokkaidoLifeSimulator, TokyoLifeSimulator
from .data_loader import REGION_CONFIG
from .correlation_visualizer import create_correlation_sankey, get_correlation_summary

__all__ = [
    "RegionalLifeSimulator",
    "HokkaidoLifeSimulator",  # 後方互換性
    "TokyoLifeSimulator",
    "REGION_CONFIG",
    "create_correlation_sankey",
    "get_correlation_summary",
]
__version__ = "2.2.0"
