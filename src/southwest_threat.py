"""Extension: what incumbents' fares do when Southwest becomes a potential entrant (Goolsbee & Syverson 2008).

A route is "threatened" in the first year Southwest serves both of its endpoint airports without flying
the route itself. If potential competition disciplines prices, incumbents should cut fares when the
threat appears, before Southwest enters. This script runs an event study of incumbents' average fare
(2024 dollars, all non-Southwest tickets) on years since the threat, with route and year fixed effects,
a separate dummy for years in which Southwest actually flies the route, never-threatened routes as
controls, and errors clustered by route.

Run src/contestability.py first; this reads its data/derived/markets.csv.gz. Usage:
    python src/southwest_threat.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DERIVED = ROOT / "data" / "derived"
RES = ROOT / "results"

ACTUAL_SHARE = 0.05       # Southwest "flies" the route once it has >= 5% of passengers (as in contestability.py)
MIN_INCUMBENT_PAX = 100   # route-years need >= 100 sampled incumbent tickets for a usable average fare
EVENT_WINDOW = (-3, 3)    # years relative to the Southwest threat; ends are binned
DROP_EVENT_YEARS = [2020]  # pandemic year: traffic fell by more than half and fares collapsed unevenly by airport
WN = "WN"
NAMES = {"AA": "American", "DL": "Delta", "UA": "United", "WN": "Southwest", "AS": "Alaska",
         "B6": "JetBlue", "NK": "Spirit", "F9": "Frontier", "G4": "Allegiant", "HA": "Hawaiian",
         "SY": "Sun Country", "VX": "Virgin America", "US": "US Airways"}


def southwest_threat(mk):
    """Event study: incumbents' fares around the year Southwest first serves both endpoints of a route it does not fly."""
    d = mk[mk.inc_pax >= MIN_INCUMBENT_PAX].copy()
    n_drop = int(d.year.isin(DROP_EVENT_YEARS).sum())
    d = d.sort_values(["route", "year"])
    d["wn_act"] = d.wn_share >= ACTUAL_SHARE
    first_year = d.groupby("route").year.transform("min")
    onset = d[d.wn_pot].groupby("route").year.min()
    d["onset"] = d.route.map(onset)
    entry = d[d.wn_act].groupby("route").year.min()
    d["entry"] = d.route.map(entry)
    n_routes = d.route.nunique()
    # treated: threat begins after the route's first observed year, Southwest not flying it before the threat
    treated = d.onset.notna() & (d.onset > first_year) & (d.entry.isna() | (d.entry > d.onset))
    never = d.onset.isna() & d.entry.isna()
    d = d[treated | never].copy()
    d["treated"] = treated[treated | never]
    print(f"Southwest threat sample: {n_routes:,} routes; {d[d.treated].route.nunique():,} threatened routes "
          f"(first threat after first year observed, no prior Southwest service); "
          f"{d[~d.treated].route.nunique():,} never-threatened controls; others dropped")
    d = d[~d.year.isin(DROP_EVENT_YEARS)]
    print(f"dropped {n_drop:,} route-years in {DROP_EVENT_YEARS} from the event study")
    main_tab, main_sum = event_regression(d, "all threatened routes")
    alt_tab, alt_sum = event_regression(d[d.onset.ne(2021) | ~d.treated], "excluding threats that began in 2021")
    ev = d[d.treated].drop_duplicates("route")
    ev_ap = (pd.concat([ev.a, ev.b]).value_counts().head(12).rename("threatened_routes")
             .rename_axis("airport").reset_index())
    onset_counts = ev.onset.value_counts().sort_index().rename("routes").rename_axis("onset_year").reset_index()
    return (pd.concat([main_tab, alt_tab]), pd.concat([main_sum, alt_sum]), ev_ap, onset_counts,
            threatened_examples(d))


def threatened_examples(d):
    """Busiest routes threatened before the pandemic (2016-2019, so neither comparison year is 2020 or 2021):
    incumbents' fare (2024 dollars) the year before and the year after the threat, next to the passenger-weighted
    change on never-threatened routes over the same two years."""
    fare = d.set_index(["route", "year"]).inc_fare24
    ctrl = d[~d.treated].groupby("year").apply(lambda g: np.average(g.inc_fare24, weights=g.inc_pax))
    rows = []
    for route, g in d[d.treated & (d.onset <= 2019)].groupby("route"):
        t0 = int(g.onset.iloc[0])
        before, after = t0 - 1, t0 + 1
        if (route, before) not in fare.index or (route, after) not in fare.index:
            continue
        top = g.sort_values("year").top_carrier.iloc[0]
        rows.append({"route": route, "threat_year": t0, "biggest_incumbent": NAMES.get(top, top),
                     "year_before": before, "fare_before": fare[(route, before)], "year_after": after,
                     "fare_after": fare[(route, after)],
                     "change_pct": 100 * (fare[(route, after)] / fare[(route, before)] - 1),
                     "control_change_pct": 100 * (ctrl[after] / ctrl[before] - 1),
                     "southwest_entered": "" if pd.isna(g.entry.iloc[0]) else int(g.entry.iloc[0]),
                     "incumbent_passengers": g.inc_pax.sum()})
    out = pd.DataFrame(rows).nlargest(12, "incumbent_passengers")
    return out.drop(columns="incumbent_passengers")


