#!/usr/bin/env python3
"""
北海道の実際の統計データを取得するためのヘルパースクリプト

このスクリプトは、e-Stat APIや公開データから実際の統計データを取得します。
"""

import os
import sys
import csv
import json
import requests
from pathlib import Path
from urllib.parse import urlencode


class HokkaidoDataFetcher:
    def __init__(self, data_dir=None, api_key=None):
        """
        初期化
        
        Args:
            data_dir: データを保存するディレクトリ
            api_key: e-Stat APIキー（オプション）
        """
        if data_dir is None:
            script_dir = Path(__file__).parent
            self.data_dir = script_dir / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.api_key = api_key or os.getenv("ESTAT_API_KEY")
    
    def print_data_sources(self):
        """データ取得元の情報を表示"""
        print("=" * 60)
        print("北海道の統計データ取得元")
        print("=" * 60)
        print()
        
        print("1. 出生数データ")
        print("   - e-Stat: https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00450011&tstat=000001028897&cycle=7&year=20230&month=0&tclass1=000001053058&tclass2=000001053061")
        print("   - 厚生労働省 人口動態調査: https://www.mhlw.go.jp/toukei/list/81-1.html")
        print()
        
        print("2. 高校進学率・大学進学率")
        print("   - 文部科学省 学校基本調査: https://www.mext.go.jp/b_menu/toukei/chousa01/kihon/kekka/k_detail/1426730.htm")
        print("   - 北海道教育委員会: https://www.dokyoi.pref.hokkaido.lg.jp/hk/gky/gks/")
        print()
        
        print("3. 産業別労働者数")
        print("   - e-Stat 国勢調査: https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00200521&tstat=000001136464&cycle=0&tclass1=000001136466")
        print("   - 総務省統計局: https://www.stat.go.jp/data/kokusei/2015/kekka.html")
        print()
        
        print("4. 年齢別死亡者数")
        print("   - 厚生労働省 人口動態調査: https://www.mhlw.go.jp/toukei/list/81-1.html")
        print("   - e-Stat: https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00450011&tstat=000001028897")
        print()
        
        print("=" * 60)
        print("データ取得方法")
        print("=" * 60)
        print()
        print("方法1: 手動でダウンロード")
        print("  1. 上記のURLからデータをダウンロード")
        print("  2. CSVまたはExcel形式で保存")
        print("  3. convert_downloaded_data.py を使用して変換")
        print()
        
        if self.api_key:
            print("方法2: e-Stat APIを使用（APIキーが設定されています）")
            print("  e-Stat APIキーを使用してデータを取得できます")
        else:
            print("方法2: e-Stat APIを使用")
            print("  1. https://www.e-stat.go.jp/api/ でAPIキーを取得")
            print("  2. 環境変数 ESTAT_API_KEY に設定するか、--api-key オプションで指定")
        print()
    
    def fetch_from_estat(self, stats_id, params):
        """
        e-Stat APIからデータを取得
        
        Args:
            stats_id: 統計表ID
            params: APIパラメータの辞書
        """
        if not self.api_key:
            print("エラー: e-Stat APIキーが設定されていません", file=sys.stderr)
            print("https://www.e-stat.go.jp/api/ でAPIキーを取得してください", file=sys.stderr)
            return None
        
        base_url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
        params["appId"] = self.api_key
        params["statsDataId"] = stats_id
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"エラー: データ取得に失敗しました: {e}", file=sys.stderr)
            return None
    
    def convert_estat_json_to_csv(self, json_data, output_file, city_column="市町村", value_column="値"):
        """
        e-Stat APIのJSONレスポンスをCSVに変換
        
        Args:
            json_data: e-Stat APIのJSONレスポンス
            output_file: 出力CSVファイルのパス
            city_column: 市町村列の名前
            value_column: 値列の名前
        """
        # e-Stat APIのレスポンス構造に応じて実装
        # 実際の構造は統計表によって異なるため、汎用的な変換は難しい
        print(f"注意: e-Stat APIのJSON形式は統計表によって異なります")
        print(f"手動でデータを確認し、適切に変換してください")
        
        # サンプル実装（実際の構造に応じて調整が必要）
        if "GET_STATS_DATA" in json_data:
            stats_data = json_data["GET_STATS_DATA"]
            # ここで実際のデータ構造に応じて変換処理を実装
            pass


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="北海道の統計データを取得")
    parser.add_argument(
        "--api-key", type=str, default=None,
        help="e-Stat APIキー（環境変数 ESTAT_API_KEY でも設定可能）"
    )
    parser.add_argument(
        "-d", "--data-dir", type=str, default=None,
        help="データを保存するディレクトリ"
    )
    parser.add_argument(
        "--sources", action="store_true",
        help="データ取得元の情報を表示"
    )
    
    args = parser.parse_args()
    
    fetcher = HokkaidoDataFetcher(data_dir=args.data_dir, api_key=args.api_key)
    
    if args.sources:
        fetcher.print_data_sources()
    else:
        print("データ取得元の情報を表示します...")
        print()
        fetcher.print_data_sources()
        print()
        print("実際のデータを取得するには:")
        print("  1. 上記のURLからデータをダウンロード")
        print("  2. convert_downloaded_data.py を使用してCSV形式に変換")
        print("  3. 変換したファイルを scripts/data/ に配置")


if __name__ == "__main__":
    main()

