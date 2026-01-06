#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
労働力調査から産業別就業者数を抽出するスクリプト（改良版）
"""

import pandas as pd
import os

def extract_industry_data():
    """産業別就業者数を抽出"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'data', 'labor_force_r6_table2.xls')
    output_file = os.path.join(script_dir, 'data', 'workers_by_industry.csv')
    
    print(f"入力ファイル: {input_file}")
    
    try:
        # Excelファイルを読み込み
        df = pd.read_excel(input_file, sheet_name=0, header=None)
        
        # ヘッダーを複数行から構築
        print("\nヘッダー構築:")
        print("行2-5の全列を確認:")
        for row_idx in range(2, 6):
            print(f"\n行{row_idx}:")
            for col_idx in range(len(df.columns)):
                val = df.iloc[row_idx, col_idx]
                if pd.notna(val):
                    print(f"  列{col_idx}: {val}")
        
        # 産業名を手動で定義（ウェブページの表1から）
        # 列2: 農業・林業
        # 列3: 非農林業（合計）
        # 列4: 漁業
        # 列6: 建設業
        # 列7: 製造業
        # ... その他
        
        # 令和6年（行24）のデータを抽出
        r6_row = 24
        
        print(f"\n\n令和6年のデータ（行{r6_row}）:")
        print("列番号: 値")
        for col_idx in range(len(df.columns)):
            val = df.iloc[r6_row, col_idx]
            if pd.notna(val) and isinstance(val, (int, float)):
                print(f"  列{col_idx}: {val}万人")
        
        # Excelの列ヘッダーから正しいマッピングを構築
        # 行3のヘッダーと令和6年のデータを照合
        industry_mapping = {
            2: '農業・林業',
            4: '漁業',
            5: '鉱業・採石業・砂利採取業',
            6: '建設業',
            7: '製造業',
            8: '電気・ガス・熱供給・水道業',
            9: '情報通信業',
            10: '運輸業・郵便業',
            11: '卸売業・小売業',
            12: '金融業・保険業',
            13: '不動産業・物品賃貸業',
            14: '学術研究・専門・技術サービス業',
            15: '宿泊業・飲食サービス業',
            16: '生活関連サービス業・娯楽業',
            17: '教育・学習支援業',
            18: '医療・福祉',
            19: '複合サービス事業',
            20: 'サービス業（他に分類されないもの）',
            21: '公務'
        }
        
        # CSVデータを構築
        industry_data = []
        for col_idx, industry_name in industry_mapping.items():
            val = df.iloc[r6_row, col_idx]
            if pd.notna(val) and isinstance(val, (int, float)):
                # 万人→人に変換（×10,000）
                workers = int(val * 10000)
                industry_data.append({
                    '産業': industry_name,
                    '労働者数': workers
                })
        
        # CSVに出力（BOMなし）
        result_df = pd.DataFrame(industry_data)
        result_df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"\n✓ 更新完了: {output_file}")
        print(f"産業数: {len(industry_data)}")
        print(f"合計労働者数: {sum([d['労働者数'] for d in industry_data]):,}人")
        
        print("\n抽出されたデータ:")
        for data in industry_data:
            print(f"  {data['産業']}: {data['労働者数']:,}人")
        
        return True
        
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    extract_industry_data()

