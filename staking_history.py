"""
Reconstruct the Ethereum staked-ETH balance, staking ratio and consensus-layer APR
month by month from on-chain flows, then compare against ETH price.

Identity:  beacon_balance(t) = beacon_balance(t-1) + deposits(t) - withdrawals(t) + issuance(t)
  deposits    : ETH sent to the beacon deposit contract 0x0000...705Fa   (Dune, ethereum.traces)
  withdrawals : ethereum.withdrawals                                     (Dune)
  issuance    : 166.28 * sqrt(balance) ETH/yr, the protocol's own reward curve

The reconstruction is validated against the independently reported 41.9M ETH staked
(Aug 2026) and ~897k active validators.
"""
import math, csv, io

K = 940.9 / math.sqrt(32)   # 166.28

DEPOSITS_CSV = """2020-11,865696
2020-12,1305058
2021-01,719840
2021-02,431136
2021-03,300512
2021-04,454688
2021-05,1133664
2021-06,795872
2021-07,466496
2021-08,807808
2021-09,539680
2021-10,271008
2021-11,360000
2021-12,387536
2022-01,432368
2022-02,385488
2022-03,1330368
2022-04,1090896
2022-05,659075
2022-06,247232
2022-07,204208
2022-08,224901
2022-09,666541
2022-10,598672
2022-11,769792
2022-12,406256
2023-01,519408
2023-02,1032160
2023-03,605056
2023-04,1673359
2023-05,3821111
2023-06,2381457
2023-07,1767551
2023-08,1584386
2023-09,1244327
2023-10,1482337
2023-11,1720825
2023-12,1785533
2024-01,2028361
2024-02,2801380
2024-03,2306467
2024-04,1637856
2024-05,1261505
2024-06,1535908
2024-07,1805566
2024-08,1233420
2024-09,1037332
2024-10,1560359
2024-11,1276919
2024-12,1359585
2025-01,1348781
2025-02,1091912
2025-03,1699680
2025-04,1263682
2025-05,1559012
2025-06,1729741
2025-07,1730981
2025-08,2293437
2025-09,1185655
2025-10,3130412
2025-11,873591
2025-12,1992961
2026-01,4921717
2026-02,1064097
2026-03,1239922
2026-04,2261198
2026-05,1451672
2026-06,1461081
2026-07,1383289"""

WITHDRAWALS_CSV = """2023-04,1962919
2023-05,987217
2023-06,579120
2023-07,340636
2023-08,374175
2023-09,399684
2023-10,779471
2023-11,1109825
2023-12,1580502
2024-01,1493311
2024-02,1097653
2024-03,1622853
2024-04,1294087
2024-05,1197264
2024-06,1031643
2024-07,1091583
2024-08,1063215
2024-09,792772
2024-10,1382441
2024-11,1601156
2024-12,1891662
2025-01,1642989
2025-02,1293106
2025-03,1242851
2025-04,1424545
2025-05,1371398
2025-06,719981
2025-07,1166995
2025-08,1894076
2025-09,1858217
2025-10,1892434
2025-11,1743999
2025-12,2027156
2026-01,1023442
2026-02,911464
2026-03,761352
2026-04,1192307
2026-05,1493034
2026-06,1047591
2026-07,792623"""

def parse(s):
    return {r.split(',')[0]: float(r.split(',')[1]) for r in s.strip().splitlines()}

dep, wd = parse(DEPOSITS_CSV), parse(WITHDRAWALS_CSV)
months = sorted(dep)

DAYS = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

bal = 0.0
rows = []
for m in months:
    y, mm_ = int(m[:4]), int(m[5:])
    d = DAYS[mm_] + (1 if (mm_ == 2 and y % 4 == 0) else 0)
    iss = K * math.sqrt(bal) * d / 365.25 if bal > 0 else 0.0
    bal = bal + dep[m] - wd.get(m, 0.0) + iss
    apr = K / math.sqrt(bal) if bal > 0 else 0.0
    rows.append((m, bal, apr, iss * 365.25 / d))

print(f"{'month':>8} {'staked ETH':>13} {'CL APR':>8} {'ann. issuance':>14}")
for m, b, a, i in rows:
    if m >= "2023-01" and (m.endswith(("-01", "-04", "-07", "-10")) or m == months[-1]):
        print(f"{m:>8} {b:13,.0f} {a*100:7.2f}% {i:14,.0f}")

print()
print(f"reconstructed staked ETH, 2026-07 : {rows[-1][1]:,.0f}")
print(f"reported staked ETH,      2026-08 : 41,900,000")
print(f"error                             : {(rows[-1][1]/41_900_000-1)*100:+.1f}%")
print(f"reconstructed CL APR              : {rows[-1][2]*100:.2f}%  (reported total APR 2.78% incl. EL)")

with open("staked_eth_reconstructed.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["month", "staked_eth", "cl_apr", "annualised_issuance_eth"])
    for m, b, a, i in rows:
        w.writerow([m, round(b), round(a, 6), round(i)])
print("\nwrote staked_eth_reconstructed.csv")
