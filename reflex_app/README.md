# 人生ガチャ - Reflex版

Streamlit版からReflexに移行したウェブアプリケーションです。
デザインの自由度が大幅に向上し、Figmaデザインに完全準拠しています。

## セットアップ

### 1. 仮想環境の作成（推奨）

```bash
cd reflex_app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt

# 親ディレクトリのcore/srcも必要
pip install -r ../requirements.txt
```

### 3. Reflexの初期化（初回のみ）

```bash
reflex init
```

### 4. アプリの起動

```bash
reflex run
```

または

```bash
./start.sh
```

ブラウザで `http://localhost:3000` にアクセスしてください。

## プロジェクト構造

```
reflex_app/
├── reflex_app/
│   ├── __init__.py
│   ├── state.py          # アプリ状態管理（GachaState）
│   ├── components/       # 再利用可能UIコンポーネント
│   │   ├── gacha_button.py
│   │   ├── rank_card.py
│   │   ├── region_selector.py
│   │   ├── detail_card.py
│   │   ├── slider.py
│   │   └── dialogs.py
│   ├── pages/            # ページコンポーネント
│   │   └── index.py      # メインページ（3画面切り替え）
│   └── reflex_app.py     # メインエントリ
├── assets/
│   └── style.css         # カスタムCSS
├── rxconfig.py           # Reflex設定
├── requirements.txt
└── README.md
```

## Streamlit版との違い

| 機能 | Streamlit版 | Reflex版 |
|------|------------|---------|
| デザイン自由度 | 制限あり | 完全自由 |
| CSS適用 | !important多用 | 直接適用 |
| 状態管理 | session_state | rx.State |
| パフォーマンス | 毎回全体再描画 | 差分更新 |
| ルーティング | 単一ページ | マルチページ対応 |

## 開発モード

```bash
# ホットリロード有効で起動
reflex run --frontend-port 3000 --backend-port 8000

# デバッグモード
reflex run --loglevel debug
```

## 本番デプロイ

```bash
# 本番ビルド
reflex export

# 出力ディレクトリ
ls .web/_static/
```

## 注意事項

- Python 3.8以上が必要です
- Node.js 18以上が必要です（Reflexが自動インストール）
- 初回起動時は依存関係のダウンロードに時間がかかります

## トラブルシューティング

### ポートが使用中の場合

```bash
reflex run --frontend-port 3001 --backend-port 8001
```

### キャッシュクリア

```bash
rm -rf .web
reflex run
```

### 依存関係の問題

```bash
pip install --upgrade reflex
reflex init --force
```
