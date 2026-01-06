#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
進学データファイルの構造を調査するスクリプト
"""

import pandas as pd
import os

def inspect_file(filename, title):
    """ファイルの構造を調査"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'data', filename)
    
    print(f"\n{'=' * 80}")
    print(f"{title}")
    print(f"{'=' * 80}")
    
    df = pd.read_excel(input_file, sheet_name=0, header=None)
    
    print(f"\n最初の30行、最初の10列:")
    for idx in range(min(30, len(df))):
        row_data = []
        for col_idx in range(min(10, len(df.columns))):
            val = df.iloc[idx, col_idx]
            if pd.notna(val):
                row_data.append(f"[{col_idx}]:{val}")
        if row_data:
            print(f"行{idx}: {' | '.join(row_data)}")

if __name__ == '__main__':
    inspect_file('junior_high_graduates_r6.xlsx', '中学校卒業後の進路')
    inspect_file('high_school_graduates_r6.xlsx', '高等学校卒業後の進路')

