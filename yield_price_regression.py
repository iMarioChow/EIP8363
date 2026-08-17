"""
Regression analysis of ETH price against staking yield, and the charts for it.

Runs OLS in levels and in changes, reports slope / t / p / R-squared, and renders
three figures to charts/. Pure standard library: the t-distribution p-value uses an
incomplete-beta continued fraction rather than scipy.

    python3 yield_price_regression.py

Inputs
    staked_eth_reconstructed.csv   month, staked_eth, cl_apr   (staking_history.py)
    eth_monthly.csv                month, eth_usd              (CoinGecko month-end)
    btc_monthly.csv                month, btc_usd              (CoinGecko month-end)
"""
import csv, math, os

OUT = "charts"

# --------------------------------------------------------------------- stats
def mean(v):
    return sum(v) / len(v)


def pearson(a, b):
    ma, mb = mean(a), mean(b)
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def _betacf(a, b, x, itmax=200, eps=3e-12):
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    for m in range(1, itmax + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        c = 1.0 + aa / c
        if abs(d) < 1e-30: d = 1e-30
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        c = 1.0 + aa / c
        if abs(d) < 1e-30: d = 1e-30
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def _betai(a, b, x):
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    lb = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
          + a * math.log(x) + b * math.log(1.0 - x))
    bt = math.exp(lb)
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def t_pvalue(t, df):
    """Two-sided p-value for a t statistic."""
    return _betai(0.5 * df, 0.5, df / (df + t * t))


def ols(x, y):
    """Simple regression y = a + b*x. Returns a dict of the usual diagnostics."""
    n = len(x)
    mx, my = mean(x), mean(y)
    sxx = sum((v - mx) ** 2 for v in x)
    b = sum((u - mx) * (v - my) for u, v in zip(x, y)) / sxx
    a = my - b * mx
    resid = [v - (a + b * u) for u, v in zip(x, y)]
    sse = sum(r * r for r in resid)
    sst = sum((v - my) ** 2 for v in y)
    df = n - 2
    se_b = math.sqrt(sse / df / sxx)
    t = b / se_b if se_b else float("inf")
    return {"a": a, "b": b, "se_b": se_b, "t": t, "p": t_pvalue(t, df),
            "r2": 1 - sse / sst, "r": pearson(x, y), "n": n, "df": df,
            "ci": (b - 2.02 * se_b, b + 2.02 * se_b),
            "resid_sd": math.sqrt(sse / df)}


def durbin_watson(x, y, fit):
    r = [v - (fit["a"] + fit["b"] * u) for u, v in zip(x, y)]
    return sum((r[i] - r[i - 1]) ** 2 for i in range(1, len(r))) / sum(v * v for v in r)


# ---------------------------------------------------------------------- data
def load():
    eth = {r["month"]: float(r["eth_usd"]) for r in csv.DictReader(open("eth_monthly.csv"))}
    btc = {r["month"]: float(r["btc_usd"]) for r in csv.DictReader(open("btc_monthly.csv"))}
    rows = [r for r in csv.DictReader(open("staked_eth_reconstructed.csv"))
            if r["month"] in eth and r["month"] in btc]
    return ([r["month"] for r in rows],
            [float(r["cl_apr"]) for r in rows],
            [eth[r["month"]] for r in rows],
            [eth[r["month"]] / btc[r["month"]] for r in rows])


# -------------------------------------------------------------------- charts
W, H = 880, 510
STYLE = """<style>
  .s{fill:var(--surface)}
  text{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}
  .ti{fill:var(--ink);font-size:17px;font-weight:600}
  .sub{fill:var(--ink2);font-size:12.5px}
  .ax{fill:var(--ink2);font-size:11.5px}
  .axt{fill:var(--ink2);font-size:11.5px;font-weight:600}
  .grid{stroke:var(--rule);stroke-width:1}
  .zero{stroke:var(--rule2);stroke-width:1.5}
  .note{fill:var(--ink2);font-size:11px}
  .stat{fill:var(--ink);font-size:12px}
  .statk{fill:var(--ink2);font-size:12px}
  .pt1{fill:var(--s1);stroke:var(--surface);stroke-width:1.5}
  .pt2{fill:var(--s2);stroke:var(--surface);stroke-width:1.5}
  .fit1{fill:none;stroke:var(--s1);stroke-width:2}
  .fit2{fill:none;stroke:var(--s2);stroke-width:2}
  .band{fill:var(--s2);opacity:0.12}
  .lab1{fill:var(--s1);font-size:12.5px;font-weight:600}
  .lab2{fill:var(--s2);font-size:12.5px;font-weight:600}
  :root{--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--rule:#e7e6e2;--rule2:#a9a8a2;
        --s1:#2a78d6;--s2:#eb6834}
  @media (prefers-color-scheme:dark){:root{
        --surface:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--rule:#2e2e2c;--rule2:#6a6a64;
        --s1:#3987e5;--s2:#d95926}}
</style>"""


def svg(body, w=W, h=H):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img">{STYLE}<rect width="{w}" height="{h}" class="s"/>'
            f'{body}</svg>')


