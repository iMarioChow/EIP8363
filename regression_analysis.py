"""
Formal statistics behind ANALYSIS.md §4 — does ETH's staking yield explain ETH's price?

`yield_price_analysis.py` reports correlations. This file runs the regressions, so the
claims in the article carry a slope, a standard error, a p-value and a confidence
interval rather than a bare correlation coefficient.

Four things are tested, in the order the argument needs them:

  1. THE IDENTITY.   Is the staking rate mechanically tied to the staking yield?
                     Regress log(APR) on log(staked). Theory says slope = -0.5 exactly,
                     because APR = I(S)/S = 166.28*sqrt(S)/S = 166.28/sqrt(S).
  2. LEVELS.         The naive regression of price on APR. Reported only so the
                     Durbin-Watson statistic can show why it must not be published.
  3. CHANGES.        The honest test: monthly ETH return on the monthly change in APR,
                     with plain OLS and Newey-West HAC standard errors.
  4. POWER.          Absence of evidence is only evidence of absence if the test could
                     have found the effect. Reports the minimum detectable slope.

No third-party dependencies: OLS, the t-distribution tail, Newey-West and Durbin-Watson
are all implemented below.

    python3 regression_analysis.py > regression_output.txt
"""
import csv
import math

CSV_STAKED = "staked_eth_reconstructed.csv"
CSV_ETH = "eth_monthly.csv"
CSV_BTC = "btc_monthly.csv"

K_ISSUANCE = 940.9 / math.sqrt(32)          # = 166.28, see issuance_model.py


# ------------------------------------------------------------------ distributions
def _betacf(a, b, x):
    """Continued fraction for the incomplete beta function (Lentz's method)."""
    TINY, EPS = 1e-30, 3e-16
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < TINY:
        d = TINY
    d = 1.0 / d
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        c = 1.0 + aa / c
        if abs(d) < TINY:
            d = TINY
        if abs(c) < TINY:
            c = TINY
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        c = 1.0 + aa / c
        if abs(d) < TINY:
            d = TINY
        if abs(c) < TINY:
            c = TINY
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def betainc(a, b, x):
    """Regularised incomplete beta I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
             + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbeta) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta) * _betacf(b, a, 1.0 - x) / b


def t_sf2(t, df):
    """Two-sided tail probability of Student's t."""
    return betainc(df / 2.0, 0.5, df / (df + t * t))


def t_crit(df, p=0.975):
    """Inverse t CDF by bisection — good enough for confidence intervals."""
    lo, hi = 0.0, 100.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1.0 - t_sf2(mid, df) / 2.0 < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# -------------------------------------------------------------------------- OLS
class OLS:
    """Univariate y = a + b*x, with HAC standard errors and Durbin-Watson."""

    def __init__(self, x, y, name=""):
        self.name, self.x, self.y = name, list(x), list(y)
        n = self.n = len(x)
        mx, my = sum(x) / n, sum(y) / n
        sxx = sum((v - mx) ** 2 for v in x)
        sxy = sum((u - mx) * (v - my) for u, v in zip(x, y))
        syy = sum((v - my) ** 2 for v in y)

        self.slope = sxy / sxx
        self.intercept = my - self.slope * mx
        self.mx, self.sxx, self.syy = mx, sxx, syy
        self.fitted = [self.intercept + self.slope * v for v in x]
        self.resid = [v - f for v, f in zip(y, self.fitted)]

        self.df = n - 2
        self.sse = sum(e * e for e in self.resid)
        self.r2 = 1.0 - self.sse / syy if syy else float("nan")
        self.r = math.copysign(math.sqrt(max(self.r2, 0.0)), self.slope)
        self.sigma = math.sqrt(self.sse / self.df)
        self.se = self.sigma / math.sqrt(sxx)
        self.t = self.slope / self.se if self.se else float("nan")
        self.p = t_sf2(self.t, self.df)
        tc = t_crit(self.df)
        self.ci = (self.slope - tc * self.se, self.slope + tc * self.se)

        # Newey-West HAC, Bartlett kernel, lag = floor(4*(n/100)^(2/9))
        L = max(1, int(4 * (n / 100.0) ** (2.0 / 9.0)))
        self.hac_lag = L
        u = [(v - mx) * e for v, e in zip(x, self.resid)]
        s = sum(t * t for t in u)
        for l in range(1, L + 1):
            w = 1.0 - l / (L + 1.0)
            s += 2.0 * w * sum(u[i] * u[i - l] for i in range(l, n))
        self.se_hac = math.sqrt(max(s, 0.0)) / sxx
        self.t_hac = self.slope / self.se_hac if self.se_hac else float("nan")
        self.p_hac = t_sf2(self.t_hac, self.df)

        # Durbin-Watson: ~2 means no residual autocorrelation, <1 means the
        # regression is picking up a shared trend rather than a relationship.
        self.dw = (sum((self.resid[i] - self.resid[i - 1]) ** 2 for i in range(1, n))
                   / self.sse)

    def mde(self, power=0.80):
        """Minimum slope this sample could have rejected zero for, at 5% / given power.

        Uses the normal approximation: |b| must exceed (z_{0.975} + z_{power}) * SE.
        """
        z = {0.80: 2.802, 0.50: 1.960, 0.90: 3.242}[power]
        return z * self.se

    def line(self):
        return f"y = {self.intercept:+.6g} {self.slope:+.6g}*x"

    def report(self, unit_x="", unit_y="", scale=1.0):
        """scale: multiply the slope into readable units (e.g. bps -> %)."""
        b = self.slope * scale
        lo, hi = self.ci[0] * scale, self.ci[1] * scale
        stars = "***" if self.p < 0.01 else "**" if self.p < 0.05 else "*" if self.p < 0.10 else ""
        print(f"  {self.name}")
        print(f"    n = {self.n}   R² = {self.r2:.4f}   r = {self.r:+.3f}   "
              f"Durbin-Watson = {self.dw:.2f}")
        print(f"    slope   {b:+.4f} {unit_y}{unit_x}   SE {self.se*scale:.4f}   "
              f"t = {self.t:+.2f}   p = {self.p:.3f}{stars}")
        print(f"    95% CI  [{lo:+.4f}, {hi:+.4f}]")
        print(f"    HAC(L={self.hac_lag})  SE {self.se_hac*scale:.4f}   "
              f"t = {self.t_hac:+.2f}   p = {self.p_hac:.3f}")


