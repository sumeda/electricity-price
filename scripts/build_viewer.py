import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FUEL_DATA_PATH = ROOT / "data/special-high-voltage-series.json"
MARKET_DATA_PATH = ROOT / "data/jepx-spot-monthly.json"
INDEX_PATH = ROOT / "index.html"


def compact_json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def replace_const(html, name, value):
    pattern = rf"const {name}=.*?;\n"
    replacement = f"const {name}={compact_json(value)};\n"
    html, count = re.subn(pattern, replacement, html, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Could not replace JavaScript constant: {name}")
    return html


def main():
    fuel = json.loads(FUEL_DATA_PATH.read_text(encoding="utf-8"))
    market = json.loads(MARKET_DATA_PATH.read_text(encoding="utf-8"))

    fuel_payload = {
        "label": "燃料費等調整単価",
        "unit": fuel["unit"],
        "months": fuel["months"],
        "names": fuel["companies"],
        "series": fuel["series"],
    }
    market_payload = {
        "label": market["name"],
        "unit": market["unit"],
        "months": market["months"],
        "names": market["areas"],
        "series": market["series"],
        "aggregation": market["aggregation"],
        "rowCounts": market["month_row_counts"],
    }

    html = INDEX_PATH.read_text(encoding="utf-8")
    html = replace_const(html, "FUEL", fuel_payload)
    html = replace_const(html, "MARKET", market_payload)
    INDEX_PATH.write_text(html, encoding="utf-8")
    print(INDEX_PATH)


if __name__ == "__main__":
    main()
