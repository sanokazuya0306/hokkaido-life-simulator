"""
北海道人生シミュレーター メインクラス

各モジュールを統合してシミュレーションを実行する
"""

from pathlib import Path
from typing import Dict, Any, Optional

from .data_loader import DataLoader
from .simulators import BirthSimulator, EducationSimulator, CareerSimulator, DeathSimulator
from .scoring import LifeScorer
from .sns_generator import SNSReactionGenerator
from .formatter import LifeFormatter


class HokkaidoLifeSimulator:
    """
    北海道人生シミュレーターのメインクラス
    
    北海道の公開データを使ってランダムに人生の軌跡を生成する
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        初期化
        
        Args:
            data_dir: データファイルが格納されているディレクトリ
                     Noneの場合はデフォルトのdataフォルダ
        """
        # データローダーの初期化
        self.data_loader = DataLoader(Path(data_dir) if data_dir else None)
        self.data_loader.load_all()
        
        # 各シミュレーターの初期化
        self.birth_sim = BirthSimulator(
            birth_data=self.data_loader.birth_data,
            workers_by_gender=self.data_loader.workers_by_gender,
            workers_by_industry_gender=self.data_loader.workers_by_industry_gender,
            workers_by_industry=self.data_loader.workers_by_industry,
        )
        
        self.education_sim = EducationSimulator(
            high_school_rates=self.data_loader.high_school_rates,
            high_schools_by_city=self.data_loader.high_schools_by_city,
            university_rates=self.data_loader.university_rates,
            university_destinations=self.data_loader.university_destinations,
            universities_by_prefecture=self.data_loader.universities_by_prefecture,
        )
        
        self.career_sim = CareerSimulator(
            workers_by_industry=self.data_loader.workers_by_industry,
            workers_by_industry_gender=self.data_loader.workers_by_industry_gender,
            retirement_age_distribution=self.data_loader.retirement_age_distribution,
        )
        
        self.death_sim = DeathSimulator(
            death_by_age=self.data_loader.death_by_age,
            death_by_cause=self.data_loader.death_by_cause,
        )
        
        # スコア計算・SNS生成・フォーマッターの初期化
        self.scorer = LifeScorer()
        self.sns_generator = SNSReactionGenerator()
        self.formatter = LifeFormatter()
    
    def generate_life(self) -> Dict[str, Any]:
        """
        1人の人生を生成
        
        Returns:
            人生データの辞書
        """
        # 性別と出生地
        gender = self.birth_sim.select_gender()
        birth_city = self.birth_sim.select_birth_city()
        
        # 両親の職業
        father_industry = self.birth_sim.select_parent_industry("男性")
        mother_industry = self.birth_sim.select_parent_industry("女性")
        
        # 高校進学
        went_to_high_school = self.education_sim.decide_high_school(birth_city)
        high_school_name = self.education_sim.select_high_school_name(birth_city) if went_to_high_school else None
        
        # 大学進学
        went_to_university = self.education_sim.decide_university(birth_city, went_to_high_school)
        university_destination = self.education_sim.select_university_destination() if went_to_university else None
        university_name = self.education_sim.select_university_name(university_destination) if went_to_university and university_destination else None
        
        # キャリア
        industry = self.career_sim.select_industry(gender)
        retirement_age = self.career_sim.select_retirement_age()
        
        # 死亡
        death_age = self.death_sim.select_death_age()
        death_cause = self.death_sim.select_death_cause()
        
        return {
            "gender": gender,
            "birth_city": birth_city,
            "father_industry": father_industry,
            "mother_industry": mother_industry,
            "high_school": went_to_high_school,
            "high_school_name": high_school_name,
            "university": went_to_university,
            "university_destination": university_destination,
            "university_name": university_name,
            "industry": industry,
            "retirement_age": retirement_age,
            "death_age": death_age,
            "death_cause": death_cause,
        }
    
    def calculate_life_score(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        人生のスコアを計算する
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            スコア結果の辞書
        """
        return self.scorer.calculate_life_score(life)
    
    def generate_sns_reactions(
        self,
        life: Dict[str, Any],
        score_result: Dict[str, Any],
    ) -> list:
        """
        SNS反応を生成する
        
        Args:
            life: 人生データ
            score_result: スコア計算結果
            
        Returns:
            SNS反応のリスト
        """
        return self.sns_generator.generate_reactions(life, score_result)
    
    def format_life(
        self,
        life: Dict[str, Any],
        show_score: bool = True,
        verbose_score: bool = True,
        show_sns: bool = True,
    ) -> str:
        """
        人生の軌跡を文字列でフォーマット
        
        Args:
            life: 人生データ
            show_score: スコアを表示するかどうか
            verbose_score: スコアの詳細な根拠を表示するかどうか
            show_sns: SNS反応を表示するかどうか
            
        Returns:
            フォーマットされた文字列
        """
        # スコアを計算
        score_result = None
        sns_reactions = None
        
        if show_score or show_sns:
            score_result = self.calculate_life_score(life)
        
        if show_sns and score_result:
            sns_reactions = self.generate_sns_reactions(life, score_result)
        
        return self.formatter.format_life(
            life=life,
            score_result=score_result if show_score else None,
            sns_reactions=sns_reactions if show_sns else None,
            show_score=show_score,
            verbose_score=verbose_score,
            show_sns=show_sns,
        )
    
    def format_score_breakdown(
        self,
        score_result: Dict[str, Any],
        verbose: bool = True,
    ) -> str:
        """
        スコアの内訳を文字列でフォーマット
        
        Args:
            score_result: calculate_life_score()の戻り値
            verbose: 詳細な根拠を表示するかどうか
            
        Returns:
            フォーマットされたスコア情報
        """
        return self.formatter.format_score_breakdown(score_result, verbose)
    
    def format_sns_reactions(self, reactions: list) -> str:
        """
        SNS反応をフォーマット
        
        Args:
            reactions: SNS反応のリスト
            
        Returns:
            フォーマットされた文字列
        """
        return self.formatter.format_sns_reactions(reactions)
    
    def get_dataset_info(self) -> str:
        """
        使用しているデータセットの情報をフォーマットして返す
        
        Returns:
            フォーマットされたデータセット情報
        """
        datasets = self.data_loader.get_dataset_info()
        return self.formatter.format_dataset_info(datasets)
    
    # 後方互換性のためのプロパティ
    @property
    def birth_data(self):
        return self.data_loader.birth_data
    
    @property
    def high_school_rates(self):
        return self.data_loader.high_school_rates
    
    @property
    def university_rates(self):
        return self.data_loader.university_rates
    
    @property
    def university_destinations(self):
        return self.data_loader.university_destinations
    
    @property
    def workers_by_industry(self):
        return self.data_loader.workers_by_industry
    
    @property
    def workers_by_gender(self):
        return self.data_loader.workers_by_gender
    
    @property
    def workers_by_industry_gender(self):
        return self.data_loader.workers_by_industry_gender
    
    @property
    def retirement_age_distribution(self):
        return self.data_loader.retirement_age_distribution
    
    @property
    def death_by_age(self):
        return self.data_loader.death_by_age
    
    @property
    def death_by_cause(self):
        return self.data_loader.death_by_cause
