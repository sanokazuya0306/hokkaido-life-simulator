"""
キャリアシミュレーター

就職先の産業、転職・離職・再就職、定年年齢の決定を担当

転職・離職データは厚生労働省「令和6年雇用動向調査」に基づく
"""

import csv
import random
from pathlib import Path
from typing import Dict, List, Any, Optional


# デフォルトの転職・離職率データ（CSVがない場合に使用）
DEFAULT_JOB_MOBILITY_DATA = [
    {"age_min": 20, "age_max": 24, "male_job_change_rate": 14.6, "female_job_change_rate": 14.1,
     "male_separation_rate": 15.2, "female_separation_rate": 17.2,
     "male_reemployment_rate": 70, "female_reemployment_rate": 60},
    {"age_min": 25, "age_max": 29, "male_job_change_rate": 13.4, "female_job_change_rate": 13.4,
     "male_separation_rate": 13.4, "female_separation_rate": 17.1,
     "male_reemployment_rate": 70, "female_reemployment_rate": 55},
    {"age_min": 30, "age_max": 34, "male_job_change_rate": 9.4, "female_job_change_rate": 11.8,
     "male_separation_rate": 9.4, "female_separation_rate": 15.3,
     "male_reemployment_rate": 65, "female_reemployment_rate": 45},
    {"age_min": 35, "age_max": 39, "male_job_change_rate": 7.4, "female_job_change_rate": 10.5,
     "male_separation_rate": 7.5, "female_separation_rate": 12.0,
     "male_reemployment_rate": 60, "female_reemployment_rate": 45},
    {"age_min": 40, "age_max": 44, "male_job_change_rate": 5.9, "female_job_change_rate": 9.8,
     "male_separation_rate": 6.0, "female_separation_rate": 10.0,
     "male_reemployment_rate": 55, "female_reemployment_rate": 50},
    {"age_min": 45, "age_max": 49, "male_job_change_rate": 5.2, "female_job_change_rate": 9.4,
     "male_separation_rate": 5.5, "female_separation_rate": 9.4,
     "male_reemployment_rate": 50, "female_reemployment_rate": 55},
    {"age_min": 50, "age_max": 54, "male_job_change_rate": 4.8, "female_job_change_rate": 8.9,
     "male_separation_rate": 5.4, "female_separation_rate": 8.9,
     "male_reemployment_rate": 45, "female_reemployment_rate": 60},
    {"age_min": 55, "age_max": 59, "male_job_change_rate": 5.5, "female_job_change_rate": 8.7,
     "male_separation_rate": 7.1, "female_separation_rate": 8.8,
     "male_reemployment_rate": 40, "female_reemployment_rate": 55},
]


