"""UIコンポーネント"""

from .gacha_button import gacha_button, secondary_button, back_button, refresh_button
from .rank_card import rank_card, rank_card_item, rank_card_with_style, rank_card_grid, rank_display, parent_rank_display
from .region_selector import region_selector
from .detail_card import detail_card, life_story_text, counter_display, expand_button
from .slider import people_slider
from .dialogs import rates_dialog, dataset_dialog, correlation_dialog, about_gacha_dialog

__all__ = [
    "gacha_button",
    "secondary_button",
    "back_button",
    "refresh_button",
    "rank_card",
    "rank_card_item",
    "rank_card_with_style",
    "rank_card_grid",
    "rank_display",
    "parent_rank_display",
    "region_selector",
    "detail_card",
    "life_story_text",
    "counter_display",
    "expand_button",
    "people_slider",
    "rates_dialog",
    "dataset_dialog",
    "correlation_dialog",
    "about_gacha_dialog",
]
