#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北海道の市町村別出生数データを抽出するスクリプト（修正版）
"""

import pandas as pd
import os

def extract_birth_data():
    """市町村別出生数データを抽出"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'data', 'hokkaido_birth_raw_2024.xlsx')
    output_file = os.path.join(script_dir, 'data', 'birth_by_city.csv')
    
    print(f"入力ファイル: {input_file}")
    
    try:
        # Excelファイルを読み込み（ヘッダーなし）
        df = pd.read_excel(input_file, sheet_name=0, header=None)
        
        # 列0が市区町村名、列4が出生数
        # データは行7から始まる
        
        # 必要な列のみ抽出
        city_col = 0
        birth_col = 4
        
        # データを抽出（行7以降）
        data_start_row = 7
        
        result_data = []
        for idx in range(data_start_row, len(df)):
            city = df.iloc[idx, city_col]
            birth = df.iloc[idx, birth_col]
            
            # 有効なデータのみ追加
            if pd.notna(city) and pd.notna(birth):
                city_str = str(city).strip()
                # 「計」を含む行や空白行をスキップ
                if city_str and '計' not in city_str and '振興局' not in city_str:
                    try:
                        birth_num = int(birth)
                        if birth_num > 0:  # 出生数が0より大きい
                            result_data.append({'市町村': city_str, '出生数': birth_num})
                    except (ValueError, TypeError):
                        pass  # 数値に変換できない場合はスキップ
        
        # DataFrameに変換
        result_df = pd.DataFrame(result_data)
        
        print(f"\n抽出されたデータ:")
        print(result_df.to_string(index=False))
        print(f"\n総データ数: {len(result_df)}市町村")
        print(f"出生数合計: {result_df['出生数'].sum()}人")
        
        # CSVに出力
        result_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n✓ データを保存しました: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    extract_birth_data()

