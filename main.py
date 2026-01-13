#!/usr/bin/env python3
"""
北海道人生シミュレーター CLI

北海道の公開データを使ってランダムに人生の軌跡を生成する
"""

import random
import argparse

from src import HokkaidoLifeSimulator


def main():
    parser = argparse.ArgumentParser(description="北海道のデータを使ってランダムに人生の軌跡を生成")
    parser.add_argument(
        "-n", "--number", type=int, default=1,
        help="生成する人数（デフォルト: 1）"
    )
    parser.add_argument(
        "-d", "--data-dir", type=str, default=None,
        help="データファイルが格納されているディレクトリ（デフォルト: スクリプトと同じディレクトリのdataフォルダ）"
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="乱数のシード値（再現性のため）"
    )
    parser.add_argument(
        "--show-datasets", action="store_true",
        help="使用したデータセット情報を表示"
    )
    parser.add_argument(
        "--no-score", action="store_true",
        help="人生スコアを非表示にする"
    )
    parser.add_argument(
        "--simple", action="store_true",
        help="スコアの詳細な根拠を省略して簡潔に表示"
    )
    parser.add_argument(
        "--no-sns", action="store_true",
        help="SNS反応を非表示にする"
    )
    # 後方互換性のため残す（非推奨）
    parser.add_argument(
        "-s", "--score", action="store_true",
        help=argparse.SUPPRESS  # ヘルプには表示しない
    )
    parser.add_argument(
        "--score-simple", action="store_true",
        help=argparse.SUPPRESS  # ヘルプには表示しない
    )
    
    args = parser.parse_args()
    
    if args.seed is not None:
        random.seed(args.seed)
    
    simulator = HokkaidoLifeSimulator(data_dir=args.data_dir)
    
    # スコア表示の設定（デフォルトで表示）
    show_score = not args.no_score
    verbose_score = not args.simple and not args.score_simple
    show_sns = not args.no_sns
    
    for i in range(args.number):
        life = simulator.generate_life()
        print(f"=== 人生 #{i+1} ===")
        print(simulator.format_life(life, show_score=show_score, verbose_score=verbose_score, show_sns=show_sns))
        print()
    
    # デフォルトで使用したデータセット情報を表示
    if args.number > 0:
        print(simulator.get_dataset_info())


if __name__ == "__main__":
    main()
