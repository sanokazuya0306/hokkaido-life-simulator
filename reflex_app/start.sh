#!/bin/bash
# Reflex版 人生ガチャ起動スクリプト

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# 仮想環境があればアクティベート
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Reflexアプリを起動
echo "人生ガチャ (Reflex版) を起動中..."
reflex run
