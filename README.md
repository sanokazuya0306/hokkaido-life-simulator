# 北海道人生シミュレーター

北海道庁が公開している公式統計データを使って、ランダムに人生の軌跡を生成するプログラムです。

## 📊 使用データ

すべて北海道庁が公開している最新の公式統計データを使用しています：

1. **市町村別出生数** (188市町村) - 2024年
2. **市町村別高校進学率** (178市町村) - 2024年度
3. **市町村別大学進学率** (125市町村) - 2024年度
4. **大学進学先都道府県** (48都道府県) - 2024年度
5. **産業別労働者数** (18産業) - 2024年
6. **年齢別死亡者数** (0-99歳) - 2022年
7. **死因別死亡者数** (10種類) - 2022年

## 🚀 セットアップ

### 1. 必要なライブラリのインストール

```bash
pip install -r requirements.txt
```

### 2. 使用方法

#### 🌐 Webアプリ版（推奨）

**シンプル版:**
```bash
./start.sh
# または
streamlit run app.py
```

**拡張版（統計分析・グラフ表示機能付き）:**
```bash
./start_advanced.sh
# または
streamlit run app_advanced.py
```

詳しくは [`README_WEB.md`](README_WEB.md) または [`QUICKSTART.md`](QUICKSTART.md) をご覧ください。

#### 💻 コマンドライン版

```bash
# 1人の人生を生成
python hokkaido_life_simulator.py

# 複数人を生成
python hokkaido_life_simulator.py -n 10

# 再現性のある結果（シード指定）
python hokkaido_life_simulator.py --seed 42
```

## 📂 プロジェクト構造

```
hokkaido_life_simulator/
├── hokkaido_life_simulator.py  # メインプログラム
├── requirements.txt             # 必要なライブラリ
├── README.md                    # このファイル
├── data/                        # データファイル
│   ├── birth_by_city.csv
│   ├── high_school_rate.csv
│   ├── university_rate.csv
│   ├── hokkaido_university_destinations.csv
│   ├── workers_by_industry.csv
│   ├── death_by_age.csv
│   ├── death_by_cause.csv
│   ├── *.xlsx                   # 元データ（Excel）
│   └── raw/                     # 生データ
├── scripts/                     # データ取得・変換スクリプト
│   ├── extract_*.py             # データ抽出スクリプト
│   ├── download_*.py            # データダウンロードスクリプト
│   └── update_*.py              # データ更新スクリプト
└── docs/                        # ドキュメント
    └── DATA_STATUS.md           # データ取得状況
```

## 💡 出力例

```
=== 人生 #1 ===
白石区で生まれる
高校に進学
神奈川県の大学に進学
大学進学後に宿泊業・飲食サービス業に就職
90歳で心疾患により死亡

================================================================================
【参照データセット】
================================================================================

1. 市町村別出生数 (188市町村)
  正式名称: 市区町村別人口、人口動態及び世帯数（令和6年）
  提供元: 北海道総合政策部地域行政局市町村課
  データ年: 2024年

2. 市町村別高校進学率 (178市町村)
  正式名称: 学校基本調査 中学校卒業後の進路別卒業者数（令和6年度）
  提供元: 北海道教育委員会
  データ年: 2024年度

... (以下略)
```

## 📖 データセット詳細

### 1. 市町村別出生数
- **正式名称**: 市区町村別人口、人口動態及び世帯数（令和6年）
- **提供元**: 北海道総合政策部地域行政局市町村課
- **URL**: https://www.pref.hokkaido.lg.jp/ss/tuk/900brr/index2.html

### 2. 市町村別高校進学率
- **正式名称**: 学校基本調査 中学校卒業後の進路別卒業者数（令和6年度）
- **提供元**: 北海道教育委員会
- **URL**: https://www.pref.hokkaido.lg.jp/ks/gsk/27334.html

### 3. 市町村別大学進学率
- **正式名称**: 学校基本調査 高等学校卒業後の進路別卒業者数（令和6年度）
- **提供元**: 北海道教育委員会
- **URL**: https://www.pref.hokkaido.lg.jp/ks/gsk/27334.html

### 4. 大学進学先都道府県
- **正式名称**: 学校基本調査 大学・短期大学への都道府県別入学者数（令和6年度）
- **提供元**: 北海道教育委員会
- **URL**: https://www.pref.hokkaido.lg.jp/ks/gsk/27334.html

### 5. 産業別労働者数
- **正式名称**: 労働力調査 第2表 産業別就業者数・雇用者数（令和6年平均）
- **提供元**: 北海道総合政策部計画局統計課
- **URL**: https://www.pref.hokkaido.lg.jp/ss/tuk/030lfs/212917.html

### 6. 年齢別死亡者数
- **正式名称**: 北海道保健統計年報 第24表 死亡数（令和4年）
- **提供元**: 北海道保健福祉部総務課
- **URL**: https://www.pref.hokkaido.lg.jp/hf/sum/hoso/hotou/hotou01/197226.html

### 7. 死因別死亡者数
- **正式名称**: 北海道保健統計年報 表3 死亡数・死亡率（令和4年）
- **提供元**: 北海道保健福祉部総務課
- **URL**: https://www.pref.hokkaido.lg.jp/hf/sum/hoso/hotou/hotou01/197226.html

## 🛠 データの更新

最新データを取得する場合は、`scripts/` ディレクトリ内のスクリプトを使用してください：

```bash
# データのダウンロード
python scripts/download_hokkaido_data.py

# データの抽出
python scripts/extract_birth_data_v2.py
python scripts/extract_advancement_rates.py
python scripts/extract_death_by_age.py
python scripts/extract_death_cause.py
python scripts/extract_industry_data_v2.py
```

## 📝 ライセンス

このプロジェクトで使用しているデータは、北海道庁が公開している公式統計データです。
各データの利用規約については、それぞれの提供元をご確認ください。

## 🤝 貢献

バグ報告や機能追加の提案は Issue でお知らせください。
