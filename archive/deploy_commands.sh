#!/bin/bash

# sanokazuya0306さん用のデプロイコマンド

echo "🚀 GitHubへアップロード開始"
echo "================================"
echo ""

# Gitの設定（まだの場合）
git config --global user.name "sanokazuya0306"
git config --global user.email "sanokazuya0306@users.noreply.github.com"

echo "📦 ファイルを追加中..."
git add .

echo "💾 コミット中..."
git commit -m "Initial commit: Hokkaido Life Simulator Web App"

echo "🔗 GitHubリポジトリに接続中..."
git remote add origin https://github.com/sanokazuya0306/hokkaido-life-simulator.git

echo "📤 GitHubにアップロード中..."
git branch -M main
git push -u origin main

echo ""
echo "================================"
echo "✅ アップロード完了！"
echo ""
echo "次のステップ:"
echo "1. https://streamlit.io/cloud にアクセス"
echo "2. GitHubアカウントでサインイン"
echo "3. 「New app」をクリック"
echo "4. Repository: sanokazuya0306/hokkaido-life-simulator を選択"
echo "5. Main file path: app.py を選択"
echo "6. 「Deploy!」をクリック"
echo ""
echo "公開URL（例）:"
echo "https://hokkaido-life-simulator.streamlit.app"
echo ""

