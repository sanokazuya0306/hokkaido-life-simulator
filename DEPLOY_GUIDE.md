# 🌐 オンラインデプロイガイド

このアプリをインターネット上で公開する方法を説明します。

---

## 🚀 方法1: Streamlit Cloud（最も簡単・無料）

### ⭐ おすすめポイント
- ✅ 完全無料
- ✅ 5分で公開可能
- ✅ GitHubと連携するだけ
- ✅ 自動デプロイ（コードを更新すると自動反映）
- ✅ SSL証明書込み（https://）

### 📋 手順

#### ステップ1: GitHubにリポジトリを作成

1. [GitHub](https://github.com)にログイン（アカウントがない場合は作成）

2. 新しいリポジトリを作成
   - リポジトリ名: `hokkaido-life-simulator`
   - Public（公開）を選択
   - READMEは追加しない

3. ローカルのプロジェクトをGitHubにプッシュ

```bash
cd "/Users/sanokazuya/Documents/Obsidian 1st/hokkaido_life_simulator"

# Gitの初期化（まだの場合）
git init

# .gitignoreを確認（既にあります）
# 不要なファイルを除外

# すべてのファイルを追加
git add .

# コミット
git commit -m "Initial commit: Hokkaido Life Simulator Web App"

# GitHubリポジトリを追加（URLは自分のものに変更）
git remote add origin https://github.com/YOUR_USERNAME/hokkaido-life-simulator.git

# プッシュ
git branch -M main
git push -u origin main
```

#### ステップ2: Streamlit Cloudでデプロイ

1. [Streamlit Cloud](https://streamlit.io/cloud)にアクセス

2. GitHubアカウントでサインイン

3. 「New app」をクリック

4. 設定を入力：
   - **Repository**: `YOUR_USERNAME/hokkaido-life-simulator`
   - **Branch**: `main`
   - **Main file path**: 
     - シンプル版: `app.py`
     - 拡張版: `app_advanced.py`

5. 「Deploy!」をクリック

6. 数分待つと公開完了！

### 🎉 完成！

以下のようなURLでアクセス可能：
```
https://YOUR_APP_NAME.streamlit.app
```

このURLを友達や同僚にシェアできます！

---

## 🔧 方法2: Heroku（スケーラブル）

### 特徴
- ✅ 無料プランあり（制限あり）
- ✅ カスタムドメイン対応
- ✅ より多くのトラフィックに対応

### 📋 手順

#### ステップ1: Herokuアカウントを作成

1. [Heroku](https://www.heroku.com)でアカウント作成
2. [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)をインストール

#### ステップ2: デプロイ

```bash
cd "/Users/sanokazuya/Documents/Obsidian 1st/hokkaido_life_simulator"

# Herokuにログイン
heroku login

# アプリを作成
heroku create hokkaido-life-simulator

# 環境変数を設定（必要に応じて）
heroku config:set STREAMLIT_SERVER_PORT=8501

# デプロイ
git push heroku main

# アプリを開く
heroku open
```

**注意**: `Procfile`と`setup.sh`は既に用意されています！

---

## 🐳 方法3: Docker + クラウド

### 特徴
- ✅ 完全なコントロール
- ✅ どのクラウドでも動作
- ✅ スケーリング可能

### Dockerfile作成

既にプロジェクトに含まれている場合はスキップ。なければ作成：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

### デプロイ先の選択肢

1. **Google Cloud Run**
   ```bash
   gcloud run deploy hokkaido-life-simulator \
     --source . \
     --platform managed \
     --region asia-northeast1
   ```

2. **AWS ECS**
3. **Azure Container Instances**
4. **DigitalOcean App Platform**

---

## 📱 方法4: Vercel（フロントエンド特化）

### 特徴
- ✅ 無料プランあり
- ✅ 高速CDN
- ✅ 簡単デプロイ

**注意**: StreamlitはPythonバックエンドなので、Vercelでは追加設定が必要です。

---

## 🎯 推奨デプロイ方法の比較

| 方法 | 難易度 | コスト | おすすめ用途 |
|-----|-------|-------|------------|
| **Streamlit Cloud** | ⭐ 簡単 | 無料 | 個人プロジェクト、デモ |
| **Heroku** | ⭐⭐ 普通 | 無料〜 | 中規模アプリ |
| **Docker + Cloud** | ⭐⭐⭐ 難しい | 従量課金 | 本格運用 |

### 🎯 結論

**初めての方 → Streamlit Cloud**がおすすめ！
- 5分で公開可能
- 完全無料
- 自動更新

---

## 🔒 セキュリティと注意点

### データについて

✅ **問題なし**: 
- すべて公開統計データ
- 個人情報は含まれていません
- ランダム生成のみ

### アクセス制限

もし限定公開したい場合：

1. **Streamlit Cloud**:
   - プライベートリポジトリを使用
   - 認証機能を追加（`streamlit-authenticator`）

2. **Heroku**:
   - Basic認証を追加
   - OAuth統合

---

## 📊 デプロイ後の確認事項

### ✅ チェックリスト

- [ ] アプリが正常に起動する
- [ ] データファイルが正しく読み込まれる
- [ ] 人生生成が動作する
- [ ] グラフが表示される（拡張版）
- [ ] モバイルで表示確認
- [ ] URLを共有してアクセス確認

### 🐛 よくある問題

#### 問題1: データファイルが読み込めない

**解決策**: 
- `data/`ディレクトリが`.gitignore`に含まれていないか確認
- GitHubに`data/`フォルダがプッシュされているか確認

#### 問題2: メモリ不足エラー

**解決策**:
- 大量生成の上限を下げる
- 拡張版の場合、表示件数を制限

#### 問題3: ライブラリのインポートエラー

**解決策**:
- `requirements.txt`が最新か確認
- バージョン指定を追加

---

## 🎨 カスタムドメインの設定

### Streamlit Cloud

無料プランでは不可。独自ドメインを使いたい場合はHerokuやCloudflareを利用。

### Heroku + Cloudflare

1. Cloudflareでドメインを管理
2. HerokuアプリのDNSを設定
3. SSL証明書を設定

---

## 📈 アクセス解析

### Google Analytics統合

`app.py`に以下を追加：

```python
# Google Analytics
st.markdown("""
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", unsafe_allow_html=True)
```

---

## 🔄 更新方法

### Streamlit Cloudの場合

```bash
# コードを編集
git add .
git commit -m "Update features"
git push origin main
```

→ 自動的に再デプロイされます！

### Herokuの場合

```bash
git push heroku main
```

---

## 💡 Tips

### パフォーマンス最適化

1. **キャッシングを活用**
   ```python
   @st.cache_resource
   def load_data():
       # データ読み込み
   ```

2. **セッション状態の活用**
   - 不要な再計算を避ける

3. **画像の最適化**
   - グラフのサイズを制限

### SEO対策

`app.py`に追加：

```python
st.set_page_config(
    page_title="北海道人生シミュレーター",
    page_icon="🌏",
    menu_items={
        'About': "北海道庁の公式統計データを使った人生シミュレーター"
    }
)
```

---

## 🎊 公開後のシェア

### SNSでシェア

デプロイ後、以下のようにシェアできます：

**Twitter/X**:
```
🌏 北海道人生シミュレーター
北海道庁の公式統計データで、ランダムに人生を体験！
https://your-app.streamlit.app
#北海道 #データサイエンス #統計
```

**README.md**:
```markdown
## 🌐 オンラインデモ

https://your-app.streamlit.app
```

---

## 🆘 サポート

デプロイで問題が発生した場合：

1. **Streamlit Cloudのログを確認**
2. **GitHubのActionsタブを確認**
3. **コミュニティフォーラムで質問**
   - [Streamlit Community](https://discuss.streamlit.io/)

---

## 📚 参考リンク

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Heroku Python Support](https://devcenter.heroku.com/articles/python-support)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**さあ、世界中の人に使ってもらいましょう！** 🌟

