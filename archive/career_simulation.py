#!/usr/bin/env python3
"""
転職・離職・再就職シミュレーター（改良版）

厚生労働省「令和6年雇用動向調査」のデータに基づき、
大卒者（22歳就業開始）が定年までの間に経験するキャリアイベントをシミュレーション

シミュレーションするイベント:
- 転職: 在職中に別の会社へ移る
- 離職: 会社を辞めて無職になる
- 再就職: 無職状態から就職する
"""

import csv
import random
from pathlib import Path


class CareerSimulator:
    def __init__(self, data_dir=None):
        if data_dir is None:
            script_dir = Path(__file__).parent
            self.data_dir = script_dir / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.job_mobility_data = []
        self.load_data()
    
    def load_data(self):
        """転職・離職・再就職率データを読み込む"""
        mobility_file = self.data_dir / "job_mobility_by_age_gender.csv"
        if mobility_file.exists():
            with open(mobility_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.job_mobility_data.append({
                        "age_min": int(row["年齢下限"]),
                        "age_max": int(row["年齢上限"]),
                        "male_job_change_rate": float(row["男性_転職入職率"]),
                        "female_job_change_rate": float(row["女性_転職入職率"]),
                        "male_separation_rate": float(row["男性_離職率"]),
                        "female_separation_rate": float(row["女性_離職率"]),
                        "male_reemployment_rate": float(row.get("男性_再就職率", 60)),
                        "female_reemployment_rate": float(row.get("女性_再就職率", 50)),
                    })
        else:
            raise FileNotFoundError(f"データファイルが見つかりません: {mobility_file}")
    
    def get_rate_for_age(self, age, gender, rate_type):
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
                return data[rate_key]
        
        # 範囲外の場合は最後のデータを使用
        if self.job_mobility_data:
            return self.job_mobility_data[-1][rate_key]
        return 5.0  # デフォルト
    
    def simulate_career(self, gender, start_age=22, retirement_age=60, seed=None):
        """
        1人のキャリアをシミュレーション（離職・再就職を含む）
        
        Args:
            gender: "男性" または "女性"
            start_age: 就業開始年齢（大卒なら22歳）
            retirement_age: 定年年齢
            seed: 乱数シード（再現性のため）
        
        Returns:
            dict: シミュレーション結果
        """
        if seed is not None:
            random.seed(seed)
        
        events = []
        current_company = 1  # 何社目か
        is_employed = True   # 現在就業中かどうか
        unemployment_start_age = None  # 無職開始年齢
        
        for age in range(start_age, retirement_age):
            if is_employed:
                # 就業中の場合
                
                # まず離職するかどうかを判定（転職ではなく単純な退職）
                separation_rate = self.get_rate_for_age(age, gender, "separation")
                job_change_rate = self.get_rate_for_age(age, gender, "job_change")
                
                # 離職率から転職率を引いた分が「純粋な離職（無職になる）」の確率
                # ただし、負にならないようにする
                pure_separation_rate = max(0, separation_rate - job_change_rate)
                
                rand = random.random() * 100
                
                if rand < job_change_rate:
                    # 転職（会社から会社へ直接移動）
                    current_company += 1
                    events.append({
                        "age": age,
                        "type": "転職",
                        "company_number": current_company,
                        "rate": job_change_rate,
                        "description": f"{age}歳で転職（{current_company}社目へ）"
                    })
                elif rand < job_change_rate + pure_separation_rate:
                    # 離職（無職になる）
                    is_employed = False
                    unemployment_start_age = age
                    events.append({
                        "age": age,
                        "type": "離職",
                        "rate": pure_separation_rate,
                        "description": f"{age}歳で離職（退職）"
                    })
            else:
                # 無職の場合：再就職するかどうかを判定
                reemployment_rate = self.get_rate_for_age(age, gender, "reemployment")
                
                if random.random() * 100 < reemployment_rate:
                    # 再就職
                    current_company += 1
                    is_employed = True
                    unemployment_duration = age - unemployment_start_age
                    events.append({
                        "age": age,
                        "type": "再就職",
                        "company_number": current_company,
                        "rate": reemployment_rate,
                        "unemployment_duration": unemployment_duration,
                        "description": f"{age}歳で再就職（{current_company}社目、無職期間{unemployment_duration}年）"
                    })
                    unemployment_start_age = None
        
        # 最終状態
        final_status = "就業中" if is_employed else "無職"
        total_unemployment_years = 0
        for i, event in enumerate(events):
            if event["type"] == "再就職":
                total_unemployment_years += event.get("unemployment_duration", 0)
        
        # 最後まで無職だった場合
        if not is_employed and unemployment_start_age is not None:
            total_unemployment_years += retirement_age - unemployment_start_age
        
        return {
            "gender": gender,
            "start_age": start_age,
            "retirement_age": retirement_age,
            "events": events,
            "total_companies": current_company,
            "total_job_changes": len([e for e in events if e["type"] == "転職"]),
            "total_separations": len([e for e in events if e["type"] == "離職"]),
            "total_reemployments": len([e for e in events if e["type"] == "再就職"]),
            "total_unemployment_years": total_unemployment_years,
            "final_status": final_status,
        }
    
    def format_result(self, result, simulation_number=None):
        """
        シミュレーション結果を読みやすい形式でフォーマット
        """
        lines = []
        
        if simulation_number is not None:
            lines.append(f"=== シミュレーション #{simulation_number} ({result['gender']}) ===")
        else:
            lines.append(f"=== シミュレーション ({result['gender']}) ===")
        
        lines.append(f"就業開始: {result['start_age']}歳（大卒）")
        lines.append(f"定年年齢: {result['retirement_age']}歳")
        lines.append(f"勤務期間: {result['retirement_age'] - result['start_age']}年間")
        lines.append("")
        
        if result['events']:
            lines.append("【キャリア履歴】")
            for event in result['events']:
                event_type = event['type']
                age = event['age']
                
                if event_type == "転職":
                    icon = "🔄"
                    lines.append(f"  {icon} {age}歳で転職（{event['company_number']}社目へ）")
                elif event_type == "離職":
                    icon = "📤"
                    lines.append(f"  {icon} {age}歳で離職（退職）")
                elif event_type == "再就職":
                    icon = "📥"
                    lines.append(f"  {icon} {age}歳で再就職（{event['company_number']}社目、無職期間{event['unemployment_duration']}年）")
            
            lines.append("")
        else:
            lines.append("【キャリア履歴】")
            lines.append("  イベントなし（同一企業で定年まで勤務）")
            lines.append("")
        
        # サマリー
        lines.append("【サマリー】")
        lines.append(f"  ・転職回数: {result['total_job_changes']}回")
        lines.append(f"  ・離職回数: {result['total_separations']}回")
        lines.append(f"  ・再就職回数: {result['total_reemployments']}回")
        lines.append(f"  ・勤務社数: {result['total_companies']}社")
        lines.append(f"  ・無職期間合計: {result['total_unemployment_years']}年")
        lines.append(f"  ・定年時の状態: {result['final_status']}")
        
        return "\n".join(lines)


def main():
    """メイン処理：男性3名、女性3名のシミュレーションを実行"""
    simulator = CareerSimulator()
    
    print("=" * 70)
    print("転職・離職・再就職シミュレーション（改良版）")
    print("厚生労働省「令和6年雇用動向調査」に基づく")
    print("=" * 70)
    print()
    
    # 使用データの説明
    print("【使用データ】年齢階級別・男女別 転職入職率／離職率／再就職率")
    print("-" * 70)
    print(f"{'年齢階級':<10}{'男性転職':>10}{'男性離職':>10}{'女性転職':>10}{'女性離職':>10}")
    print("-" * 70)
    for data in simulator.job_mobility_data:
        age_range = f"{data['age_min']}-{data['age_max']}歳"
        print(f"{age_range:<10}{data['male_job_change_rate']:>9.1f}%{data['male_separation_rate']:>9.1f}%{data['female_job_change_rate']:>9.1f}%{data['female_separation_rate']:>9.1f}%")
    print("-" * 70)
    print()
    print("※ 離職率 - 転職率 = 純粋な離職（無職になる）確率として計算")
    print("※ 再就職率は年齢・性別により40-75%で設定（労働力調査に基づく推定値）")
    print()
    print("出典: 厚生労働省「令和6年雇用動向調査」")
    print()
    print("=" * 70)
    print()
    
    # 男性3名のシミュレーション
    print("■ 男性のシミュレーション（3名）")
    print("=" * 70)
    for i in range(1, 4):
        result = simulator.simulate_career("男性", start_age=22, retirement_age=60, seed=None)
        print(simulator.format_result(result, i))
        print()
    
    # 女性3名のシミュレーション
    print("■ 女性のシミュレーション（3名）")
    print("=" * 70)
    for i in range(1, 4):
        result = simulator.simulate_career("女性", start_age=22, retirement_age=60, seed=None)
        print(simulator.format_result(result, i))
        print()
    
    # 統計的な傾向
    print("=" * 70)
    print("【補足】シミュレーションのロジック")
    print("=" * 70)
    print()
    print("各年齢で以下の判定を行います：")
    print()
    print("■ 就業中の場合:")
    print("  1. 転職入職率の確率で → 転職（別の会社へ直接移動）")
    print("  2. (離職率 - 転職率)の確率で → 離職（無職になる）")
    print("  3. それ以外 → 現職継続")
    print()
    print("■ 無職の場合:")
    print("  1. 再就職率の確率で → 再就職")
    print("  2. それ以外 → 無職継続")
    print()
    print("特徴:")
    print("  - 女性は離職率が高く、特に30代で顕著（結婚・出産・育児）")
    print("  - 女性50代は再就職率が高い（子育て後の復帰）")
    print("  - 男性は相対的に離職せず転職する傾向")
    print()


if __name__ == "__main__":
    main()
