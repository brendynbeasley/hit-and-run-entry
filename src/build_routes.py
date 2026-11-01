"""Collapse the DOT airline ticket sample (DB1B Market, 2014-2024) into small route tables.

DB1B is a 10% sample of every domestic airline ticket, published quarterly by the Bureau of
Transportation Statistics. Each quarterly zip is about 100 MB (1.9 GB unzipped), so the 44 raw files
are fetched into data/raw/db1b/ if they are not already there and are ignored by git. This script
reads only the columns it needs, applies the ticket filters below, and writes one compact table,
data/derived/pair_carrier_year.csv.gz (airport pair x ticketing airline x year: sampled passengers,
fare revenue, nonstop passengers and distance), which src/contestability.py reads.

Airport pairs are non-directional (ATL-BOS and BOS-ATL are one market). Passenger counts are the
sample counts (multiply by ten for the population).

Usage (from the repository root):
    python src/build_routes.py                       # all years, fetching any missing zip
    python src/build_routes.py --raw-dir path/to/zips --workers 3
"""

import argparse
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.csv as pv
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "db1b"
OUT = ROOT / "data" / "derived"
URL = "https://transtats.bts.gov/PREZIP/Origin_and_Destination_Survey_DB1BMarket_{y}_{q}.zip"

YEARS = range(2014, 2025)
FARE_MIN, FARE_MAX = 25.0, 2500.0  # one-direction fare bounds; below are award/employee tickets, above are
                                   # coding errors (a common cut in work with DB1B)
MAX_COUPONS = 3                    # at most two connections in a direction (drops odd routings)
MIN_PAIR_CARRIER_PAX = 5           # pair-airline-years with fewer than 5 sampled tickets are dropped as noise

COLS = ["MktCoupons", "Origin", "Dest", "TkCarrierChange", "TkCarrier", "BulkFare", "Passengers", "MktFare",
        "NonStopMiles"]


def fetch(raw_dir, year, quarter):
    path = raw_dir / f"Origin_and_Destination_Survey_DB1BMarket_{year}_{quarter}.zip"
    if path.exists():
        return path
    raw_dir.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part")
    print(f"  downloading {URL.format(y=year, q=quarter)}", flush=True)
    with requests.get(URL.format(y=year, q=quarter), stream=True, timeout=900) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.rename(path)
    return path


def one_quarter(args):
    raw_dir, year, quarter = args
    path = fetch(raw_dir, year, quarter)
    with zipfile.ZipFile(path) as z:
        name = [n for n in z.namelist() if n.endswith(".csv")][0]
        with z.open(name) as f:
            d = pv.read_csv(f, convert_options=pv.ConvertOptions(include_columns=COLS)).to_pandas()
    n0, p0 = len(d), d.Passengers.sum()

    keep = ((d.BulkFare == 0) & d.MktFare.between(FARE_MIN, FARE_MAX)
            & (d.MktCoupons <= MAX_COUPONS) & (d.TkCarrierChange == 0))
    d = d[keep].copy()
    d["a"] = np.minimum(d.Origin, d.Dest)
    d["b"] = np.maximum(d.Origin, d.Dest)
    d["rev"] = d.MktFare * d.Passengers
    d["ns_pax"] = np.where(d.MktCoupons == 1, d.Passengers, 0.0)
    d["miles_x_pax"] = d.NonStopMiles * d.Passengers
    pair = (d.groupby(["a", "b", "TkCarrier"])[["Passengers", "rev", "ns_pax", "miles_x_pax"]].sum()
            .reset_index().rename(columns={"TkCarrier": "carrier", "Passengers": "pax"}))
    msg = (f"{year} Q{quarter}: {n0:,} market records ({p0:,.0f} sampled passengers); "
           f"kept {keep.sum():,} after fare, bulk, coupon and interline filters; dropped {(~keep).sum():,}")
    pair["year"] = year
    return msg, pair


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", type=Path, default=RAW)
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()

    jobs = [(args.raw_dir, y, q) for y in YEARS for q in (1, 2, 3, 4)]
    pairs = []
    with ProcessPoolExecutor(args.workers) as ex:
        for msg, p in ex.map(one_quarter, jobs):
            print(msg, flush=True)
            pairs.append(p)

    pair = pd.concat(pairs).groupby(["year", "a", "b", "carrier"]).sum().reset_index()
    n_all = len(pair)
    pair = pair[pair.pax >= MIN_PAIR_CARRIER_PAX]
    pair["miles"] = (pair.miles_x_pax / pair.pax).round()
    pair = pair.drop(columns="miles_x_pax")
    pair["rev"] = pair.rev.round()
    print(f"\npair x airline x year rows: {n_all:,}; kept {len(pair):,} with >= {MIN_PAIR_CARRIER_PAX} "
          f"sampled tickets; dropped {n_all - len(pair):,}")

    OUT.mkdir(parents=True, exist_ok=True)
    pair.to_csv(OUT / "pair_carrier_year.csv.gz", index=False)
    print(f"wrote data/derived/pair_carrier_year.csv.gz ({len(pair):,} rows)")


if __name__ == "__main__":
    main()
