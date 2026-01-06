#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北海道保健統計年報から死因データを抽出するスクリプト
"""

import pandas as pd
import os

def extract_death_cause():
    """死因別死亡者数を抽出"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'data', 'health_stats_r4_t1-3.xls')
    output_file = os.path.join(script_dir, 'data', 'death_by_cause.csv')
    
    print(f"入力ファイル: {input_file}")
    print(f"出力ファイル: {output_file}\n")
    
    try:
        # Excelファイルのシート名を確認
        xl_file = pd.ExcelFile(input_file)
        print(f"利用可能なシート: {xl_file.sheet_names}\n")
        
        # 表3のシートを探す
        sheet_name = None
        for name in xl_file.sheet_names:
            if '表3' in name or 't3' in name.lower():
                sheet_name = name
                break
        
        if sheet_name is None:
            # 3番目のシートを使用
            if len(xl_file.sheet_names) >= 3:
                sheet_name = xl_file.sheet_names[2]
            else:
                sheet_name = xl_file.sheet_names[-1]
        
        print(f"使用するシート: {sheet_name}\n")
        
        df = pd.read_excel(input_file, sheet_name=sheet_name, header=None)
        
        # 死因データは行7から始まる
        # 列1: 死因名、列3: 死亡数
        cause_data = []
        
        for idx in range(7, len(df)):
            cause = df.iloc[idx, 1]  # 列1: 死因名
            deaths = df.iloc[idx, 3]  # 列3: 死亡数
            
            # データが終了したらループを抜ける
            if pd.isna(cause) or cause == '' or str(cause).strip() == '':
                break
            
            # 死亡数が有効な数値かチェック
            if pd.notna(deaths):
                try:
                    deaths_int = int(deaths)
                    if deaths_int > 0:
                        cause_data.append({
                            '死因': str(cause).strip(),
                            '死亡者数': deaths_int
                        })
                except (ValueError, TypeError):
                    pass
        
        if not cause_data:
            print("エラー: 死因データを抽出できませんでした")
            return False
        
        # CSVに出力
        result_df = pd.DataFrame(cause_data)
        result_df.to_csv(output_file, index=False, encoding='utf-8')
        
        total_deaths = sum([d['死亡者数'] for d in cause_data])
        
        print(f"✓ 更新完了: {output_file}")
        print(f"死因数: {len(cause_data)}")
        print(f"合計死亡者数: {total_deaths:,}人")
        print("\n抽出された死因:")
        for data in cause_data[:15]:  # 最初の15件を表示
            print(f"  {data['死因']}: {data['死亡者数']:,}人")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    extract_death_cause()

