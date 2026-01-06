#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北海道の市町村別出生数データを抽出するスクリプト

北海道庁「市区町村別人口、人口動態及び世帯数」から
市町村別の出生数を抽出してCSVに出力する
"""

import pandas as pd
import os

def extract_birth_data():
    """市町村別出生数データを抽出"""
    
    # スクリプトのディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # ファイルパス設定
    input_file = os.path.join(script_dir, 'data', 'hokkaido_birth_raw_2024.xlsx')
    output_file = os.path.join(script_dir, 'data', 'birth_by_city.csv')
    
    print(f"入力ファイル: {input_file}")
    
    try:
        # Excelファイルを読み込み
        # まずはどんなシートがあるか確認
        xl_file = pd.ExcelFile(input_file)
        print(f"\n利用可能なシート: {xl_file.sheet_names}")
        
        # 最初のシートを読み込んで内容を確認
        df = pd.read_excel(input_file, sheet_name=0, header=None)
        
        print("\n最初の20行:")
        print(df.head(20))
        
        # データの形式を確認
        print(f"\nデータ形状: {df.shape}")
        print(f"\n列数: {len(df.columns)}")
        
        # 市町村名と出生数を含む列を探す
        # 通常、市町村名は最初の列、出生数は「出生」という文字を含む列
        
        # ヘッダー行を探す（「市町村」「出生」などのキーワードを含む行）
        header_row = None
        for idx, row in df.iterrows():
            row_str = ' '.join([str(x) for x in row if pd.notna(x)])
            if '市町村' in row_str or '市区町村' in row_str:
                header_row = idx
                print(f"\nヘッダー行を発見: {idx}行目")
                print(f"ヘッダー内容: {row_str[:200]}")
                break
        
        if header_row is None:
            print("\nエラー: ヘッダー行が見つかりません")
            return False
        
        # ヘッダー行でデータを再読み込み
        df = pd.read_excel(input_file, sheet_name=0, header=header_row)
        
        print(f"\n再読み込み後のデータ:")
        print(df.head(10))
        print(f"\n列名: {list(df.columns)}")
        
        # 市町村名と出生数の列を特定
        city_col = None
        birth_col = None
        
        for col in df.columns:
            col_str = str(col)
            if '市町村' in col_str or '市区町村' in col_str:
                city_col = col
                print(f"\n市町村列を発見: {col}")
            if '出生' in col_str and '数' in col_str:
                birth_col = col
                print(f"出生数列を発見: {col}")
        
        if city_col is None or birth_col is None:
            print(f"\nエラー: 必要な列が見つかりません")
            print(f"市町村列: {city_col}")
            print(f"出生数列: {birth_col}")
            return False
        
        # 必要な列のみ抽出
        result_df = df[[city_col, birth_col]].copy()
        
        # 列名を標準化
        result_df.columns = ['市町村', '出生数']
        
        # 空白行と無効なデータを除去
        result_df = result_df.dropna(subset=['市町村', '出生数'])
        result_df = result_df[result_df['市町村'].astype(str).str.strip() != '']
        result_df = result_df[result_df['出生数'].astype(str).str.strip() != '']
        
        # 出生数を数値に変換（カンマなどを除去）
        result_df['出生数'] = pd.to_numeric(result_df['出生数'], errors='coerce')
        result_df = result_df.dropna(subset=['出生数'])
        result_df['出生数'] = result_df['出生数'].astype(int)
        
        # 市町村名をクリーンアップ
        result_df['市町村'] = result_df['市町村'].astype(str).str.strip()
        
        # 合計行などを除外（出生数が極端に大きい行）
        result_df = result_df[result_df['出生数'] < 20000]
        
        # 出生数が0より大きいもののみ
        result_df = result_df[result_df['出生数'] > 0]
        
        print(f"\n抽出されたデータ:")
        print(result_df.head(20))
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

