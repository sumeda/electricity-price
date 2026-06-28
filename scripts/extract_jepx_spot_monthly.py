import csv
import json
import urllib.request
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SOURCE_DIR = ROOT / "work/sources"
OUT_JSON = DATA_DIR / "jepx-spot-monthly.json"
OUT_CSV = DATA_DIR / "jepx-spot-monthly.csv"

START_MONTH = "2024-03"
END_MONTH = "2026-06"
YEARS = [2023, 2024, 2025, 2026]

AREAS = [
    ("九州", 14),
    ("東北", 7),
    ("東京", 8),
    ("関西", 11),
    ("中部", 9),
    ("四国", 13),
]


def month_range(start, end):
    year, month = map(int, start.split("-"))
    end_year, end_month = map(int, end.split("-"))
    while (year, month) <= (end_year, end_month):
        yield f"{year:04d}-{month:02d}"
        month += 1
        if month == 13:
            year += 1
            month = 1


def fetch_csv(year):
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    path = SOURCE_DIR / f"jepx-spot-summary-{year}.csv"
    url = (
        "https://www.jepx.jp/js/csv_read.php"
        f"?dir=spot_summary&file=spot_summary_{year}.csv"
    )
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.jepx.jp/electricpower/market-data/spot/",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()
    if not data:
        raise RuntimeError(f"JEPX CSV is empty: {url}")
    path.write_bytes(data)
    return path


def parse_float(value):
    value = value.strip().replace(",", "")
    if not value:
        return None
    return float(value)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    files = [fetch_csv(year) for year in YEARS]
    totals = defaultdict(float)
    counts = defaultdict(int)
    row_counts = defaultdict(int)

    for path in files:
        rows = csv.reader(path.read_text(encoding="utf-8-sig").splitlines())
        next(rows, None)
        for row in rows:
            if len(row) < 15 or not row[0]:
                continue
            try:
                date = datetime.strptime(row[0], "%Y/%m/%d")
            except ValueError:
                continue
            month = date.strftime("%Y-%m")
            if not (START_MONTH <= month <= END_MONTH):
                continue
            row_counts[month] += 1
            for area, index in AREAS:
                value = parse_float(row[index])
                if value is None:
                    continue
                key = (area, month)
                totals[key] += value
                counts[key] += 1

    months = list(month_range(START_MONTH, END_MONTH))
    areas = [area for area, _ in AREAS]
    series = {}

    for area in areas:
        values = []
        for month in months:
            key = (area, month)
            value = round(totals[key] / counts[key], 2) if counts[key] else None
            values.append(value)
        series[area] = values

    payload = {
        "name": "JEPXスポット市場 月平均価格",
        "unit": "円/kWh",
        "aggregation": "30分ごとのエリアプライスを月別に単純平均",
        "source": "https://www.jepx.jp/electricpower/market-data/spot/",
        "source_files": [path.name for path in files],
        "months": months,
        "areas": areas,
        "series": series,
        "month_row_counts": {month: row_counts[month] for month in months},
    }

    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["area", "month", "monthly_average_yen_per_kwh", "sample_count"])
        for area in areas:
            for month, value in zip(months, series[area]):
                writer.writerow([area, month, value, counts[(area, month)]])

    print(OUT_JSON)
    print(OUT_CSV)


if __name__ == "__main__":
    main()
