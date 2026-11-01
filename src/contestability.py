"""Are US airline routes contestable? Baumol (1982) tested on the DOT ticket sample, 2014-2024.

Baumol's theory says that where entry and exit are free, the threat of entry alone holds prices to
cost, so the number of airlines actually flying a route should not matter once costs are held fixed,
and an airline waiting at both ends of a route should discipline fares as well as one already flying
it. This script builds one row per airport pair and year from src/build_routes.py's output and runs:

  1. the contestability test: log average fare on route concentration (HHI) and the number of
     potential entrants, with distance controls and endpoint-airport fixed effects, for 2019 and 2024
     (and every year 2014-2024 as a check); then actual versus potential competitors directly;
  2. an instrumented version, with HHI predicted from each airline's presence at the two endpoints.
It also writes data/derived/markets.csv.gz, the route-year table that src/southwest_threat.py
(the extension) reads.

Run src/build_routes.py first. Usage (from the repository root):
    python src/contestability.py
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
RAW = ROOT / "data" / "raw"
RES = ROOT / "results"

MIN_MARKET_PAX = 730      # sampled tickets a year = 7,300 actual, about 20 passengers a day (a regularly served route)
MIN_MILES = 100           # very short airport pairs are mostly connections to a nearby hub; dropped
ACTUAL_SHARE = 0.05       # an airline with >= 5% of a route's passengers counts as an actual competitor
                          # (my threshold: drops carriers selling only stray connecting tickets on the pair)
PRESENCE_MIN = 1000       # an airline is "present" at an airport with >= 1,000 sampled nonstop passengers a year
                          # (10,000 actual, a little over one daily round trip)
MAIN_YEARS = [2019, 2024]  # last pre-pandemic year and latest full year
WN = "WN"

NAMES = {"AA": "American", "DL": "Delta", "UA": "United", "WN": "Southwest", "AS": "Alaska",
         "B6": "JetBlue", "NK": "Spirit", "F9": "Frontier", "G4": "Allegiant", "HA": "Hawaiian",
         "SY": "Sun Country", "VX": "Virgin America", "US": "US Airways", "MX": "Breeze", "XP": "Avelo"}


def load():
    p = pd.read_csv(DERIVED / "pair_carrier_year.csv.gz", dtype={"carrier": str})
    print(f"loaded pair_carrier_year: {len(p):,} airport-pair x airline x year rows, "
          f"{p.pax.sum():,.0f} sampled passengers, {p.year.min()}-{p.year.max()}")
    cpi = pd.read_csv(RAW / "CPIAUCSL.csv", parse_dates=["observation_date"])
    cpi = cpi.groupby(cpi.observation_date.dt.year).CPIAUCSL.mean()
    return p, cpi.loc[2024] / cpi


def build_markets(p, deflator):
    """One row per airport pair and year with fares, concentration, and actual and potential rivals."""
    flow = []
    mk = p.groupby(["year", "a", "b"]).agg(pax=("pax", "sum"), rev=("rev", "sum"), ns=("ns_pax", "sum"))
    miles = (p.miles * p.pax).groupby([p.year, p.a, p.b]).sum() / mk.pax
    mk["miles"] = miles
    flow.append(("sampled passengers loaded (after ticket filters)", int(p.pax.sum())))
    flow.append(("all airport-pair years", len(mk)))
    keep = (mk.pax >= MIN_MARKET_PAX) & (mk.miles >= MIN_MILES)
    flow.append((f"dropped: under {MIN_MARKET_PAX} sampled passengers or under {MIN_MILES} miles", int((~keep).sum())))
    mk = mk[keep].copy()
    flow.append(("kept markets", len(mk)))

    p = p.join(mk[["pax"]].rename(columns={"pax": "mkt_pax"}), on=["year", "a", "b"], how="inner")
    p["share"] = p.pax / p.mkt_pax
    mk["hhi"] = (p.share ** 2).groupby([p.year, p.a, p.b]).sum()
    act = p[p.share >= ACTUAL_SHARE]
    mk["n_act"] = act.groupby(["year", "a", "b"]).size()
    top = p.sort_values("share").groupby(["year", "a", "b"]).tail(1).set_index(["year", "a", "b"])
    mk["top_carrier"], mk["top_share"] = top.carrier, top.share

    # presence: nonstop passengers ticketed by the airline from or to the airport (all pairs, not just kept)
    full = pd.read_csv(DERIVED / "pair_carrier_year.csv.gz", dtype={"carrier": str})
    ap = pd.concat([full[["year", "a", "carrier", "ns_pax"]].rename(columns={"a": "airport"}),
                    full[["year", "b", "carrier", "ns_pax"]].rename(columns={"b": "airport"})])
    ap = ap.groupby(["year", "airport", "carrier"]).ns_pax.sum().reset_index()
    ap["ap_share"] = ap.ns_pax / ap.groupby(["year", "airport"]).ns_pax.transform("sum")
    present = ap[ap.ns_pax >= PRESENCE_MIN]
    pres_set = set(zip(present.year, present.airport, present.carrier))
    wn_first = present[present.carrier == WN].groupby("airport").year.min()
    wn_first = wn_first[wn_first > present.year.min()].sort_values().rename("first_year_present").reset_index()
    wn_first.to_csv(RES / "southwest_new_airports.csv", index=False)
    print(f"airline-airport-years with presence (>= {PRESENCE_MIN} sampled nonstop passengers): {len(present):,}")

    both = (mk.reset_index()[["year", "a", "b"]]
            .merge(present[["year", "airport", "carrier"]].rename(columns={"airport": "a"}), on=["year", "a"])
            .merge(present[["year", "airport", "carrier"]].rename(columns={"airport": "b"}),
                   on=["year", "b", "carrier"]))
    act_set = set(zip(act.year, act.a, act.b, act.carrier))
    both["is_act"] = [k in act_set for k in zip(both.year, both.a, both.b, both.carrier)]
    pot = both[~both.is_act]
    mk["n_pot"] = pot.groupby(["year", "a", "b"]).size()
    mk[["n_act", "n_pot"]] = mk[["n_act", "n_pot"]].fillna(0).astype(int)

    # predicted HHI from endpoint presence (instrument): s_j proportional to sqrt(share_a * share_b)
    sh = ap[["year", "airport", "carrier", "ap_share"]]
    pr = (mk.reset_index()[["year", "a", "b"]]
          .merge(sh.rename(columns={"airport": "a", "ap_share": "sa"}), on=["year", "a"])
          .merge(sh.rename(columns={"airport": "b", "ap_share": "sb"}), on=["year", "b", "carrier"]))
    pr["g"] = np.sqrt(pr.sa * pr.sb)
    pr["s"] = pr.g / pr.groupby(["year", "a", "b"]).g.transform("sum")
    mk["hhi_pred"] = (pr.s ** 2).groupby([pr.year, pr.a, pr.b]).sum()

    wn = p[p.carrier == WN].set_index(["year", "a", "b"])
    mk["wn_share"] = wn.share.reindex(mk.index).fillna(0)
    mk["wn_pot"] = [(y, a, WN) in pres_set and (y, b, WN) in pres_set for y, a, b in mk.index]
    inc = p[p.carrier != WN].groupby(["year", "a", "b"])[["pax", "rev"]].sum()
    mk["inc_pax"], mk["inc_fare"] = inc.pax, inc.rev / inc.pax

    mk["fare"] = mk.rev / mk.pax
    mk = mk.reset_index()
    mk["fare24"] = mk.fare * mk.year.map(deflator)
    mk["inc_fare24"] = mk.inc_fare * mk.year.map(deflator)
    mk["route"] = mk.a + "-" + mk.b
    print(f"markets kept: {len(mk):,} airport-pair years; {mk.route.nunique():,} distinct pairs")
    return mk, ap, pd.DataFrame(flow, columns=["step", "rows"])


def ols(y, X, groups, names):
    """OLS with airport-clustered (dyadic) standard errors; see iv()."""
    return iv(y, X, X, groups, names)


def iv(y, X, Z, groups, names):
    """2SLS (OLS when Z is X) with dyadic airport-clustered errors. groups: array (n, 2) of the two endpoint airports.

    Any two routes that share an endpoint airport, in either position, may have correlated errors. The meat sums
    each route's score into both of its airports' clusters and subtracts the route's own outer product once, since
    a route sits in two clusters: meat = sum_g S_g S_g' - sum_m u_m u_m' (each route appears once per year).
    """
    ZZi = np.linalg.pinv(Z.T @ Z)
    Xh = Z @ (ZZi @ (Z.T @ X))
    A = np.linalg.pinv(Xh.T @ Xh)
    b = A @ (Xh.T @ y)
    e = y - X @ b

    u = Xh * e[:, None]
    airports, codes = np.unique(groups.astype(str), return_inverse=True)
    codes = codes.reshape(groups.shape)
    S = np.zeros((len(airports), u.shape[1]))
    np.add.at(S, codes[:, 0], u)
    np.add.at(S, codes[:, 1], u)
    V = A @ (S.T @ S - u.T @ u) @ A
    G = len(airports)
    V *= G / (G - 1)
    se = np.sqrt(np.clip(np.diag(V), 0, None))
    r2 = 1 - (e @ e) / ((y - y.mean()) @ (y - y.mean()))
    k = len(names)
    return pd.DataFrame({"term": names, "coef": b[:k], "se": se[:k]}), V[:k, :k], r2, G


def design(d, regressors):
    """Regressors, distance controls, and one dummy per endpoint airport (both ends share the dummy set)."""
    lm = np.log(d.miles.to_numpy())
    base = [d[r].to_numpy(float) for r in regressors] + [lm, lm ** 2]
    names = regressors + ["log_miles", "log_miles_sq"]
    airports = pd.Index(sorted(set(d.a) | set(d.b)))
    D = np.zeros((len(d), len(airports)))
    D[np.arange(len(d)), airports.get_indexer(d.a)] = 1
    D[np.arange(len(d)), airports.get_indexer(d.b)] = 1
    X = np.column_stack(base + [D])  # airport dummies span the constant (each row sums to 2)
    return X, names


def fit(d, regressors, label, year, instrument=None):
    X, names = design(d, regressors)
    y = np.log(d.fare.to_numpy())
    groups = d[["a", "b"]].to_numpy()
    if instrument is None:
        tab, V, r2, G = ols(y, X, groups, names)
    else:
        Zx = d[instrument].to_numpy(float)
        Z = X.copy()
        Z[:, 0] = Zx
        tab, V, r2, G = iv(y, X, Z, groups, names)
    tab["t"] = tab.coef / tab.se
    tab["p"] = 2 * stats.t.sf(np.abs(tab.t), G - 1)
    tab["ci_lo"] = tab.coef - stats.t.ppf(0.975, G - 1) * tab.se
    tab["ci_hi"] = tab.coef + stats.t.ppf(0.975, G - 1) * tab.se
    tab.insert(0, "spec", label)
    tab.insert(1, "year", year)
    tab["n"], tab["r2"], tab["clusters"] = len(d), r2, G
    return tab, V


def wald_equal(tab, V, t1, t2, G):
    i, j = list(tab.term).index(t1), list(tab.term).index(t2)
    diff = tab.coef.iloc[i] - tab.coef.iloc[j]
    se = np.sqrt(V[i, i] + V[j, j] - 2 * V[i, j])
    return diff, se, 2 * stats.t.sf(abs(diff / se), G - 1)


def contestability_tests(mk):
    rows, tests = [], []
    for year in MAIN_YEARS + [y for y in sorted(mk.year.unique()) if y not in MAIN_YEARS]:
        d = mk[mk.year == year].copy()
        d["log_hhi"] = np.log(d.hhi)
        d["log_hhi_pred"] = np.log(d.hhi_pred)
        t1, _ = fit(d, ["log_hhi", "n_pot"], "A: log HHI + potential entrants", year)
        t2, V2 = fit(d, ["n_act", "n_pot"], "B: actual vs potential competitors", year)
        rows += [t1, t2]
        diff, se, pv = wald_equal(t2, V2, "n_act", "n_pot", t2.clusters.iloc[0])
        tests.append({"year": year, "test": "actual competitor effect = potential entrant effect",
                      "estimate": diff, "se": se, "p": pv, "n": len(d)})
        b = t1.set_index("term").loc["log_hhi"]
        tests.append({"year": year, "test": "log HHI coefficient = 0 (perfect contestability)",
                      "estimate": b.coef, "se": b.se, "p": b.p, "n": len(d)})
        if year in MAIN_YEARS:
            t3, _ = fit(d, ["log_hhi", "n_pot"], "C: 2SLS, HHI instrumented by endpoint-presence HHI",
                        year, instrument="log_hhi_pred")
            fs = np.corrcoef(d.log_hhi, d.log_hhi_pred)[0, 1]
            t3["first_stage_corr"] = fs
            rows.append(t3)
            for k in (2, 3, 4):
                d[f"act{k}"] = (d.n_act == k) if k < 4 else (d.n_act >= 4)
                d[f"pot{k}"] = (d.n_pot == k) if k < 4 else (d.n_pot >= 4)
            d["pot1"] = d.n_pot == 1
            regs = ["act2", "act3", "act4", "pot1", "pot2", "pot3", "pot4"]
            t4, _ = fit(d, regs, "D: dummies (base = one airline, no potential entrant)", year)
            d["ns_share"] = d.ns / d.pax
            t5, _ = fit(d, ["n_act", "n_pot", "ns_share"], "E: B plus share of nonstop passengers", year)
            rows += [t4, t5]
    out = pd.concat(rows, ignore_index=True)
    out["pct"] = 100 * (np.exp(out.coef) - 1)
    for spec in ("A", "C"):
        for year in MAIN_YEARS:
            b = out[(out.year == year) & out.spec.str.startswith(spec) & (out.term == "log_hhi")].iloc[0]
            tests.append({"year": year, "test": f"spec {spec}: implied fare gap, monopoly vs two equal airlines (%)",
                          "estimate": 100 * (np.exp(b.coef * np.log(2)) - 1),
                          "se": 100 * np.log(2) * b.se, "p": b.p, "n": b.n})
    return out[out.term.isin(["log_hhi", "n_pot", "n_act", "act2", "act3", "act4",
                              "pot1", "pot2", "pot3", "pot4"])], pd.DataFrame(tests)


def structure_table(mk, year):
    d = mk[mk.year == year].copy()
    d["airlines"] = d.n_act.clip(upper=4).map({1: "1", 2: "2", 3: "3", 4: "4 or more"})
    g = d.groupby("airlines")
    t = pd.DataFrame({"markets": g.size(), "share_of_passengers": g.pax.sum() / d.pax.sum(),
                      "avg_fare": g.rev.sum() / g.pax.sum(), "avg_miles": g.miles.mean(),
                      "fare_per_100_miles": 100 * g.rev.sum() / (g.miles.mean() * g.pax.sum()),
                      "avg_potential_entrants": g.n_pot.mean(), "avg_hhi_x10000": 10000 * g.hhi.mean(),
                      "nonstop_share_of_passengers": g.ns.sum() / g.pax.sum()})
    t.insert(0, "year", year)
    return t.reset_index()


def named_routes(mk, year, coef_hhi):
    """The busiest one-airline routes with rivals waiting at both ends, against competitive routes of similar length."""
    d = mk[mk.year == year].copy()
    d["band"] = pd.cut(d.miles, [0, 500, 1000, 1500, 2000, 3000, 6000])
    comp = d[d.n_act >= 3]
    bench = (comp.groupby("band", observed=True).rev.sum() / comp.groupby("band", observed=True).pax.sum())
    mono = d[(d.top_share >= 0.90) & (d.n_pot >= 2)].nlargest(15, "pax").copy()
    mono["airline"] = mono.top_carrier.map(NAMES).fillna(mono.top_carrier)
    mono["benchmark_fare_3plus"] = mono.band.map(bench).astype(float)
    mono["premium_pct"] = 100 * (mono.fare / mono.benchmark_fare_3plus - 1)
    cols = ["route", "airline", "top_share", "n_pot", "miles", "pax", "fare", "benchmark_fare_3plus", "premium_pct"]
    return mono[cols].rename(columns={"pax": "sampled_passengers"})


def plot_structure(tab, path):
    t = tab[(tab.spec.str.startswith("D")) & (tab.year == 2024)].set_index("term")
    fig, ax = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True)
    for axis, terms, labels, title in [
        (ax[0], ["act2", "act3", "act4"], ["2", "3", "4+"], "Airlines actually flying the route"),
        (ax[1], ["pot1", "pot2", "pot3", "pot4"], ["1", "2", "3", "4+"], "Rivals at both ends, not flying it")]:
        c = 100 * (np.exp(t.loc[terms, "coef"]) - 1)
        lo = 100 * (np.exp(t.loc[terms, "ci_lo"]) - 1)
        hi = 100 * (np.exp(t.loc[terms, "ci_hi"]) - 1)
        axis.bar(labels, c, color="#3b6ea5" if "actually" in title else "#c9822b", width=0.6)
        axis.errorbar(labels, c, yerr=[c - lo, hi - c], fmt="none", color="black", capsize=3, lw=1)
        axis.axhline(0, color="black", lw=0.8)
        axis.set_title(title, fontsize=10)
        axis.set_xlabel("number")
    ax[0].set_ylabel("Fare vs. a one-airline route\nwith no rival at both ends (%)")
    fig.suptitle("2024 average fares by competition on the route, same distance and airports", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    RES.mkdir(exist_ok=True)
    p, deflator = load()
    mk, ap, flow = build_markets(p, deflator)
    flow.to_csv(RES / "sample_flow.csv", index=False)
    by_year = p.groupby("year").pax.sum().rename("sampled_passengers").reset_index()
    by_year["markets_kept"] = by_year.year.map(mk.groupby("year").size())
    by_year.to_csv(RES / "passengers_by_year.csv", index=False)

    st = pd.concat([structure_table(mk, y) for y in MAIN_YEARS])
    st.to_csv(RES / "market_structure.csv", index=False)
    print("\nmarket structure:\n", st.round(3).to_string(index=False))

    reg, tests = contestability_tests(mk)
    reg.to_csv(RES / "fare_regressions.csv", index=False)
    tests.to_csv(RES / "contestability_tests.csv", index=False)
    print("\nmain regressions (2019, 2024):\n",
          reg[reg.year.isin(MAIN_YEARS)].round(4).to_string(index=False))
    print("\ntests:\n", tests.round(4).to_string(index=False))

    b24 = reg[(reg.year == 2024) & (reg.spec.str.startswith("A")) & (reg.term == "log_hhi")].coef.iloc[0]
    nr = named_routes(mk, 2024, b24)
    nr.to_csv(RES / "monopoly_routes_2024.csv", index=False)
    print("\nbusiest one-airline routes with >= 2 rivals at both ends, 2024:\n", nr.round(2).to_string(index=False))

    ex = mk[(mk.year == 2024) & (mk.route.isin(["ATL-MSP", "BOS-DCA", "DEN-SLC", "BWI-MCO"]))]
    shares = p[(p.year == 2024) & (p.a + "-" + p.b).isin(ex.route)].copy()
    shares["route"] = shares.a + "-" + shares.b
    shares["share"] = shares.pax / shares.groupby("route").pax.transform("sum")
    shares = shares[shares.share >= 0.01][["route", "carrier", "pax", "share"]].sort_values(["route", "share"],
                                                                                            ascending=[True, False])
    shares = shares.merge(ex[["route", "hhi", "n_act", "n_pot", "fare", "miles"]], on="route")
    shares.to_csv(RES / "worked_example_routes_2024.csv", index=False)

    plot_structure(reg, RES / "fares_by_competition_2024.png")
    cols = ["year", "a", "b", "route", "pax", "miles", "top_carrier", "wn_share", "wn_pot", "inc_pax", "inc_fare24"]
    mk[cols].to_csv(DERIVED / "markets.csv.gz", index=False)
    print("\nwrote results/*.csv, results/fares_by_competition_2024.png and data/derived/markets.csv.gz")


if __name__ == "__main__":
    main()
