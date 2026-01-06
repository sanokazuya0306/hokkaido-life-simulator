#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北海道の高校出身者の都道府県別大学進学先データをダウンロード・分析するスクリプト

e-Stat 学校基本調査「出身高校の所在地県別 入学者数」から
北海道出身者がどの都道府県の大学に進学したかを分析します。
"""

import requests
import pandas as pd
import os
from pathlib import Path


def download_file(url, filename):
    """ファイルをダウンロード"""
    script_dir = Path(__file__).parent
    output_path = script_dir / 'data' / filename
    
    print(f"ダウンロード中: {filename}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ ダウンロード完了: {output_path}")
        return output_path
    except Exception as e:
        print(f"✗ エラー: {e}")
        return None


def analyze_hokkaido_university_destinations(excel_path):
    """
    北海道出身者の大学進学先を分析
    
    Args:
        excel_path: ダウンロードしたExcelファイルのパス
    """
    print("\n" + "=" * 80)
    print("北海道の高校出身者の進学先分析")
    print("=" * 80 + "\n")
    
    try:
        # Excelファイルを読み込み（シート名やヘッダー行は実際のファイルに応じて調整）
        # 学校基本調査の場合、通常は複数シートがあり、データは数行目から始まる
        df = pd.read_excel(excel_path, sheet_name=0)
        
        print("データの最初の10行:")
        print(df.head(10))
        print("\n列名:")
        print(df.columns.tolist())
        
        # 以下は実際のデータ構造に応じて調整が必要
        # 一般的な構造: 行=出身都道府県、列=進学先都道府県
        
        return df
        
    except Exception as e:
        print(f"エラー: データの読み込みに失敗しました: {e}")
        print("\n注意: このファイルは手動で確認し、適切に処理する必要があります。")
        print("Excelファイルを開いて、データの構造を確認してください。")
        return None


def calculate_destination_ratio(df, origin_prefecture="北海道"):
    """
    特定の出身都道府県からの進学先割合を計算
    
    Args:
        df: データフレーム
        origin_prefecture: 出身都道府県名
    """
    try:
        # 北海道出身者のデータを抽出
        # ※実際のデータ構造に応じて調整が必要
        hokkaido_data = df[df['出身都道府県'] == origin_prefecture]
        
        if hokkaido_data.empty:
            print(f"警告: {origin_prefecture}のデータが見つかりません")
            return None
        
        # 進学先都道府県別の人数を集計
        destinations = {}
        total = 0
        
        for col in df.columns:
            if col not in ['出身都道府県', '合計']:
                count = hokkaido_data[col].iloc[0]
                if pd.notna(count) and count > 0:
                    destinations[col] = int(count)
                    total += int(count)
        
        # 割合を計算
        print(f"\n【{origin_prefecture}の高校出身者の進学先】")
        print(f"合計進学者数: {total:,}人\n")
        
        # 割合の高い順にソート
        sorted_destinations = sorted(destinations.items(), key=lambda x: x[1], reverse=True)
        
        print("進学先都道府県別の内訳:")
        print("-" * 60)
        for dest, count in sorted_destinations[:10]:  # 上位10都道府県
            ratio = (count / total) * 100
            print(f"{dest:10s}: {count:6,}人 ({ratio:5.2f}%)")
        
        # 道内・道外の割合
        hokkaido_count = destinations.get('北海道', 0)
        dogai_count = total - hokkaido_count
        
        print("\n" + "=" * 60)
        print("【道内・道外の内訳】")
        print(f"道内進学: {hokkaido_count:6,}人 ({(hokkaido_count/total)*100:5.2f}%)")
        print(f"道外進学: {dogai_count:6,}人 ({(dogai_count/total)*100:5.2f}%)")
        print("=" * 60)
        
        # CSVとして保存
        script_dir = Path(__file__).parent
        output_path = script_dir / 'data' / f'{origin_prefecture}_university_destinations.csv'
        
        result_df = pd.DataFrame([
            {'進学先都道府県': dest, '進学者数': count, '割合(%)': round((count/total)*100, 2)}
            for dest, count in sorted_destinations
        ])
        result_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n結果を保存しました: {output_path}")
        
        return result_df
        
    except Exception as e:
        print(f"エラー: 分析に失敗しました: {e}")
        print("データの構造を確認して、スクリプトを調整してください。")
        return None


def main():
    """メイン処理"""
    
    print("=" * 80)
    print("北海道の高校出身者の大学進学先データ取得・分析")
    print("=" * 80)
    print()
    
    print("【データソース】")
    print("e-Stat > 学校基本調査 > 令和6年度（2024年）")
    print("表番号16: 出身高校の所在地県別 入学者数")
    print()
    
    # データフォルダのパスを確認
    script_dir = Path(__file__).parent
    data_dir = script_dir / 'data'
    data_dir.mkdir(exist_ok=True)
    
    expected_file = data_dir / 'university_enrollment_by_prefecture_2024.xlsx'
    
    # ファイルが存在しない場合は自動ダウンロードを試みる
    if not expected_file.exists():
        print("ファイルが見つかりません。自動ダウンロードを開始します...\n")
        
        # e-Statの学校基本調査 2024年度 表16のダウンロードURL
        # statInfId=000040230324 (2024年12月18日更新)
        download_urls = [
            {
                'url': 'https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040230324&fileKind=0',
                'name': '2024年度 表16（出身高校の所在地県別 入学者数）',
                'filename': 'university_enrollment_by_prefecture_2024.xlsx'
            },
        ]
        
        downloaded_file = None
        for item in download_urls:
            print(f"試行中: {item['name']}")
            result = download_file(item['url'], item['filename'])
            if result:
                downloaded_file = result
                expected_file = result
                break
            print()
        
        if not downloaded_file:
            print("\n" + "=" * 80)
            print("自動ダウンロードに失敗しました")
            print("=" * 80)
            print("\n【手動でのダウンロード方法】")
            print("1. https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist")
            print("   &toukei=00400001&tstat=000001011528&cycle=0&tclass1=000001223980")
            print("   &tclass2=000001223981&tclass3=000001223982&tclass4=000001223984")
            print("   にアクセス")
            print("2. 「表番号7: 出身高校の所在地県別 入学者数」を探す")
            print("3. Excelファイルをダウンロード")
            print(f"4. {expected_file} として保存")
            print("5. 再度このスクリプトを実行")
            return
    else:
        print(f"✓ ファイルが見つかりました: {expected_file}\n")
    
    # データを分析
    print("データを分析します...\n")
    df = analyze_hokkaido_university_destinations(expected_file)
    
    if df is not None:
        print("\n" + "=" * 80)
        print("次のステップ")
        print("=" * 80)
        print("\n上記でデータの構造を確認できました。")
        print("データの列名や構造を確認して、必要に応じてスクリプトを調整してください。")
        print("\n実際の分析を実行するには:")
        print("  calculate_destination_ratio(df)")
        print("を呼び出してください。")


if __name__ == '__main__':
    main()

