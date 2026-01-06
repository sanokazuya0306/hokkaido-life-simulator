# 🚀 クイックスタートガイド

北海道人生シミュレーターのWebアプリを今すぐ起動する方法です。

## 最速で起動する方法

### macOS / Linux

```bash
./start.sh
```

### Windows

```bash
pip install -r requirements.txt
streamlit run app.py
```

それだけです！ブラウザが自動的に開き、アプリが起動します。

## 手動で起動する場合

### ステップ1: ライブラリのインストール

```bash
pip install -r requirements.txt
```

### ステップ2: アプリの起動

```bash
streamlit run app.py
```

### ステップ3: ブラウザでアクセス

ブラウザで以下のURLを開いてください：

```
http://localhost:8501
```

## トラブルシューティング

### エラー: `streamlit: command not found`

Streamlitがインストールされていません：

```bash
pip install streamlit
```

### エラー: データファイルが見つからない

`data/`フォルダに必要なCSVファイルがあることを確認してください。

必要なファイル：
- `birth_by_city.csv`
- `high_school_rate.csv`
- `university_rate.csv`
- `hokkaido_university_destinations.csv`
- `workers_by_industry.csv`
- `retirement_age.csv`
- `death_by_age.csv`
- `death_by_cause.csv`

### ポートが既に使用されている

別のポートで起動する場合：

```bash
streamlit run app.py --server.port=8502
```

## 使い方

1. **「人生を生成する」ボタンをクリック**
   - ランダムに人生が生成されます

2. **サイドバーで設定を変更**
   - 生成人数：1〜20人まで選択可能
   - シード値：再現性のある結果を得る場合にチェック

3. **詳細データを確認**
   - 各人生の「詳細データを見る」をクリックすると、統計情報が表示されます

4. **データセット情報を確認**
   - サイドバーの「データセット情報を表示」をチェックすると、使用している公式データの出典が表示されます

## 楽しみ方

- **何度も生成してみる**: 毎回異なる人生が生成されます
- **複数人を同時に生成**: 最大20人まで一度に生成できます
- **データセットを確認**: どのような統計データを使用しているか確認できます
- **シード値を使う**: 同じシード値を使うと、同じ人生が再現されます（友達と同じ結果を共有できます）

---

詳しい使い方は `README_WEB.md` をご覧ください。

