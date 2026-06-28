import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FUEL_DATA_PATH = ROOT / "data/special-high-voltage-series.json"
MARKET_DATA_PATH = ROOT / "data/jepx-spot-monthly.json"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def validate_aligned_series(names, months, series, label):
    require(isinstance(months, list) and months, f"{label}: months is empty")
    require(isinstance(names, list) and names, f"{label}: names is empty")
    for name in names:
        require(name in series, f"{label}: missing series for {name}")
        require(
            len(series[name]) == len(months),
            f"{label}: {name} has {len(series[name])} values for {len(months)} months",
        )
        for value in series[name]:
            require(value is None or isinstance(value, (int, float)), f"{label}: invalid value {value!r}")


def main():
    fuel = json.loads(FUEL_DATA_PATH.read_text(encoding="utf-8"))
    market = json.loads(MARKET_DATA_PATH.read_text(encoding="utf-8"))

    validate_aligned_series(
        fuel["companies"],
        fuel["months"],
        fuel["series"],
        "fuel",
    )
    validate_aligned_series(
        market["areas"],
        market["months"],
        market["series"],
        "market",
    )

    for company in fuel["companies"]:
        require(company in fuel["latest"], f"fuel: missing latest for {company}")

    print("data ok")


if __name__ == "__main__":
    main()
