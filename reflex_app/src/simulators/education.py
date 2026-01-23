"""
教育シミュレーター

高校・大学進学の決定を担当
"""

import random
from typing import Dict, List, Any, Optional


# 女子校リスト（北海道・東京）
GIRLS_ONLY_HIGH_SCHOOLS = {
    # 北海道
    "藤女子高校",
    "遺愛女子高校",
    "北見藤女子高校",
    # 東京
    "女子学院高校",
    "雙葉高校",
    "白百合学園高校",
    "大妻高校",
    "共立女子高校",
    "三輪田学園高校",
    "和洋九段女子高校",
    "慶應義塾女子高校",
    "東洋英和女学院高校",
    "頌栄女子学院高校",
    "山脇学園高校",
    "東京女子学園高校",
    "桜蔭高校",
    "お茶の水女子大学附属高校",
    "京華女子高校",
    "村田女子高校",
    "香蘭女学校高校",
    "鷗友学園女子高校",
    "昭和女子大学附属昭和高校",
    "恵泉女学園高校",
    "玉川聖学院高校",
    "下北沢成徳高校",
    "実践女子学園高校",
    "東京女学館高校",
    "大妻中野高校",
    "光塩女子学院高校",
    "女子美術大学付属高校",
    "立教女学院高校",
    "豊島岡女子学園高校",
    "十文字高校",
    "川村高校",
    "星美学園高校",
    "瀧野川女子学園高校",
    "女子聖学院高校",
    "日本大学豊山女子高校",
    "富士見高校",
    "潤徳女子高校",
    "愛国高校",
    "江戸川女子高校",
    "共立女子第二高校",
    "吉祥女子高校",
    "藤村女子高校",
    "桐朋女子高校",
    "晃華学園高校",
    "大妻多摩高校",
    "白梅学園高校",
    "日本体育大学桜華高校",
    "文華女子高校",
    "蒲田女子高校",
    "トキワ松学園高校",
}

# 男子校リスト（主に東京の私立）
BOYS_ONLY_HIGH_SCHOOLS = {
    "開成高校",
    "芝高校",
    "早稲田高校",
    "海城高校",
    "攻玉社高校",
    "駒場東邦高校",
    "世田谷学園高校",
    "巣鴨高校",
    "本郷高校",
    "城北高校",
    "明治大学付属中野高校",
    "早稲田大学高等学院",
    "武蔵高校",
    "聖学院高校",
    "足立学園高校",
    "桐朋高校",
    "明法高校",
    "学習院高等科",
    "立教池袋高校",
    "成城高校",
    "暁星高校",
    "麻布高校",
    "駒場東邦高校",
}

# 女子大リスト
WOMENS_UNIVERSITIES = {
    # 北海道
    "藤女子大学",
    "天使大学",
    # 東京
    "東京女子大学",
    "日本女子大学",
    "津田塾大学",
    "お茶の水女子大学",
    # 神奈川
    "フェリス女学院大学",
    # 千葉
    "和洋女子大学",
    # 奈良
    "奈良女子大学",
    # 共学だが名前に「女子」を含むため注意
    # 実践女子大学、昭和女子大学なども女子大
    "実践女子大学",
    "昭和女子大学",
    "大妻女子大学",
    "共立女子大学",
    "聖心女子大学",
    "清泉女子大学",
    "白百合女子大学",
    "東京家政大学",
    "跡見学園女子大学",
    "十文字学園女子大学",
    "女子栄養大学",
    "川村学園女子大学",
    "相模女子大学",
    "鎌倉女子大学",
    "京都女子大学",
    "同志社女子大学",
    "武庫川女子大学",
    "神戸女学院大学",
    "甲南女子大学",
    "福岡女学院大学",
    "筑紫女学園大学",
    "活水女子大学",
}


