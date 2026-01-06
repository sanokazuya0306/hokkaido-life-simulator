#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
労働力調査から産業別就業者数を抽出するスクリプト
"""

import pandas as pd
import os

def extract_industry_data():
    """産業別就業者数を抽出"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'data', 'labor_force_r6_table2.xls')
    output_file = os.path.join(script_dir, 'data', 'workers_by_industry.csv')
    
    print(f"入力ファイル: {input_file}")
    print(f"出力ファイル: {output_file}\n")
    
    try:
        # Excelファイルを読み込み
        df = pd.read_excel(input_file, sheet_name=0, header=None)
        
        print("行3（ヘッダー）の全列:")
        for col_idx in range(len(df.columns)):
            val = df.iloc[2, col_idx]
            if pd.notna(val):
                print(f"列{col_idx}: {val}")
        
        print("\n行24（令和6年）の全列:")
        for col_idx in range(len(df.columns)):
            val = df.iloc[24, col_idx]
            if pd.notna(val):
                print(f"列{col_idx}: {val}")
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    extract_industry_data()

