"""
アプリケーション状態管理

Streamlitのsession_stateに相当する状態管理をReflexのStateクラスで実装
"""

import reflex as rx
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# reflex_appディレクトリ（core/src/dataが含まれる）を参照
# reflex_app/reflex_app/state.py -> reflex_app/
_app_root = Path(__file__).parent.parent
if str(_app_root) not in sys.path:
    sys.path.insert(0, str(_app_root))

from core import GachaService

# グローバルなサービスキャッシュ（Stateの外部で管理）
_service_cache: Dict[str, GachaService] = {}

def get_service(region: str) -> GachaService:
    """GachaServiceのインスタンスを取得（キャッシュ対応）"""
    if region not in _service_cache:
        data_dir = str(_app_root / "data")
        _service_cache[region] = GachaService(
            region=region, 
            data_dir=data_dir
        )
    return _service_cache[region]


class GachaState(rx.State):
    """ガチャアプリの状態管理クラス"""
    
    # 基本状態
    region: str = "hokkaido"
    num_people: int = 1
    view_mode: str = "gacha"  # "gacha" | "result" | "detail"
    total_generated: int = 0
    
    # 生成された人生データ
    lives: List[Dict[str, Any]] = []
    score_results: List[Dict[str, Any]] = []
    
    # 詳細表示用
    selected_life_index: int = -1
    
    # 詳細画面用のキャッシュされた値
    _cached_life_story: str = ""
    _cached_parent_rank: str = "B"
    _cached_total_score: int = 0
    _cached_rank_label: str = ""
    
    # スコア内訳（フラット化）
    _edu_score: float = 0.0
    _edu_value: str = ""
    _edu_reason: str = ""
    _income_score: float = 0.0
    _income_value: str = ""
    _income_reason: str = ""
    _lifespan_score: float = 0.0
    _lifespan_value: str = ""
    _lifespan_reason: str = ""
    
    # 親ガチャ結果（フラット化）
    _parent_total_score: int = 0
    _parent_rank_label: str = ""
    _parent_edu_score: float = 0.0
    _parent_edu_value: str = ""
    _parent_income_score: float = 0.0
    _parent_income_value: str = ""
    _parent_birthplace_score: float = 0.0
    _parent_birthplace_value: str = ""
    
    # 人生詳細（フラット化）
    _detail_gender: str = ""
    _detail_birth_city: str = ""
    _detail_household_income: str = ""
    _detail_father_education: str = ""
    _detail_mother_education: str = ""
    _detail_high_school: bool = False
    _detail_high_school_name: str = ""
    _detail_high_school_deviation: float = 0.0  # 高校の偏差値
    _detail_university: bool = False
    _detail_university_name: str = ""
    _detail_university_rank: str = ""
    _detail_company_size: str = ""
    _detail_employment_type: str = ""
    _detail_job_changes: int = 0
    _detail_death_age: int = 0
    _detail_death_cause: str = ""
    
    # 偏差値関連
    _detail_deviation_value: float = 0.0  # 個人の偏差値（初期）
    _detail_graduation_deviation: float = 0.0  # 卒業時の偏差値
    
    # 詳細展開フラグ
    show_detail_breakdown: bool = False
    
    # ダイアログ表示状態
    show_rates_dialog: bool = False
    show_dataset_dialog: bool = False
    show_correlation_dialog: bool = False
    
    # 演出フラグ
    show_result_effect: bool = False
    is_loading: bool = False
    
    # ============================================
    # 地域選択
    # ============================================
    
    def set_region(self, region: str):
        """地域を変更"""
        if region != self.region:
            self.region = region
            self.lives = []
            self.score_results = []
            self.view_mode = "gacha"
    
    def select_hokkaido(self):
        """北海道を選択"""
        self.set_region("hokkaido")
    
    def select_tokyo(self):
        """東京を選択"""
        self.set_region("tokyo")
    
    # ============================================
    # スライダー
    # ============================================
    
    def set_num_people(self, value: List[int]):
        """人数を設定"""
        if value:
            self.num_people = value[0]
    
    # ============================================
    # ガチャ実行
    # ============================================
    
    def pull_gacha(self):
        """ガチャを引く"""
        if self.num_people <= 0:
            return
        
        self.is_loading = True
        service = get_service(self.region)
        
        # 人生を生成
        self.lives = []
        self.score_results = []
        
        for _ in range(self.num_people):
            life = service.simulator.generate_life()
            score_result = service.simulator.calculate_life_score(life)
            self.lives.append(life)
            self.score_results.append(score_result)
        
        self.total_generated += self.num_people
        self.view_mode = "result"
        self.show_result_effect = True
        self.is_loading = False
    
    def regenerate(self):
        """再生成"""
        self.pull_gacha()
    
    # ============================================
    # 画面遷移
    # ============================================
    
    def go_to_gacha(self):
        """ガチャ画面へ戻る"""
        self.view_mode = "gacha"
        self.selected_life_index = -1
    
    def go_to_result(self):
        """結果一覧へ戻る"""
        self.view_mode = "result"
        self.selected_life_index = -1
    
    def select_life(self, index: int):
        """人生を選択して詳細表示"""
        self.selected_life_index = index
        self.show_detail_breakdown = False  # 展開状態をリセット
        
        # 詳細情報をキャッシュ
        if 0 <= index < len(self.lives):
            service = get_service(self.region)
            life = self.lives[index]
            score_result = self.score_results[index]
            
            # 基本情報
            self._cached_life_story = service._generate_life_story(life)
            self._cached_total_score = int(score_result.get('total_score', 0))
            self._cached_rank_label = score_result.get('rank_label', '')
            
            # スコア内訳（フラット化）
            breakdown = score_result.get('breakdown', {})
            edu = breakdown.get('education', {})
            self._edu_score = float(edu.get('score', 0))
            self._edu_value = str(edu.get('value', ''))
            self._edu_reason = str(edu.get('reason', ''))
            
            income = breakdown.get('lifetime_income', {})
            self._income_score = float(income.get('score', 0))
            self._income_value = str(income.get('value', ''))
            self._income_reason = str(income.get('reason', ''))
            
            lifespan = breakdown.get('lifespan', {})
            self._lifespan_score = float(lifespan.get('score', 0))
            self._lifespan_value = str(lifespan.get('value', ''))
            self._lifespan_reason = str(lifespan.get('reason', ''))
            
            # 親ガチャスコア（フラット化）
            parent_result = service.simulator.calculate_parent_gacha_score(life)
            self._parent_total_score = int(parent_result.get('total_score', 0))
            self._parent_rank_label = parent_result.get('rank_label', '')
            # 親ガチャランクも同じ計算結果から取得（一貫性を保つ）
            self._cached_parent_rank = parent_result.get('rank', 'B')
            
            p_breakdown = parent_result.get('breakdown', {})
            p_edu = p_breakdown.get('parent_education', {})
            self._parent_edu_score = float(p_edu.get('score', 0))
            self._parent_edu_value = str(p_edu.get('value', ''))
            
            p_income = p_breakdown.get('household_income', {})
            self._parent_income_score = float(p_income.get('score', 0))
            self._parent_income_value = str(p_income.get('value', ''))
            
            p_birth = p_breakdown.get('birthplace', {})
            self._parent_birthplace_score = float(p_birth.get('score', 0))
            self._parent_birthplace_value = str(p_birth.get('value', ''))
            
            # 人生の詳細データ（フラット化）
            self._detail_gender = "男性" if life.get('gender') == 'male' else "女性"
            self._detail_birth_city = life.get('birth_city', '不明')
            self._detail_household_income = life.get('household_income', '不明')
            self._detail_father_education = life.get('father_education', '不明')
            self._detail_mother_education = life.get('mother_education', '不明')
            self._detail_high_school = life.get('high_school', False)
            hs_name = life.get('high_school_name', '')
            self._detail_high_school_name = hs_name.get('name', '') if isinstance(hs_name, dict) else str(hs_name or '')
            self._detail_high_school_deviation = float(life.get('high_school_deviation') or 0.0)
            self._detail_university = life.get('university', False)
            
            # 偏差値関連
            self._detail_deviation_value = float(life.get('deviation_value') or 0.0)
            self._detail_graduation_deviation = float(life.get('graduation_deviation') or 0.0)
            uni_name = life.get('university_name', '')
            self._detail_university_name = uni_name.get('name', '') if isinstance(uni_name, dict) else str(uni_name or '')
            self._detail_university_rank = life.get('university_rank') or ''
            self._detail_company_size = life.get('company_size', '不明')
            self._detail_employment_type = life.get('employment_type', '不明')
            self._detail_job_changes = life.get('career_summary', {}).get('total_job_changes', 0)
            self._detail_death_age = life.get('death_age', 0)
            self._detail_death_cause = life.get('death_cause', '不明')
        
        self.view_mode = "detail"
    
    def toggle_detail_breakdown(self):
        """詳細展開をトグル"""
        self.show_detail_breakdown = not self.show_detail_breakdown
    
    # ============================================
    # ダイアログ制御
    # ============================================
    
    def open_rates_dialog(self):
        """確率ダイアログを開く"""
        self.show_rates_dialog = True
    
    def close_rates_dialog(self):
        """確率ダイアログを閉じる"""
        self.show_rates_dialog = False
    
    def open_dataset_dialog(self):
        """データセットダイアログを開く"""
        self.show_dataset_dialog = True
    
    def close_dataset_dialog(self):
        """データセットダイアログを閉じる"""
        self.show_dataset_dialog = False
    
    def open_correlation_dialog(self):
        """相関図ダイアログを開く"""
        self.show_correlation_dialog = True
    
    def close_correlation_dialog(self):
        """相関図ダイアログを閉じる"""
        self.show_correlation_dialog = False
    
    def clear_effect(self):
        """演出フラグをクリア"""
        self.show_result_effect = False
    
    # ============================================
    # 計算プロパティ（Computed Vars）
    # ============================================
    
    @rx.var
    def region_name(self) -> str:
        """地域の表示名"""
        return "北海道" if self.region == "hokkaido" else "東京"
    
    @rx.var
    def has_lives(self) -> bool:
        """人生データがあるか"""
        return len(self.lives) > 0
    
    @rx.var
    def selected_life(self) -> Dict[str, Any]:
        """選択中の人生データ"""
        if 0 <= self.selected_life_index < len(self.lives):
            return self.lives[self.selected_life_index]
        return {}
    
    @rx.var
    def selected_score_result(self) -> Dict[str, Any]:
        """選択中のスコア結果"""
        if 0 <= self.selected_life_index < len(self.score_results):
            return self.score_results[self.selected_life_index]
        return {}
    
    @rx.var
    def selected_life_rank(self) -> str:
        """選択中の人生ランク"""
        result = self.selected_score_result
        return result.get("rank", "B") if result else "B"
    
    @rx.var
    def selected_life_story(self) -> str:
        """選択中の人生ストーリー"""
        return self._cached_life_story
    
    @rx.var
    def selected_parent_rank(self) -> str:
        """選択中の親ガチャランク"""
        return self._cached_parent_rank
    
    @rx.var
    def gacha_rates(self) -> Dict[str, str]:
        """現在の地域のガチャ確率"""
        return GachaService.GACHA_RATES.get(self.region, {})
    
    @rx.var
    def has_ss_or_s(self) -> bool:
        """SS/Sランクが含まれるか"""
        for result in self.score_results:
            rank = result.get("rank", "B")
            if rank in ["SS", "S"]:
                return True
        return False
    
    @rx.var
    def is_hokkaido(self) -> bool:
        """北海道が選択されているか"""
        return self.region == "hokkaido"
    
    @rx.var
    def is_tokyo(self) -> bool:
        """東京が選択されているか"""
        return self.region == "tokyo"
    
    @rx.var
    def total_score(self) -> int:
        """総合スコア"""
        return self._cached_total_score
    
    @rx.var
    def rank_label(self) -> str:
        """ランクラベル"""
        return self._cached_rank_label
    
    # スコア内訳（学歴）
    @rx.var
    def edu_score(self) -> float:
        return self._edu_score
    
    @rx.var
    def edu_value(self) -> str:
        return self._edu_value
    
    # スコア内訳（年収）
    @rx.var
    def income_score(self) -> float:
        return self._income_score
    
    @rx.var
    def income_value(self) -> str:
        return self._income_value
    
    # スコア内訳（寿命）
    @rx.var
    def lifespan_score(self) -> float:
        return self._lifespan_score
    
    @rx.var
    def lifespan_value(self) -> str:
        return self._lifespan_value
    
    # 親ガチャ結果
    @rx.var
    def parent_total_score(self) -> int:
        return self._parent_total_score
    
    @rx.var
    def parent_rank_label(self) -> str:
        return self._parent_rank_label
    
    @rx.var
    def parent_edu_score(self) -> float:
        return self._parent_edu_score
    
    @rx.var
    def parent_edu_value(self) -> str:
        return self._parent_edu_value
    
    @rx.var
    def parent_income_score(self) -> float:
        return self._parent_income_score
    
    @rx.var
    def parent_income_value(self) -> str:
        return self._parent_income_value
    
    @rx.var
    def parent_birthplace_score(self) -> float:
        return self._parent_birthplace_score
    
    @rx.var
    def parent_birthplace_value(self) -> str:
        return self._parent_birthplace_value
    
    # 人生詳細
    @rx.var
    def detail_gender(self) -> str:
        return self._detail_gender
    
    @rx.var
    def detail_birth_city(self) -> str:
        return self._detail_birth_city
    
    @rx.var
    def detail_household_income(self) -> str:
        return self._detail_household_income
    
    @rx.var
    def detail_father_education(self) -> str:
        return self._detail_father_education
    
    @rx.var
    def detail_mother_education(self) -> str:
        return self._detail_mother_education
    
    @rx.var
    def detail_father_education_display(self) -> str:
        """父学歴を表示用にフォーマット"""
        education = self._detail_father_education
        if not education or education == "不明":
            return "不明"
        education = str(education).strip()
        if "大学院" in education or "院卒" in education:
            return "院卒"
        elif "大学" in education or "大卒" in education:
            return "大卒"
        elif "短大" in education or "専門" in education or "専門学校" in education:
            return "短大・専門卒"
        elif "高校" in education or "高卒" in education:
            return "高卒"
        elif "中学" in education or "中卒" in education:
            return "中学卒"
        else:
            return education
    
    @rx.var
    def detail_mother_education_display(self) -> str:
        """母学歴を表示用にフォーマット"""
        education = self._detail_mother_education
        if not education or education == "不明":
            return "不明"
        education = str(education).strip()
        if "大学院" in education or "院卒" in education:
            return "院卒"
        elif "大学" in education or "大卒" in education:
            return "大卒"
        elif "短大" in education or "専門" in education or "専門学校" in education:
            return "短大・専門卒"
        elif "高校" in education or "高卒" in education:
            return "高卒"
        elif "中学" in education or "中卒" in education:
            return "中学卒"
        else:
            return education
    
    @rx.var
    def detail_high_school(self) -> bool:
        return self._detail_high_school
    
    @rx.var
    def detail_high_school_name(self) -> str:
        return self._detail_high_school_name
    
    @rx.var
    def detail_high_school_deviation(self) -> float:
        """高校の偏差値"""
        return self._detail_high_school_deviation
    
    @rx.var
    def detail_deviation_value(self) -> float:
        """個人の偏差値（初期）"""
        return self._detail_deviation_value
    
    @rx.var
    def detail_graduation_deviation(self) -> float:
        """卒業時の偏差値"""
        return self._detail_graduation_deviation
    
    @rx.var
    def detail_deviation_growth(self) -> str:
        """偏差値の成長（卒業時 - 初期）を表示用にフォーマット"""
        if self._detail_deviation_value == 0.0 or self._detail_graduation_deviation == 0.0:
            return ""
        growth = self._detail_graduation_deviation - self._detail_deviation_value
        if growth >= 0:
            return f"+{growth:.1f}"
        return f"{growth:.1f}"
    
    @rx.var
    def detail_university(self) -> bool:
        return self._detail_university
    
    @rx.var
    def detail_university_name(self) -> str:
        return self._detail_university_name
    
    @rx.var
    def detail_university_rank(self) -> str:
        return self._detail_university_rank
    
    @rx.var
    def detail_company_size(self) -> str:
        return self._detail_company_size
    
    @rx.var
    def detail_employment_type(self) -> str:
        return self._detail_employment_type
    
    @rx.var
    def detail_job_changes(self) -> int:
        return self._detail_job_changes
    
    @rx.var
    def detail_death_age(self) -> int:
        return self._detail_death_age
    
    @rx.var
    def detail_death_cause(self) -> str:
        return self._detail_death_cause


def get_rank_for_index(state: GachaState, index: int) -> str:
    """指定インデックスのランクを取得"""
    if 0 <= index < len(state.score_results):
        return state.score_results[index].get("rank", "B")
    return "B"