class EducationSimulator:
    """教育に関するシミュレーションを担当するクラス"""
    
    # 偏差値別の大学進学率補正係数
    # 根拠: 文部科学省「学校基本調査」2024年 学科別進学率
    #   - 普通科: 71.3%（偏差値50以上が多い）
    #   - 商業科: 33.0%（偏差値45-55が多い）
    #   - 工業科: 17.9%（偏差値40-50が多い）
    #   - 定時制: 17.8%（偏差値40未満相当）
    # 普通科を基準(1.0)として、他の学科の進学率比率から補正係数を算出
    DEVIATION_VALUE_UNIVERSITY_MODIFIER = {
        # 偏差値70以上: 進学校上位（進学率90%以上想定）
        # 根拠: 進学校では9割以上が大学進学（各種高校別進学実績データより推定）
        70: 1.30,
        # 偏差値65-69: 進学校（進学率85%程度想定）
        65: 1.20,
        # 偏差値60-64: 普通科上位（進学率80%程度想定）
        60: 1.10,
        # 偏差値55-59: 普通科中位（進学率75%程度想定）
        55: 1.05,
        # 偏差値50-54: 普通科平均（基準=71.3%）
        50: 1.00,
        # 偏差値45-49: 普通科下位〜商業科上位
        # 商業科33.0%/普通科71.3% ≈ 0.46 を参考に設定
        45: 0.70,
        # 偏差値40-44: 商業科相当
        # 33.0%/71.3% ≈ 0.46
        40: 0.46,
        # 偏差値35-39: 工業科相当
        # 17.9%/71.3% ≈ 0.25
        35: 0.25,
        # 偏差値35未満: 定時制相当
        # 17.8%/71.3% ≈ 0.25
        0: 0.25,
    }
    
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
    
    def _get_deviation_value_modifier(self, deviation_value: Optional[float]) -> float:
        """
        高校偏差値から大学進学率の補正係数を計算
        
        根拠: 文部科学省「学校基本調査」2024年
        高校の学科別進学率（普通科71.3%、商業科33.0%、工業科17.9%）と
        学科別の平均偏差値帯の対応関係から算出
        
        Args:
            deviation_value: 高校偏差値（または個人の偏差値）
            
        Returns:
            補正係数（0.25〜1.30）
        """
        if deviation_value is None:
            return 1.0
        
        # 偏差値の閾値を降順でチェック
        thresholds = sorted(self.DEVIATION_VALUE_UNIVERSITY_MODIFIER.keys(), reverse=True)
        
        for threshold in thresholds:
            if deviation_value >= threshold:
                return self.DEVIATION_VALUE_UNIVERSITY_MODIFIER[threshold]
        
        # 最低値（偏差値35未満）
        return self.DEVIATION_VALUE_UNIVERSITY_MODIFIER[0]
    
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
    
    # 東京都の市区町村リスト（地理的制約を排除する判定に使用）
    TOKYO_CITIES = {
        "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区",
        "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区", "豊島区",
        "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区",
        "八王子市", "立川市", "武蔵野市", "三鷹市", "青梅市", "府中市", "昭島市",
        "調布市", "町田市", "小金井市", "小平市", "日野市", "東村山市", "国分寺市",
        "国立市", "福生市", "狛江市", "東大和市", "清瀬市", "東久留米市", "武蔵村山市",
        "多摩市", "稲城市", "羽村市", "あきる野市", "西東京市",
    }
    
    def _is_tokyo_city(self, city: str) -> bool:
        """東京都の市区町村かどうかを判定"""
        return city in self.TOKYO_CITIES
    
    def select_high_school_name(self, city: str, deviation_value: float = None, gender: str = None) -> tuple:
        """
        出生地に近接した高校名を偏差値・入学者数に基づいて選択
        
        東京都の場合は地理的制約を排除し、全高校から選択可能。
        入学者数に基づいた重み付け選択を実装。
        
        Args:
            city: 出身市町村
            deviation_value: 個人の偏差値（指定がなければランダム選択）
            gender: 性別（"男性" or "女性"）- 男女別学校のフィルタリングに使用
            
        Returns:
            (高校名, 高校偏差値) のタプル
        """
        # 候補となる高校を集める
        candidate_schools = []
        
        # 東京都の場合は全高校から選択（地理的制約なし）
        if self._is_tokyo_city(city):
            for schools in self.high_schools_by_city.values():
                candidate_schools.extend(schools)
        else:
            # 北海道など他の地域の場合は従来のロジック
            # まず出生地の市町村で高校を探す
            if city in self.high_schools_by_city:
                candidate_schools.extend(self.high_schools_by_city[city])
            
            # 札幌市の場合は全区から選択
            if "札幌市" in city or "札幌" in city:
                for key, schools in self.high_schools_by_city.items():
                    if "札幌" in key:
                        for school in schools:
                            if school not in candidate_schools:
                                candidate_schools.append(school)
            
            # 市町村名の部分一致で探す
            if not candidate_schools:
                city_base = city.replace("市", "").replace("町", "").replace("村", "")
                for key, schools in self.high_schools_by_city.items():
                    if city_base in key or key.replace("市", "").replace("町", "").replace("村", "") in city:
                        candidate_schools.extend(schools)
            
            # 候補がない場合は全体から選択
            if not candidate_schools:
                for schools in self.high_schools_by_city.values():
                    candidate_schools.extend(schools)
        
        # 性別に基づいて異性の学校をフィルタリング
        # gender は "male" / "female" または "男性" / "女性" の両方に対応
        if gender and candidate_schools:
            is_male = gender in ("male", "男性")
            is_female = gender in ("female", "女性")
            
            filtered_schools = []
            for school in candidate_schools:
                # 高校名を取得（辞書形式の場合は"name"キー、文字列の場合はそのまま）
                school_name = school.get("name", school) if isinstance(school, dict) else school
                
                if is_male:
                    # 男性は女子校に入学できない
                    if school_name not in GIRLS_ONLY_HIGH_SCHOOLS:
                        filtered_schools.append(school)
                elif is_female:
                    # 女性は男子校に入学できない
                    if school_name not in BOYS_ONLY_HIGH_SCHOOLS:
                        filtered_schools.append(school)
                else:
                    filtered_schools.append(school)
            
            # フィルタ後に候補が残っていれば使用
            if filtered_schools:
                candidate_schools = filtered_schools
        
        if not candidate_schools:
            # 見つからない場合は汎用名を生成
            city_short = city.replace("市", "").replace("町", "").replace("村", "")
            return (f"{city_short}高校", 50.0)
        
        # 偏差値が指定されている場合、マッチする高校を優先選択
        if deviation_value is not None:
            # 新形式（辞書）かどうかを確認
            if isinstance(candidate_schools[0], dict):
                # 偏差値±7の範囲内の高校を抽出
                min_dev = deviation_value - 7
                max_dev = deviation_value + 5
                matching_schools = [
                    s for s in candidate_schools 
                    if min_dev <= s.get("deviation_value", 50) <= max_dev
                ]
                
                if matching_schools:
                    # マッチする高校から重み付き選択
                    # 重み = 入学者数 × 偏差値近接ボーナス
                    weights = []
                    for s in matching_schools:
                        enrollment = s.get("enrollment", 280)
                        diff = abs(s.get("deviation_value", 50) - deviation_value)
                        # 偏差値が近いほどボーナス（0-5の差で1.5倍、5-10の差で1.0倍）
                        proximity_bonus = 1.5 if diff <= 5 else 1.0
                        weight = enrollment * proximity_bonus
                        weights.append(weight)
                    
                    total_weight = sum(weights)
                    rand = random.uniform(0, total_weight)
                    cumulative = 0
                    for i, s in enumerate(matching_schools):
                        cumulative += weights[i]
                        if rand <= cumulative:
                            return (s["name"], s.get("deviation_value", 50.0))
                    selected = matching_schools[-1]
                    return (selected["name"], selected.get("deviation_value", 50.0))
                else:
                    # マッチする高校がなければ最も近い偏差値の高校から入学者数で重み付け選択
                    sorted_schools = sorted(
                        candidate_schools,
                        key=lambda s: abs(s.get("deviation_value", 50) - deviation_value)
                    )
                    # 上位10校から入学者数で重み付け選択
                    top_schools = sorted_schools[:10]
                    weights = [s.get("enrollment", 280) for s in top_schools]
                    total_weight = sum(weights)
                    rand = random.uniform(0, total_weight)
                    cumulative = 0
                    for i, s in enumerate(top_schools):
                        cumulative += weights[i]
                        if rand <= cumulative:
                            return (s["name"], s.get("deviation_value", 50.0))
                    selected = top_schools[-1]
                    return (selected["name"], selected.get("deviation_value", 50.0))
            else:
                # 旧形式（文字列リスト）の場合
                return (random.choice(candidate_schools), 50.0)
        else:
            # 偏差値指定なしの場合は入学者数に基づいた重み付け選択
            if isinstance(candidate_schools[0], dict):
                weights = [s.get("enrollment", 280) for s in candidate_schools]
                total_weight = sum(weights)
                rand = random.uniform(0, total_weight)
                cumulative = 0
                for i, s in enumerate(candidate_schools):
                    cumulative += weights[i]
                    if rand <= cumulative:
                        return (s["name"], s.get("deviation_value", 50.0))
                selected = candidate_schools[-1]
                return (selected["name"], selected.get("deviation_value", 50.0))
            else:
                return (random.choice(candidate_schools), 50.0)
    
    def decide_university(
        self,
        city: str,
        went_to_high_school: bool,
        father_education: Optional[str] = None,
        mother_education: Optional[str] = None,
        household_income: Optional[str] = None,
        high_school_deviation_value: Optional[float] = None
    ) -> bool:
        """
        大学進学を決定（高校に進学した場合のみ、親学歴・世帯年収・偏差値を考慮）
        
        進学率の計算式:
          進学率 = 市町村別基本進学率 × 家庭環境補正 × 偏差値補正
          
        家庭環境補正 = (親学歴補正 + 世帯年収補正) / 2
          - 親学歴・世帯年収は相関が高いため平均を取る
          
        偏差値補正の根拠:
          文部科学省「学校基本調査」2024年 学科別進学率
          - 普通科: 71.3% → 偏差値50以上（基準=1.0）
          - 商業科: 33.0% → 偏差値40-50（補正≈0.46）
          - 工業科: 17.9% → 偏差値35-45（補正≈0.25）
        
        Args:
            city: 出身市町村
            went_to_high_school: 高校に進学したかどうか
            father_education: 父親の最終学歴
            mother_education: 母親の最終学歴
            household_income: 世帯年収
            high_school_deviation_value: 高校偏差値（または個人の学力偏差値）
            
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
        
        # 偏差値による補正
        deviation_modifier = self._get_deviation_value_modifier(high_school_deviation_value)
        
        # 補正後の進学率（100%を超えないように、0%を下回らないように）
        # 親学歴と世帯年収の補正を組み合わせる（相関があるため平均を取る）
        # 偏差値補正は独立した要因として乗算
        family_modifier = (education_modifier + income_modifier) / 2
        adjusted_rate = min(100.0, max(0.0, base_rate * family_modifier * deviation_modifier))
        
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
    
    def select_university_name(self, prefecture: str, deviation_value: float = None, gender: str = None) -> tuple:
        """
        進学先都道府県から大学名を偏差値に基づいて選択
        
        偏差値ベースのマッチングロジック:
        1. 各大学の偏差値データを参照
        2. 個人の偏差値に近い大学ほど高い重みを付与
        3. 入学者数も重みに考慮（大規模大学ほど選ばれやすい）
        4. 重み = 入学者数 × 偏差値近接ボーナス
        
        偏差値近接ボーナス:
        - 差5以内: 2.0倍
        - 差5-10: 1.5倍
        - 差10-15: 1.0倍
        - 差15以上: 0.5倍（かなり稀なケース）
        
        Args:
            prefecture: 都道府県名
            deviation_value: 個人の偏差値（高校卒業時）
            gender: 性別（"男性" or "女性"）- 女子大のフィルタリングに使用
            
        Returns:
            (大学名, 大学ランク) のタプル
        """
        from ..constants import UNIVERSITY_RANKS
        
        if prefecture in self.universities_by_prefecture:
            universities = self.universities_by_prefecture[prefecture]
        else:
            return (f"{prefecture}の大学", "D")
        
        if not universities:
            return (f"{prefecture}の大学", "D")
        
        # 性別に基づいて女子大をフィルタリング（男性は女子大に入学できない）
        # gender は "male" / "female" または "男性" / "女性" の両方に対応
        is_male = gender in ("male", "男性")
        if is_male:
            filtered_universities = [
                u for u in universities
                if u.get("name", u) not in WOMENS_UNIVERSITIES
            ]
            # フィルタ後に候補が残っていれば使用
            if filtered_universities:
                universities = filtered_universities
        
        # 偏差値に基づく選択
        if deviation_value is not None:
            # 候補大学とその重みを計算
            weighted_candidates = []
            for univ in universities:
                univ_dev = univ.get("deviation_value", 50)
                
                # 偏差値の差を計算
                diff = abs(univ_dev - deviation_value)
                
                # 偏差値近接ボーナスを計算
                if diff <= 5:
                    proximity_bonus = 2.0  # 偏差値差5以内は2倍
                elif diff <= 10:
                    proximity_bonus = 1.5  # 偏差値差5-10は1.5倍
                elif diff <= 15:
                    proximity_bonus = 1.0  # 偏差値差10-15は1.0倍
                else:
                    proximity_bonus = 0.3  # 偏差値差15以上は0.3倍（稀なケース）
                
                # 上位校への進学は難しい（偏差値が自分より高い場合は重みを下げる）
                if univ_dev > deviation_value + 5:
                    # 自分より5以上高い大学は確率を下げる
                    overshoot = univ_dev - deviation_value - 5
                    proximity_bonus *= max(0.1, 1.0 - overshoot * 0.1)
                
                # 重み = 入学者数 × 偏差値近接ボーナス
                weight = univ["enrollment"] * proximity_bonus
                
                if weight > 0:
                    weighted_candidates.append((univ, weight))
            
            # 重み付き選択
            if weighted_candidates:
                total_weight = sum(w for _, w in weighted_candidates)
                if total_weight > 0:
                    rand = random.uniform(0, total_weight)
                    cumulative = 0
                    for univ, weight in weighted_candidates:
                        cumulative += weight
                        if rand <= cumulative:
                            return (univ["name"], UNIVERSITY_RANKS.get(univ["name"], "D"))
                    selected = weighted_candidates[-1][0]
                    return (selected["name"], UNIVERSITY_RANKS.get(selected["name"], "D"))
        
        # 偏差値指定なし or マッチなしの場合は入学者数に基づく選択
        total_enrollment = sum(u["enrollment"] for u in universities)
        if total_enrollment == 0:
            selected = random.choice(universities)
            return (selected["name"], UNIVERSITY_RANKS.get(selected["name"], "D"))
        
        rand = random.uniform(0, total_enrollment)
        cumulative = 0
        for univ in universities:
            cumulative += univ["enrollment"]
            if rand <= cumulative:
                return (univ["name"], UNIVERSITY_RANKS.get(univ["name"], "D"))
        
        selected = universities[-1]
        return (selected["name"], UNIVERSITY_RANKS.get(selected["name"], "D"))
    
    def _get_expected_university_rank(self, deviation_value: float) -> str:
        """
        偏差値から期待される大学ランクを取得
        
        Args:
            deviation_value: 偏差値
            
        Returns:
            大学ランク（"S", "A", "B", "C", "D"）
        """
        # 確率的に決定（偏差値に応じてランクが上下する可能性）
        if deviation_value >= 70:
            # 偏差値70+: Sランク70%, Aランク30%
            return "S" if random.random() < 0.7 else "A"
        elif deviation_value >= 60:
            # 偏差値60-69: Sランク10%, Aランク60%, Bランク30%
            rand = random.random()
            if rand < 0.10:
                return "S"
            elif rand < 0.70:
                return "A"
            else:
                return "B"
        elif deviation_value >= 52:
            # 偏差値52-59: Aランク10%, Bランク60%, Cランク30%
            rand = random.random()
            if rand < 0.10:
                return "A"
            elif rand < 0.70:
                return "B"
            else:
                return "C"
        elif deviation_value >= 45:
            # 偏差値45-51: Bランク10%, Cランク60%, Dランク30%
            rand = random.random()
            if rand < 0.10:
                return "B"
            elif rand < 0.70:
                return "C"
            else:
                return "D"
        else:
            # 偏差値45未満: Cランク10%, Dランク90%
            return "C" if random.random() < 0.1 else "D"
    
    # 大学ランク別の大学院進学率（%）
    # 出典: 文部科学省「学校基本調査」、各大学の進学実績データ
    GRADUATE_SCHOOL_RATE_BY_UNIVERSITY_RANK = {
        "S": 35.0,  # 難関大（東大・京大・旧帝大・早慶）: 35%程度
        "A": 20.0,  # 上位大（MARCH・関関同立等）: 20%程度
        "B": 12.0,  # 中堅大: 12%程度
        "C": 6.0,   # 標準大: 6%程度
        "D": 3.0,   # その他: 3%程度
        "default": 10.0,
    }

    # 性別による大学院進学率の補正係数
    # 出典: 文部科学省「学校基本調査」
    # 大学院進学率: 男性約14%、女性約6%（全国平均）
    GRADUATE_SCHOOL_GENDER_MODIFIER = {
        "男性": 1.4,   # 男性は平均より高い
        "女性": 0.6,   # 女性は平均より低い
    }

    def decide_graduate_school(
        self,
        went_to_university: bool,
        university_rank: Optional[str] = None,
        gender: str = "男性",
        father_education: Optional[str] = None,
        mother_education: Optional[str] = None,
        household_income: Optional[str] = None,
    ) -> bool:
        """
        大学院進学を決定（大学に進学した場合のみ）

        大学院進学率は:
        - 大学ランクに依存（難関大ほど高い）
        - 性別に依存（男性の方が高い）
        - 親の学歴・世帯年収にも影響される

        出典: 文部科学省「学校基本調査」

        Args:
            went_to_university: 大学に進学したかどうか
            university_rank: 大学ランク（S/A/B/C/D）
            gender: 性別
            father_education: 父親の最終学歴
            mother_education: 母親の最終学歴
            household_income: 世帯年収

        Returns:
            大学院に進学するかどうか
        """
        if not went_to_university:
            return False

        # 大学ランクに基づく基本進学率
        base_rate = self.GRADUATE_SCHOOL_RATE_BY_UNIVERSITY_RANK.get(
            university_rank,
            self.GRADUATE_SCHOOL_RATE_BY_UNIVERSITY_RANK["default"]
        )

        # 性別による補正
        gender_modifier = self.GRADUATE_SCHOOL_GENDER_MODIFIER.get(gender, 1.0)
        adjusted_rate = base_rate * gender_modifier

        # 親学歴による補正（大学進学と同様）
        education_modifier = self._get_parent_education_modifier(
            father_education, mother_education, "university_modifier"
        )

        # 世帯年収による補正
        income_modifier = self._get_income_modifier(
            household_income, "university_modifier"
        )

        # 補正を適用（相関があるため平均を取る）
        combined_modifier = (education_modifier + income_modifier) / 2
        final_rate = min(100.0, adjusted_rate * combined_modifier)

        return random.random() * 100 < final_rate

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

