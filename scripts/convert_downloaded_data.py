#!/usr/bin/env python3
"""
ダウンロードした統計データをプログラムで使用できるCSV形式に変換するスクリプト

使用方法:
1. 統計データをExcelまたはCSV形式でダウンロード
2. このスクリプトを使用して変換
3. scripts/data/ ディレクトリに保存
"""

import sys
import csv
import argparse
from pathlib import Path
import pandas as pd


def convert_birth_data(input_file, output_file):
    """
    出生数データを変換
    
    入力形式の例:
    - 列: 市町村名, 出生数
    - または: 都道府県, 市町村, 出生数
    """
    try:
        # Excelファイルの場合はpandasで読み込み
        if input_file.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(input_file)
        else:
            df = pd.read_csv(input_file, encoding='utf-8')
        
        # 列名を確認して適切な列を選択
        print(f"データの列: {list(df.columns)}")
        
        # 市町村名と出生数の列を特定（手動で調整が必要な場合あり）
        city_col = None
        birth_col = None
        
        for col in df.columns:
            col_lower = str(col).lower()
            if '市' in str(col) or '町' in str(col) or '村' in str(col) or '市町村' in str(col):
                city_col = col
            if '出生' in str(col) or '数' in str(col) and '出生' in str(col):
                birth_col = col
        
        if city_col is None or birth_col is None:
            print("エラー: 市町村名または出生数の列が見つかりません", file=sys.stderr)
            print("手動で列名を指定してください", file=sys.stderr)
            return False
        
        # 北海道のデータのみを抽出（都道府県列がある場合）
        if '都道府県' in df.columns or '都道府県名' in df.columns:
            pref_col = '都道府県' if '都道府県' in df.columns else '都道府県名'
            df = df[df[pref_col].str.contains('北海道', na=False)]
        
        # CSV形式で出力
        output_df = pd.DataFrame({
            '市町村': df[city_col],
            '出生数': pd.to_numeric(df[birth_col], errors='coerce').fillna(0).astype(int)
        })
        
        # 出生数が0より大きいもののみ
        output_df = output_df[output_df['出生数'] > 0]
        
        output_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"変換完了: {output_file}")
        return True
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return False


def convert_education_rate(input_file, output_file, rate_type='high_school'):
    """
    進学率データを変換
    
    Args:
        rate_type: 'high_school' または 'university'
    """
    try:
        if input_file.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(input_file)
        else:
            df = pd.read_csv(input_file, encoding='utf-8')
        
        print(f"データの列: {list(df.columns)}")
        
        city_col = None
        rate_col = None
        
        for col in df.columns:
            col_str = str(col)
            if '市' in col_str or '町' in col_str or '村' in col_str or '市町村' in col_str:
                city_col = col
            if rate_type == 'high_school':
                if '高校' in col_str and ('進学' in col_str or '率' in col_str):
                    rate_col = col
            else:
                if '大学' in col_str and ('進学' in col_str or '率' in col_str):
                    rate_col = col
        
        if city_col is None or rate_col is None:
            print("エラー: 市町村名または進学率の列が見つかりません", file=sys.stderr)
            return False
        
        # 北海道のデータのみを抽出
        if '都道府県' in df.columns or '都道府県名' in df.columns:
            pref_col = '都道府県' if '都道府県' in df.columns else '都道府県名'
            df = df[df[pref_col].str.contains('北海道', na=False)]
        
        output_df = pd.DataFrame({
            '市町村': df[city_col],
            '進学率': pd.to_numeric(df[rate_col], errors='coerce').fillna(0)
        })
        
        output_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"変換完了: {output_file}")
        return True
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return False


def convert_industry_data(input_file, output_file):
    """産業別労働者数データを変換"""
    try:
        if input_file.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(input_file)
        else:
            df = pd.read_csv(input_file, encoding='utf-8')
        
        print(f"データの列: {list(df.columns)}")
        
        industry_col = None
        workers_col = None
        
        for col in df.columns:
            col_str = str(col)
            if '産業' in col_str or '業種' in col_str:
                industry_col = col
            if '労働者' in col_str or '就業者' in col_str or ('数' in col_str and '労働' in col_str):
                workers_col = col
        
        if industry_col is None or workers_col is None:
            print("エラー: 産業名または労働者数の列が見つかりません", file=sys.stderr)
            return False
        
        output_df = pd.DataFrame({
            '産業': df[industry_col],
            '労働者数': pd.to_numeric(df[workers_col], errors='coerce').fillna(0).astype(int)
        })
        
        output_df = output_df[output_df['労働者数'] > 0]
        
        output_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"変換完了: {output_file}")
        return True
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return False


def convert_death_age_data(input_file, output_file):
    """年齢別死亡者数データを変換"""
    try:
        if input_file.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(input_file)
        else:
            df = pd.read_csv(input_file, encoding='utf-8')
        
        print(f"データの列: {list(df.columns)}")
        
        age_col = None
        death_col = None
        
        for col in df.columns:
            col_str = str(col)
            if '年齢' in col_str:
                age_col = col
            if '死亡' in col_str and '数' in col_str:
                death_col = col
        
        if age_col is None or death_col is None:
            print("エラー: 年齢または死亡者数の列が見つかりません", file=sys.stderr)
            return False
        
        output_df = pd.DataFrame({
            '年齢': pd.to_numeric(df[age_col], errors='coerce').fillna(0).astype(int),
            '死亡者数': pd.to_numeric(df[death_col], errors='coerce').fillna(0).astype(int)
        })
        
        output_df = output_df[output_df['死亡者数'] > 0]
        output_df = output_df.sort_values('年齢')
        
        output_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"変換完了: {output_file}")
        return True
        
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="統計データをCSV形式に変換")
    parser.add_argument("type", choices=['birth', 'high_school', 'university', 'industry', 'death'],
                        help="データの種類")
    parser.add_argument("input", type=Path, help="入力ファイル（ExcelまたはCSV）")
    parser.add_argument("-o", "--output", type=Path, default=None,
                        help="出力ファイル（省略時は自動生成）")
    
    args = parser.parse_args()
    
    if not args.input.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    if args.output is None:
        script_dir = Path(__file__).parent
        data_dir = script_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        if args.type == 'birth':
            args.output = data_dir / "birth_by_city.csv"
        elif args.type == 'high_school':
            args.output = data_dir / "high_school_rate.csv"
        elif args.type == 'university':
            args.output = data_dir / "university_rate.csv"
        elif args.type == 'industry':
            args.output = data_dir / "workers_by_industry.csv"
        elif args.type == 'death':
            args.output = data_dir / "death_by_age.csv"
    
    success = False
    if args.type == 'birth':
        success = convert_birth_data(args.input, args.output)
    elif args.type == 'high_school':
        success = convert_education_rate(args.input, args.output, 'high_school')
    elif args.type == 'university':
        success = convert_education_rate(args.input, args.output, 'university')
    elif args.type == 'industry':
        success = convert_industry_data(args.input, args.output)
    elif args.type == 'death':
        success = convert_death_age_data(args.input, args.output)
    
    if success:
        print(f"\n変換されたファイル: {args.output}")
        print("このファイルを scripts/data/ に配置してください")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

