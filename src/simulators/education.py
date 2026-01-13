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
    ):
        """
        初期化
        
        Args:
            high_school_rates: 市町村別高校進学率
            high_schools_by_city: 市町村別高校リスト
            university_rates: 市町村別大学進学率
            university_destinations: 大学進学先都道府県データ
            universities_by_prefecture: 都道府県別大学リスト
        """
        self.high_school_rates = high_school_rates
        self.high_schools_by_city = high_schools_by_city
        self.university_rates = university_rates
        self.university_destinations = university_destinations
        self.universities_by_prefecture = universities_by_prefecture
    
    def decide_high_school(self, city: str) -> bool:
        """
        高校進学を決定
        
        Args:
            city: 出身市町村
            
        Returns:
            高校に進学するかどうか
        """
        rate = self.high_school_rates.get(city, self.high_school_rates.get("default", 98.0))
        return random.random() * 100 < rate
    
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
    
    def decide_university(self, city: str, went_to_high_school: bool) -> bool:
        """
        大学進学を決定（高校に進学した場合のみ）
        
        Args:
            city: 出身市町村
            went_to_high_school: 高校に進学したかどうか
            
        Returns:
            大学に進学するかどうか
        """
        if not went_to_high_school:
            return False
        
        rate = self.university_rates.get(city, self.university_rates.get("default", 50.0))
        return random.random() * 100 < rate
    
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