class CareerSimulator:
    """キャリアに関するシミュレーションを担当するクラス"""
    
    def __init__(
        self,
        workers_by_industry: List[Dict[str, Any]],
        workers_by_industry_gender: Dict[str, Dict[str, int]],
        retirement_age_distribution: List[Dict[str, Any]],
        job_mobility_data: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        初期化
        
        Args:
            workers_by_industry: 産業別労働者数データ
            workers_by_industry_gender: 性別×産業別労働者数
            retirement_age_distribution: 定年年齢分布
            job_mobility_data: 転職・離職率データ（Noneの場合はデフォルト使用）
        """
        self.workers_by_industry = workers_by_industry
        self.workers_by_industry_gender = workers_by_industry_gender
        self.retirement_age_distribution = retirement_age_distribution
        self.job_mobility_data = job_mobility_data or DEFAULT_JOB_MOBILITY_DATA
    
    def select_industry(self, gender: Optional[str] = None) -> str:
        """
        就職先の産業をランダムに選択（労働者数に基づく重み付き選択）
        
        Args:
            gender: 性別（指定された場合、性別に応じた産業分布を使用）
            
        Returns:
            産業名
        """
        # 性別が指定されていて、性別×産業データがある場合
        if gender and self.workers_by_industry_gender:
            industry_weights = []
            for industry, gender_data in self.workers_by_industry_gender.items():
                count = gender_data.get(gender, 0)
                if count > 0:
                    industry_weights.append({"industry": industry, "count": count})
            
            if industry_weights:
                total_workers = sum(item["count"] for item in industry_weights)
                if total_workers > 0:
                    rand = random.uniform(0, total_workers)
                    cumulative = 0
                    for item in industry_weights:
                        cumulative += item["count"]
                        if rand <= cumulative:
                            return item["industry"]
                    return industry_weights[-1]["industry"]
        
        # 性別データがない場合は従来の全体データを使用
        if not self.workers_by_industry:
            return "不明"
        
        total_workers = sum(item["count"] for item in self.workers_by_industry)
        if total_workers == 0:
            return random.choice(self.workers_by_industry)["industry"] if self.workers_by_industry else "不明"
        
        rand = random.uniform(0, total_workers)
        cumulative = 0
        for item in self.workers_by_industry:
            cumulative += item["count"]
            if rand <= cumulative:
                return item["industry"]
        
        return self.workers_by_industry[-1]["industry"]
    
    def select_retirement_age(self) -> Optional[int]:
        """
        定年年齢をランダムに選択（定年年齢分布に基づく重み付き選択）
        
        Returns:
            定年年齢（定年なしの場合はNone）
        """
        if not self.retirement_age_distribution:
            return 60  # デフォルト
        
        total_ratio = sum(item["ratio"] for item in self.retirement_age_distribution)
        if total_ratio == 0:
            return 60
        
        rand = random.uniform(0, total_ratio)
        cumulative = 0
        for item in self.retirement_age_distribution:
            cumulative += item["ratio"]
            if rand <= cumulative:
                category = item["category"]
                
                # カテゴリに応じて具体的な年齢を返す
                if category == "60歳":
                    return 60
                elif category == "61-64歳":
                    return random.randint(61, 64)
                elif category == "65歳":
                    return 65
                elif category == "66歳以上":
                    return random.randint(66, 75)
                elif category == "定年なし":
                    return None  # 定年なし
                else:
                    return 60
        
        return 60
    
    def _get_rate_for_age(self, age: int, gender: str, rate_type: str) -> float:
        """
        指定年齢・性別の各種率を取得
        
        Args:
            age: 年齢
            gender: "男性" または "女性"
            rate_type: "job_change"（転職）, "separation"（離職）, "reemployment"（再就職）
        
        Returns:
            該当年齢の率（%）
        """
        gender_prefix = "male" if gender == "男性" else "female"
        rate_key = f"{gender_prefix}_{rate_type}_rate"
        
        for data in self.job_mobility_data:
            if data["age_min"] <= age <= data["age_max"]:
                return data.get(rate_key, 5.0)
        
        # 範囲外の場合は最後のデータを使用
        if self.job_mobility_data:
            return self.job_mobility_data[-1].get(rate_key, 5.0)
        return 5.0  # デフォルト
    
    def simulate_career_history(
        self,
        gender: str,
        start_age: int,
        end_age: int,
        first_industry: str,
    ) -> List[Dict[str, Any]]:
        """
        就職から定年または死亡までのキャリア履歴をシミュレーション
        
        Args:
            gender: "男性" または "女性"
            start_age: 就業開始年齢
            end_age: 終了年齢（定年または死亡年齢の小さい方）
            first_industry: 最初の就職先産業
        
        Returns:
            キャリアイベントのリスト
        """
        events = []
        current_company = 1
        current_industry = first_industry
        is_employed = True
        unemployment_start_age = None
        
        # 最初の就職イベントを記録
        events.append({
            "age": start_age,
            "type": "就職",
            "industry": current_industry,
            "company_number": current_company,
        })
        
        for age in range(start_age, end_age):
            if is_employed:
                # 就業中の場合
                separation_rate = self._get_rate_for_age(age, gender, "separation")
                job_change_rate = self._get_rate_for_age(age, gender, "job_change")
                
                # 離職率から転職率を引いた分が「純粋な離職（無職になる）」の確率
                pure_separation_rate = max(0, separation_rate - job_change_rate)
                
                rand = random.random() * 100
                
                if rand < job_change_rate:
                    # 転職（会社から会社へ直接移動）
                    current_company += 1
                    # 転職時に新しい産業を選択（同じ産業の可能性もある）
                    new_industry = self.select_industry(gender)
                    events.append({
                        "age": age,
                        "type": "転職",
                        "industry": new_industry,
                        "previous_industry": current_industry,
                        "company_number": current_company,
                    })
                    current_industry = new_industry
                    
                elif rand < job_change_rate + pure_separation_rate:
                    # 離職（無職になる）
                    is_employed = False
                    unemployment_start_age = age
                    events.append({
                        "age": age,
                        "type": "離職",
                        "industry": current_industry,
                    })
            else:
                # 無職の場合：再就職するかどうかを判定
                reemployment_rate = self._get_rate_for_age(age, gender, "reemployment")
                
                if random.random() * 100 < reemployment_rate:
                    # 再就職
                    current_company += 1
                    is_employed = True
                    unemployment_duration = age - unemployment_start_age
                    new_industry = self.select_industry(gender)
                    events.append({
                        "age": age,
                        "type": "再就職",
                        "industry": new_industry,
                        "company_number": current_company,
                        "unemployment_duration": unemployment_duration,
                    })
                    current_industry = new_industry
                    unemployment_start_age = None
        
        return events
    
    def get_career_summary(self, career_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        キャリア履歴からサマリー情報を生成
        
        Args:
            career_history: キャリアイベントのリスト
            
        Returns:
            サマリー情報
        """
        job_changes = [e for e in career_history if e["type"] == "転職"]
        separations = [e for e in career_history if e["type"] == "離職"]
        reemployments = [e for e in career_history if e["type"] == "再就職"]
        
        total_unemployment_years = sum(
            e.get("unemployment_duration", 0) for e in reemployments
        )
        
        # 最後の状態を確認
        if career_history:
            last_event = career_history[-1]
            is_employed = last_event["type"] != "離職"
        else:
            is_employed = True
        
        # 最後の産業を取得
        last_industry = None
        for event in reversed(career_history):
            if event.get("industry"):
                last_industry = event["industry"]
                break
        
        return {
            "total_job_changes": len(job_changes),
            "total_separations": len(separations),
            "total_reemployments": len(reemployments),
            "total_companies": max([e.get("company_number", 1) for e in career_history], default=1),
            "total_unemployment_years": total_unemployment_years,
            "final_employment_status": "就業中" if is_employed else "無職",
            "final_industry": last_industry,
        }
