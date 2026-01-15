"""
出力フォーマッター

シミュレーション結果を文字列でフォーマットする
"""

from typing import Dict, List, Any

from .constants import SCORE_WEIGHTS


class LifeFormatter:
    """人生データのフォーマットを担当するクラス"""
    
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
        # 出生地（市町村名）と両親の職業
        birth_city = life['birth_city']
        father_industry = life.get('father_industry', '不明')
        mother_industry = life.get('mother_industry', '不明')
        
        # 性別の表示
        gender = life.get('gender', '不明')
        
        # 出生地の整形
        if "北海道" not in birth_city:
            birth_location = f"北海道{birth_city}"
        else:
            birth_location = birth_city
        
        # 進学の表示
        education_parts = []
        if life["high_school"]:
            high_school_name = life.get("high_school_name", "地元の高校")
            education_parts.append(f"{high_school_name}に進学")
        
        if life["university"] and life.get("university_destination"):
            university_dest = life["university_destination"]
            university_name = life.get("university_name", f"{university_dest}の大学")
            education_parts.append(f"{university_dest}の{university_name}に進学")
        
        education_str = "\n".join(education_parts) if education_parts else "中学卒業"
        
        # 最初の就職の表示
        first_industry = life.get('first_industry') or life.get('industry', '不明')
        if life["university"]:
            job_str = f"大学卒業後、{first_industry}に就職"
        elif life["high_school"]:
            job_str = f"高校卒業後、{first_industry}に就職"
        else:
            job_str = f"中学卒業後、{first_industry}に就職"
        
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
        
        # 定年退職できたか、その前に死亡したかで表示を分ける
        retirement_str = None
        death_str = None
        
        if retirement_age is not None and death_age >= retirement_age:
            # 定年退職できた場合
            retirement_str = f"{career_prefix}{retirement_age}歳で定年退職"
            death_str = f"{death_age}歳で{death_cause}により死亡"
        else:
            # 定年前に死亡した場合
            death_str = f"{career_prefix}{death_age}歳で{death_cause}により死亡"
        
        # 最終的な出力
        parts = [
            f"{birth_location}に{gender}として、{father_industry}の父親と{mother_industry}の母親の元に生まれる",
            education_str,
            job_str
        ]
        
        if retirement_str:
            parts.append(retirement_str)
        
        parts.append(death_str)
        
        return "\n".join(parts)
    
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
        lines.append("※ 東京で生まれ育ち最大限に充実した人生を100点として算出")
        lines.append("※ 各要素の幾何平均で計算（掛け算方式）")
        lines.append("")
        
        breakdown = score_result["breakdown"]
        
        lines.append("【スコア内訳】")
        lines.append("-" * 60)
        
        for key in ["location", "gender", "education", "university_dest", "industry", "lifespan", "death_cause"]:
            item = breakdown[key]
            score = item["score"]
            
            # 計算に含まれるかどうかを表示
            if item.get("include_in_calc") == False:
                calc_note = "（計算対象外）"
            else:
                calc_note = ""
            
            lines.append(f"  {item['label']}: {score}点 {calc_note}")
            lines.append(f"    → {item['value']}")
            
            if verbose:
                lines.append(f"    理由: {item['reason']}")
                if item['source'] != "-":
                    lines.append(f"    出典: {item['source']}")
            lines.append("")
        
        lines.append("-" * 60)
        
        # スコア計算式を表示
        lines.append("【スコア計算】")
        calc_items = []
        for key in ["location", "gender", "education", "university_dest", "industry", "lifespan", "death_cause"]:
            item = breakdown[key]
            if item.get("include_in_calc") != False:
                calc_items.append((item['label'], item['score']))
        
        # 計算式の表示
        calc_formula = " × ".join([f"{label}({score}%)" for label, score in calc_items])
        lines.append(f"  {calc_formula}")
        
        # 実際の計算
        product = 1.0
        for _, score in calc_items:
            product *= score / 100
        
        lines.append(f"  = {product:.6f}")
        lines.append(f"  √({product:.6f}) × 100 = {(product ** 0.5) * 100:.1f}点")
        lines.append("")
        
        lines.append("-" * 60)
        lines.append(f"総合スコア: {score_result['total_score']:.1f}点")
        lines.append("")
        
        # スコアの解釈（掛け算方式用に調整）
        total = score_result['total_score']
        if total >= 60:
            interpretation = "非常に恵まれた人生（上位5%相当）"
        elif total >= 45:
            interpretation = "平均以上の充実した人生"
        elif total >= 35:
            interpretation = "平均的な人生"
        elif total >= 25:
            interpretation = "やや困難の多い人生"
        elif total >= 15:
            interpretation = "多くの困難に直面した人生"
        else:
            interpretation = "極めて厳しい人生"
        
        lines.append(f"【評価】 {interpretation}")
        
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
        lines.append("すべて北海道庁が公開している公式統計データを使用しています。")
        lines.append("=" * 80)
        
        return "\n".join(lines)
