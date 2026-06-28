# 電力価格ビューア 更新手順

このリポジトリは、以下を GitHub Pages で公開します。

- 特別高圧向け燃料費等調整単価
- JEPXスポット市場のエリア別月平均価格

公開URL:

`https://sumeda.github.io/electricity-price/`

## ファイル構成

- `index.html`: 公開ビューア
- `data/special-high-voltage-series.json`: 燃料費等調整単価データ
- `data/jepx-spot-monthly.json`: JEPXスポット市場の月平均価格データ
- `scripts/build_viewer.py`: `data/` から `index.html` を生成
- `scripts/extract_jepx_spot_monthly.py`: JEPX公式CSVから月平均価格を生成

## JEPXデータを更新する

```bash
python3 scripts/extract_jepx_spot_monthly.py
python3 scripts/build_viewer.py
```

JEPXのCSVは年度単位です。2024年3月は2023年度CSVに含まれるため、スクリプトでは2023〜2026年度分を取得します。

月平均は、30分ごとのエリアプライスを対象月ごとに単純平均しています。

## 燃料費等調整単価を更新する

燃料費等調整単価は各電力会社の公式ページ・公式PDFを確認し、`data/special-high-voltage-series.json` を更新します。

対象会社:

- 九州電力
- 東北電力
- 東京電力
- 関西電力
- 中部電力
- 四国電力

対象電圧:

- 特別高圧のみ

注意:

- 低圧・高圧の単価は混ぜない
- 欠損月は推測で補完しない
- 公式情報を優先する

データ更新後にビューアを再生成します。

```bash
python3 scripts/build_viewer.py
```

## 確認

生成後、`index.html` のJavaScript構文を確認します。

```bash
node -e "const fs=require('fs');const html=fs.readFileSync('index.html','utf8');new Function(html.match(/<script>([\\s\\S]*)<\\/script>/)[1]);console.log('ok')"
```

## 公開

変更したファイルをGitHubへコミットすると、GitHub Pagesに反映されます。

主な更新対象:

- `index.html`
- `data/special-high-voltage-series.json`
- `data/jepx-spot-monthly.json`
- 必要に応じて `data/summary.json`