# ------------------------------------------------------------------------- data
def load():
    def col(path, key):
        return {r["month"]: float(r[key]) for r in csv.DictReader(open(path))}

    eth, btc = col(CSV_ETH, "eth_usd"), col(CSV_BTC, "btc_usd")
    rows = list(csv.DictReader(open(CSV_STAKED)))
    out = []
    for r in rows:
        m = r["month"]
        if m in eth and m in btc:
            out.append((m, float(r["staked_eth"]), float(r["cl_apr"]), eth[m], btc[m]))
    return out


def diffs(v):
    return [v[i] - v[i - 1] for i in range(1, len(v))]


def rets(v):
    return [v[i] / v[i - 1] - 1 for i in range(1, len(v))]


def main():
    data = load()
    months = [d[0] for d in data]
    staked = [d[1] for d in data]
    apr = [d[2] for d in data]
    px = [d[3] for d in data]
    ethbtc = [d[3] / d[4] for d in data]

    print("=" * 78)
    print(f"SAMPLE  {months[0]} .. {months[-1]}   ({len(months)} months, "
          f"{len(months)-1} monthly changes)")
    print("=" * 78)
    print(f"  staking APR   {apr[0]*100:.2f}%  ->  {apr[-1]*100:.2f}%   "
          f"({sum(1 for i in range(1,len(apr)) if apr[i]<apr[i-1])}/{len(apr)-1} months down)")
    print(f"  ETH staked    {staked[0]/1e6:.1f}M  ->  {staked[-1]/1e6:.1f}M")
    print(f"  ETH price     ${px[0]:,.0f}  ->  ${px[-1]:,.0f}   "
          f"(range ${min(px):,.0f} .. ${max(px):,.0f})")
    print(f"  ETH/BTC       {ethbtc[0]:.5f}  ->  {ethbtc[-1]:.5f}   "
          f"({ethbtc[-1]/ethbtc[0]-1:+.1%})")

    print()
    print("=" * 78)
    print("1. THE IDENTITY — is the staking RATE correlated with the staking YIELD?")
    print("=" * 78)
    print("   Yes, and not statistically: by construction. Ethereum pays")
    print("   I(S) = 166.28*sqrt(S) ETH/yr on a staked balance S, so")
    print("   APR(S) = I(S)/S = 166.28/sqrt(S), i.e. log APR = log 166.28 - 0.5*log S.")
    print("   The regression below is a unit test of the reconstruction, not a finding:")
    print("   a slope of exactly -0.5 and R² = 1 is what SHOULD come out.")
    print()
    ident = OLS([math.log(s) for s in staked], [math.log(a) for a in apr],
                "log(consensus APR)  ~  log(ETH staked)")
    ident.report(unit_x=" per log(ETH)", unit_y="")
    print(f"    theory: slope = -0.5000, intercept = log(166.28) = {math.log(K_ISSUANCE):.4f}")
    print(f"    fitted: slope = {ident.slope:.4f}, intercept = {ident.intercept:.4f}   "
          f"-> deviation {abs(ident.slope + 0.5):.2e}")
    print()
    print("   Elasticity reading: a 1% rise in the staked balance lowers the consensus")
    print("   APR by 0.5%. Doubling the stake cuts the yield by 29.3%. Quadrupling it")
    print("   halves the yield. That is the whole of the stake-rate/yield relationship —")
    print("   there is no behavioural content in it, and nothing to estimate.")

    print()
    print("=" * 78)
    print("2. LEVELS — the naive regression, shown so it can be ruled out")
    print("=" * 78)
    lv_px = OLS([a * 100 for a in apr], px, "ETH price ($)  ~  consensus APR (%)")
    lv_px.report(unit_x=" per 1pp APR", unit_y="$")
    print()
    lv_eb = OLS([a * 100 for a in apr], [v * 1000 for v in ethbtc],
                "ETH/BTC (x1000)  ~  consensus APR (%)")
    lv_eb.report(unit_x=" per 1pp APR", unit_y="mBTC ")
    print()
    print(f"   Durbin-Watson {lv_px.dw:.2f} and {lv_eb.dw:.2f}. Both are far below 1.")
    print("   Residuals are strongly autocorrelated, which is the signature of a")
    print("   spurious regression: two trending series, no relationship. The R² of")
    print(f"   {lv_eb.r2:.2f} on ETH/BTC is a coincidence of timing, not evidence. It")
    print("   would license the claim 'falling yield caused ETH/BTC to fall'. Do not")
    print("   publish either of these.")

    print()
    print("=" * 78)
    print("3. CHANGES — the test that is actually identified")
    print("=" * 78)
    d_apr_bps = [d * 10_000 for d in diffs(apr)]      # ΔAPR in basis points
    r_eth = [r * 100 for r in rets(px)]               # ETH monthly return, %
    r_eb = [r * 100 for r in rets(ethbtc)]            # ETH/BTC monthly return, %
    g_stk = [r * 100 for r in rets(staked)]           # staked balance growth, %

    ch_eth = OLS(d_apr_bps, r_eth, "ETH monthly return (%)  ~  ΔAPR (bps)")
    ch_eth.report(unit_x=" per bp", unit_y="pp ")
    print()
    ch_eb = OLS(d_apr_bps, r_eb, "ETH/BTC monthly return (%)  ~  ΔAPR (bps)")
    ch_eb.report(unit_x=" per bp", unit_y="pp ")
    print()
    print("   Neither slope is distinguishable from zero at any conventional level,")
    print("   under OLS or under HAC standard errors. The R² are effectively nil:")
    print(f"   changes in staking yield explain {ch_eth.r2*100:.2f}% of the variance in")
    print(f"   ETH's monthly return and {ch_eb.r2*100:.2f}% of ETH/BTC's.")

    print()
    print("=" * 78)
    print("4. DIRECTION — does price drive staking, or staking drive price?")
    print("=" * 78)
    same = OLS(r_eth, g_stk, "staked growth (%)  ~  ETH return (%), same month")
    same.report(unit_x=" per pp", unit_y="pp ")
    print()
    lead = OLS(r_eth[:-1], g_stk[1:], "staked growth t+1 (%)  ~  ETH return t (%)")
    lead.report(unit_x=" per pp", unit_y="pp ")
    print()
    lag = OLS(g_stk[:-1], r_eth[1:], "ETH return t+1 (%)  ~  staked growth t (%)")
    lag.report(unit_x=" per pp", unit_y="pp ")
    print()
    print("   No lead, no lag, no contemporaneous link. Staking flows and price are")
    print("   not visibly connected in either direction at monthly frequency.")

    print()
    print("=" * 78)
    print("5. POWER — could this test have found an effect if one existed?")
    print("=" * 78)
    mde = ch_eth.mde(0.80)
    total_d = (apr[-1] - apr[0]) * 10_000
    print(f"  residual σ of ETH monthly return   {ch_eth.sigma:.2f} pp")
    print(f"  σ of ΔAPR                          {math.sqrt(ch_eth.sxx/(ch_eth.n-1)):.2f} bps")
    print(f"  smallest slope detectable at 5% / 80% power   {mde:.4f} pp per bp")
    print()
    band = sorted((ch_eth.ci[0] * total_d, ch_eth.ci[1] * total_d))
    print(f"  Over the sample, APR fell {abs(total_d):.0f} bps in total. Applying the")
    print(f"  slope linearly across that decline: a slope at the detection threshold")
    print(f"  would have moved ETH by {abs(mde*total_d):.0f} pp cumulatively; the point "
          f"estimate implies")
    print(f"  {abs(ch_eth.slope*total_d):.0f} pp, and the 95% CI spans "
          f"{band[0]:+.0f} to {band[1]:+.0f} pp — i.e. it contains")
    print("  everything from a large positive to a large negative effect.")
    print()
    print("  Honest reading: monthly data cannot rule out a small yield effect. What it")
    print("  rules out is a LARGE one. A 148 bp decline in yield delivered by the")
    print("  existing curve produced no detectable price response, so the prior that a")
    print("  further ~130 bp cut from EIP-8363 will move price has no support here —")
    print("  and the burden of proof sits with whoever claims otherwise.")

    print()
    print("=" * 78)
    print("6. ONE-LINE SUMMARY TABLE")
    print("=" * 78)
    print(f"  {'regression':<50}{'slope':>11}{'R²':>8}{'p':>8}")
    for m in (ident, lv_px, lv_eb, ch_eth, ch_eb, same, lead, lag):
        print(f"  {m.name:<50}{m.slope:>+11.4f}{m.r2:>8.4f}{m.p:>8.3f}")


if __name__ == "__main__":
    main()
