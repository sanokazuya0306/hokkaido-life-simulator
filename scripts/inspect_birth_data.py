#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ダウンロードしたExcelファイルの構造を詳しく調査するスクリプト
"""

import pandas as pd
import os

def inspect_excel():
    """Excelファイルの構造を詳しく調査"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'data', 'hokkaido_birth_raw_2024.xlsx')
    
    print(f"ファイル: {input_file}\n")
    
    # シート一覧
    xl_file = pd.ExcelFile(input_file)
    print(f"シート一覧: {xl_file.sheet_names}\n")
    
    # 最初のシートの詳細
    df = pd.read_excel(input_file, sheet_name=0, header=None)
    
    print("=" * 80)
    print("最初の40行を表示:")
    print("=" * 80)
    for idx in range(min(40, len(df))):
        row_data = []
        for col_idx in range(min(19, len(df.columns))):
            val = df.iloc[idx, col_idx]
            if pd.notna(val):
                row_data.append(f"[{col_idx}]:{val}")
        if row_data:
            print(f"行{idx}: {' | '.join(row_data)}")
    
    print("\n" + "=" * 80)
    print("各列の最初の20個の非NaN値:")
    print("=" * 80)
    for col_idx in range(min(19, len(df.columns))):
        print(f"\n列{col_idx}:")
        non_nan_values = df[col_idx].dropna().head(20).tolist()
        for i, val in enumerate(non_nan_values):
            print(f"  {i}: {val}")

if __name__ == '__main__':
    inspect_excel()

