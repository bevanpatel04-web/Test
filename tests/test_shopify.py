import csv
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "shopify"


def rows():
    with (ROOT / "products.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_every_variant_keeps_15_dollars_before_ads():
    for r in rows():
        price, cost = float(r["Variant Price"]), float(r["Cost per item"])
        profit = price - cost - (price * 0.029 + 0.30) - price * 0.05
        assert profit >= 15, (r["Variant SKU"], round(profit, 2))
        assert float(r["Variant Compare At Price"]) > price


def test_five_products_with_unique_skus():
    rs = rows()
    assert len({r["Handle"] for r in rs}) == 5
    assert len({r["Variant SKU"] for r in rs}) == len(rs)


def test_homepage_gift_tiles_point_at_real_products():
    handles = {r["Handle"] for r in rows()}
    index = json.loads((ROOT / "theme/templates/index.json").read_text())
    tiles = index["sections"]["gifts"]["blocks"].values()
    assert all(t["settings"]["product"] in handles for t in tiles)


def test_theme_zip_is_current():
    with zipfile.ZipFile(ROOT / "snug-hearth-theme.zip") as z:
        names = set(z.namelist())
        assert "layout/theme.liquid" in names and "config/settings_schema.json" in names
        for path in (ROOT / "theme").rglob("*"):
            if path.is_file():
                rel = path.relative_to(ROOT / "theme").as_posix()
                assert z.read(rel) == path.read_bytes(), f"{rel} changed: rebuild the zip"
