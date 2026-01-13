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
            university_name = life.get("university_name", f"{life['university_destination']}の大学")
            education_parts.append(f"{university_name}に進学")
        
        education_str = "\n".join(education_parts) if education_parts else "中学卒業"
        
        # キャリア履歴の表示
        career_parts = []
        career_history = life.get("career_history", [])
        
        if career_history:
            for event in career_history:
                event_type = event.get("type")
                age = event.get("age")
                industry = event.get("industry", "")
                
                if event_type == "就職":
                    # 最初の就職
                    if life["university"]:
                        career_parts.append(f"大学卒業後、{industry}に就職")
                    elif life["high_school"]:
                        career_parts.append(f"高校卒業後、{industry}に就職")
                    else:
                        career_parts.append(f"中学卒業後、{industry}に就職")
                
                elif event_type == "転職":
                    prev_industry = event.get("previous_industry", "")
                    if prev_industry and prev_industry != industry:
                        career_parts.append(f"{age}歳で{industry}に転職")
                    else:
                        career_parts.append(f"{age}歳で転職（{event.get('company_number', '')}社目）")
                
                elif event_type == "離職":
                    career_parts.append(f"{age}歳で離職")
                
                elif event_type == "再就職":
                    unemployment_duration = event.get("unemployment_duration", 0)
                    if unemployment_duration > 0:
                        career_parts.append(f"{age}歳で{industry}に再就職（無職期間{unemployment_duration}年）")
                    else:
                        career_parts.append(f"{age}歳で{industry}に再就職")
        else:
            # キャリア履歴がない場合（後方互換性）
            industry = life.get('industry', '不明')
            if life["university"]:
                career_parts.append(f"大学卒業後、{industry}に就職")
            elif life["high_school"]:
                career_parts.append(f"高校卒業後、{industry}に就職")
            else:
                career_parts.append(f"中学卒業後、{industry}に就職")
        
        career_str = "\n".join(career_parts)
        
        # 定年の表示
        retirement_age = life.get('retirement_age')
        death_age = life['death_age']
        
        retirement_str = None
        # キャリアサマリーから最終状態を確認
        career_summary = life.get("career_summary", {})
        final_status = career_summary.get("final_employment_status", "就業中")
        
        if retirement_age is not None and death_age >= retirement_age:
            if final_status == "就業中":
                retirement_str = f"{retirement_age}歳で定年退職"
            else:
                # 無職のまま定年を迎えた場合は表示しない
                pass
        elif retirement_age is None and death_age >= 60:
            if final_status == "就業中":
                retirement_str = "定年なし（生涯現役）"
        
        # 死因の表示
        death_cause = life['death_cause']
        if "悪性新生物" in death_cause or "腫瘍" in death_cause:
            death_cause = "ガン"
        
        death_str = f"{life['death_age']}歳で{death_cause}により死亡"
        
        # 最終的な出力
        parts = [
            f"{birth_location}に{gender}として、{father_industry}の父親と{mother_industry}の母親の元に生まれる",
            education_str,
            career_str
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
        lines.append("")
        
        breakdown = score_result["breakdown"]
        weights = score_result["weights"]
        
        lines.append("【スコア内訳】")
        lines.append("-" * 60)
        
        for key in ["location", "gender", "education", "university_dest", "industry", "lifespan", "death_cause"]:
            item = breakdown[key]
            weight = weights[key]
            weighted_score = item["score"] * weight
            
            lines.append(f"  {item['label']}: {item['score']}点 × {weight*100:.0f}% = {weighted_score:.1f}点")
            lines.append(f"    → {item['value']}")
            
            if verbose:
                lines.append(f"    理由: {item['reason']}")
                if item['source'] != "-":
                    lines.append(f"    出典: {item['source']}")
            lines.append("")
        
        lines.append("-" * 60)
        lines.append(f"合計: {score_result['total_score']:.1f}点")
        lines.append("")
        
        # スコアの解釈
        total = score_result['total_score']
        if total >= 80:
            interpretation = "非常に恵まれた人生（上位10%相当）"
        elif total >= 65:
            interpretation = "平均以上の充実した人生"
        elif total >= 50:
            interpretation = "平均的な人生"
        elif total >= 35:
            interpretation = "やや困難の多い人生"
        else:
            interpretation = "多くの困難に直面した人生"
        
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
