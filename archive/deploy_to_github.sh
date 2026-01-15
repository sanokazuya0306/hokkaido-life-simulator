#!/bin/bash

# GitHubへのデプロイスクリプト

echo "🚀 北海道人生シミュレーター - GitHubデプロイ準備"
echo "=================================================="
echo ""

# 現在のディレクトリ確認
if [ ! -f "app.py" ]; then
    echo "❌ エラー: プロジェクトディレクトリで実行してください"
    exit 1
fi

echo "📁 プロジェクトディレクトリ: $(pwd)"
echo ""

# Gitが初期化されているか確認
if [ ! -d ".git" ]; then
    echo "📦 Gitリポジトリを初期化中..."
    git init
    echo "✅ Git初期化完了"
    echo ""
fi

# READMEの確認
if [ ! -f "README.md" ]; then
    echo "⚠️  警告: README.mdが見つかりません"
else
    echo "✅ README.md確認完了"
fi

# requirements.txtの確認
if [ ! -f "requirements.txt" ]; then
    echo "❌ エラー: requirements.txtが見つかりません"
    exit 1
else
    echo "✅ requirements.txt確認完了"
fi

# dataディレクトリの確認
if [ ! -d "data" ]; then
    echo "❌ エラー: dataディレクトリが見つかりません"
    exit 1
else
    echo "✅ dataディレクトリ確認完了"
fi

echo ""
echo "=================================================="
echo "📝 次のステップ:"
echo "=================================================="
echo ""
echo "1️⃣  GitHubで新しいリポジトリを作成"
echo "   👉 https://github.com/new"
echo "   - リポジトリ名: hokkaido-life-simulator"
echo "   - 公開設定: Public"
echo "   - READMEは追加しない"
echo ""
echo "2️⃣  以下のコマンドを実行（YOUR_USERNAMEを自分のものに変更）:"
echo ""
echo "   git add ."
echo "   git commit -m \"Initial commit: Hokkaido Life Simulator Web App\""
echo "   git remote add origin https://github.com/YOUR_USERNAME/hokkaido-life-simulator.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3️⃣  Streamlit Cloudでデプロイ"
echo "   👉 https://streamlit.io/cloud"
echo "   - GitHubアカウントでサインイン"
echo "   - 「New app」をクリック"
echo "   - リポジトリとapp.pyを選択"
echo "   - 「Deploy!」をクリック"
echo ""
echo "=================================================="
echo ""
echo "詳しくは DEPLOY_GUIDE.md をご覧ください"
echo ""

