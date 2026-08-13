"""
Does ETH's staking yield explain ETH's price?

Inputs
  staked_eth_reconstructed.csv : on-chain reconstruction (see staking_history.py)
  eth_monthly.csv, btc_monthly.csv : CoinGecko daily closes collapsed to month-end.

The test the draft asks for -- "correlation between ETH price and staking yield" --
is run three ways, because the naive version is a trap: the consensus-layer APR is a
deterministic function of the staked balance (APR = 166.28 / sqrt(S)), so it is a
near-monotone series with almost no independent variation. Correlating a monotone
series against a mean-reverting one measures the trend, not the relationship.

This file reports correlations. `regression_analysis.py` runs the same relationships
as regressions, with standard errors, p-values, Durbin-Watson and a power calculation.
"""
import csv, math


def monthly(path, col):
    return {r["month"]: float(r[col]) for r in csv.DictReader(open(path))}


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def spearman(a, b):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos + 1
        return r
    return pearson(rank(a), rank(b))


eth = monthly("eth_monthly.csv", "eth_usd")
btc = monthly("btc_monthly.csv", "btc_usd")
rows = list(csv.DictReader(open("staked_eth_reconstructed.csv")))
data = [(r["month"], float(r["staked_eth"]), float(r["cl_apr"]), eth[r["month"]], btc[r["month"]])
        for r in rows if r["month"] in eth and r["month"] in btc]

months  = [d[0] for d in data]
staked  = [d[1] for d in data]
apr     = [d[2] for d in data]
px_eth  = [d[3] for d in data]
ethbtc  = [d[3] / d[4] for d in data]

print(f"sample: {months[0]} .. {months[-1]}  ({len(months)} months)")
print(f"staking APR range: {max(apr)*100:.2f}%  ->  {min(apr)*100:.2f}%   "
      f"(monotone decline, {sum(1 for i in range(1,len(apr)) if apr[i]<apr[i-1])}/{len(apr)-1} months down)")
print(f"ETH price range:   ${min(px_eth):,.0f} .. ${max(px_eth):,.0f}")
print()

print("--- 1. levels (the naive test the draft asks for) ---")
print(f"  corr(APR, ETH price)     Pearson {pearson(apr, px_eth):+.3f}   Spearman {spearman(apr, px_eth):+.3f}")
print(f"  corr(APR, ETH/BTC)       Pearson {pearson(apr, ethbtc):+.3f}   Spearman {spearman(apr, ethbtc):+.3f}")
print("  -> both are trend artefacts. APR fell in a near-straight line while ETH round-tripped.")
print()

print("--- 2. monthly changes (removes the trend) ---")
d_apr = [apr[i] - apr[i-1] for i in range(1, len(apr))]
r_eth = [px_eth[i] / px_eth[i-1] - 1 for i in range(1, len(px_eth))]
r_eb  = [ethbtc[i] / ethbtc[i-1] - 1 for i in range(1, len(ethbtc))]
print(f"  corr(dAPR, ETH return)   Pearson {pearson(d_apr, r_eth):+.3f}   Spearman {spearman(d_apr, r_eth):+.3f}")
print(f"  corr(dAPR, ETH/BTC ret)  Pearson {pearson(d_apr, r_eb):+.3f}   Spearman {spearman(d_apr, r_eb):+.3f}")
print()

print("--- 3. the reverse causality check: does price drive staking, or staking drive yield? ---")
r_stk = [staked[i] / staked[i-1] - 1 for i in range(1, len(staked))]
print(f"  corr(ETH return, staked growth, same month) {pearson(r_eth, r_stk):+.3f}")
lag = pearson(r_eth[:-1], r_stk[1:])
print(f"  corr(ETH return t, staked growth t+1)       {lag:+.3f}")
print(f"  corr(staked growth t, ETH return t+1)       {pearson(r_stk[:-1], r_eth[1:]):+.3f}")
print()

print("--- 4. yield vs ETH/BTC, the question that actually matters ---")
print(f"  {'month':>8} {'CL APR':>7} {'ETH/BTC':>9} {'ETH $':>9}")
for i, m in enumerate(months):
    if m.endswith(("-01", "-07")) or i == len(months) - 1:
        print(f"  {m:>8} {apr[i]*100:6.2f}% {ethbtc[i]:9.5f} {px_eth[i]:9,.0f}")
print()
print(f"  ETH/BTC {months[0]}: {ethbtc[0]:.5f}   {months[-1]}: {ethbtc[-1]:.5f}   "
      f"change {(ethbtc[-1]/ethbtc[0]-1)*100:+.1f}%")
print(f"  staking APR over the same window: {apr[0]*100:.2f}% -> {apr[-1]*100:.2f}%")
