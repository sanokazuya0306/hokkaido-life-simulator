#!/usr/bin/env python3
"""
e-Statから北海道の統計データをダウンロードするスクリプト

このスクリプトは、人口動態調査や国勢調査などのデータをダウンロードします。
"""

import os
import sys
import requests
from pathlib import Path


def download_file(url, output_path):
    """
    URLからファイルをダウンロード
    
    Args:
        url: ダウンロードするURL
        output_path: 保存先のパス
    """
    try:
        print(f"ダウンロード中: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ 保存完了: {output_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ ダウンロードエラー: {e}", file=sys.stderr)
        return False


def main():
    # データ保存先
    script_dir = Path(__file__).parent
    data_dir = script_dir / "data" / "raw"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("北海道の統計データをダウンロード")
    print("=" * 60)
    print()
    
    # ダウンロードするデータのリスト
    datasets = [
        {
            "name": "都道府県別出生数 (2023年)",
            "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040207116&fileKind=1",
            "filename": "birth_by_prefecture_2023.csv"
        },
        {
            "name": "都道府県別死亡数・死亡率 (2023年)",
            "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040207303&fileKind=1",
            "filename": "death_by_prefecture_2023.csv"
        },
        {
            "name": "年齢別死亡数 (2023年)",
            "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040207330&fileKind=1",
            "filename": "death_by_age_2023.csv"
        },
    ]
    
    success_count = 0
    for dataset in datasets:
        print(f"データセット: {dataset['name']}")
        output_path = data_dir / dataset['filename']
        
        if download_file(dataset['url'], output_path):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"完了: {success_count}/{len(datasets)} 件のデータをダウンロードしました")
    print("=" * 60)
    print()
    
    if success_count > 0:
        print("次のステップ:")
        print("1. ダウンロードしたデータを確認")
        print(f"   場所: {data_dir}")
        print("2. convert_downloaded_data.py を使用してCSV形式に変換")
        print("3. hokkaido_life_simulator.py で使用")


if __name__ == "__main__":
    main()

