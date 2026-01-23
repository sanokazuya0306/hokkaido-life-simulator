# Reflex App デプロイガイド

このガイドでは、Reflexアプリをウォーターマークなしでデプロイする方法を説明します。

---

## オプション1: Railway（推奨）

**料金**: $5/月〜（使った分だけ）
**メリット**: 簡単、ウォーターマークなし、カスタムドメイン対応

### 手順

1. **Railwayアカウント作成**
   - https://railway.app/ にアクセス
   - GitHubアカウントでサインアップ

2. **新規プロジェクト作成**
   - Dashboard → New Project → Deploy from GitHub repo
   - このリポジトリを選択

3. **環境変数設定**（Railwayダッシュボードで）
   ```
   PYTHON_VERSION=3.11
   PORT=8080
   ```

4. **デプロイ**
   - Railwayが自動的にビルド・デプロイを開始
   - 数分待つとURLが発行される

5. **カスタムドメイン（オプション）**
   - Settings → Domains → Add Custom Domain
   - DNSの設定を行う

---

## オプション2: Render

**料金**: $7/月〜
**メリット**: シンプル、安定

### 手順

1. **Renderアカウント作成**
   - https://render.com/ にアクセス

2. **新規Web Service作成**
   - Dashboard → New → Web Service
   - GitHubリポジトリを接続

3. **設定**
   ```
   Environment: Docker
   Instance Type: Starter ($7/month)
   ```

4. **デプロイ**
   - Create Web Serviceをクリック

---

## オプション3: DigitalOcean App Platform

**料金**: $5/月〜
**メリット**: 柔軟、スケーラブル

### 手順

1. **DigitalOceanアカウント作成**
   - https://www.digitalocean.com/

2. **App Platform → Create App**
   - Source: GitHub
   - このリポジトリを選択

3. **設定**
   - Type: Web Service
   - Dockerfile: 使用する
   - Plan: Basic ($5/month)

---

## オプション4: Reflex Cloud Enterprise

**料金**: 要問い合わせ（営業連絡必要）
**メリット**: 公式サポート、最も簡単

### 手順

1. https://reflex.dev/pricing/ にアクセス
2. デモ予約フォームに記入
3. 営業からの連絡を待つ

---

## トラブルシューティング

### ビルドが失敗する場合

```bash
# ローカルでDockerビルドをテスト
docker build -t reflex-app .
docker run -p 8080:8080 reflex-app
```

### データが読み込めない場合

`data/` ディレクトリがDockerイメージに含まれているか確認：
```dockerfile
COPY data/ /app/data/
```

### WebSocket接続エラー

環境変数 `API_URL` を正しく設定：
```
API_URL=https://your-app.railway.app
```

---

## 料金比較

| サービス | 月額 | ウォーターマーク | カスタムドメイン | 難易度 |
|---------|------|----------------|----------------|--------|
| Railway | $5〜 | なし | ○ | 簡単 |
| Render | $7〜 | なし | ○ | 簡単 |
| DigitalOcean | $5〜 | なし | ○ | 普通 |
| Reflex Cloud (Hobby) | 無料 | あり | × | 最も簡単 |
| Reflex Cloud (Enterprise) | 要問合せ | なし | ○ | 最も簡単 |

---

## 推奨

**コスト重視**: Railway ($5/月〜)
**安定性重視**: Render ($7/月〜)
**サポート重視**: Reflex Cloud Enterprise（要問い合わせ）
