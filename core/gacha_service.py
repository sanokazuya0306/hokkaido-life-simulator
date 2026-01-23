"""
ガチャサービス - UI非依存のコアロジック

このモジュールはUIに依存せず、純粋なPythonで人生ガチャの
ロジックを提供します。異なるUIフレームワーク（Streamlit, Flask,
FastAPI, CLI等）から同じ機能を利用できます。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path

# srcモジュールからインポート
import sys
_base_path = Path(__file__).parent.parent
if str(_base_path) not in sys.path:
    sys.path.insert(0, str(_base_path))

from src import RegionalLifeSimulator, REGION_CONFIG
from src.correlation_visualizer import create_correlation_sankey, get_correlation_summary


@dataclass
class LifeResult:
    """人生シミュレーション結果を保持するデータクラス"""
    life_data: Dict[str, Any]
    score_result: Dict[str, Any]
    parent_gacha_result: Dict[str, Any]
    life_story: str
    parent_rank: str
    
    @property
    def rank(self) -> str:
        """人生ランク"""
        return self.score_result.get('rank', 'B')
    
    @property
    def total_score(self) -> float:
        """総合スコア"""
        return self.score_result.get('total_score', 0)
    
    @property
    def rank_label(self) -> str:
        """ランクラベル"""
        return self.score_result.get('rank_label', '普通')


class GachaService:
    """
    ガチャサービス - UI非依存のコアサービスクラス
    
    使用例:
        # サービスのインスタンス化
        service = GachaService(region="hokkaido")
        
        # 人生を生成
        results = service.generate_lives(count=5)
        
        # 結果を取得
        for result in results:
            print(f"ランク: {result.rank}")
            print(f"ストーリー: {result.life_story}")
    """
    
    # 地域設定
    REGION_DISPLAY = {
        "hokkaido": {"name": "北海道", "icon": "🏔️", "color": "#1f77b4", "data_source": "北海道庁・厚生労働省"},
        "tokyo": {"name": "東京", "icon": "🗼", "color": "#e63946", "data_source": "東京都・厚生労働省"},
    }
    
    # ガチャ確率（10,000サンプルで計算済み）
    GACHA_RATES = {
        "hokkaido": {"SS": "1.95%", "S": "10.15%", "A": "15.36%", "B": "31.70%", "C": "39.84%", "D": "1.00%"},
        "tokyo": {"SS": "4.97%", "S": "16.15%", "A": "19.78%", "B": "31.70%", "C": "26.51%", "D": "0.89%"},
    }
    
    # ランク情報
    RANK_INFO = {
        "SS": {"color": "#1a1a1a", "label": "超大当たり", "desc": "生涯年収上位1%、高学歴、長寿"},
        "S": {"color": "#333333", "label": "大当たり", "desc": "生涯年収上位10%、高学歴"},
        "A": {"color": "#4d4d4d", "label": "当たり", "desc": "平均以上の人生"},
        "B": {"color": "#666666", "label": "普通", "desc": "一般的な人生"},
        "C": {"color": "#808080", "label": "ハズレ", "desc": "平均以下の人生"},
        "D": {"color": "#999999", "label": "大ハズレ", "desc": "早逝など"},
    }
    
    def __init__(self, region: str = "hokkaido", data_dir: Optional[str] = None):
        """
        初期化
        
        Args:
            region: 地域識別子 ("hokkaido" または "tokyo")
            data_dir: データディレクトリのパス（省略時はデフォルト）
        """
        if region not in REGION_CONFIG:
            raise ValueError(f"未対応の地域: {region}。対応地域: {list(REGION_CONFIG.keys())}")
        
        self.region = region
        self._simulator = RegionalLifeSimulator(data_dir=data_dir, region=region)
    
    @property
    def simulator(self) -> RegionalLifeSimulator:
        """シミュレーターインスタンス"""
        return self._simulator
    
    @property
    def region_info(self) -> Dict[str, Any]:
        """現在の地域情報"""
        return self.REGION_DISPLAY[self.region]
    
    @property
    def rates(self) -> Dict[str, str]:
        """現在の地域のガチャ確率"""
        return self.GACHA_RATES[self.region]
    
    def generate_life(self) -> LifeResult:
        """
        1人の人生を生成
        
        Returns:
            LifeResult: 人生シミュレーション結果
        """
        life = self._simulator.generate_life()
        score_result = self._simulator.calculate_life_score(life)
        parent_gacha_result = self._simulator.calculate_parent_gacha_score(life)
        life_story = self._generate_life_story(life)
        parent_rank = self._calculate_parent_rank(life)
        
        return LifeResult(
            life_data=life,
            score_result=score_result,
            parent_gacha_result=parent_gacha_result,
            life_story=life_story,
            parent_rank=parent_rank,
        )
    
    def generate_lives(self, count: int) -> List[LifeResult]:
        """
        複数の人生を生成
        
        Args:
            count: 生成する人数
            
        Returns:
            LifeResultのリスト
        """
        return [self.generate_life() for _ in range(count)]
    
    def _generate_life_story(self, life: Dict[str, Any]) -> str:
        """人生データからストーリーテキストを生成"""
        lines = []
        
        # 出生
        birth_city = life.get('birth_city', '不明')
        gender = "男性" if life.get('gender') == 'male' else "女性"
        lines.append(f"{birth_city}に{gender}として生まれる")
        
        # 家庭環境
        income = life.get('household_income', '不明')
        father_edu = life.get('father_education', '不明')
        mother_edu = life.get('mother_education', '不明')
        lines.append(f"世帯年収{income}、父親は{father_edu}、母親は{mother_edu}")
        
        # 高校進学
        if life.get('high_school'):
            hs_name = life.get('high_school_name')
            if hs_name:
                if isinstance(hs_name, dict):
                    hs_name = hs_name.get('name', '不明な高校')
                lines.append(f"{hs_name}に進学")
            else:
                lines.append("高校に進学")
        
        # 大学進学
        if life.get('university'):
            uni_name = life.get('university_name')
            uni_dest = life.get('university_destination', '')
            if uni_name:
                if isinstance(uni_name, dict):
                    uni_name = uni_name.get('name', '不明な大学')
                prefix = f"{uni_dest}の" if uni_dest and uni_dest != '北海道' else ""
                lines.append(f"{prefix}{uni_name}に進学")
            else:
                lines.append("大学に進学")
        
        # 就職
        first_industry = life.get('first_industry') or life.get('industry')
        company_size = life.get('company_size')
        employment_type = life.get('employment_type', '正社員')
        education_level = life.get('education_level', '')
        
        if first_industry and company_size:
            if '大学' in education_level:
                lines.append(f"大学卒業後、{first_industry}の{company_size}に{employment_type}として就職")
            elif '高校' in education_level:
                lines.append(f"高校卒業後、{first_industry}の{company_size}に{employment_type}として就職")
            else:
                lines.append(f"{first_industry}の{company_size}に{employment_type}として就職")
        
        # キャリア
        career_summary = life.get('career_summary', {})
        job_changes = career_summary.get('total_job_changes', 0)
        retirement_age = life.get('retirement_age')
        
        # 生涯年収を計算（スコアから取得、万円単位）
        score_result = self._simulator.calculate_life_score(life)
        lifetime_income = score_result.get('breakdown', {}).get('lifetime_income', {}).get('raw_value', 0)
        # 万円 → 億円 に変換（10000万円 = 1億円）
        income_oku = lifetime_income / 10000 if lifetime_income else 0
        
        if retirement_age:
            lines.append(f"{job_changes}回の転職を経て、{retirement_age}歳で定年退職。生涯年収約{income_oku:.1f}億円")
        else:
            lines.append(f"{job_changes}回の転職。生涯年収約{income_oku:.1f}億円")
        
        # 死亡
        death_age = life.get('death_age', 80)
        death_cause = life.get('death_cause', '老衰')
        lines.append(f"{death_age}歳で{death_cause}により死亡")
        
        return "\n".join(lines)
    
    def _calculate_parent_rank(self, life: Dict[str, Any]) -> str:
        """親ガチャランクを計算"""
        score = 0
        
        income = life.get('household_income', '')
        if '1000万以上' in income or '1500万' in income:
            score += 40
        elif '700' in income or '800' in income or '900' in income:
            score += 30
        elif '500' in income or '600' in income:
            score += 20
        elif '300' in income or '400' in income:
            score += 10
        else:
            score += 5
        
        father_edu = life.get('father_education', '')
        if '大卒' in father_edu or '大学' in father_edu:
            score += 30
        elif '高卒' in father_edu:
            score += 15
        else:
            score += 5
        
        mother_edu = life.get('mother_education', '')
        if '大卒' in mother_edu or '大学' in mother_edu:
            score += 30
        elif '高卒' in mother_edu:
            score += 15
        else:
            score += 5
        
        if score >= 90:
            return 'SS'
        elif score >= 75:
            return 'S'
        elif score >= 60:
            return 'A'
        elif score >= 45:
            return 'B'
        elif score >= 30:
            return 'C'
        else:
            return 'D'
    
    def get_dataset_info(self) -> List[Dict[str, Any]]:
        """データセット情報を取得"""
        return self._simulator.data_loader.get_dataset_info()
    
    @staticmethod
    def get_correlation_summary() -> Dict[str, int]:
        """相関図のサマリー情報を取得"""
        return get_correlation_summary()
    
    @staticmethod
    def create_correlation_figure():
        """相関図（Plotly Figure）を作成"""
        return create_correlation_sankey()
    
    @staticmethod
    def get_available_regions() -> List[str]:
        """利用可能な地域のリストを取得"""
        return list(REGION_CONFIG.keys())
    
    def format_life(self, life: Dict[str, Any], show_score: bool = True, show_sns: bool = False) -> str:
        """人生の軌跡を文字列でフォーマット"""
        return self._simulator.format_life(life, show_score=show_score, show_sns=show_sns)


# ============================================
# キャッシュ機能付きファクトリー関数
# ============================================

# シングルトンキャッシュ（UIフレームワーク非依存）
_service_cache: Dict[str, GachaService] = {}


def get_gacha_service(region: str = "hokkaido", use_cache: bool = True) -> GachaService:
    """
    GachaServiceのインスタンスを取得（キャッシュ対応）
    
    Args:
        region: 地域識別子
        use_cache: キャッシュを使用するかどうか
        
    Returns:
        GachaService インスタンス
    """
    if use_cache and region in _service_cache:
        return _service_cache[region]
    
    service = GachaService(region=region)
    
    if use_cache:
        _service_cache[region] = service
    
    return service


def clear_service_cache(region: Optional[str] = None):
    """
    サービスキャッシュをクリア
    
    Args:
        region: 特定の地域のみクリアする場合は地域名、全てクリアする場合はNone
    """
    global _service_cache
    if region:
        _service_cache.pop(region, None)
    else:
        _service_cache.clear()
