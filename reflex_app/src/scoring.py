"""
スコア計算モジュール

人生データからスコアを計算する
- 親ガチャスコア: 親の学歴、世帯年収、出生地（北海道か東京か）
- 人生スコア: 最終学歴、生涯年収、寿命
"""

from typing import Dict, Any

from .constants import (
    LOCATION_SCORES,
    GENDER_SCORES,
    EDUCATION_SCORES,
    UNIVERSITY_DESTINATION_SCORES,
    INDUSTRY_SALARY_SCORES,
    DEATH_CAUSE_SCORES,
    get_lifespan_score,
    get_university_rank,
    get_university_rank_score,
    # 親ガチャスコア用
    PARENT_EDUCATION_SCORES,
    HOUSEHOLD_INCOME_SCORES,
    BIRTHPLACE_SCORES,
    # ランク関連
    get_rank,
    get_rank_label,
    # 生涯年収関連
    LIFETIME_INCOME_BASE,
    get_lifetime_income_score,
    # 企業規模・雇用形態関連
    COMPANY_SIZE_SALARY_MULTIPLIER,
    EMPLOYMENT_TYPE_SALARY_MULTIPLIER,
    # 最終学歴スコアリング（新）
    get_education_score,
)


class LifeScorer:
    """人生スコアを計算するクラス"""
    
    def __init__(self, birthplace_scores: Dict[str, float] = None):
        """
        初期化
        
        Args:
            birthplace_scores: 市区町村別の出生地スコア辞書
                             キー: 市区町村名、値: スコア（0-100）
        """
        self.birthplace_scores = birthplace_scores or {}
    
    def get_birthplace_score(self, city: str, region: str = "") -> tuple:
        """
        市区町村名から出生地スコアを取得
        
        Args:
            city: 市区町村名
            region: 地域識別子（hokkaido/tokyo）
            
        Returns:
            (スコア, 地域名) のタプル
        """
        # 市区町村別スコアがある場合はそれを使用
        if self.birthplace_scores:
            # 完全一致を試行
            if city in self.birthplace_scores:
                region_name = "東京" if region == "tokyo" else "北海道"
                return self.birthplace_scores[city], region_name
            
            # 札幌市の区の場合、「札幌市○○区」形式でも検索
            if city.endswith("区") and "札幌" not in city:
                sapporo_city = f"札幌市{city}"
                if sapporo_city in self.birthplace_scores:
                    return self.birthplace_scores[sapporo_city], "北海道"
        
        # 市区町村別スコアがない場合はデフォルト（旧方式）
        if region == "tokyo":
            return BIRTHPLACE_SCORES["東京"], "東京"
        elif region == "hokkaido":
            return BIRTHPLACE_SCORES["北海道"], "北海道"
        else:
            # region情報がない場合は都市名から推定
            if "東京" in city or (city.endswith("区") and "札幌" not in city):
                return BIRTHPLACE_SCORES["東京"], "東京"
            else:
                return BIRTHPLACE_SCORES["北海道"], "北海道"
    
    def calculate_parent_gacha_score(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        親ガチャスコアを計算する（0〜100点）
        親の学歴、世帯年収、出生地（北海道か東京か）の3要素で算定
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            dict: 総合スコアとランク、各項目のスコア詳細
        """
        scores = {}
        
        # 1. 親の学歴スコア（父母の平均）
        father_edu = life.get("father_education", "高校卒")
        mother_edu = life.get("mother_education", "高校卒")
        
        father_edu_score = PARENT_EDUCATION_SCORES.get(father_edu, PARENT_EDUCATION_SCORES["default"])
        mother_edu_score = PARENT_EDUCATION_SCORES.get(mother_edu, PARENT_EDUCATION_SCORES["default"])
        parent_edu_score = (father_edu_score + mother_edu_score) / 2
        
        scores["parent_education"] = {
            "score": parent_edu_score,
            "max_score": 100,
            "label": "親の学歴",
            "value": f"父:{father_edu} / 母:{mother_edu}",
            "reason": f"父親{father_edu_score}点 + 母親{mother_edu_score}点 の平均",
            "source": "文部科学省「学校基本調査」"
        }
        
        # 2. 世帯年収スコア
        household_income = life.get("household_income", "400〜600万円")
        income_score = HOUSEHOLD_INCOME_SCORES.get(household_income, HOUSEHOLD_INCOME_SCORES["default"])
        
        scores["household_income"] = {
            "score": income_score,
            "max_score": 100,
            "label": "世帯年収",
            "value": household_income,
            "reason": f"世帯年収{household_income}",
            "source": "厚生労働省「国民生活基礎調査」"
        }
        
        # 3. 出生地スコア（市区町村別）
        birth_city = life.get("birth_city", "")
        region = life.get("region", "")  # シミュレーター実行時の地域設定
        
        # 市区町村別スコアを取得
        birthplace_score, region_name = self.get_birthplace_score(birth_city, region)
        
        scores["birthplace"] = {
            "score": birthplace_score,
            "max_score": 100,
            "label": "出生地",
            "value": f"{birth_city}（{region_name}）",
            "reason": f"{birth_city}生まれ（世帯年収・大学進学率・有効求人倍率の複合指標）",
            "source": "総務省「住宅・土地統計調査」、文部科学省「学校基本調査」、厚生労働省「一般職業紹介状況」"
        }
        
        # 総合スコア計算（幸福度研究に基づく2025年改訂版）
        # 
        # 配分根拠（幸福度・子どもの発達に関する研究に基づく）:
        # 
        # 1. 世帯年収: 35%
        #    - 経済的機会への直接的影響は大きい
        #    - ただし研究では「世帯年収と子どもの幸福度の関連は想像より小さい」
        #    - ひとり親世帯の貧困率44.5%など、経済基盤の重要性は無視できない
        # 
        # 2. 親の学歴: 30%
        #    - 子どもの教育機会、文化資本（本、会話、価値観）に影響
        #    - 大卒の子の大学進学率は非大卒の約2倍
        #    - ただし直接的な幸福度への影響は限定的
        # 
        # 3. 出生地: 35%
        #    - 地域による機会格差（進学率、求人倍率、医療アクセス、文化施設）
        #    - 東京の大学進学率は約68%、北海道は約45%
        #    - 社会インフラ、教育機会へのアクセスに大きく影響
        #    - 世帯年収と同等の重みに引き上げ
        #
        # 極端な値がある場合は影響を強める（現実の格差を反映）

        # 極端な値の閾値
        HIGH_THRESHOLD = 85  # これ以上は「極端に高い」
        LOW_THRESHOLD = 15   # これ以下は「極端に低い」

        # デフォルトの重み（2025年改訂）
        edu_weight = 0.30
        income_weight = 0.35
        birthplace_weight = 0.35

        # 学歴と年収の最高値・最低値を確認
        max_score = max(parent_edu_score, income_score)
        min_score = min(parent_edu_score, income_score)

        # 極端に高い値がある場合、高い方の影響を強める（正のフィードバック）
        if max_score >= HIGH_THRESHOLD:
            if parent_edu_score >= income_score:
                # 学歴が高い方 → 学歴の重みを上げる
                edu_weight = 0.45
                income_weight = 0.20
            else:
                # 年収が高い方 → 年収の重みを上げる
                edu_weight = 0.20
                income_weight = 0.45
        # 極端に高い値がなく、極端に低い値がある場合、低い方の影響を強める
        elif min_score <= LOW_THRESHOLD:
            if parent_edu_score <= income_score:
                # 学歴が低い方 → 学歴の重みを上げる（負のフィードバック）
                edu_weight = 0.45
                income_weight = 0.20
            else:
                # 年収が低い方 → 年収の重みを上げる（負のフィードバック）
                edu_weight = 0.20
                income_weight = 0.45

        total_score = (
            parent_edu_score * edu_weight +
            income_score * income_weight +
            birthplace_score * birthplace_weight
        )
        
        # ランク判定
        rank = get_rank(total_score)
        rank_label = get_rank_label(rank)
        
        return {
            "total_score": round(total_score, 1),
            "rank": rank,
            "rank_label": rank_label,
            "breakdown": scores,
            "calculation_method": "親ガチャ（世帯年収35%、出生地35%、親の学歴30%）",
        }
    
    def calculate_lifetime_income(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        生涯年収を計算する（万円）
        定年前に死亡した場合は、按分計算を行う
        
        計算式:
        生涯年収 = 基準生涯年収 × 勤務年数比率 × 産業補正 × 性別補正 × 企業規模補正 × 雇用形態補正
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            dict: 生涯年収（万円）と各補正係数の詳細
        """
        # 最終学歴を判定
        if life.get("graduate_school"):
            education_level = "大学院卒"
            start_work_age = 24
        elif life.get("university"):
            education_level = "大学卒"
            start_work_age = 22
        elif life.get("vocational_school"):
            education_level = "短大・専門卒"
            start_work_age = 20
        elif life.get("high_school"):
            education_level = "高校卒"
            start_work_age = 18
        else:
            education_level = "中学卒"
            start_work_age = 15
        
        # 基準生涯年収を取得
        base_income = LIFETIME_INCOME_BASE.get(education_level, LIFETIME_INCOME_BASE["高校卒"])
        
        # 定年年齢（なければ65歳を仮定）
        retirement_age = life.get("retirement_age") or 65
        death_age = life.get("death_age", 80)
        
        # 定年まで働けた場合の勤務年数
        full_working_years = retirement_age - start_work_age
        
        # 実際の勤務年数（死亡年齢と定年年齢の早い方まで）
        actual_end_age = min(death_age, retirement_age)
        actual_working_years = max(0, actual_end_age - start_work_age)
        
        # 勤務年数比率を計算
        if actual_working_years < full_working_years and full_working_years > 0:
            working_years_ratio = actual_working_years / full_working_years
        else:
            working_years_ratio = 1.0
        
        lifetime_income = base_income * working_years_ratio
        
        # 産業による補正（産業スコアを年収に反映）
        industry = life.get("industry", "")
        industry_score = INDUSTRY_SALARY_SCORES.get("default")
        for ind_name, ind_score in INDUSTRY_SALARY_SCORES.items():
            if ind_name in industry or industry in ind_name:
                industry_score = ind_score
                break
        
        # 産業スコア（0-100）を補正係数（0.7-1.3）に変換
        industry_multiplier = 0.7 + (industry_score / 100) * 0.6
        lifetime_income *= industry_multiplier
        
        # 性別による補正
        gender = life.get("gender", "男性")
        gender_multiplier = 0.76 if gender == "女性" else 1.0
        lifetime_income *= gender_multiplier
        
        # 企業規模による補正（大企業1.00、中企業0.82、小企業0.72）
        company_size = life.get("company_size", "中企業")
        company_size_multiplier = COMPANY_SIZE_SALARY_MULTIPLIER.get(
            company_size,
            COMPANY_SIZE_SALARY_MULTIPLIER["default"]
        )
        lifetime_income *= company_size_multiplier
        
        # 雇用形態による補正（正社員1.00、非正規0.65）
        employment_type = life.get("employment_type", "正社員")
        employment_type_multiplier = EMPLOYMENT_TYPE_SALARY_MULTIPLIER.get(
            employment_type,
            EMPLOYMENT_TYPE_SALARY_MULTIPLIER["default"]
        )
        lifetime_income *= employment_type_multiplier
        
        # 大学ランクによる補正（Sランク大学卒は年収が高い傾向）
        university_rank = life.get("university_rank")
        university_rank_multiplier = 1.0
        if life.get("university") and university_rank:
            university_rank_multipliers = {
                "S": 1.15,  # 難関大卒: +15%
                "A": 1.08,  # 上位大卒: +8%
                "B": 1.00,  # 中堅大卒: 基準
                "C": 0.95,  # 標準大卒: -5%
                "D": 0.92,  # その他大卒: -8%
            }
            university_rank_multiplier = university_rank_multipliers.get(university_rank, 1.0)
            lifetime_income *= university_rank_multiplier
        
        return {
            "total": round(lifetime_income, 0),
            "base_income": base_income,
            "education_level": education_level,
            "working_years_ratio": working_years_ratio,
            "industry_multiplier": industry_multiplier,
            "gender_multiplier": gender_multiplier,
            "company_size": company_size,
            "company_size_multiplier": company_size_multiplier,
            "employment_type": employment_type,
            "employment_type_multiplier": employment_type_multiplier,
            "university_rank": university_rank,
            "university_rank_multiplier": university_rank_multiplier,
        }
    
    def calculate_life_score(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        人生スコアを計算する（0〜100点）
        最終学歴、生涯年収、寿命の3要素で算定
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            dict: 総合スコアとランク、各項目のスコア詳細
        """
        scores = {}
        
        # 1. 最終学歴スコア（パーセンタイルベース）
        if life.get("graduate_school"):
            education_level = "大学院卒"
        elif life.get("university"):
            education_level = "大学卒"
        elif life.get("vocational_school"):
            education_level = "短大・専門卒"
        elif life.get("high_school"):
            education_level = "高校卒"
        else:
            education_level = "中学卒"
        
        # 大学ランクと大学名を取得
        university_rank = life.get("university_rank")
        university_name = life.get("university_name")
        
        # パーセンタイルベースのスコア計算
        education_score = get_education_score(
            education_level=education_level,
            university_rank=university_rank,
            university_name=university_name,
        )
        
        # 表示用の値を作成
        if education_level == "大学院卒" and university_name:
            if isinstance(university_name, dict):
                uni_name = university_name.get("name", "")
            else:
                uni_name = university_name
            if university_rank:
                education_display = f"{education_level}（{uni_name}、{university_rank}ランク）"
            else:
                education_display = f"{education_level}（{uni_name}）"
        elif education_level == "大学卒" and university_name:
            if isinstance(university_name, dict):
                uni_name = university_name.get("name", "")
            else:
                uni_name = university_name
            if university_rank:
                education_display = f"{education_level}（{uni_name}、{university_rank}ランク）"
            else:
                education_display = f"{education_level}（{uni_name}）"
        else:
            education_display = education_level
        
        scores["education"] = {
            "score": education_score,
            "max_score": 100,
            "label": "最終学歴",
            "value": education_display,
            "reason": f"{education_display}（パーセンタイルベースの統計的スコアリング）",
            "source": "文部科学省「学校基本調査」・2020年国勢調査に基づく"
        }
        
        # 2. 生涯年収スコア
        income_result = self.calculate_lifetime_income(life)
        lifetime_income = income_result["total"]
        lifetime_income_score = get_lifetime_income_score(lifetime_income)
        
        # 定年前死亡の場合の注記
        death_age = life.get("death_age", 80)
        retirement_age = life.get("retirement_age") or 65
        if death_age < retirement_age:
            income_note = f"（{death_age}歳で死亡のため按分）"
        else:
            income_note = ""
        
        # 補正係数の説明文を生成
        multiplier_details = []
        if income_result["company_size_multiplier"] != 1.0:
            multiplier_details.append(f"{income_result['company_size']}×{income_result['company_size_multiplier']:.2f}")
        if income_result["employment_type_multiplier"] != 1.0:
            multiplier_details.append(f"{income_result['employment_type']}×{income_result['employment_type_multiplier']:.2f}")
        multiplier_note = f"（{', '.join(multiplier_details)}）" if multiplier_details else ""
        
        scores["lifetime_income"] = {
            "score": lifetime_income_score,
            "max_score": 100,
            "label": "生涯年収",
            "value": f"約{lifetime_income/10000:.1f}億円{income_note}",
            "reason": f"推定生涯年収{lifetime_income:.0f}万円{multiplier_note}",
            "source": "労働政策研究・研修機構「ユースフル労働統計」",
            "raw_value": lifetime_income,
            "income_details": income_result,
        }
        
        # 3. 寿命スコア
        lifespan_score = get_lifespan_score(death_age, life.get("gender", "男性"))
        avg_lifespan = 81.09 if life.get("gender") == "男性" else 87.13
        
        scores["lifespan"] = {
            "score": lifespan_score,
            "max_score": 100,
            "label": "寿命",
            "value": f"{death_age}歳",
            "reason": f"{death_age}歳で死亡（平均寿命: {life.get('gender', '男性')}{avg_lifespan}歳）",
            "source": "厚生労働省「簡易生命表」2024年"
        }
        
        # 総合スコア計算（3要素の加重平均）
        # 
        # 配分根拠（2025年 幸福度研究に基づく改訂）:
        # 
        # 1. 寿命/健康: 40%
        #    - 内閣府「満足度・生活の質に関する調査2025」で健康状態の回帰係数0.104
        #    - WHO等「健康は幸福の基盤」、健康寿命と主観的幸福度の強い相関
        #    - 日本は健康寿命世界2位だが幸福度50位→健康は必要条件だが十分条件ではない
        #    - 早逝は本人の人生の質に直接的・最大の影響
        # 
        # 2. 生涯年収: 35%
        #    - 内閣府調査「家計と資産」の回帰係数0.243（2番目に高い）
        #    - ただし一定水準以上では幸福度への影響が減少（収穫逓減）
        #    - 「経済的安心感」が重要（所得絶対額より主観的ゆとり感）
        # 
        # 3. 学歴: 25%
        #    - 内閣府調査「教育水準」の回帰係数0.038（直接効果は小さい）
        #    - しかし「人生選択の自由度」との強い相関（幸福度変動の82%を説明）
        #    - 学歴は年収・社会的地位・キャリア選択肢に間接的に影響
        #    - 「達成感」「自己実現」の指標としても機能
        #
        total_score = (
            lifespan_score * 0.40 +
            lifetime_income_score * 0.35 +
            education_score * 0.25
        )
        
        # ランク判定
        rank = get_rank(total_score)
        rank_label = get_rank_label(rank)
        
        return {
            "total_score": round(total_score, 1),
            "rank": rank,
            "rank_label": rank_label,
            "breakdown": scores,
            "calculation_method": "人生スコア（寿命40%、生涯年収35%、学歴25%）",
        }
    
    def calculate_all_scores(self, life: Dict[str, Any]) -> Dict[str, Any]:
        """
        親ガチャスコアと人生スコアの両方を計算する
        
        Args:
            life: generate_life()で生成された人生データ
            
        Returns:
            dict: 両方のスコア結果
        """
        parent_gacha = self.calculate_parent_gacha_score(life)
        life_score = self.calculate_life_score(life)
        
        return {
            "parent_gacha": parent_gacha,
            "life_score": life_score,
        }
    
    def get_score_interpretation(self, total_score: float) -> str:
        """
        スコアの解釈を返す
        
        統計的スケール: 平均60点を基準
        
        Args:
            total_score: 総合スコア
            
        Returns:
            解釈文字列
        """
        rank = get_rank(total_score)
        if rank == "SS":
            return "神レベル！（上位2-5%相当）"
        elif rank == "S":
            return "大当たり！（上位10-20%相当）"
        elif rank == "A":
            return "当たり（上位30-40%相当）"
        elif rank == "B":
            return "普通（平均付近）"
        elif rank == "C":
            return "ハズレ（下位25-30%相当）"
        else:
            return "大ハズレ（下位10-20%相当）"
