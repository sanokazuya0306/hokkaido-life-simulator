#!/bin/bash

# Personal Access Tokenを使ったデプロイ

echo "🔐 Personal Access Tokenを使ったGitHubアップロード"
echo "===================================================="
echo ""
echo "⚠️  Personal Access Tokenを準備してください"
echo ""
echo "1. https://github.com/settings/tokens にアクセス"
echo "2. 「Generate new token (classic)」をクリック"
echo "3. Note: hokkaido-simulator"
echo "4. Expiration: 90 days"
echo "5. Scopes: repo にチェック"
echo "6. 「Generate token」をクリック"
echo "7. トークンをコピー（ghp_xxxxx...）"
echo ""
read -p "トークンを作成しましたか？ (y/n): " answer

if [ "$answer" != "y" ]; then
    echo "トークンを作成してから再度実行してください"
    exit 1
fi

echo ""
read -p "Personal Access Token (ghp_xxxxx...): " TOKEN

if [ -z "$TOKEN" ]; then
    echo "❌ トークンが入力されていません"
    exit 1
fi

echo ""
echo "📦 ファイルを追加中..."
git add .

echo "💾 コミット中..."
git commit -m "Initial commit: Hokkaido Life Simulator Web App"

echo "🔗 GitHubリポジトリに接続中..."
# 既存のremoteを削除（もしあれば）
git remote remove origin 2>/dev/null

# トークンを使ったURLでremoteを設定
git remote add origin https://${TOKEN}@github.com/sanokazuya0306/hokkaido-life-simulator.git

echo "📤 GitHubにアップロード中..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "===================================================="
    echo "✅ アップロード完了！"
    echo ""
    echo "GitHubリポジトリ:"
    echo "https://github.com/sanokazuya0306/hokkaido-life-simulator"
    echo ""
    echo "次のステップ:"
    echo "1. https://streamlit.io/cloud にアクセス"
    echo "2. GitHubアカウントでサインイン"
    echo "3. 「New app」をクリック"
    echo "4. Repository: sanokazuya0306/hokkaido-life-simulator"
    echo "5. Main file path: app.py"
    echo "6. 「Deploy!」をクリック"
    echo ""
else
    echo ""
    echo "❌ アップロードに失敗しました"
    echo "トークンが正しいか確認してください"
fi

