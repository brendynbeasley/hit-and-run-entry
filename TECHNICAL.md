# Technical notes

This is the technical companion to the [README](README.md). It covers the data, the rules, every test statistic and
how to reproduce the results. Every table is in [results/FINDINGS.md](results/FINDINGS.md).

## The original study

William J. Baumol, "Contestable Markets: An Uprising in the Theory of Industry Structure," *American Economic Review*
72(1), March 1982, pp. 1–15, with the full treatment in Baumol, Panzar and Willig, *Contestable Markets and the
Theory of Industry Structure* (1982). It is a theory paper with no data. The results tested here are taken from the
restatement in Bailey and Baumol (1984, *Yale Journal on Regulation* 1: 111), because the 1982 article was not
available to me. A market is perfectly contestable if no price can be in equilibrium when an entrant could undercut
it and still profit (p. 113). Such a market rules out excess profit and inefficiency (p. 116), and with two or more
efficient firms forces price to marginal cost (p. 117). Airlines were offered as a close approximation (p. 128),
with the concession that actual competition had mattered in virtually all airline markets since the first years of
deregulation (p. 129).

## Headline results

| Test (route-level, distance and endpoint-airport controls) | 2019 | 2024 |
|---|---|---|
| Each additional actual competitor, $`\theta_A`$ | −0.047 (0.013) | −0.048 (0.013) |
| Each additional potential entrant, $`\theta_P`$ | −0.017 (0.010) | −0.016 (0.010) |
| $`\theta_A - \theta_P`$, p-value | −0.029, p < 0.001 | −0.032, p < 0.001 |
| $`\theta_P`$ with nonstop-share control | −0.004 (0.009) | 0.000 (0.010) |
| Four or more actual airlines vs one, % | −10.9 | −11.5 |
| Log HHI, OLS, $`\beta`$ | 0.071 (0.028) | 0.045 (0.035) |
| Log HHI, 2SLS, $`\beta`$ | 0.091 (0.064) | 0.146 (0.077) |
| Routes | 5,810 | 6,186 |

Southwest extension (2014–2024, 2020 omitted): incumbents' fares average −0.061 (0.008) log points in years 0 to 3
after Southwest first serves both endpoints; the added effect once Southwest flies the route is 0.007 (0.012);
507 threatened routes, 2,982 controls, 24,153 route-years.

## Data

- **Tickets:** Bureau of Transportation Statistics, Airline Origin and Destination Survey, DB1B Market,
  `Origin_and_Destination_Survey_DB1BMarket_{year}_{quarter}.zip` for 2014 Q1 to 2024 Q4, from
  `https://transtats.bts.gov/PREZIP/` (downloaded November 2026). A 10% sample of domestic tickets. The 44 zips
  (about 4 GB) are not committed; `src/build_routes.py` fetches any that are missing into `data/raw/db1b/`.
- **Derived tables (committed):** `data/derived/pair_carrier_year.csv.gz` (727,519 rows: airport pair, ticketing
  airline, year, sampled passengers, fare revenue, nonstop passengers, distance) and `data/derived/markets.csv.gz`
  (one row per market-year, written by `src/contestability.py`).
- **Prices:** FRED series CPIAUCSL (`data/raw/CPIAUCSL.csv`), annual average, to put event-study fares in 2024
  dollars.

## Method

Rules fixed before looking at the results:

- **Tickets:** fare between $25 and $2,500 per direction, bulk fares dropped, at most three coupons per direction,
  a single ticketing airline on the itinerary. Airline codes as ticketed (no merging of US Airways into American or
  Virgin America into Alaska).
- **Market:** non-directional airport pair and year with at least 730 sampled passengers (about 20 a day) and a
  nonstop distance of at least 100 miles. Fare is total fare revenue over passengers.
- **Actual competitor:** at least 5% of the route's passengers. **Presence:** at least 1,000 sampled nonstop
  passengers a year from or to the airport. **Potential entrant:** present at both endpoints and not an actual
  competitor.
- **Estimating equations,** for each year separately:

```math
\begin{aligned}
\ln F_m &= \beta \ln \text{HHI}_m + \gamma N^{\text{pot}}_m + g(D_m) + \mu_{a(m)} + \mu_{b(m)} + \varepsilon_m \\
\ln F_m &= \theta_A N^{\text{act}}_m + \theta_P N^{\text{pot}}_m + g(D_m) + \mu_{a(m)} + \mu_{b(m)} + \varepsilon_m \\
g(D) &= \delta_1 \ln D + \delta_2 (\ln D)^2
\end{aligned}
```

  with one dummy per airport switched on at either endpoint. Standard errors are dyadic airport-clustered: any two
  routes that share an endpoint airport, in either position, may have correlated errors. With $`u_m`$ route
  $`m`$'s score and $`S_g`$ the sum of $`u_m`$ over routes with an endpoint at airport $`g`$, the middle of the
  sandwich is $`\sum_g S_g S_g' - \sum_m u_m u_m'`$ (a route sits in two clusters, so its own term is counted
  once), with a small-sample factor $`G/(G-1)`$ and $`G - 1`$ degrees of freedom, where $`G`$ is the number of
  airports (296 in 2019, 295 in 2024). Null hypotheses are $`\beta = 0`$ and $`\theta_A = \theta_P`$.
