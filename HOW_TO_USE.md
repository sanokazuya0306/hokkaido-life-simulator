# 🌐 Webで使う方法

## ステップ1: ターミナルを開く

macOSの場合：
1. Spotlight検索（Command + Space）を開く
2. 「ターミナル」と入力
3. Enterキーを押す

## ステップ2: プロジェクトディレクトリに移動

```bash
cd "/Users/sanokazuya/Documents/Obsidian 1st/hokkaido_life_simulator"
```

## ステップ3: Webアプリを起動

### オプションA: シンプル版（初心者向け）

```bash
./start.sh
```

または

```bash
python3 -m streamlit run app.py
```

### オプションB: 拡張版（データ分析向け）

```bash
./start_advanced.sh
```

または

```bash
python3 -m streamlit run app_advanced.py
```

## ステップ4: ブラウザでアクセス

自動的にブラウザが開きます。開かない場合は：

```
http://localhost:8501
```

をブラウザのアドレスバーに入力してください。

---

## 🎮 使い方

### 画面が開いたら

1. **「人生を生成する」ボタンをクリック**
   - ランダムに人生が生成されます

2. **サイドバーで設定を変更**（左側）
   - 生成人数：スライダーで調整
   - シード値：再現性のある結果を得たい場合にチェック

3. **詳細を確認**
   - 「詳細データを見る」をクリックすると統計情報が表示されます

### 拡張版を使う場合

4. **統計分析を確認**
   - 主要指標（進学率、平均寿命など）が表示されます

5. **グラフを確認**
   - 出生地分布
   - 産業分布（円グラフ）
   - 死因分布
   - 大学進学先分布
   - 年齢分布

---

## 🛑 停止方法

ターミナルで `Ctrl + C` を押すと停止します。

---

## 💡 便利な使い方

### スマホやタブレットで見る

同じWi-Fiに接続している場合：

1. ターミナルで起動後、表示されるIPアドレスを確認
2. スマホのブラウザで `http://[IPアドレス]:8501` を開く

### 別のポートで起動

ポート8501が使用中の場合：

```bash
python3 -m streamlit run app.py --server.port=8502
```

### 自動リロードを有効化（開発モード）

```bash
streamlit run app.py --server.runOnSave=true
```

---

## 🎯 シーン別の使い方

### 1回だけ試したい
```bash
./start.sh
```
→ ボタンを1回クリック → 終了

### データを分析したい
```bash
./start_advanced.sh
```
→ 生成人数を100に設定 → グラフタブを確認

### プレゼンテーションで使う
```bash
./start_advanced.sh
```
→ 大画面で表示 → グラフを見せながら説明

### 友達に見せたい
```bash
./start.sh
```
→ スマホでアクセスしてもらう

---

## ⚠️ トラブルシューティング

### エラー: `streamlit: command not found`

```bash
pip3 install streamlit
```

### エラー: `Address already in use`

別のポートで起動：
```bash
python3 -m streamlit run app.py --server.port=8502
```

### ブラウザが自動で開かない

手動でブラウザを開いて以下にアクセス：
```
http://localhost:8501
```

### データが表示されない

セットアップを確認：
```bash
python3 check_setup.py
```

---

## 🌟 もっと詳しく知りたい

- 全機能: `FEATURES.md`
- Webアプリ詳細: `README_WEB.md`
- プロジェクト概要: `SUMMARY.md`

