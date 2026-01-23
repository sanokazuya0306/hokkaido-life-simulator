"""
出力フォーマッター

シミュレーション結果を文字列でフォーマットする
"""

from typing import Dict, List, Any

from .constants import SCORE_WEIGHTS


class LifeFormatter:
    """人生データのフォーマットを担当するクラス"""
    
    def __init__(self, region: str = "hokkaido"):
        """
        初期化
        
        Args:
            region: 地域識別子 ("hokkaido" または "tokyo")
        """
        self.region = region
        self.region_names = {
            "hokkaido": "北海道",
            "tokyo": "東京都",
        }
    
    def format_life(
        self,
        life: Dict[str, Any],
        score_result: Dict[str, Any] = None,
        sns_reactions: List[str] = None,
        show_score: bool = True,
        verbose_score: bool = True,
        show_sns: bool = True,
    ) -> str:
        """
        人生の軌跡を文字列でフォーマット
        
        Args:
            life: 人生データ
            score_result: スコア計算結果（Noneの場合はスコア非表示）
            sns_reactions: SNS反応リスト（Noneの場合はSNS非表示）
            show_score: スコアを表示するかどうか
            verbose_score: スコアの詳細な根拠を表示するかどうか
            show_sns: SNS反応を表示するかどうか
            
        Returns:
            フォーマットされた文字列
        """
        result = self._format_life_story(life)
        
        # スコアを表示する場合
        if show_score and score_result:
            result += "\n\n" + self.format_score_breakdown(score_result, verbose=verbose_score)
        
        # SNS反応を表示する場合
        if show_sns and sns_reactions:
            result += "\n" + self.format_sns_reactions(sns_reactions)
        
        return result
    
    def _format_life_story(self, life: Dict[str, Any]) -> str:
        """人生のストーリー部分をフォーマット"""
        # 出生地（市町村名）と両親の学歴
        birth_city = life['birth_city']
        father_education = life.get('father_education', '')
        mother_education = life.get('mother_education', '')
        household_income = life.get('household_income', '')
        
        # 性別の表示
        gender = life.get('gender', '不明')
        
        # 出生地の整形（地域に応じて）- 都道府県名は含めず市町村名のみ
        # birth_cityから市町村名のみを抽出
        birth_city_only = birth_city
        for prefix in ["北海道", "東京都"]:
            if birth_city.startswith(prefix):
                birth_city_only = birth_city[len(prefix):]
                break
        
        # 進学の表示
        education_parts = []
        if life["high_school"]:
            high_school_name = life.get("high_school_name", "地元の高校")
            # 辞書型の場合は name キーを取り出す
            if isinstance(high_school_name, dict):
                high_school_name = high_school_name.get("name", "地元の高校")
            education_parts.append(f"{high_school_name}に進学")
        
        if life["university"] and life.get("university_destination"):
            university_dest = life["university_destination"]
            university_name = life.get("university_name", f"{university_dest}の大学")
            # 辞書型の場合は name キーを取り出す
            if isinstance(university_name, dict):
                university_name = university_name.get("name", f"{university_dest}の大学")
            education_parts.append(f"{university_dest}の{university_name}に進学")
            # 大学院進学
            if life.get("graduate_school"):
                education_parts.append("大学院に進学")
        elif life.get("vocational_school"):
            # 専門学校・短大に進学した場合
            education_parts.append("専門学校に進学")
        
        education_str = "\n".join(education_parts) if education_parts else "中学卒業"
        
        # 最初の就職の表示（企業規模・雇用形態を追加）
        first_industry = life.get('first_industry') or life.get('industry', '不明')
        employment_type = life.get('employment_type', '正社員')
        company_size = life.get('company_size', '中企業')
        
        # 雇用形態の表示を調整（正社員→正社員、非正規→非正規社員）
        employment_display = "正社員" if employment_type == "正社員" else "非正規社員"
        
        if life.get("graduate_school"):
            job_str = f"大学院修了後、{first_industry}の{company_size}に{employment_display}として就職"
        elif life["university"]:
            job_str = f"大学卒業後、{first_industry}の{company_size}に{employment_display}として就職"
        elif life.get("vocational_school"):
            job_str = f"専門学校卒業後、{first_industry}の{company_size}に{employment_display}として就職"
        elif life["high_school"]:
            job_str = f"高校卒業後、{first_industry}の{company_size}に{employment_display}として就職"
        else:
            job_str = f"中学卒業後、{first_industry}の{company_size}に{employment_display}として就職"
        
        # キャリアサマリーから転職回数と無職年数を取得
        career_summary = life.get("career_summary", {})
        job_changes = career_summary.get("total_job_changes", 0)
        unemployment_years = career_summary.get("total_unemployment_years", 0)
        
        # 転職・無職のプレフィックスを作成
        career_prefix_parts = []
        if job_changes > 0:
            career_prefix_parts.append(f"{job_changes}回の転職")
        if unemployment_years > 0:
            career_prefix_parts.append(f"{unemployment_years}年の無職")
        
        career_prefix = "、".join(career_prefix_parts)
        if career_prefix:
            career_prefix += "を経て、"
        
        # 定年の表示
        retirement_age = life.get('retirement_age')
        death_age = life['death_age']
        
        # 死因の表示
        death_cause = life['death_cause']
        if "悪性新生物" in death_cause or "腫瘍" in death_cause:
            death_cause = "ガン"
        
        # 生涯年収を計算（LifeScorerを使用）
        from .scoring import LifeScorer
        scorer = LifeScorer()
        income_result = scorer.calculate_lifetime_income(life)
        lifetime_income = income_result["total"]  # 万円
        lifetime_income_oku = lifetime_income / 10000  # 億円に変換
        
        # 定年退職できたか、その前に死亡したかで表示を分ける
        retirement_str = None
        death_str = None
        
        if retirement_age is not None and death_age >= retirement_age:
            # 定年退職できた場合（生涯年収も表示）
            retirement_str = f"{career_prefix}{retirement_age}歳で定年退職。生涯年収約{lifetime_income_oku:.1f}億円"
            death_str = f"{death_age}歳で{death_cause}により死亡"
        else:
            # 定年前に死亡した場合（生涯年収も表示）
            death_str = f"{career_prefix}{death_age}歳で{death_cause}により死亡。生涯年収約{lifetime_income_oku:.1f}億円"
        
        # 世帯年収の表示（万円単位に変換）
        if household_income:
            # 「400〜600万円」→「400〜600万」のように整形
            income_display = household_income.replace("万円", "万")
            income_str = f"世帯年収{income_display}"
        else:
            income_str = "世帯年収不明"
        
        # 両親の学歴表示（簡略化）
        father_edu_short = self._shorten_education(father_education) if father_education else "不明"
        mother_edu_short = self._shorten_education(mother_education) if mother_education else "不明"
        
        # 最終的な出力（新形式）
        # 1行目: ◯◯市に◯性として生まれる
        line1 = f"{birth_city_only}に{gender}として生まれる"
        # 2行目: 世帯年収◯◯万、父親は◯卒、母親は◯卒
        line2 = f"{income_str}、父親は{father_edu_short}卒、母親は{mother_edu_short}卒"
        
        parts = [
            line1,
            line2,
            education_str,
            job_str
        ]
        
        if retirement_str:
            parts.append(retirement_str)
        
        parts.append(death_str)
        
        return "\n".join(parts)
    
    def _shorten_education(self, education: str) -> str:
        """学歴を短縮形に変換"""
        # 「大学院」→「院」、「大学卒」→「大」、「高校卒」→「高」、「中学卒」→「中」、「短大・専門」→「短大・専門」
        if "大学院" in education or "院卒" in education:
            return "院"
        elif "大学" in education or "大卒" in education:
            return "大"
        elif "短大" in education or "専門" in education:
            return "短大・専門"
        elif "高校" in education or "高卒" in education:
            return "高"
        elif "中学" in education or "中卒" in education:
            return "中"
        else:
            return education
    
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
        lines = []
        lines.append("=" * 60)
        lines.append(f"【人生スコア】 {score_result['total_score']:.1f} / 100点")
        lines.append("=" * 60)
        lines.append(f"ランク: {score_result.get('rank', '-')} ({score_result.get('rank_label', '-')})")
        lines.append(f"計算方法: {score_result.get('calculation_method', '-')}")
        lines.append("")
        
        breakdown = score_result["breakdown"]
        
        lines.append("【スコア内訳】")
        lines.append("-" * 60)
        
        # 新しいキー構造に対応（education、lifetime_income、lifespan）
        for key in ["education", "lifetime_income", "lifespan"]:
            if key not in breakdown:
                continue
            item = breakdown[key]
            score = item["score"]
            
            lines.append(f"  {item['label']}: {score}点")
            lines.append(f"    → {item['value']}")
            
            if verbose:
                lines.append(f"    理由: {item['reason']}")
                if item.get('source') and item['source'] != "-":
                    lines.append(f"    出典: {item['source']}")
            lines.append("")
        
        lines.append("-" * 60)
        lines.append(f"総合スコア: {score_result['total_score']:.1f}点")
        lines.append("")
        
        # スコアの解釈
        total = score_result['total_score']
        if total >= 90:
            interpretation = "神レベル！（上位1%相当）"
        elif total >= 80:
            interpretation = "大当たり！（上位5%相当）"
        elif total >= 70:
            interpretation = "当たり（上位20%相当）"
        elif total >= 50:
            interpretation = "普通（平均付近）"
        elif total >= 30:
            interpretation = "ハズレ（下位20%相当）"
        else:
            interpretation = "大ハズレ（下位5%相当）"
        
        lines.append(f"【評価】 {interpretation}")
        
        return "\n".join(lines)
        return "\n".join(lines)
    
    def format_sns_reactions(self, reactions: List[str]) -> str:
        """
        SNS反応をフォーマット
        
        Args:
            reactions: SNS反応のリスト
            
        Returns:
            フォーマットされた文字列
        """
        lines = []
        lines.append("")
        lines.append("=" * 60)
        lines.append("【SNSでの予想される反応】")
        lines.append("=" * 60)
        
        for i, reaction in enumerate(reactions, 1):
            lines.append(f"💬 {reaction}")
            if i < len(reactions):
                lines.append("")
        
        return "\n".join(lines)
    
    def format_dataset_info(self, datasets: List[Dict[str, str]]) -> str:
        """
        データセット情報をフォーマット
        
        Args:
            datasets: データセット情報のリスト
            
        Returns:
            フォーマットされた文字列
        """
        lines = []
        lines.append("=" * 80)
        lines.append("【参照データセット】")
        lines.append("=" * 80)
        
        for dataset in datasets:
            lines.append(f"\n{dataset['name']} ({dataset['count']})")
            lines.append(f"  正式名称: {dataset['official_name']}")
            lines.append(f"  提供元: {dataset['source']}")
            lines.append(f"  データ年: {dataset['year']}")
        
        lines.append("\n" + "=" * 80)
        region_name = self.region_names.get(self.region, "各自治体")
        lines.append(f"すべて{region_name}が公開している公式統計データを使用しています。")
        lines.append("=" * 80)
        
        return "\n".join(lines)
