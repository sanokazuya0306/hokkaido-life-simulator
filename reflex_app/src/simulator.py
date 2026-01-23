"""
人生シミュレーター メインクラス

各モジュールを統合してシミュレーションを実行する
"""

from pathlib import Path
from typing import Dict, Any, Optional

from .data_loader import DataLoader, REGION_CONFIG
from .simulators import BirthSimulator, EducationSimulator, CareerSimulator, DeathSimulator
from .scoring import LifeScorer
from .sns_generator import SNSReactionGenerator
from .formatter import LifeFormatter


class RegionalLifeSimulator:
    """
    地域別人生シミュレーターのメインクラス
    
    指定地域の公開データを使ってランダムに人生の軌跡を生成する
    """
    
    def __init__(self, data_dir: Optional[str] = None, region: str = "hokkaido"):
        """
        初期化
        
        Args:
            data_dir: データファイルが格納されているディレクトリ
                     Noneの場合はデフォルトのdataフォルダ
            region: 地域識別子 ("hokkaido" または "tokyo")
        """
        self.region = region
        if region not in REGION_CONFIG:
            raise ValueError(f"未対応の地域: {region}。対応地域: {list(REGION_CONFIG.keys())}")
        
        self.region_name = REGION_CONFIG[region]["name"]
        
        # データローダーの初期化
        self.data_loader = DataLoader(Path(data_dir) if data_dir else None, region=region)
        self.data_loader.load_all()
        
        # 各シミュレーターの初期化
        self.birth_sim = BirthSimulator(
            birth_data=self.data_loader.birth_data,
            workers_by_gender=self.data_loader.workers_by_gender,
            workers_by_industry_gender=self.data_loader.workers_by_industry_gender,
            workers_by_industry=self.data_loader.workers_by_industry,
            income_by_city=self.data_loader.income_by_city,
            education_level_by_gender=self.data_loader.education_level_by_gender,
            region=region,
        )
        
        self.education_sim = EducationSimulator(
            high_school_rates=self.data_loader.high_school_rates,
            high_schools_by_city=self.data_loader.high_schools_by_city,
            university_rates=self.data_loader.university_rates,
            university_destinations=self.data_loader.university_destinations,
            universities_by_prefecture=self.data_loader.universities_by_prefecture,
            parent_education_effect=self.data_loader.parent_education_effect,
            parent_income_effect=self.data_loader.parent_income_effect,
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
        self.scorer = LifeScorer(birthplace_scores=self.data_loader.birthplace_scores)
        self.sns_generator = SNSReactionGenerator()
        self.formatter = LifeFormatter(region=region)
    
    def generate_life(self) -> Dict[str, Any]:
        """
        1人の人生を生成
        
        Returns:
            人生データの辞書
        """
        from .deviation_value import DeviationValueCalculator
        
        # 性別と出生地
        gender = self.birth_sim.select_gender()
        birth_city = self.birth_sim.select_birth_city()
        
        # 世帯年収（出生地に基づく）
        household_income = self.birth_sim.select_household_income(birth_city)
        
        # 両親の職業
        father_industry = self.birth_sim.select_parent_industry("男性")
        mother_industry = self.birth_sim.select_parent_industry("女性")
        
        # 両親の最終学歴
        father_education = self.birth_sim.select_parent_education("男性")
        mother_education = self.birth_sim.select_parent_education("女性")
        
        # 個人の偏差値を計算（環境要因に基づく）
        deviation_value = DeviationValueCalculator.calculate_individual_deviation(
            father_education=father_education,
            mother_education=mother_education,
            household_income=household_income,
            birth_city=birth_city,
        )
        
        # 高校進学（親学歴・世帯年収を考慮）
        went_to_high_school = self.education_sim.decide_high_school(
            birth_city,
            father_education=father_education,
            mother_education=mother_education,
            household_income=household_income
        )
        
        # 高校選択（偏差値に基づく、性別で男女別学校をフィルタ）
        high_school_name = None
        high_school_deviation = None
        if went_to_high_school:
            high_school_name, high_school_deviation = self.education_sim.select_high_school_name(
                birth_city, deviation_value, gender
            )
            # 高校での学力成長をシミュレート
            graduation_deviation = DeviationValueCalculator.simulate_academic_growth(
                deviation_value, high_school_deviation
            )
        else:
            graduation_deviation = deviation_value
        
        # 大学進学（親学歴・世帯年収・高校偏差値を考慮）
        went_to_university = self.education_sim.decide_university(
            birth_city,
            went_to_high_school,
            father_education=father_education,
            mother_education=mother_education,
            household_income=household_income,
            high_school_deviation_value=high_school_deviation if went_to_high_school else None
        )
        
        # 大学選択（卒業時偏差値に基づく、性別で女子大をフィルタ）
        university_destination = None
        university_name = None
        university_rank = None
        if went_to_university:
            university_destination = self.education_sim.select_university_destination()
            if university_destination:
                university_name, university_rank = self.education_sim.select_university_name(
                    university_destination, graduation_deviation, gender
                )
        
        # 専門学校・短大進学（大学に進学しなかった高卒者対象）
        went_to_vocational_school = self.education_sim.decide_vocational_school(
            birth_city,
            went_to_high_school,
            went_to_university,
            father_education=father_education,
            mother_education=mother_education,
            household_income=household_income
        )

        # 大学院進学（大学に進学した場合のみ）
        went_to_graduate_school = self.education_sim.decide_graduate_school(
            went_to_university=went_to_university,
            university_rank=university_rank,
            gender=gender,
            father_education=father_education,
            mother_education=mother_education,
            household_income=household_income,
        )

        # 就業開始年齢と最終学歴を計算
        if went_to_graduate_school:
            start_work_age = 24  # 大学院卒（修士）
            education_level = "大学院卒"
        elif went_to_university:
            start_work_age = 22  # 大卒
            education_level = "大学卒"
        elif went_to_vocational_school:
            start_work_age = 20  # 短大・専門卒
            education_level = "短大・専門卒"
        elif went_to_high_school:
            start_work_age = 18  # 高卒
            education_level = "高校卒"
        else:
            start_work_age = 15  # 中卒
            education_level = "中学卒"
        
        # 企業規模と雇用形態を決定（学歴・性別・大学ランクに基づく）
        company_size = self.career_sim.select_company_size(education_level, university_rank)
        employment_type = self.career_sim.select_employment_type(education_level, gender, university_rank)
        
        # 定年年齢
        retirement_age = self.career_sim.select_retirement_age()
        
        # 死亡
        death_age = self.death_sim.select_death_age()
        death_cause = self.death_sim.select_death_cause(death_age)
        
        # 最初の就職先産業
        first_industry = self.career_sim.select_industry(gender)
        
        # キャリア履歴をシミュレーション
        # 終了年齢は定年または死亡の早い方
        if retirement_age is not None:
            career_end_age = min(retirement_age, death_age)
        else:
            # 定年なしの場合は死亡年齢まで（ただし75歳を上限とする）
            career_end_age = min(75, death_age)
        
        # 就業開始年齢が終了年齢より前の場合のみキャリア履歴を生成
        if start_work_age < career_end_age:
            career_history = self.career_sim.simulate_career_history(
                gender=gender,
                start_age=start_work_age,
                end_age=career_end_age,
                first_industry=first_industry,
            )
            career_summary = self.career_sim.get_career_summary(career_history)
        else:
            career_history = []
            career_summary = {
                "total_job_changes": 0,
                "total_separations": 0,
                "total_reemployments": 0,
                "total_companies": 0,
                "total_unemployment_years": 0,
                "final_employment_status": "未就業",
                "final_industry": None,
            }
        
        # 最終的な産業（キャリア履歴がある場合はそこから、なければ最初の産業）
        final_industry = career_summary.get("final_industry") or first_industry
        
        return {
            "region": self.region,  # 地域識別子（hokkaido/tokyo）
            "gender": gender,
            "birth_city": birth_city,
            "household_income": household_income,
            "father_industry": father_industry,
            "mother_industry": mother_industry,
            "father_education": father_education,
            "mother_education": mother_education,
            "deviation_value": deviation_value,  # 個人の偏差値（初期）
            "high_school": went_to_high_school,
            "high_school_name": high_school_name,
            "high_school_deviation": high_school_deviation,  # 高校の偏差値
            "graduation_deviation": graduation_deviation,  # 高校卒業時の偏差値
            "university": went_to_university,
            "university_destination": university_destination,
            "university_name": university_name,
            "university_rank": university_rank,  # 大学のランク（S/A/B/C/D）
            "vocational_school": went_to_vocational_school,  # 専門学校・短大進学
            "graduate_school": went_to_graduate_school,  # 大学院進学
            "start_work_age": start_work_age,
            "education_level": education_level,  # 最終学歴
            "company_size": company_size,  # 企業規模（大企業/中企業/小企業）
            "employment_type": employment_type,  # 雇用形態（正社員/非正規）
            "industry": final_industry,  # 後方互換性のため残す（最終的な産業）
            "first_industry": first_industry,  # 最初の就職先
            "career_history": career_history,  # キャリア履歴
            "career_summary": career_summary,  # キャリアサマリー
            "retirement_age": retirement_age,
            "death_age": death_age,
            "death_cause": death_cause,
        }
    
    def calculate_life_score(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        人生スコアを計算する（最終学歴、生涯年収、寿命の3要素）
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            スコア結果の辞書
        """
        return self.scorer.calculate_life_score(life)
    
    def calculate_parent_gacha_score(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        親ガチャスコアを計算する（親の学歴、世帯年収、出生地の3要素）
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            スコア結果の辞書
        """
        return self.scorer.calculate_parent_gacha_score(life)
    
    def calculate_all_scores(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        親ガチャスコアと人生スコアの両方を計算する
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            両方のスコア結果の辞書
        """
        return self.scorer.calculate_all_scores(life)
    
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
    
    @property
    def income_by_city(self):
        return self.data_loader.income_by_city
    
    @property
    def education_level_by_gender(self):
        return self.data_loader.education_level_by_gender
    
    @property
    def parent_education_effect(self):
        return self.data_loader.parent_education_effect
    
    @property
    def parent_income_effect(self):
        return self.data_loader.parent_income_effect


# 後方互換性のためのエイリアス
class HokkaidoLifeSimulator(RegionalLifeSimulator):
    """
    北海道人生シミュレーター（後方互換性のためのエイリアス）
    
    RegionalLifeSimulator(region="hokkaido") と同等
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        super().__init__(data_dir=data_dir, region="hokkaido")


class TokyoLifeSimulator(RegionalLifeSimulator):
    """
    東京人生シミュレーター
    
    RegionalLifeSimulator(region="tokyo") と同等
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        super().__init__(data_dir=data_dir, region="tokyo")
