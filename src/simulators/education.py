"""
教育シミュレーター

高校・大学進学の決定を担当
"""

import random
from typing import Dict, List, Any, Optional


class EducationSimulator:
    """教育に関するシミュレーションを担当するクラス"""
    
    def __init__(
        self,
        high_school_rates: Dict[str, float],
        high_schools_by_city: Dict[str, List[str]],
        university_rates: Dict[str, float],
        university_destinations: List[Dict[str, Any]],
        universities_by_prefecture: Dict[str, List[Dict[str, Any]]],
        parent_education_effect: Optional[Dict[str, Dict[str, float]]] = None,
        parent_income_effect: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        """
        初期化
        
        Args:
            high_school_rates: 市町村別高校進学率
            high_schools_by_city: 市町村別高校リスト
            university_rates: 市町村別大学進学率
            university_destinations: 大学進学先都道府県データ
            universities_by_prefecture: 都道府県別大学リスト
            parent_education_effect: 親学歴が子学歴に与える影響の係数
            parent_income_effect: 親の世帯年収が子学歴に与える影響の係数
        """
        self.high_school_rates = high_school_rates
        self.high_schools_by_city = high_schools_by_city
        self.university_rates = university_rates
        self.university_destinations = university_destinations
        self.universities_by_prefecture = universities_by_prefecture
        self.parent_education_effect = parent_education_effect or {}
        self.parent_income_effect = parent_income_effect or {}
    
    def _get_parent_education_modifier(
        self,
        father_education: Optional[str],
        mother_education: Optional[str],
        modifier_type: str
    ) -> float:
        """
        両親の学歴から進学率の補正係数を計算
        
        Args:
            father_education: 父親の最終学歴
            mother_education: 母親の最終学歴
            modifier_type: "high_school_modifier" or "university_modifier"
            
        Returns:
            補正係数（両親の平均値）
        """
        if not self.parent_education_effect:
            return 1.0
        
        modifiers = []
        
        # 父親の学歴から補正係数を取得
        if father_education and father_education in self.parent_education_effect:
            modifiers.append(self.parent_education_effect[father_education].get(modifier_type, 1.0))
        
        # 母親の学歴から補正係数を取得
        if mother_education and mother_education in self.parent_education_effect:
            modifiers.append(self.parent_education_effect[mother_education].get(modifier_type, 1.0))
        
        # 両親の平均を取る（データがない場合は1.0）
        if modifiers:
            return sum(modifiers) / len(modifiers)
        return 1.0
    
    def _get_income_modifier(
        self,
        household_income: Optional[str],
        modifier_type: str
    ) -> float:
        """
        世帯年収から進学率の補正係数を計算
        
        Args:
            household_income: 世帯年収（例: "500〜700万円"）
            modifier_type: "high_school_modifier" or "university_modifier"
            
        Returns:
            補正係数
        """
        if not self.parent_income_effect or not household_income:
            return 1.0
        
        if household_income in self.parent_income_effect:
            return self.parent_income_effect[household_income].get(modifier_type, 1.0)
        
        return 1.0
    
    def decide_high_school(
        self,
        city: str,
        father_education: Optional[str] = None,
        mother_education: Optional[str] = None,
        household_income: Optional[str] = None
    ) -> bool:
        """
        高校進学を決定（親学歴・世帯年収を考慮）
        
        Args:
            city: 出身市町村
            father_education: 父親の最終学歴
            mother_education: 母親の最終学歴
            household_income: 世帯年収
            
        Returns:
            高校に進学するかどうか
        """
        base_rate = self.high_school_rates.get(city, self.high_school_rates.get("default", 98.0))
        
        # 親学歴による補正
        education_modifier = self._get_parent_education_modifier(
            father_education, mother_education, "high_school_modifier"
        )
        
        # 世帯年収による補正
        income_modifier = self._get_income_modifier(
            household_income, "high_school_modifier"
        )
        
        # 補正後の進学率（100%を超えないように）
        # 親学歴と世帯年収の補正を組み合わせる（相関があるため平均を取る）
        combined_modifier = (education_modifier + income_modifier) / 2
        adjusted_rate = min(100.0, base_rate * combined_modifier)
        
        return random.random() * 100 < adjusted_rate
    
    def select_high_school_name(self, city: str) -> str:
        """
        出生地に近接した高校名を選択
        
        Args:
            city: 出身市町村
            
        Returns:
            高校名
        """
        # まず出生地の市町村で高校を探す
        if city in self.high_schools_by_city:
            return random.choice(self.high_schools_by_city[city])
        
        # 札幌市の区の場合
        if "札幌市" in city:
            if city in self.high_schools_by_city:
                return random.choice(self.high_schools_by_city[city])
            # 区名だけを抽出して検索
            for key in self.high_schools_by_city:
                if key in city or city in key:
                    return random.choice(self.high_schools_by_city[key])
            # 札幌市内のいずれかの高校を選択
            sapporo_schools = []
            for key, schools in self.high_schools_by_city.items():
                if "札幌" in key:
                    sapporo_schools.extend(schools)
            if sapporo_schools:
                return random.choice(sapporo_schools)
        
        # 市町村名の部分一致で探す
        city_base = city.replace("市", "").replace("町", "").replace("村", "")
        for key, schools in self.high_schools_by_city.items():
            if city_base in key or key.replace("市", "").replace("町", "").replace("村", "") in city:
                return random.choice(schools)
        
        # 見つからない場合は汎用名を生成
        city_short = city.replace("市", "").replace("町", "").replace("村", "")
        return f"{city_short}高校"
    
    def decide_university(
        self,
        city: str,
        went_to_high_school: bool,
        father_education: Optional[str] = None,
        mother_education: Optional[str] = None,
        household_income: Optional[str] = None
    ) -> bool:
        """
        大学進学を決定（高校に進学した場合のみ、親学歴・世帯年収を考慮）
        
        Args:
            city: 出身市町村
            went_to_high_school: 高校に進学したかどうか
            father_education: 父親の最終学歴
            mother_education: 母親の最終学歴
            household_income: 世帯年収
            
        Returns:
            大学に進学するかどうか
        """
        if not went_to_high_school:
            return False
        
        base_rate = self.university_rates.get(city, self.university_rates.get("default", 50.0))
        
        # 親学歴による補正
        education_modifier = self._get_parent_education_modifier(
            father_education, mother_education, "university_modifier"
        )
        
        # 世帯年収による補正
        income_modifier = self._get_income_modifier(
            household_income, "university_modifier"
        )
        
        # 補正後の進学率（100%を超えないように）
        # 親学歴と世帯年収の補正を組み合わせる（相関があるため平均を取る）
        combined_modifier = (education_modifier + income_modifier) / 2
        adjusted_rate = min(100.0, base_rate * combined_modifier)
        
        return random.random() * 100 < adjusted_rate
    
    def select_university_destination(self) -> str:
        """
        大学進学先の都道府県をランダムに選択（進学者数に基づく重み付き選択）
        
        Returns:
            都道府県名
        """
        if not self.university_destinations:
            return "北海道"
        
        total_students = sum(item["count"] for item in self.university_destinations)
        if total_students == 0:
            return random.choice(self.university_destinations)["prefecture"] if self.university_destinations else "北海道"
        
        rand = random.uniform(0, total_students)
        cumulative = 0
        for item in self.university_destinations:
            cumulative += item["count"]
            if rand <= cumulative:
                return item["prefecture"]
        
        return self.university_destinations[-1]["prefecture"]
    
    def select_university_name(self, prefecture: str) -> str:
        """
        進学先都道府県から大学名を入学者数に基づいて選択
        
        Args:
            prefecture: 都道府県名
            
        Returns:
            大学名
        """
        if prefecture in self.universities_by_prefecture:
            universities = self.universities_by_prefecture[prefecture]
        else:
            return f"{prefecture}の大学"
        
        if not universities:
            return f"{prefecture}の大学"
        
        # 入学者数に基づく重み付き選択
        total_enrollment = sum(u["enrollment"] for u in universities)
        if total_enrollment == 0:
            return random.choice(universities)["name"]
        
        rand = random.uniform(0, total_enrollment)
        cumulative = 0
        for univ in universities:
            cumulative += univ["enrollment"]
            if rand <= cumulative:
                return univ["name"]
        
        return universities[-1]["name"]
    
    def decide_vocational_school(
        self,
        city: str,
        went_to_high_school: bool,
        went_to_university: bool,
        father_education: Optional[str] = None,
        mother_education: Optional[str] = None,
        household_income: Optional[str] = None
    ) -> bool:
        """
        専門学校・短大への進学を決定（大学に進学しなかった高卒者対象）
        
        北海道の統計データ:
        - 専修学校卒業者: 8,339人
        - 短期大学卒業者: 1,332人
        - 大学に進学しない高卒者のうち約30%が専門学校・短大に進学と仮定
        
        Args:
            city: 出身市町村
            went_to_high_school: 高校に進学したかどうか
            went_to_university: 大学に進学したかどうか
            father_education: 父親の最終学歴
            mother_education: 母親の最終学歴
            household_income: 世帯年収
            
        Returns:
            専門学校・短大に進学するかどうか
        """
        # 大学に進学した場合は専門学校・短大には行かない
        if went_to_university:
            return False
        
        # 高校に進学していない場合は専門学校・短大にも行かない
        if not went_to_high_school:
            return False
        
        # 基本進学率: 大学不進学者の約30%が専門・短大に進学
        base_rate = 30.0
        
        # 親学歴による補正（大学進学と同様の補正を使用）
        education_modifier = self._get_parent_education_modifier(
            father_education, mother_education, "university_modifier"
        )
        
        # 世帯年収による補正
        income_modifier = self._get_income_modifier(
            household_income, "university_modifier"
        )
        
        # 補正後の進学率（100%を超えないように、0%を下回らないように）
        combined_modifier = (education_modifier + income_modifier) / 2
        adjusted_rate = max(0.0, min(100.0, base_rate * combined_modifier))
        
        return random.random() * 100 < adjusted_rate

