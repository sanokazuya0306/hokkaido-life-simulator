#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北海道保健統計年報から年齢別死亡者数を抽出するスクリプト
"""

import pandas as pd
import os

def extract_death_by_age():
    """年齢別死亡者数を抽出"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'data', 'health_stats_r4_t21-24.xlsx')
    output_file = os.path.join(script_dir, 'data', 'death_by_age.csv')
    
    print(f"入力ファイル: {input_file}")
    print(f"出力ファイル: {output_file}\n")
    
    try:
        # Excelファイルのシート名を確認
        xl_file = pd.ExcelFile(input_file)
        print(f"利用可能なシート: {xl_file.sheet_names}\n")
        
        # 第24表のシートを読み込み
        # シート名は「第24表」または「t24」などの可能性
        sheet_name = None
        for name in xl_file.sheet_names:
            if '24' in name:
                sheet_name = name
                break
        
        if sheet_name is None:
            # 最後のシートを使用
            sheet_name = xl_file.sheet_names[-1]
        
        print(f"使用するシート: {sheet_name}\n")
        
        df = pd.read_excel(input_file, sheet_name=sheet_name, header=None)
        
        # 行5の「全　　道」のデータを抽出
        hokkaido_row = 5
        
        # 列の確認
        print("全道のデータ（行5）:")
        for col_idx in range(min(30, len(df.columns))):
            val = df.iloc[hokkaido_row, col_idx]
            if pd.notna(val):
                print(f"  列{col_idx}: {val}")
        
        # ヘッダー（行3）を確認
        print("\nヘッダー（行3）:")
        for col_idx in range(min(30, len(df.columns))):
            val = df.iloc[3, col_idx]
            if pd.notna(val):
                print(f"  列{col_idx}: {val}")
        
        # 年齢階級のマッピング
        # 列3-7: 0歳、1歳、2歳、3歳、4歳
        # 列8以降: 0～4歳、5～9歳、10～14歳、...
        # 各歳のデータがある場合はそれを使い、ない場合は5歳階級を5で割る
        
        age_data = []
        
        # 0-4歳: 個別データがある
        for age in range(5):
            col_idx = 3 + age  # 列3-7
            deaths = df.iloc[hokkaido_row, col_idx]
            if pd.isna(deaths) or deaths == '-':
                deaths = 0
            else:
                deaths = int(deaths)
            age_data.append({'年齢': age, '死亡者数': deaths})
        
        # 5歳以降: 5歳階級データを使用
        # 列9以降が 5～9, 10～14, 15～19, ...
        age_group_start_col = 9
        
        for age_group_idx in range(19):  # 5～9歳から95～99歳まで（19グループ）
            col_idx = age_group_start_col + age_group_idx
            if col_idx >= len(df.columns):
                break
            
            deaths_5year = df.iloc[hokkaido_row, col_idx]
            if pd.isna(deaths_5year) or deaths_5year == '-':
                deaths_5year = 0
            else:
                deaths_5year = int(deaths_5year)
            
            # 5歳階級を5で割って各歳に按分
            deaths_per_year = deaths_5year / 5
            
            base_age = 5 + (age_group_idx * 5)
            for offset in range(5):
                age = base_age + offset
                if age < 100:
                    age_data.append({
                        '年齢': age,
                        '死亡者数': int(deaths_per_year)
                    })
        
        # CSVに出力
        result_df = pd.DataFrame(age_data)
        result_df.to_csv(output_file, index=False, encoding='utf-8')
        
        total_deaths = sum([d['死亡者数'] for d in age_data])
        hokkaido_total = df.iloc[hokkaido_row, 2]  # 列2が総数
        
        print(f"\n✓ 更新完了: {output_file}")
        print(f"年齢範囲: 0-99歳")
        print(f"合計死亡者数: {total_deaths:,}人")
        print(f"北海道総数（参考）: {hokkaido_total:,}人")
        print("\n注: 5歳以降のデータは5歳階級を各歳に均等按分しています")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    extract_death_by_age()