def wrap(text, width=118):
    """Greedy wrap into lines of at most `width` characters."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def footer(p, text, x, y):
    for i, line in enumerate(wrap(text)):
        p.append(f'<text x="{x}" y="{y + i * 15}" class="note">{line}</text>')


def scatter(title, sub, xs, ys, fit, xlab, ylab, xfmt, yfmt, cls, foot,
            xticks=None, yticks=None):
    L, R, T, B = 74, 210, 58, 108
    PW, PH = W - L - R, H - T - B
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    padx, pady = (x1 - x0) * 0.08, (y1 - y0) * 0.08
    x0, x1, y0, y1 = x0 - padx, x1 + padx, y0 - pady, y1 + pady
    px = lambda v: L + (v - x0) / (x1 - x0) * PW
    py = lambda v: T + PH - (v - y0) / (y1 - y0) * PH

    p = [f'<text x="{L}" y="26" class="ti">{title}</text>',
         f'<text x="{L}" y="45" class="sub">{sub}</text>']
    xticks = xticks or [x0 + (x1 - x0) * i / 4 for i in range(5)]
    yticks = yticks or [y0 + (y1 - y0) * i / 4 for i in range(5)]
    for v in yticks:
        p.append(f'<line x1="{L}" y1="{py(v):.1f}" x2="{L+PW}" y2="{py(v):.1f}" class="grid"/>')
        p.append(f'<text x="{L-9}" y="{py(v)+4:.1f}" class="ax" text-anchor="end">{yfmt(v)}</text>')
    for v in xticks:
        p.append(f'<text x="{px(v):.1f}" y="{T+PH+20:.1f}" class="ax" text-anchor="middle">{xfmt(v)}</text>')
    p.append(f'<text x="{L+PW/2:.0f}" y="{T+PH+42:.0f}" class="axt" text-anchor="middle">{xlab}</text>')
    p.append(f'<text x="18" y="{T+PH/2:.0f}" class="axt" text-anchor="middle" '
             f'transform="rotate(-90 18 {T+PH/2:.0f})">{ylab}</text>')

    if y0 < 0 < y1:
        p.append(f'<line x1="{L}" y1="{py(0):.1f}" x2="{L+PW}" y2="{py(0):.1f}" class="zero"/>')
    if x0 < 0 < x1:
        p.append(f'<line x1="{px(0):.1f}" y1="{T}" x2="{px(0):.1f}" y2="{T+PH}" class="zero"/>')

    # 1-sigma band around the fit, then the fit, then the points
    band = ([f"{px(x0):.1f},{py(fit['a']+fit['b']*x0+fit['resid_sd']):.1f}",
             f"{px(x1):.1f},{py(fit['a']+fit['b']*x1+fit['resid_sd']):.1f}",
             f"{px(x1):.1f},{py(fit['a']+fit['b']*x1-fit['resid_sd']):.1f}",
             f"{px(x0):.1f},{py(fit['a']+fit['b']*x0-fit['resid_sd']):.1f}"])
    p.append(f'<polygon points="{" ".join(band)}" class="band"/>')
    p.append(f'<line x1="{px(x0):.1f}" y1="{py(fit["a"]+fit["b"]*x0):.1f}" '
             f'x2="{px(x1):.1f}" y2="{py(fit["a"]+fit["b"]*x1):.1f}" class="fit{cls}"/>')
    for u, v in zip(xs, ys):
        p.append(f'<circle cx="{px(u):.1f}" cy="{py(v):.1f}" r="4.5" class="pt{cls}"/>')

    sx = L + PW + 22
    p.append(f'<text x="{sx}" y="{T+14}" class="lab{cls}">OLS fit</text>')
    stats = [("n", f"{fit['n']}"),
             ("slope", f"{fit['b']:+.3g}"),
             ("95% CI", f"[{fit['ci'][0]:+.2g}, {fit['ci'][1]:+.2g}]"),
             ("t", f"{fit['t']:+.2f}"),
             ("p", f"{fit['p']:.2f}" if fit['p'] >= 0.01 else f"{fit['p']:.1e}"),
             ("R²", f"{fit['r2']:.3f}"),
             ("r", f"{fit['r']:+.3f}")]
    for i, (k, v) in enumerate(stats):
        y = T + 38 + i * 19
        p.append(f'<text x="{sx}" y="{y}" class="statk">{k}</text>')
        p.append(f'<text x="{W-30}" y="{y}" class="stat" text-anchor="end">{v}</text>')
    footer(p, foot, L, T + PH + 66)
    return svg("".join(p))


def rolling_chart(months, dapr, reth, win=12):
    L, R, T, B = 68, 30, 58, 100
    PW, PH = W - L - R, H - T - B
    pts = []
    for i in range(win, len(dapr) + 1):
        pts.append((months[i], pearson(dapr[i - win:i], reth[i - win:i])))
    n = len(pts)
    px = lambda i: L + i / (n - 1) * PW
    py = lambda v: T + PH / 2 - v * PH / 2
    crit = 2.0 / math.sqrt(win)          # ~95% band for r under the null of zero

    p = [f'<text x="{L}" y="26" class="ti">The relationship never stabilises</text>',
         f'<text x="{L}" y="45" class="sub">Rolling {win}-month correlation between the '
         f'monthly change in staking yield and ETH’s monthly return.</text>']
    p.append(f'<rect x="{L}" y="{py(crit):.1f}" width="{PW}" height="{py(-crit)-py(crit):.1f}" '
             f'class="band"/>')
    for v in (-1, -0.5, 0, 0.5, 1):
        p.append(f'<line x1="{L}" y1="{py(v):.1f}" x2="{L+PW}" y2="{py(v):.1f}" '
                 f'class="{"zero" if v == 0 else "grid"}"/>')
        p.append(f'<text x="{L-9}" y="{py(v)+4:.1f}" class="ax" text-anchor="end">{v:+.1f}</text>')
    p.append("<path d=\"M" + "L".join(f"{px(i):.1f},{py(v):.1f}" for i, (_, v) in enumerate(pts))
             + '" class="fit1"/>')
    for i, (m, _) in enumerate(pts):
        if m.endswith("-01") or m.endswith("-07"):
            p.append(f'<text x="{px(i):.1f}" y="{T+PH+20:.1f}" class="ax" '
                     f'text-anchor="middle">{m}</text>')
    inside = sum(1 for _, v in pts if abs(v) < crit)
    p.append(f'<text x="{L+PW-6}" y="{py(crit)-8:.1f}" class="note" text-anchor="end">'
             f'shaded = indistinguishable from zero (95%). {inside} of {n} windows sit inside.</text>')
    footer(p, 'A real relationship would hold its sign. This one crosses zero repeatedly and '
              'spends most of its life inside the band where the correlation cannot be '
              'distinguished from zero.', L, T + PH + 46)
    return svg("".join(p))


# ----------------------------------------------------------------------- run
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    months, apr, eth, ethbtc = load()

    lv = ols([a * 100 for a in apr], eth)
    dapr = [(apr[i] - apr[i - 1]) * 10000 for i in range(1, len(apr))]        # bps
    reth = [(eth[i] / eth[i - 1] - 1) * 100 for i in range(1, len(eth))]      # %
    rebt = [(ethbtc[i] / ethbtc[i - 1] - 1) * 100 for i in range(1, len(ethbtc))]
    ch = ols(dapr, reth)
    cb = ols(dapr, rebt)

    print(f"sample {months[0]} .. {months[-1]}  n={len(months)}")
    print("\n[1] LEVELS   ETH price ~ staking APR")
    print(f"    slope {lv['b']:+,.0f} $/pp   t={lv['t']:+.2f}  p={lv['p']:.4f}  "
          f"R2={lv['r2']:.3f}  r={lv['r']:+.3f}")
    print(f"    Durbin-Watson {durbin_watson([a*100 for a in apr], eth, lv):.2f} "
          "(<1 = heavy autocorrelation; the t and p above are not trustworthy)")
    print("\n[2] CHANGES  ETH monthly return ~ change in staking APR")
    print(f"    slope {ch['b']:+.4f} %/bp   t={ch['t']:+.2f}  p={ch['p']:.3f}  "
          f"R2={ch['r2']:.4f}  r={ch['r']:+.3f}")
    print(f"    95% CI on slope [{ch['ci'][0]:+.3f}, {ch['ci'][1]:+.3f}]")
    print(f"    Durbin-Watson {durbin_watson(dapr, reth, ch):.2f}")
    print("\n[3] CHANGES  ETH/BTC monthly return ~ change in staking APR")
    print(f"    slope {cb['b']:+.4f} %/bp   t={cb['t']:+.2f}  p={cb['p']:.3f}  "
          f"R2={cb['r2']:.4f}  r={cb['r']:+.3f}")

    files = [
        ("regression-levels", scatter(
            "In levels the fit looks real — and it is an artefact",
            "Month-end ETH price against consensus-layer staking APR, Jan 2023 – Jul 2026.",
            [a * 100 for a in apr], eth, lv,
            "Staking APR (%)", "ETH price (USD)",
            lambda v: f"{v:.1f}%", lambda v: f"${v:,.0f}", 1,
            "Both series trend, so they correlate. Durbin–Watson "
            f"{durbin_watson([a*100 for a in apr], eth, lv):.2f} confirms the residuals are "
            "serially correlated: the p-value here is not usable. Do not publish this chart "
            "as evidence.")),
        ("regression-changes", scatter(
            "In changes there is nothing there",
            "ETH’s monthly return against the same month’s change in staking APR.",
            dapr, reth, ch,
            "Change in staking APR (basis points)", "ETH monthly return (%)",
            lambda v: f"{v:+.0f}", lambda v: f"{v:+.0f}%", 2,
            "Differencing removes the shared trend. The slope is statistically "
            f"indistinguishable from zero (p={ch['p']:.2f}) and yield changes explain "
            f"{ch['r2']*100:.1f}% of the variance in ETH’s return. Shaded band = ±1 residual SD.")),
        ("regression-rolling", rolling_chart(months, dapr, reth)),
    ]
    for name, s in files:
        open(f"{OUT}/{name}.svg", "w").write(s)
        print(f"\nwrote {OUT}/{name}.svg")
