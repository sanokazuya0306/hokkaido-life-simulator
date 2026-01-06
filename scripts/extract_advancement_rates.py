#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北海道の市町村別進学率データを抽出するスクリプト

学校基本調査から高校進学率と大学進学率を抽出してCSVに出力する
"""

import pandas as pd
import os

def extract_high_school_rate():
    """市町村別高校進学率を抽出"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'data', 'junior_high_graduates_r6.xlsx')
    output_file = os.path.join(script_dir, 'data', 'high_school_rate.csv')
    
    print(f"=== 高校進学率の抽出 ===")
    print(f"入力ファイル: {input_file}")
    
    try:
        # Excelファイルを読み込み
        df = pd.read_excel(input_file, sheet_name=0, header=None)
        
        print(f"\n最初の20行:")
        print(df.head(20))
        
        # 列0または列1が市町村名、列3が卒業者数、列4が高校進学者数
        # 列0は振興局レベル、列1は市町村レベル
        city_col_0 = 0
        city_col_1 = 1
        total_col = 3
        hs_col = 4
        
        print(f"\n市町村列: {city_col_0} または {city_col_1}")
        print(f"卒業者数列: {total_col}")
        print(f"高校進学者列: {hs_col}")
        
        # データを抽出（行7以降）
        result_data = []
        for idx in range(7, len(df)):
            # 列1を優先、なければ列0を使用
            city = df.iloc[idx, city_col_1]
            if pd.isna(city):
                city = df.iloc[idx, city_col_0]
            
            total = df.iloc[idx, total_col]
            hs = df.iloc[idx, hs_col]
            
            if pd.notna(city) and pd.notna(total) and pd.notna(hs):
                city_str = str(city).strip()
                # 「計」を含む行や空白行をスキップ
                if city_str and city_str not in ['全道計', '市部計', '郡部計', '町村計', '市計'] and '振興局' not in city_str:
                    try:
                        total_num = float(total)
                        hs_num = float(hs)
                        if total_num > 0:
                            rate = (hs_num / total_num) * 100
                            result_data.append({
                                '市町村': city_str,
                                '進学率': round(rate, 2)
                            })
                    except (ValueError, TypeError):
                        pass
        
        # DataFrameに変換
        result_df = pd.DataFrame(result_data)
        
        # デフォルト値を追加
        result_df = pd.concat([result_df, pd.DataFrame([{'市町村': 'default', '進学率': 98.5}])], ignore_index=True)
        
        print(f"\n抽出されたデータ（最初の20件）:")
        print(result_df.head(20))
        print(f"\n総データ数: {len(result_df)}市町村")
        print(f"平均進学率: {result_df[result_df['市町村'] != 'default']['進学率'].mean():.2f}%")
        
        # CSVに出力
        result_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n✓ データを保存しました: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return False

def extract_university_rate():
    """市町村別大学進学率を抽出"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'data', 'high_school_graduates_r6.xlsx')
    output_file = os.path.join(script_dir, 'data', 'university_rate.csv')
    
    print(f"\n=== 大学進学率の抽出 ===")
    print(f"入力ファイル: {input_file}")
    
    try:
        # Excelファイルを読み込み
        df = pd.read_excel(input_file, sheet_name=0, header=None)
        
        # 列0または列1が市町村名、列3が卒業者数、列4が大学進学者数
        city_col_0 = 0
        city_col_1 = 1
        total_col = 3
        univ_col = 4
        
        print(f"\n市町村列: {city_col_0} または {city_col_1}")
        print(f"卒業者数列: {total_col}")
        print(f"大学進学者列: {univ_col}")
        
        # データを抽出（行7以降）
        result_data = []
        for idx in range(7, len(df)):
            # 列1を優先、なければ列0を使用
            city = df.iloc[idx, city_col_1]
            if pd.isna(city):
                city = df.iloc[idx, city_col_0]
            
            total = df.iloc[idx, total_col]
            univ = df.iloc[idx, univ_col]
            
            if pd.notna(city) and pd.notna(total) and pd.notna(univ):
                city_str = str(city).strip()
                # 「計」を含む行や空白行をスキップ
                if city_str and city_str not in ['全道計', '市部計', '郡部計', '町村計', '市計'] and '振興局' not in city_str:
                    try:
                        total_num = float(total)
                        univ_num = float(univ)
                        if total_num > 0:
                            rate = (univ_num / total_num) * 100
                            result_data.append({
                                '市町村': city_str,
                                '進学率': round(rate, 2)
                            })
                    except (ValueError, TypeError):
                        pass
        
        # DataFrameに変換
        result_df = pd.DataFrame(result_data)
        
        # デフォルト値を追加
        result_df = pd.concat([result_df, pd.DataFrame([{'市町村': 'default', '進学率': 51.5}])], ignore_index=True)
        
        print(f"\n抽出されたデータ（最初の20件）:")
        print(result_df.head(20))
        print(f"\n総データ数: {len(result_df)}市町村")
        print(f"平均進学率: {result_df[result_df['市町村'] != 'default']['進学率'].mean():.2f}%")
        
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
    success1 = extract_high_school_rate()
    success2 = extract_university_rate()
    
    if success1 and success2:
        print("\n" + "=" * 60)
        print("✓ すべてのデータ抽出が完了しました！")
        print("=" * 60)

