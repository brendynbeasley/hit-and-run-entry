# Baumol (1982) on US airline routes: findings

## In plain English

William Baumol argued in 1982 that where entry and exit are cheap, the airlines that could enter a route discipline
its fares as well as the airlines already flying it. This study checks that against the DOT's 10% ticket sample for
2014 to 2024.

- **The airlines flying a route set its price.** Between the same airports and at the same distance, each extra
  airline actually flying a route cut the average fare by about 4.7% in 2024, and four or more airlines cut it 11.5%
  against a one-airline route with no rival at both ends. American's near-monopoly from Washington National to Dallas/Fort Worth averaged $304
  in 2024, against $227 on comparable routes with three or more airlines, although five other airlines served both
  airports.
- **Airlines merely present at both ends barely matter.** Each such potential entrant (Delta, United, JetBlue and
  others sitting at both airports without flying the route) lowered fares by about 1.6% in 2024 (not significant on
  its own), a third of an actual competitor's effect, and nothing at all once the share of nonstop passengers is held
  fixed. The gap between actual and potential competitors is significant at 5% in 2018 to 2021, 2023 and 2024, but
  not in 2014 to 2017 or 2022.
- **Southwest is the exception.** When Southwest began serving both ends of a route it did not fly (at Chicago
  O'Hare, Miami, Houston Bush, Honolulu, Cincinnati and elsewhere), the airlines already flying the route cut their
  fares by about 6% on average, and the data show no further cut once Southwest actually started flying it.

A friendlier tour is in the [README](../README.md); methods are in [TECHNICAL.md](../TECHNICAL.md).

**Key to the labels below.** *Market* or *route*: a non-directional airport pair in a year. *Sampled passengers*:
DB1B ticket counts, one-tenth of the population. *n_act*: airlines with at least 5% of the route's passengers.
*n_pot*: airlines with at least 1,000 sampled nonstop passengers a year at both endpoint airports that are not
actual competitors. *HHI*: sum of squared passenger shares (0 to 1 in the CSVs, 0 to 10,000 in the README). *Spec A*:
log fare on log HHI and n_pot. *Spec B*: log fare on n_act and n_pot. *Spec C*: spec A with log HHI instrumented by
the endpoint-presence HHI. *Spec D*: dummies for 2, 3, 4+ actual airlines and 1, 2, 3, 4+ potential entrants (base
is one airline, no potential entrant). *Spec E*: spec B plus the nonstop share of passengers. All specs include log
distance, its square and a dummy for each airport at either end, with dyadic airport-clustered errors (two routes
sharing an endpoint airport, at either end, may be correlated).
*pct*: 100 × (exp(coef) − 1). *k*: years since Southwest first served both endpoints; *wn_flying*: years in which
Southwest has 5%+ of the route. Fares in the cross-section tables are nominal dollars for that year; event-study
fares are 2024 dollars.

## Every table

### sample_flow.csv

| step | rows |
|---|---|
| sampled passengers loaded (after ticket filters) | 499,540,799 |
| all airport-pair years | 350,019 |
| dropped: under 730 sampled passengers or under 100 miles | 291,498 |
| kept markets | 58,521 |

### passengers_by_year.csv

| year | sampled_passengers | markets_kept |
|---|---|---|
| 2014 | 41,299,602 | 5,071 |
| 2015 | 43,547,159 | 5,092 |
| 2016 | 46,132,501 | 5,249 |
| 2017 | 47,926,638 | 5,281 |
| 2018 | 50,498,412 | 5,493 |
| 2019 | 52,713,011 | 5,810 |
| 2020 | 20,788,906 | 3,643 |
| 2021 | 38,767,455 | 5,220 |
| 2022 | 49,557,153 | 5,653 |
| 2023 | 52,904,682 | 5,823 |
| 2024 | 55,405,280 | 6,186 |

### market_structure.csv

| airlines | year | markets | share_of_passengers | avg_fare | avg_miles | fare_per_100_miles | avg_potential_entrants | avg_hhi_x10000 | nonstop_share_of_passengers |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 2019 | 994 | 0.142 | 192.50 | 737 | 26.12 | 1.96 | 9,641 | 0.937 |
| 2 | 2019 | 1438 | 0.274 | 210.10 | 971 | 21.64 | 2.39 | 6,234 | 0.865 |
| 3 | 2019 | 1957 | 0.305 | 215.67 | 1,351 | 15.96 | 1.95 | 4,484 | 0.770 |
| 4 or more | 2019 | 1421 | 0.279 | 221.14 | 1,580 | 14.00 | 2.06 | 3,262 | 0.674 |
| 1 | 2024 | 1071 | 0.124 | 201.94 | 756 | 26.72 | 2.21 | 9,638 | 0.940 |
| 2 | 2024 | 1351 | 0.248 | 231.71 | 1,013 | 22.88 | 2.80 | 6,266 | 0.870 |
| 3 | 2024 | 1845 | 0.310 | 237.29 | 1,298 | 18.29 | 2.28 | 4,472 | 0.803 |
| 4 or more | 2024 | 1919 | 0.318 | 239.70 | 1,582 | 15.15 | 2.27 | 3,240 | 0.679 |

### fare_regressions.csv (2019 and 2024; every year for specs A and B is in the CSV)

| spec | year | term | coef | se | p | ci_lo | ci_hi | pct | n | r2 | clusters |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A: log HHI + potential entrants | 2019 | log_hhi | 0.0706 | 0.0276 | 0.0111 | 0.0163 | 0.1250 | 7.3 | 5810 | 0.8192 | 296 |
| A: log HHI + potential entrants | 2019 | n_pot | -0.0023 | 0.0069 | 0.7359 | -0.0158 | 0.0112 | -0.2 | 5810 | 0.8192 | 296 |
| B: actual vs potential competitors | 2019 | n_act | -0.0468 | 0.0129 | 0.0004 | -0.0722 | -0.0213 | -4.6 | 5810 | 0.8219 | 296 |
| B: actual vs potential competitors | 2019 | n_pot | -0.0173 | 0.0104 | 0.0975 | -0.0378 | 0.0032 | -1.7 | 5810 | 0.8219 | 296 |
| C: 2SLS, HHI instrumented by endpoint-presence HHI | 2019 | log_hhi | 0.0911 | 0.0642 | 0.1567 | -0.0352 | 0.2173 | 9.5 | 5810 | 0.8191 | 296 |
| C: 2SLS, HHI instrumented by endpoint-presence HHI | 2019 | n_pot | -0.0047 | 0.0104 | 0.6497 | -0.0251 | 0.0157 | -0.5 | 5810 | 0.8191 | 296 |
| D: dummies (base = one airline, no potential entrant) | 2019 | act2 | -0.0254 | 0.0239 | 0.2884 | -0.0724 | 0.0216 | -2.5 | 5810 | 0.8210 | 296 |
| D: dummies (base = one airline, no potential entrant) | 2019 | act3 | -0.0689 | 0.0337 | 0.0417 | -0.1352 | -0.0026 | -6.7 | 5810 | 0.8210 | 296 |
| D: dummies (base = one airline, no potential entrant) | 2019 | act4 | -0.1158 | 0.0427 | 0.0071 | -0.1998 | -0.0318 | -10.9 | 5810 | 0.8210 | 296 |
| D: dummies (base = one airline, no potential entrant) | 2019 | pot1 | -0.0074 | 0.0206 | 0.7203 | -0.0478 | 0.0331 | -0.7 | 5810 | 0.8210 | 296 |
| D: dummies (base = one airline, no potential entrant) | 2019 | pot2 | -0.0067 | 0.0294 | 0.8204 | -0.0645 | 0.0512 | -0.7 | 5810 | 0.8210 | 296 |
| D: dummies (base = one airline, no potential entrant) | 2019 | pot3 | -0.0138 | 0.0375 | 0.7140 | -0.0876 | 0.0601 | -1.4 | 5810 | 0.8210 | 296 |
| D: dummies (base = one airline, no potential entrant) | 2019 | pot4 | -0.0546 | 0.0497 | 0.2727 | -0.1524 | 0.0432 | -5.3 | 5810 | 0.8210 | 296 |
| E: B plus share of nonstop passengers | 2019 | n_act | -0.0694 | 0.0116 | 0.0000 | -0.0921 | -0.0466 | -6.7 | 5810 | 0.8568 | 296 |
| E: B plus share of nonstop passengers | 2019 | n_pot | -0.0045 | 0.0089 | 0.6159 | -0.0220 | 0.0131 | -0.4 | 5810 | 0.8568 | 296 |
| A: log HHI + potential entrants | 2024 | log_hhi | 0.0445 | 0.0354 | 0.2102 | -0.0252 | 0.1142 | 4.5 | 6186 | 0.8141 | 295 |
| A: log HHI + potential entrants | 2024 | n_pot | 0.0019 | 0.0075 | 0.7977 | -0.0128 | 0.0167 | 0.2 | 6186 | 0.8141 | 295 |
| B: actual vs potential competitors | 2024 | n_act | -0.0477 | 0.0126 | 0.0002 | -0.0725 | -0.0230 | -4.7 | 6186 | 0.8183 | 295 |
| B: actual vs potential competitors | 2024 | n_pot | -0.0158 | 0.0103 | 0.1255 | -0.0359 | 0.0044 | -1.6 | 6186 | 0.8183 | 295 |
| C: 2SLS, HHI instrumented by endpoint-presence HHI | 2024 | log_hhi | 0.1456 | 0.0766 | 0.0584 | -0.0052 | 0.2965 | 15.7 | 6186 | 0.8105 | 295 |
| C: 2SLS, HHI instrumented by endpoint-presence HHI | 2024 | n_pot | -0.0089 | 0.0117 | 0.4470 | -0.0321 | 0.0142 | -0.9 | 6186 | 0.8105 | 295 |
| D: dummies (base = one airline, no potential entrant) | 2024 | act2 | -0.0362 | 0.0257 | 0.1593 | -0.0868 | 0.0143 | -3.6 | 6186 | 0.8174 | 295 |
| D: dummies (base = one airline, no potential entrant) | 2024 | act3 | -0.0703 | 0.0354 | 0.0482 | -0.1400 | -0.0006 | -6.8 | 6186 | 0.8174 | 295 |
| D: dummies (base = one airline, no potential entrant) | 2024 | act4 | -0.1222 | 0.0414 | 0.0034 | -0.2035 | -0.0408 | -11.5 | 6186 | 0.8174 | 295 |
| D: dummies (base = one airline, no potential entrant) | 2024 | pot1 | -0.0036 | 0.0159 | 0.8195 | -0.0350 | 0.0277 | -0.4 | 6186 | 0.8174 | 295 |
| D: dummies (base = one airline, no potential entrant) | 2024 | pot2 | 0.0084 | 0.0257 | 0.7441 | -0.0422 | 0.0589 | 0.8 | 6186 | 0.8174 | 295 |
| D: dummies (base = one airline, no potential entrant) | 2024 | pot3 | -0.0078 | 0.0330 | 0.8130 | -0.0727 | 0.0571 | -0.8 | 6186 | 0.8174 | 295 |
| D: dummies (base = one airline, no potential entrant) | 2024 | pot4 | -0.0398 | 0.0431 | 0.3572 | -0.1246 | 0.0451 | -3.9 | 6186 | 0.8174 | 295 |
| E: B plus share of nonstop passengers | 2024 | n_act | -0.0710 | 0.0112 | 0.0000 | -0.0930 | -0.0491 | -6.9 | 6186 | 0.8564 | 295 |
| E: B plus share of nonstop passengers | 2024 | n_pot | 0.0004 | 0.0099 | 0.9709 | -0.0192 | 0.0199 | 0.0 | 6186 | 0.8564 | 295 |

### contestability_tests.csv

| year | test | estimate | se | p | n |
|---|---|---|---|---|---|
| 2014 | actual competitor effect = potential entrant effect | -0.0056 | 0.0067 | 0.4005 | 5071 |
| 2014 | log HHI coefficient = 0 (perfect contestability) | 0.0514 | 0.0264 | 0.0526 | 5071 |
| 2015 | actual competitor effect = potential entrant effect | 0.0105 | 0.0074 | 0.1585 | 5092 |
| 2015 | log HHI coefficient = 0 (perfect contestability) | 0.0188 | 0.0329 | 0.5679 | 5092 |
| 2016 | actual competitor effect = potential entrant effect | -0.0103 | 0.0067 | 0.1246 | 5249 |
| 2016 | log HHI coefficient = 0 (perfect contestability) | 0.0480 | 0.0336 | 0.1544 | 5249 |
| 2017 | actual competitor effect = potential entrant effect | -0.0147 | 0.0078 | 0.0625 | 5281 |
| 2017 | log HHI coefficient = 0 (perfect contestability) | 0.0531 | 0.0344 | 0.1232 | 5281 |
| 2018 | actual competitor effect = potential entrant effect | -0.0195 | 0.0064 | 0.0027 | 5493 |
| 2018 | log HHI coefficient = 0 (perfect contestability) | 0.0507 | 0.0293 | 0.0850 | 5493 |
| 2019 | actual competitor effect = potential entrant effect | -0.0294 | 0.0062 | 0.0000 | 5810 |
| 2019 | log HHI coefficient = 0 (perfect contestability) | 0.0706 | 0.0276 | 0.0111 | 5810 |
| 2020 | actual competitor effect = potential entrant effect | -0.0316 | 0.0073 | 0.0000 | 3643 |
| 2020 | log HHI coefficient = 0 (perfect contestability) | 0.1224 | 0.0404 | 0.0027 | 3643 |
| 2021 | actual competitor effect = potential entrant effect | -0.0267 | 0.0057 | 0.0000 | 5220 |
| 2021 | log HHI coefficient = 0 (perfect contestability) | 0.0590 | 0.0314 | 0.0610 | 5220 |
| 2022 | actual competitor effect = potential entrant effect | -0.0115 | 0.0060 | 0.0559 | 5653 |
| 2022 | log HHI coefficient = 0 (perfect contestability) | 0.0002 | 0.0327 | 0.9950 | 5653 |
| 2023 | actual competitor effect = potential entrant effect | -0.0242 | 0.0058 | 0.0000 | 5823 |
| 2023 | log HHI coefficient = 0 (perfect contestability) | 0.0429 | 0.0342 | 0.2104 | 5823 |
| 2024 | actual competitor effect = potential entrant effect | -0.0320 | 0.0060 | 0.0000 | 6186 |
| 2024 | log HHI coefficient = 0 (perfect contestability) | 0.0445 | 0.0354 | 0.2102 | 6186 |
| 2019 | spec A: implied fare gap, monopoly vs two equal airlines (%) | 5.0171 | 1.9144 | 0.0111 | 5810 |
| 2019 | spec C: implied fare gap, monopoly vs two equal airlines (%) | 6.5179 | 4.4466 | 0.1567 | 5810 |
| 2024 | spec A: implied fare gap, monopoly vs two equal airlines (%) | 3.1302 | 2.4545 | 0.2102 | 6186 |
| 2024 | spec C: implied fare gap, monopoly vs two equal airlines (%) | 10.6203 | 5.3125 | 0.0584 | 6186 |

### worked_example_routes_2024.csv

| route | carrier | pax | share | hhi | n_act | n_pot | fare | miles |
|---|---|---|---|---|---|---|---|---|
| ATL-MSP | DL | 28,436 | 0.6119 | 0.4443 | 3 | 6 | 255.94 | 907 |
| ATL-MSP | NK | 11,791 | 0.2537 | 0.4443 | 3 | 6 | 255.94 | 907 |
| ATL-MSP | F9 | 2,549 | 0.0548 | 0.4443 | 3 | 6 | 255.94 | 907 |
| ATL-MSP | SY | 1,836 | 0.0395 | 0.4443 | 3 | 6 | 255.94 | 907 |
| ATL-MSP | WN | 1,436 | 0.0309 | 0.4443 | 3 | 6 | 255.94 | 907 |
| BOS-DCA | B6 | 56,324 | 0.4498 | 0.3526 | 3 | 4 | 166.33 | 399 |
| BOS-DCA | AA | 36,314 | 0.2900 | 0.3526 | 3 | 4 | 166.33 | 399 |
| BOS-DCA | DL | 32,202 | 0.2572 | 0.3526 | 3 | 4 | 166.33 | 399 |
| BWI-MCO | WN | 50,184 | 0.5422 | 0.3982 | 3 | 8 | 156.81 | 787 |
| BWI-MCO | NK | 25,943 | 0.2803 | 0.3982 | 3 | 8 | 156.81 | 787 |
| BWI-MCO | F9 | 14,752 | 0.1594 | 0.3982 | 3 | 8 | 156.81 | 787 |
| DEN-SLC | DL | 20,530 | 0.3217 | 0.2697 | 4 | 4 | 146.45 | 391 |
| DEN-SLC | WN | 20,096 | 0.3149 | 0.2697 | 4 | 4 | 146.45 | 391 |
| DEN-SLC | UA | 13,055 | 0.2046 | 0.2697 | 4 | 4 | 146.45 | 391 |
| DEN-SLC | F9 | 10,134 | 0.1588 | 0.2697 | 4 | 4 | 146.45 | 391 |

### monopoly_routes_2024.csv

| route | airline | top_share | n_pot | miles | sampled_passengers | fare | benchmark_fare_3plus | premium_pct |
|---|---|---|---|---|---|---|---|---|
| DAL-DEN | Southwest | 1.000 | 2 | 651 | 47,922 | 164.88 | 196.26 | -16.0 |
| DEN-EWR | United | 0.981 | 7 | 1,605 | 47,832 | 307.92 | 283.43 | 8.6 |
| HPN-PBI | JetBlue | 0.963 | 3 | 1,056 | 46,087 | 213.22 | 226.71 | -5.9 |
| DCA-DFW | American | 0.971 | 5 | 1,192 | 43,416 | 303.75 | 226.71 | 34.0 |
| SJC-SNA | Southwest | 0.996 | 6 | 342 | 40,871 | 216.41 | 163.12 | 32.7 |
| DAL-PHX | Southwest | 0.999 | 2 | 879 | 40,409 | 196.99 | 196.26 | 0.4 |
| LGA-MDW | Southwest | 0.998 | 2 | 725 | 38,510 | 154.02 | 196.26 | -21.5 |
| BUR-SMF | Southwest | 0.947 | 6 | 358 | 37,517 | 172.13 | 163.12 | 5.5 |
| DAL-LAS | Southwest | 0.999 | 2 | 1,067 | 36,847 | 222.49 | 226.71 | -1.9 |
| OAK-PHX | Southwest | 0.992 | 5 | 646 | 36,145 | 168.65 | 196.26 | -14.1 |
| DAL-MCO | Southwest | 0.989 | 2 | 973 | 35,899 | 199.89 | 196.26 | 1.9 |
| SMF-SNA | Southwest | 0.984 | 6 | 404 | 35,571 | 217.09 | 163.12 | 33.1 |
| BUR-SEA | Alaska | 0.929 | 7 | 937 | 35,091 | 212.36 | 196.26 | 8.2 |
| ONT-SMF | Southwest | 0.920 | 6 | 390 | 34,953 | 177.64 | 163.12 | 8.9 |
| LAS-LGB | Southwest | 1.000 | 2 | 231 | 33,253 | 122.36 | 163.12 | -25.0 |

### southwest_threat_event.csv

| sample | term | coef | se | p | ci_lo | ci_hi | n_obs | n_routes | n_threatened |
|---|---|---|---|---|---|---|---|---|---|
| all threatened routes | k-3 | 0.0110 | 0.0079 | 0.1677 | -0.0046 | 0.0265 | 24153 | 3489 | 507 |
| all threatened routes | k-2 | 0.0054 | 0.0076 | 0.4730 | -0.0094 | 0.0202 | 24153 | 3489 | 507 |
| all threatened routes | k0 | -0.0572 | 0.0073 | 0.0000 | -0.0714 | -0.0429 | 24153 | 3489 | 507 |
| all threatened routes | k1 | -0.0783 | 0.0103 | 0.0000 | -0.0986 | -0.0581 | 24153 | 3489 | 507 |
| all threatened routes | k2 | -0.0440 | 0.0099 | 0.0000 | -0.0634 | -0.0245 | 24153 | 3489 | 507 |
| all threatened routes | k3 | -0.0653 | 0.0103 | 0.0000 | -0.0855 | -0.0450 | 24153 | 3489 | 507 |
| all threatened routes | wn_flying | 0.0075 | 0.0116 | 0.5176 | -0.0152 | 0.0302 | 24153 | 3489 | 507 |
| excluding threats that began in 2021 | k-3 | 0.0203 | 0.0091 | 0.0256 | 0.0025 | 0.0381 | 21896 | 3253 | 271 |
| excluding threats that began in 2021 | k-2 | 0.0250 | 0.0084 | 0.0029 | 0.0085 | 0.0415 | 21896 | 3253 | 271 |
| excluding threats that began in 2021 | k0 | -0.0560 | 0.0073 | 0.0000 | -0.0702 | -0.0418 | 21896 | 3253 | 271 |
| excluding threats that began in 2021 | k1 | -0.1168 | 0.0138 | 0.0000 | -0.1438 | -0.0898 | 21896 | 3253 | 271 |
| excluding threats that began in 2021 | k2 | -0.0312 | 0.0119 | 0.0090 | -0.0546 | -0.0078 | 21896 | 3253 | 271 |
| excluding threats that began in 2021 | k3 | -0.0757 | 0.0124 | 0.0000 | -0.0999 | -0.0514 | 21896 | 3253 | 271 |
| excluding threats that began in 2021 | wn_flying | 0.0096 | 0.0149 | 0.5212 | -0.0197 | 0.0388 | 21896 | 3253 | 271 |

### southwest_threat_summary.csv

| sample | quantity | value | se |
|---|---|---|---|
| all threatened routes | avg threat effect, years 0..+3 (log points) | -0.0612 | 0.0082 |
| all threatened routes | additional effect once Southwest flies the route (log points) | 0.0075 | 0.0116 |
| all threatened routes | threat plus entry, years 0..+3 (log points) | -0.0537 |  |
| all threatened routes | threatened routes | 507.0000 |  |
| all threatened routes | threatened routes Southwest later entered | 227.0000 |  |
| all threatened routes | never-threatened control routes | 2982.0000 |  |
| excluding threats that began in 2021 | avg threat effect, years 0..+3 (log points) | -0.0699 | 0.0093 |
| excluding threats that began in 2021 | additional effect once Southwest flies the route (log points) | 0.0096 | 0.0149 |
| excluding threats that began in 2021 | threat plus entry, years 0..+3 (log points) | -0.0604 |  |
| excluding threats that began in 2021 | threatened routes | 271.0000 |  |
| excluding threats that began in 2021 | threatened routes Southwest later entered | 156.0000 |  |
| excluding threats that began in 2021 | never-threatened control routes | 2982.0000 |  |

### southwest_threat_onsets.csv

| onset_year | routes |
|---|---|
| 2016 | 11 |
| 2017 | 28 |
| 2019 | 137 |
| 2020 | 64 |
| 2021 | 236 |
| 2022 | 30 |
| 2023 | 1 |

### southwest_threat_airports.csv

| airport | threatened_routes |
|---|---|
| ORD | 73 |
| MIA | 68 |
| IAH | 61 |
| HNL | 58 |
| OGG | 39 |
| CVG | 36 |
| KOA | 28 |
| LIH | 28 |
| SYR | 21 |
| SAV | 20 |
| BOS | 19 |
| SFO | 19 |

### southwest_new_airports.csv

| airport | first_year_present |
|---|---|
| LGB | 2016 |
| CVG | 2017 |
| LIH | 2019 |
| HNL | 2019 |
| KOA | 2019 |
| OGG | 2019 |
| ITO | 2020 |
| MIA | 2020 |
| SRQ | 2021 |
| SBA | 2021 |
| SAV | 2021 |
| PSP | 2021 |
| ORD | 2021 |
| MYR | 2021 |
| BLI | 2021 |
| IAH | 2021 |
| FAT | 2021 |
| EUG | 2021 |
| COS | 2021 |
| BZN | 2021 |
| MTJ | 2021 |
| VPS | 2021 |
| SYR | 2022 |

### southwest_threat_routes.csv

| route | threat_year | biggest_incumbent | year_before | fare_before | year_after | fare_after | change_pct | control_change_pct | southwest_entered |
|---|---|---|---|---|---|---|---|---|---|
| CVG-MCO | 2017 | Delta | 2016 | 187.38 | 2018 | 173.94 | -7.2 | -0.7 | 2020 |
| LGB-SLC | 2016 | JetBlue | 2015 | 174.07 | 2017 | 143.56 | -17.5 | -7.7 | 2021 |
| CVG-LAS | 2017 | Delta | 2016 | 197.60 | 2018 | 171.30 | -13.3 | -0.7 | 2020 |
| CVG-DEN | 2017 | Frontier | 2016 | 238.08 | 2018 | 185.58 | -22.1 | -0.7 | 2018 |
| CVG-LGA | 2017 | Delta | 2016 | 348.35 | 2018 | 220.02 | -36.8 | -0.7 |  |
| CVG-FLL | 2017 | Delta | 2016 | 202.45 | 2018 | 176.88 | -12.6 | -0.7 |  |
| CVG-LAX | 2017 | Delta | 2016 | 357.99 | 2018 | 275.15 | -23.1 | -0.7 | 2020 |
| CVG-EWR | 2017 | United | 2016 | 332.03 | 2018 | 223.81 | -32.6 | -0.7 |  |
| ATL-CVG | 2017 | Delta | 2016 | 343.41 | 2018 | 269.32 | -21.6 | -0.7 |  |
| CVG-TPA | 2017 | Delta | 2016 | 253.32 | 2018 | 203.38 | -19.7 | -0.7 | 2020 |
| BOS-CVG | 2017 | Delta | 2016 | 433.94 | 2018 | 347.87 | -19.8 | -0.7 | 2020 |
| CVG-RSW | 2017 | Delta | 2016 | 208.19 | 2018 | 185.32 | -11.0 | -0.7 |  |

