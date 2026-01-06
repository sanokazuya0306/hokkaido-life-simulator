#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
北海道の詳細データ（年齢別死亡、産業別労働者）をダウンロードするスクリプト
"""

import requests
import os

def download_file(url, filename):
    """ファイルをダウンロード"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'data', filename)
    
    print(f"ダウンロード中: {filename}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ ダウンロード完了: {output_path}")
        return True
    except Exception as e:
        print(f"✗ エラー: {e}")
        return False

def main():
    """メイン処理"""
    
    print("=" * 80)
    print("北海道の詳細データをダウンロード")
    print("=" * 80)
    
    downloads = [
        # 人口動態調査 2023年 保管統計表 死亡 年齢別死亡（都道府県別）
        # 表5-10 年齢（5歳階級）・都道府県（21大都市再掲）別死亡数
        {
            'url': 'https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040208806&fileKind=0',
            'filename': 'death_by_age_prefecture_2023.xlsx'
        },
        
        # 国勢調査 2020年 産業別就業者数（都道府県別）
        # 表12 産業（大分類），従業上の地位（7区分），男女別15歳以上就業者数
        {
            'url': 'https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032142399&fileKind=0',
            'filename': 'workers_by_industry_2020.xlsx'
        }
    ]
    
    print("\n【ダウンロード対象】")
    print("1. 年齢別死亡者数（2023年、都道府県別）")
    print("2. 産業別就業者数（2020年国勢調査、都道府県別）")
    print()
    
    success_count = 0
    for item in downloads:
        if download_file(item['url'], item['filename']):
            success_count += 1
        print()
    
    print("=" * 80)
    print(f"完了: {success_count}/{len(downloads)} ファイル")
    print("=" * 80)

if __name__ == '__main__':
    main()