- **Instrument:** predicted shares $`\hat{s}_{jm} \propto \sqrt{\sigma_{ja}\,\sigma_{jb}}`$, where
  $`\sigma_{ja}`$ is airline $`j`$'s share of nonstop passengers at airport $`a`$, and
  $`\widehat{\text{HHI}}_m = \sum_j \hat{s}_{jm}^2`$. The correlation of the log instrument with log HHI is 0.69
  (2019) and 0.71 (2024).
- **Extension:** route $`r`$ is threatened in year $`T_r`$, the first year Southwest is present at both endpoints,
  if that is after the route's first observed year and Southwest had not flown the route (5% share) before. Controls
  are routes never threatened and never served by Southwest. Outcome is the non-Southwest average fare in 2024
  dollars, route-years with at least 100 sampled incumbent passengers.

```math
\ln F^{\text{inc}}_{rt} = \sum_{k \ne -1} \tau_k \,\mathbf{1}[t - T_r = k] + \lambda W_{rt} + \alpha_r + \phi_t + u_{rt}
```

  Event time is binned at −3 and +3. Fixed effects are absorbed by alternating projections; errors are clustered
  by route. Year 2020 is dropped.

## Full test statistics

Actual against potential, all years (spec B, log points; p-values in parentheses):

| Year | $`\theta_A`$ | $`\theta_P`$ | Difference p |
|---|---|---|---|
| 2014 | −0.027 (0.006) | −0.021 (0.004) | 0.40 |
| 2015 | −0.007 (0.49) | −0.017 (0.026) | 0.16 |
| 2016 | −0.026 (0.027) | −0.016 (0.095) | 0.12 |
| 2017 | −0.027 (0.057) | −0.012 (0.20) | 0.063 |
| 2018 | −0.027 (0.031) | −0.008 (0.44) | 0.003 |
| 2019 | −0.047 (< 0.001) | −0.017 (0.098) | < 0.001 |
| 2020 | −0.056 (< 0.001) | −0.025 (0.058) | < 0.001 |
| 2021 | −0.047 (< 0.001) | −0.020 (0.047) | < 0.001 |
| 2022 | −0.025 (0.048) | −0.013 (0.19) | 0.056 |
| 2023 | −0.047 (< 0.001) | −0.023 (0.023) | < 0.001 |
| 2024 | −0.048 (< 0.001) | −0.016 (0.13) | < 0.001 |

The OLS log-HHI coefficient is positive in every year, from 0.0002 (2022) to 0.122 (2020), and significant at 5%
only in 2019 and 2020. The 2SLS estimate has p = 0.16 in 2019 and p = 0.058 in 2024. Potential-entrant dummies (one, two, three, four or more) are never significant
in 2019 or 2024. Event-study coefficients (all threatened routes): $`\tau_{-3}`$ = 0.011 (0.008),
$`\tau_{-2}`$ = 0.005 (0.008), $`\tau_0`$ = −0.057 (0.007), $`\tau_1`$ = −0.078 (0.010), $`\tau_2`$ = −0.044
(0.010), $`\tau_3`$ = −0.065 (0.010). Excluding 2021 threats: average threat effect −0.070 (0.009), with
$`\tau_{-3}`$ = 0.020 (0.009) and $`\tau_{-2}`$ = 0.025 (0.008), so that sample shows a pre-threat downward drift.

## Reproducing the results

```bash
pip install -r requirements.txt
python src/build_routes.py --workers 3      # downloads 44 DB1B zips (~4 GB) and rebuilds data/derived/
python src/contestability.py                # cross-section tests, tables, first figure
python src/southwest_threat.py              # Southwest event study, second figure
```

The first step can be skipped, since its output is committed. It takes about six minutes with three worker processes once the
zips are on disk.

## Repository layout

| Path | What it is |
|---|---|
| `src/build_routes.py` | DB1B quarterly files to the airport-pair, airline, year table |
| `src/contestability.py` | Markets, concentration, potential entrants, fare regressions, named routes |
| `src/southwest_threat.py` | Goolsbee–Syverson style event study on 2014–2024 |
| `results/*.csv`, `results/*.png` | Every number and chart in the README |

## References

- Bailey, E. E. & Baumol, W. J. (1984). Deregulation and the theory of contestable markets. *Yale Journal on
  Regulation* 1: 111.
- Baumol, W. J. (1982). Contestable markets: an uprising in the theory of industry structure. *American Economic
  Review* 72(1): 1–15.
- Baumol, W. J., Panzar, J. C. & Willig, R. D. (1982). *Contestable Markets and the Theory of Industry Structure*.
  Harcourt Brace Jovanovich.
- Goolsbee, A. & Syverson, C. (2008). How do incumbents respond to the threat of entry? Evidence from the major
  airlines. *Quarterly Journal of Economics* 123(4): 1611–1633.
- Schwartz, M. & Reynolds, R. J. (1983). Contestable markets: an uprising in the theory of industry structure:
  comment. *American Economic Review* 73: 488.