def event_regression(d, label):
    lo, hi = EVENT_WINDOW
    rel = (d.year - d.onset).clip(lo, hi)
    names, cols = [], []
    for k in range(lo, hi + 1):
        if k == -1:
            continue
        names.append(f"k{k}")
        cols.append(((rel == k) & d.treated).to_numpy(float))
    d["wn_flying"] = (d.year >= d.entry).fillna(False)
    names.append("wn_flying")
    cols.append(d.wn_flying.to_numpy(float))
    y = np.log(d.inc_fare24.to_numpy())
    # absorb route and year fixed effects by alternating demeaning
    M = np.column_stack(cols + [y])
    route_id, year_id = pd.factorize(d.route)[0], pd.factorize(d.year)[0]
    for _ in range(200):
        M_old = M.copy()
        M = M - pd.DataFrame(M).groupby(route_id).transform("mean").to_numpy()
        M = M - pd.DataFrame(M).groupby(year_id).transform("mean").to_numpy()
        if np.abs(M - M_old).max() < 1e-10:
            break
    X, yd = M[:, :-1], M[:, -1]
    A = np.linalg.pinv(X.T @ X)
    b = A @ X.T @ yd
    e = yd - X @ b
    s = pd.DataFrame(X * e[:, None]).groupby(route_id).sum().to_numpy()
    G = len(np.unique(route_id))
    k_fe = G + len(np.unique(year_id)) - 1
    V = A @ (s.T @ s) @ A * (G / (G - 1)) * ((len(y) - 1) / (len(y) - k_fe - len(b)))
    se = np.sqrt(np.diag(V))
    tab = pd.DataFrame({"term": names, "coef": b, "se": se})
    tab["p"] = 2 * stats.t.sf(np.abs(tab.coef / tab.se), G - 1)
    tab["ci_lo"] = tab.coef - 1.96 * tab.se
    tab["ci_hi"] = tab.coef + 1.96 * tab.se
    tab["n_obs"], tab["n_routes"], tab["n_threatened"] = len(y), G, d[d.treated].route.nunique()
    tab.insert(0, "sample", label)
    # how much of Southwest's total effect arrives before it flies: average post-threat k>=0 effect vs that plus entry
    post = [f"k{k}" for k in range(0, hi + 1)]
    i_post = [names.index(n) for n in post]
    w = np.zeros(len(b))
    w[i_post] = 1 / len(i_post)
    threat = w @ b
    threat_se = np.sqrt(w @ V @ w)
    j = names.index("wn_flying")
    total = threat + b[j]
    summary = pd.DataFrame([
        {"quantity": "avg threat effect, years 0..+3 (log points)", "value": threat, "se": threat_se},
        {"quantity": "additional effect once Southwest flies the route (log points)", "value": b[j], "se": se[j]},
        {"quantity": "threat plus entry, years 0..+3 (log points)", "value": total, "se": np.nan},
        {"quantity": "threatened routes", "value": d[d.treated].route.nunique(), "se": np.nan},
        {"quantity": "threatened routes Southwest later entered", "value":
            d[d.treated & d.entry.notna()].route.nunique(), "se": np.nan},
        {"quantity": "never-threatened control routes", "value": d[~d.treated].route.nunique(), "se": np.nan},
    ])
    summary.insert(0, "sample", label)
    return tab, summary



def plot_event(tab, path):
    t = tab[tab.term.str.startswith("k") & (tab["sample"] == "all threatened routes")].copy()
    t["k"] = t.term.str[1:].astype(int)
    t = pd.concat([t, pd.DataFrame({"k": [-1], "coef": [0.0], "ci_lo": [0.0], "ci_hi": [0.0]})]).sort_values("k")
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    ax.errorbar(t.k, 100 * t.coef, yerr=[100 * (t.coef - t.ci_lo), 100 * (t.ci_hi - t.coef)],
                fmt="o-", color="#c9822b", capsize=3)
    ax.axhline(0, color="black", lw=0.8)
    ax.axvline(-0.5, color="grey", ls="--", lw=0.8)
    ax.set_xlabel("Years since Southwest began serving both ends of the route (ends binned)")
    ax.set_ylabel("Incumbents' average fare (log points x 100)")
    ax.set_title("Incumbent fares once Southwest serves both ends, 2014-2024 (2020 omitted)", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)



def main():
    mk = pd.read_csv(DERIVED / "markets.csv.gz")
    print(f"loaded markets.csv.gz: {len(mk):,} route-years, {mk.route.nunique():,} routes")
    ev, summary, ev_ap, onsets, examples = southwest_threat(mk)
    ev.to_csv(RES / "southwest_threat_event.csv", index=False)
    summary.to_csv(RES / "southwest_threat_summary.csv", index=False)
    ev_ap.to_csv(RES / "southwest_threat_airports.csv", index=False)
    onsets.to_csv(RES / "southwest_threat_onsets.csv", index=False)
    examples.to_csv(RES / "southwest_threat_routes.csv", index=False)
    print("\nevent study:\n", ev.round(4).to_string(index=False))
    print("\n", summary.round(4).to_string(index=False))
    print("\nairports with the most threatened routes:\n", ev_ap.to_string(index=False))
    print("\nthreat onsets by year:\n", onsets.to_string(index=False))
    print("\nbusiest threatened routes:\n", examples.round(1).to_string(index=False))
    plot_event(ev, RES / "southwest_threat.png")
    print("\nwrote results/southwest_threat_*.csv and results/southwest_threat.png")


if __name__ == "__main__":
    main()
