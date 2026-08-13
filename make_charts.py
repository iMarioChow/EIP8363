"""
Render every chart in the ANALYSIS.md chart list as a standalone, theme-aware SVG.

No dependencies. Colours are the validated categorical slots 1-3 (blue / orange /
aqua), stepped separately for the light and dark surfaces; every series is direct-
labelled so identity never rests on colour alone. Both axes carry a named title and
a unit on every chart.

    python3 make_charts.py        # writes charts/*.svg
"""
import csv, math, os
from issuance_model import (SUPPLY, STAKED, D_SAT, issuance, burn_fraction,
                            net_issuance_8363, yields, status_quo_yields,
                            equilibrium_stake, EL_TOTAL, K_ISSUANCE, BURN_ANNUAL)
from regression_analysis import OLS, load as load_series, diffs, rets, t_crit

OUT = "charts"
W, H = 880, 470
L, R, T, B = 84, 30, 58, 66          # plot margins
PW, PH = W - L - R, H - T - B

STYLE = """<style>
  .s{fill:var(--surface)}
  text{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}
  .ti{fill:var(--ink);font-size:17px;font-weight:600}
  .sub{fill:var(--ink2);font-size:12.5px}
  .ax{fill:var(--ink2);font-size:11.5px}
  .axt{fill:var(--ink2);font-size:11.5px;font-weight:600}
  .grid{stroke:var(--rule);stroke-width:1}
  .base{stroke:var(--rule2);stroke-width:1.5}
  .lab{font-size:12.5px;font-weight:600}
  .note{fill:var(--ink2);font-size:11px}
  .c1{--c:var(--s1)} .c2{--c:var(--s2)} .c3{--c:var(--s3)}
  .ln{fill:none;stroke:var(--c);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
  .dsh{fill:none;stroke:var(--c);stroke-width:2;stroke-dasharray:6 4;stroke-linecap:round}
  .dot{fill:var(--c);stroke:var(--surface);stroke-width:2}
  .txt{fill:var(--c)}
  .bar{fill:var(--s1)}
  .bar2{fill:var(--s2)} .bar3{fill:var(--s3)}
  .pt{fill:var(--c);fill-opacity:.55;stroke:none}
  .band{fill:var(--c);fill-opacity:.14;stroke:none}
  .fit{fill:none;stroke:var(--c);stroke-width:2.4;stroke-linecap:round}
  .zero{stroke:var(--rule2);stroke-width:1.2;stroke-dasharray:4 4}
  .area{fill:var(--c);fill-opacity:.22;stroke:none}
  .box{fill:var(--surface);stroke:var(--rule2);stroke-width:1;rx:5}
  .mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
        font-size:11px;fill:var(--ink2)}
  .monob{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
        font-size:11px;fill:var(--ink);font-weight:600}
  :root{--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--rule:#e7e6e2;--rule2:#c9c8c2;
        --s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a}
  @media (prefers-color-scheme:dark){:root{
        --surface:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--rule:#2e2e2c;--rule2:#4a4a46;
        --s1:#3987e5;--s2:#d95926;--s3:#199e70}}
</style>"""


def svg(body, w=W, h=H):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img">{STYLE}'
            f'<rect width="{w}" height="{h}" class="s"/>{body}</svg>')


def head(title, sub):
    return (f'<text x="{L}" y="26" class="ti">{title}</text>'
            f'<text x="{L}" y="45" class="sub">{sub}</text>')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def xtitle(text, y=None, x=None, w=None):
    """Named x-axis title, centred under the tick labels."""
    y = (T + PH + 42) if y is None else y
    x = (L + PW / 2) if x is None else x
    return (f'<text x="{x:.0f}" y="{y:.0f}" class="axt" text-anchor="middle">'
            f'{esc(text)}</text>')


def ytitle(text, x=20, top=None, bot=None):
    """Named y-axis title, rotated, centred on the plot band it labels."""
    top = T if top is None else top
    bot = T + PH if bot is None else bot
    cy = (top + bot) / 2
    return (f'<text transform="rotate(-90 {x} {cy:.1f})" x="{x}" y="{cy:.1f}" '
            f'class="axt" text-anchor="middle">{esc(text)}</text>')


def note(text, y=None, x=None, width=150, lh=14):
    """Footnote under the plot, wrapped so it never runs past the right edge.

    `width` is in characters: 150 fits the 880px canvas at the 11px note size.
    """
    y = (T + PH + 58) if y is None else y
    x = L if x is None else x
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    return "".join(f'<text x="{x}" y="{y+i*lh:.0f}" class="note">{esc(l)}</text>'
                   for i, l in enumerate(lines))


# ---------------------------------------------------------------- chart 1: burn
def chart_burn():
    # ETH burned per day, annual average. Denominators are days elapsed, so 2021
    # starts at the 5 Aug London fork and 2026 stops at 31 Jul.
    bars = [("2021", 1_317_700 / 149), ("2022", 1_482_912 / 365),
            ("2023", 1_093_504 / 365), ("2024", 634_265 / 366),
            ("2025", 91_175 / 365),    ("2026\nYTD", 12_638 / 212)]
    iss_now = issuance(STAKED) / 365
    iss_max = max(net_issuance_8363(s) for s in range(10_000_000, D_SAT, 250_000)) / 365
    ymax = 9600
    y = lambda v: T + PH - v / ymax * PH

    p = [head("The burn stopped working",
              "EIP-1559 fee burn, average ETH destroyed per day. Bars above a line "
              "mean ETH supply was shrinking under that issuance regime.")]
    for v in (0, 2000, 4000, 6000, 8000):
        p.append(f'<line x1="{L}" y1="{y(v):.1f}" x2="{L+PW}" y2="{y(v):.1f}" class="grid"/>')
        p.append(f'<text x="{L-10}" y="{y(v)+4:.1f}" class="ax" text-anchor="end">{v:,}</text>')

    bw, gap = PW / len(bars) * 0.52, PW / len(bars)
    for i, (lab, v) in enumerate(bars):
        cx = L + gap * (i + 0.5)
        h = max(2.0, PH - (y(v) - T))
        p.append(f'<rect x="{cx-bw/2:.1f}" y="{y(v):.1f}" width="{bw:.1f}" height="{h:.1f}" '
                 f'rx="4" class="bar"/>')
        p.append(f'<text x="{cx:.1f}" y="{y(v)-9:.1f}" class="lab" text-anchor="middle" '
                 f'fill="var(--ink)">{v:,.0f}</text>')
        for j, line in enumerate(lab.split("\n")):
            p.append(f'<text x="{cx:.1f}" y="{T+PH+20+j*14:.1f}" class="ax" '
                     f'text-anchor="middle">{line}</text>')

    for val, cls, txt in ((iss_now, "c2", "Issuance today, 2,950/day"),
                          (iss_max, "c3", "Max issuance under EIP-8363, 1,669/day")):
        p.append(f'<g class="{cls}"><line x1="{L}" y1="{y(val):.1f}" x2="{L+PW}" '
                 f'y2="{y(val):.1f}" class="dsh"/>'
                 f'<text x="{L+PW}" y="{y(val)-8:.1f}" class="lab txt" text-anchor="end">'
                 f'{esc(txt)}</text></g>')

    p.append(xtitle("Year", y=T + PH + 46))
    p.append(ytitle("ETH burned per day (annual average)"))
    p.append(note("Base-fee burn measured from every Ethereum block (Dune). "
                  "2021 dates from the 5 Aug London fork; 2026 through 31 Jul. "
                  "Latest month, Jul 2026: 37 ETH/day.", y=T + PH + 62))
    p.append(f'<line x1="{L}" y1="{y(0):.1f}" x2="{L+PW}" y2="{y(0):.1f}" class="base"/>')
    return svg("".join(p))


# ------------------------------------------------------- chart 2: issuance curves
def chart_issuance():
    xs = [r / 100 for r in range(2, 101)]
    ymax = 1.6
    px = lambda r: L + r * PW
    py = lambda v: T + PH - v / ymax * PH

    def path(f):
        pts = []
        for r in xs:
            s = r * SUPPLY
            pts.append(f"{px(r):.1f},{py(f(s) / SUPPLY * 100):.1f}")
        return "M" + "L".join(pts)

    cur = path(issuance)
    m0 = path(lambda s: net_issuance_8363(s, 128.0))
    m18 = path(lambda s: net_issuance_8363(s, 64.0))

    p = [head("EIP-8363 halves issuance now, not zeroes it",
              "Annual ETH issuance as a share of supply, by staking ratio. "
              "Zero requires 50% of supply staked — today's record is 34.7%.")]
    for v in (0, 0.4, 0.8, 1.2, 1.6):
        p.append(f'<line x1="{L}" y1="{py(v):.1f}" x2="{L+PW}" y2="{py(v):.1f}" class="grid"/>')
        p.append(f'<text x="{L-10}" y="{py(v)+4:.1f}" class="ax" text-anchor="end">{v:.1f}%</text>')
    for r in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        p.append(f'<text x="{px(r):.1f}" y="{T+PH+20:.1f}" class="ax" text-anchor="middle">'
                 f'{r*100:.0f}%</text>')
    p.append(xtitle("Share of ETH supply staked (%)"))
    p.append(ytitle("Annual ETH issuance (% of supply per year)"))

    for r, lab in ((STAKED / SUPPLY, "today 34.7%"), (D_SAT / SUPPLY, "saturation 49.9%")):
        p.append(f'<line x1="{px(r):.1f}" y1="{T}" x2="{px(r):.1f}" y2="{T+PH}" '
                 f'class="grid" stroke-dasharray="3 4"/>')
        p.append(f'<text x="{px(r)+5:.1f}" y="{T+12}" class="note">{lab}</text>')

    p.append(f'<g class="c1"><path d="{cur}" class="ln"/></g>')
    p.append(f'<g class="c2"><path d="{m0}" class="ln"/></g>')
    p.append(f'<g class="c3"><path d="{m18}" class="dsh"/></g>')

    for cls, r, v, txt, dy, anc in (
            ("c1", 0.82, issuance(0.82 * SUPPLY) / SUPPLY * 100, "Today's curve", -12, "middle"),
            ("c2", 0.135, net_issuance_8363(0.135 * SUPPLY, 128) / SUPPLY * 100,
             "EIP-8363, month 0", -14, "middle"),
            ("c3", 0.60, 0.30, "EIP-8363, month 18 (permanent)", 0, "start")):
        p.append(f'<g class="{cls}"><text x="{px(r):.1f}" y="{py(v)+dy:.1f}" '
                 f'class="lab txt" text-anchor="{anc}">{esc(txt)}</text></g>')

    for cls, f in (("c1", lambda s: issuance(s)),
                   ("c2", lambda s: net_issuance_8363(s, 128.0)),
                   ("c3", lambda s: net_issuance_8363(s, 64.0))):
        v = f(STAKED) / SUPPLY * 100
        p.append(f'<g class="{cls}"><circle cx="{px(STAKED/SUPPLY):.1f}" cy="{py(v):.1f}" '
                 f'r="5" class="dot"/></g>')

    p.append(f'<text x="{L}" y="{T+PH+58:.0f}" class="note">'
             'At today’s 34.7% staked: 0.89% today → 0.75% at launch (base reward factor '
             '128) → 0.37% once the factor tapers to 64 over ~18 months.</text>')
    return svg("".join(p))


# ---------------------------------------------------- chart 3: staking equilibrium
def chart_equilibrium():
    lo, hi = 8_000_000, 60_250_000
    ymax = 6.0
    px = lambda s: L + (s - lo) / (hi - lo) * PW
    py = lambda v: T + PH - v / ymax * PH

    def path(f, dash=False):
        pts = [f"{px(s):.1f},{py(min(ymax, f(s)*100)):.1f}"
               for s in range(lo, hi + 1, 250_000)]
        return "M" + "L".join(pts)

    p = [head("The mechanism is self-limiting",
              "Total staking yield (issuance + fees) against the amount staked. "
              "Stakers exit until yield clears their hurdle — which is where the "
              "system settles.")]
    for v in (0, 1.5, 3.0, 4.5, 6.0):
        p.append(f'<line x1="{L}" y1="{py(v):.1f}" x2="{L+PW}" y2="{py(v):.1f}" class="grid"/>')
        p.append(f'<text x="{L-10}" y="{py(v)+4:.1f}" class="ax" text-anchor="end">{v:.1f}%</text>')
    for s in range(10_000_000, hi + 1, 10_000_000):
        p.append(f'<text x="{px(s):.1f}" y="{T+PH+20:.1f}" class="ax" text-anchor="middle">'
                 f'{s/1e6:.0f}M</text>')
    p.append(xtitle("ETH staked (millions of ETH)"))
    p.append(ytitle("Total staking yield (% APR)"))

    p.append(f'<g class="c1"><path d="{path(lambda s: status_quo_yields(s)[2])}" class="ln"/></g>')
    p.append(f'<g class="c2"><path d="{path(lambda s: yields(s)[2])}" class="ln"/></g>')
    p.append(f'<g class="c1"><text x="{px(30_000_000):.1f}" y="{py(3.33)-12:.1f}" '
             'class="lab txt" text-anchor="middle">Today’s rules</text></g>')
    p.append(f'<g class="c2"><text x="{px(17_500_000):.1f}" y="{py(2.55):.1f}" '
             'class="lab txt" text-anchor="middle">Under EIP-8363</text></g>')

    for req in (0.02, 0.0125):
        s = equilibrium_stake(req)
        p.append(f'<line x1="{L}" y1="{py(req*100):.1f}" x2="{px(s):.1f}" y2="{py(req*100):.1f}" '
                 f'class="grid" stroke-dasharray="3 4"/>')
        p.append(f'<line x1="{px(s):.1f}" y1="{py(req*100):.1f}" x2="{px(s):.1f}" '
                 f'y2="{T+PH:.1f}" class="grid" stroke-dasharray="3 4"/>')
        p.append(f'<g class="c2"><circle cx="{px(s):.1f}" cy="{py(req*100):.1f}" r="5" '
                 f'class="dot"/></g>')
        p.append(f'<text x="{px(s)+9:.1f}" y="{py(req*100)-7:.1f}" class="note">'
                 f'hurdle {req*100:.2f}% → {s/1e6:.1f}M staked '
                 f'({s/SUPPLY*100:.0f}% of supply)</text>')

    p.append(f'<line x1="{px(STAKED):.1f}" y1="{T}" x2="{px(STAKED):.1f}" y2="{T+PH}" '
             f'class="grid" stroke-dasharray="3 4"/>')
    p.append(f'<text x="{px(STAKED)+5:.1f}" y="{T+12}" class="note">today 41.9M</text>')
    p.append(note("Execution-layer income (priority fees + MEV, ~88k ETH/yr) is untouched "
                  "by the proposal and sets the floor. Yield is capped at 6% for legibility."))
    return svg("".join(p))


# ============================================================ shared chart data
def series():
    """Monthly panel: month, staked ETH, consensus APR, ETH/USD, BTC/USD."""
    return load_series()


def annual_issuance():
    """Gross CL issuance per calendar year, ETH/yr, from the monthly reconstruction."""
    by_year = {}
    for r in csv.DictReader(open("staked_eth_reconstructed.csv")):
        y = r["month"][:4]
        v = float(r["annualised_issuance_eth"])
        if v > 0:
            by_year.setdefault(y, []).append(v)
    return {y: sum(v) / len(v) for y, v in by_year.items()}


def priority_fees():
    return {r["month"]: float(r["priority_fees_eth"])
            for r in csv.DictReader(open("eth_supply_monthly.csv"))}


def month_ticks(months, every=6):
    """Indices of x tick positions, one every `every` months, plus the last month.

    The last regular tick is dropped if it would collide with the final label.
    """
    ticks = [i for i in range(len(months)) if i % every == 0]
    last = len(months) - 1
    while ticks and last - ticks[-1] < max(2, every // 2):
        ticks.pop()
    return ticks + [last]


# ------------------------------------------- chart 2: gross issuance vs burn vs net
def chart_issuance_vs_burn():
    """Post-Merge only. Before Sep 2022 most issuance was proof-of-work, which this
    model does not carry, so 2021-22 would understate issuance by roughly 5x."""
    burn = {r["year"].replace("_ytd", ""): float(r["eth_burned"])
            for r in csv.DictReader(open("burn_history.csv"))}
    iss = annual_issuance()
    years = [("2023", "2023"), ("2024", "2024"), ("2025", "2025"), ("2026", "2026\nYTD")]
    iss["2026"] *= 7 / 12.0                # both series run through 31 Jul 2026
    ymax = 1_350_000
    y = lambda v: T + PH - v / ymax * PH

    p = [head("Issuance now dwarfs the burn",
              "Consensus-layer issuance against EIP-1559 burn, ETH per calendar year. "
              "Post-Merge only: before Sep 2022 most issuance was proof-of-work.")]
    for v in range(0, ymax + 1, 300_000):
        p.append(f'<line x1="{L}" y1="{y(v):.1f}" x2="{L+PW}" y2="{y(v):.1f}" class="grid"/>')
        p.append(f'<text x="{L-10}" y="{y(v)+4:.1f}" class="ax" text-anchor="end">'
                 f'{v/1000:,.0f}k</text>')

    gap = PW / len(years)
    bw = gap * 0.26
    for i, (yr, lab) in enumerate(years):
        cx = L + gap * (i + 0.5)
        g, b = iss[yr], burn[yr]
        for dx, v, cls in ((-bw * 0.58, g, "bar"), (bw * 0.58, b, "bar2")):
            p.append(f'<rect x="{cx+dx-bw/2:.1f}" y="{y(v):.1f}" width="{bw:.1f}" '
                     f'height="{max(1.5, PH-(y(v)-T)):.1f}" rx="3" class="{cls}"/>')
            p.append(f'<text x="{cx+dx:.1f}" y="{y(v)-8:.1f}" class="ax" '
                     f'text-anchor="middle">{v/1000:,.0f}k</text>')
        p.append(f'<text x="{cx:.1f}" y="{y(max(g,b))-28:.1f}" class="lab" '
                 f'text-anchor="middle" fill="var(--ink)">{(g-b)/1000:+,.0f}k net</text>')
        for j, line in enumerate(lab.split("\n")):
            p.append(f'<text x="{cx:.1f}" y="{T+PH+20+j*14:.1f}" class="ax" '
                     f'text-anchor="middle">{line}</text>')

    for dx, cls, lab in ((-bw * 0.58, "bar", "Issuance"), (bw * 0.58, "bar2", "Burn")):
        cx = L + gap * 0.5 + dx
        p.append(f'<text transform="rotate(-90 {cx:.1f} {T+PH-16:.1f})" x="{cx:.1f}" '
                 f'y="{T+PH-16:.1f}" class="lab" text-anchor="start" '
                 f'fill="var(--surface)">{lab}</text>')
    p.append(xtitle("Calendar year", y=T + PH + 48))
    p.append(ytitle("ETH per year"))
    p.append(note("2023 was the last year the burn exceeded issuance. Since then the gap "
                  "has widened every year, and in 2026 the burn offsets under 2% of what "
                  "the protocol issues — which is the fact EIP-8363 is a response to. "
                  "2026 covers 1 Jan to 31 Jul on both series.", y=T + PH + 62))
    p.append(f'<line x1="{L}" y1="{y(0):.1f}" x2="{L+PW}" y2="{y(0):.1f}" class="base"/>')
    return svg("".join(p))


# ------------------------------------------------ chart 3: staked ETH over time
def chart_staked_history():
    rows = list(csv.DictReader(open("staked_eth_reconstructed.csv")))
    months = [r["month"] for r in rows]
    staked = [float(r["staked_eth"]) for r in rows]
    ymax = 50e6
    px = lambda i: L + i / (len(months) - 1) * PW
    py = lambda v: T + PH - v / ymax * PH

    p = [head("Staking grew through every price regime",
              "ETH staked, reconstructed month by month from deposit and exit flows. "
              "The right axis reads the same series as a share of today's 120.7M supply.")]
    for v in range(0, 50_000_001, 10_000_000):
        p.append(f'<line x1="{L}" y1="{py(v):.1f}" x2="{L+PW}" y2="{py(v):.1f}" class="grid"/>')
        p.append(f'<text x="{L-10}" y="{py(v)+4:.1f}" class="ax" text-anchor="end">'
                 f'{v/1e6:.0f}M</text>')
        p.append(f'<text x="{L+PW+10}" y="{py(v)+4:.1f}" class="ax" text-anchor="start">'
                 f'{v/SUPPLY*100:.0f}%</text>')
    for i in month_ticks(months, 6):
        p.append(f'<text x="{px(i):.1f}" y="{T+PH+20:.1f}" class="ax" '
                 f'text-anchor="middle">{months[i]}</text>')

    pts = "L".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(staked))
    p.append(f'<g class="c1"><path d="M{px(0):.1f},{py(0):.1f}L{pts}L{px(len(staked)-1):.1f},'
             f'{py(0):.1f}Z" class="area"/><path d="M{pts}" class="ln"/></g>')

    for i, lab in ((months.index("2022-09"), "Merge"),
                   (months.index("2023-04"), "Shapella (exits enabled)")):
        p.append(f'<line x1="{px(i):.1f}" y1="{T}" x2="{px(i):.1f}" y2="{T+PH}" '
                 f'class="grid" stroke-dasharray="3 4"/>')
        p.append(f'<text x="{px(i)+5:.1f}" y="{T+12}" class="note">{esc(lab)}</text>')

    p.append(f'<g class="c1"><circle cx="{px(len(staked)-1):.1f}" '
             f'cy="{py(staked[-1]):.1f}" r="5" class="dot"/>'
             f'<text x="{px(len(staked)-1):.1f}" y="{py(staked[-1])-14:.1f}" '
             f'class="lab txt" text-anchor="end">{staked[-1]/1e6:.1f}M staked '
             f'({staked[-1]/SUPPLY*100:.1f}%)</text></g>')
    p.append(xtitle("Month", y=T + PH + 44))
    p.append(ytitle("ETH staked (millions)"))
    p.append(ytitle("Share of supply (%)", x=W - 12))
    p.append(note("Reconstruction lands ~5.4% above the reported 41.9M record: it counts "
                  "the activation queue and does not net out inactive balances. Shape and "
                  "direction are reliable, the level is not exact.", y=T + PH + 60))
    return svg("".join(p))


# ----------------------------------- chart 4: staking APR, consensus vs execution
def chart_apr_split():
    rows = list(csv.DictReader(open("staked_eth_reconstructed.csv")))
    fees = priority_fees()
    mev_mult = EL_TOTAL / 39_150.0            # priority fees -> priority fees + MEV
    data = [(r["month"], float(r["staked_eth"]), float(r["cl_apr"]),
             fees[r["month"]] * 12 * mev_mult / float(r["staked_eth"]))
            for r in rows if r["month"] in fees]
    months = [d[0] for d in data]
    cl = [d[2] * 100 for d in data]
    el = [d[3] * 100 for d in data]
    ymax = 3.6
    px = lambda i: L + i / (len(months) - 1) * PW
    py = lambda v: T + PH - v / ymax * PH

    p = [head("Almost all of the staking yield is issuance",
              "Staking APR split into its two sources. Execution-layer income is what "
              "survives EIP-8363 untouched — and it is a thin sliver.")]
    for v in (0, 0.9, 1.8, 2.7, 3.6):
        p.append(f'<line x1="{L}" y1="{py(v):.1f}" x2="{L+PW}" y2="{py(v):.1f}" class="grid"/>')
        p.append(f'<text x="{L-10}" y="{py(v)+4:.1f}" class="ax" text-anchor="end">'
                 f'{v:.1f}%</text>')
    for i in month_ticks(months, 4):
        p.append(f'<text x="{px(i):.1f}" y="{T+PH+20:.1f}" class="ax" '
                 f'text-anchor="middle">{months[i]}</text>')

    tot = [c + e for c, e in zip(cl, el)]
    n = len(months)
    cl_pts = [f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(cl)]
    tot_pts = [f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(tot)]
    # band 1: zero to consensus APR.  band 2: consensus APR to total.  Disjoint, so
    # the two translucent fills never sit on top of one another.
    p.append(f'<g class="c1"><path d="M{px(0):.1f},{py(0):.1f}L{"L".join(cl_pts)}'
             f'L{px(n-1):.1f},{py(0):.1f}Z" class="area"/>'
             f'<path d="M{"L".join(cl_pts)}" class="ln"/></g>')
    p.append(f'<g class="c2"><path d="M{"L".join(cl_pts)}'
             f'L{"L".join(reversed(tot_pts))}Z" class="area"/>'
             f'<path d="M{"L".join(tot_pts)}" class="ln"/></g>')

    j = len(months) // 3
    p.append(f'<g class="c1"><text x="{px(j):.1f}" y="{py(cl[j]/2):.1f}" '
             'class="lab txt" text-anchor="middle">Consensus layer (issuance)</text></g>')
    p.append(f'<g class="c2"><text x="{px(j):.1f}" y="{py(tot[j])-12:.1f}" '
             'class="lab txt" text-anchor="middle">Execution layer '
             '(priority fees + MEV)</text></g>')
    p.append(xtitle("Month", y=T + PH + 44))
    p.append(ytitle("Staking APR (%)"))
    p.append(note(f"Execution-layer APR is observed priority fees annualised and grossed "
                  f"up for MEV at {mev_mult:.2f}x, the ratio implied by the reported 2.78% "
                  f"total APR. Latest: {cl[-1]:.2f}% + {el[-1]:.2f}% = {tot[-1]:.2f}%.",
                  y=T + PH + 60))
    p.append(f'<line x1="{L}" y1="{py(0):.1f}" x2="{L+PW}" y2="{py(0):.1f}" class="base"/>')
    return svg("".join(p))


# ------------------------------------------------------- chart 7: LST dominance
def chart_lst_share():
    bars = [("Lido (stETH)", 22.6, 17.94), ("Binance staked ETH", 8.9, 7.04),
            ("ether.fi (weETH)", 4.2, 3.31), ("Rocket Pool (rETH)", 1.3, 1.00),
            ("Coinbase (cbETH)", 0.4, 0.35),
            ("Solo, CEX and other custody", 62.7, 49.76)]
    l = 210                                 # wide left margin: the row labels are names
    pw = W - l - 60
    xmax = 75.0
    px = lambda v: l + v / xmax * pw
    rowh = PH / len(bars)

    p = [head("One protocol intermediates a fifth of all staked ETH",
              "Share of the 41.9M staked ETH ($79.4B) by custody route. "
              "Lido alone is 43% of Ethereum's entire $41.3B DeFi TVL.")]
    for v in range(0, 71, 10):
        p.append(f'<line x1="{px(v):.1f}" y1="{T}" x2="{px(v):.1f}" y2="{T+PH}" class="grid"/>')
        p.append(f'<text x="{px(v):.1f}" y="{T+PH+20:.1f}" class="ax" '
                 f'text-anchor="middle">{v}%</text>')

    for i, (lab, share, tvl) in enumerate(bars):
        cy = T + rowh * (i + 0.5)
        h = rowh * 0.52
        cls = "bar" if i < 5 else "bar3"
        p.append(f'<rect x="{l}" y="{cy-h/2:.1f}" width="{max(2,px(share)-l):.1f}" '
                 f'height="{h:.1f}" rx="3" class="{cls}"/>')
        p.append(f'<text x="{px(share)+9:.1f}" y="{cy+4:.1f}" class="lab" '
                 f'fill="var(--ink)">{share:.1f}%  ·  ${tvl:.2f}B</text>')
        p.append(f'<text x="{l-12}" y="{cy+4:.1f}" class="ax" text-anchor="end">'
                 f'{esc(lab)}</text>')

    p.append(xtitle("Share of all staked ETH (%)", y=T + PH + 44, x=l + pw / 2))
    p.append(ytitle("Custody route", x=20))
    p.append(note("DefiLlama TVL, 13 Aug 2026. The top five liquid-staking routes are 37.3% "
                  "of staked ETH; the rest is solo validators, exchanges and institutional "
                  "custody. Green is the unintermediated remainder.", y=T + PH + 62, x=20))
    return svg("".join(p))


# --------------------------------------- chart 8: LST collateral in lending markets
def chart_lst_collateral():
    # protocol, total TVL $B, wstETH $B, weETH $B
    bars = [("SparkLend", 3.57, 2.37, 0.08), ("Aave V3", 14.19, 2.46, 2.51),
            ("Morpho Blue", 7.97, 0.56, 0.25)]
    ymax = 75.0
    gap = PW / len(bars)
    py = lambda v: T + PH - v / ymax * PH

    p = [head("A third of major lending collateral is a staking-yield derivative",
              "wstETH and weETH as a share of each lending market's total TVL. "
              "Exposure, not dependency — but SparkLend is a single-asset book.")]
    for v in range(0, 76, 15):
        p.append(f'<line x1="{L}" y1="{py(v):.1f}" x2="{L+PW}" y2="{py(v):.1f}" class="grid"/>')
        p.append(f'<text x="{L-10}" y="{py(v)+4:.1f}" class="ax" text-anchor="end">{v}%</text>')

    for i, (lab, tvl, wst, wee) in enumerate(bars):
        cx = L + gap * (i + 0.5)
        bw = gap * 0.34
        base = 0.0
        for v, cls, nm in ((wst / tvl * 100, "bar", "wstETH"),
                           (wee / tvl * 100, "bar2", "weETH")):
            p.append(f'<rect x="{cx-bw/2:.1f}" y="{py(base+v):.1f}" width="{bw:.1f}" '
                     f'height="{max(1.5, py(base)-py(base+v)):.1f}" rx="3" class="{cls}"/>')
            if v > 4:
                p.append(f'<text x="{cx:.1f}" y="{py(base+v/2)+4:.1f}" class="lab" '
                         f'text-anchor="middle" fill="var(--surface)">{nm} {v:.0f}%</text>')
            base += v
        p.append(f'<text x="{cx:.1f}" y="{py(base)-10:.1f}" class="lab" '
                 f'text-anchor="middle" fill="var(--ink)">{base:.1f}%</text>')
        p.append(f'<text x="{cx:.1f}" y="{T+PH+20:.1f}" class="ax" '
                 f'text-anchor="middle">{esc(lab)}</text>')
        p.append(f'<text x="{cx:.1f}" y="{T+PH+35:.1f}" class="note" '
                 f'text-anchor="middle">${tvl:.2f}B TVL</text>')

    p.append(xtitle("Lending market", y=T + PH + 54))
    p.append(ytitle("LST collateral (% of protocol TVL)"))
    p.append(note("~$8.2B of ~$25.7B of collateral across the three largest Ethereum "
                  "lending markets is tokenised staked ETH. What breaks at a lower yield "
                  "is the leveraged staking loop, not the collateral itself.",
                  y=T + PH + 68))
    p.append(f'<line x1="{L}" y1="{py(0):.1f}" x2="{L+PW}" y2="{py(0):.1f}" class="base"/>')
    return svg("".join(p))


# ================================================== the §4 statistics charts ===
def _fit_band(reg, x0, x1, px, py, steps=60):
    """Upper/lower 95% confidence band for the fitted line, as an SVG polygon."""
    tc = t_crit(reg.df)
    up, lo = [], []
    for i in range(steps + 1):
        x = x0 + (x1 - x0) * i / steps
        yh = reg.intercept + reg.slope * x
        se = reg.sigma * math.sqrt(1.0 / reg.n + (x - reg.mx) ** 2 / reg.sxx)
        up.append(f"{px(x):.1f},{py(yh + tc * se):.1f}")
        lo.append(f"{px(x):.1f},{py(yh - tc * se):.1f}")
    return "M" + "L".join(up + list(reversed(lo))) + "Z"


def _statbox(reg, x, y, w, lines):
    h = 16 + 15 * len(lines)
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" class="box"/>']
    for i, (txt, strong) in enumerate(lines):
        cls = "monob" if strong else "mono"
        out.append(f'<text x="{x+10}" y="{y+22+15*i}" class="{cls}">{esc(txt)}</text>')
    return "".join(out)


# ------------------------- chart 9: two stacked panels, yield and price, shared x
def chart_yield_price_panels():
    h = 540
    data = series()
    months = [d[0] for d in data]
    apr = [d[2] * 100 for d in data]
    ethbtc = [d[3] / d[4] * 1000 for d in data]
    l, r = L, W - 46
    pw = r - l
    t1, b1 = 72, 240                       # top panel: APR
    t2, b2 = 300, 452                      # bottom panel: ETH/BTC
    px = lambda i: l + i / (len(months) - 1) * pw

    p = [f'<text x="{l}" y="26" class="ti">The yield fell the whole way down. '
         f'It did not defend the price.</text>',
         f'<text x="{l}" y="45" class="sub">Consensus staking APR and ETH/BTC on a '
         f'shared time axis, Jan 2023 - Jul 2026. Two panels, not two y-axes: a dual '
         f'axis would imply a link the data does not support.</text>']

    def panel(vals, top, bot, lo, hi, ticks, fmt, cls, lab, yname):
        py = lambda v: bot - (v - lo) / (hi - lo) * (bot - top)
        o = []
        for v in ticks:
            o.append(f'<line x1="{l}" y1="{py(v):.1f}" x2="{r}" y2="{py(v):.1f}" class="grid"/>')
            o.append(f'<text x="{l-10}" y="{py(v)+4:.1f}" class="ax" text-anchor="end">'
                     f'{fmt(v)}</text>')
        pts = "L".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(vals))
        o.append(f'<g class="{cls}"><path d="M{pts}" class="ln"/>'
                 f'<circle cx="{px(0):.1f}" cy="{py(vals[0]):.1f}" r="4.5" class="dot"/>'
                 f'<circle cx="{px(len(vals)-1):.1f}" cy="{py(vals[-1]):.1f}" r="4.5" '
                 f'class="dot"/>'
                 f'<text x="{px(0)+10:.1f}" y="{py(vals[0])-10:.1f}" class="lab txt">'
                 f'{esc(lab)}</text></g>')
        o.append(ytitle(yname, x=22, top=top, bot=bot))
        return "".join(o)

    p.append(panel(apr, t1, b1, 2.4, 4.1, [2.5, 3.0, 3.5, 4.0],
                   lambda v: f"{v:.1f}%", "c1",
                   f"Staking APR  {apr[0]:.2f}% → {apr[-1]:.2f}%",
                   "Consensus staking APR (%)"))
    p.append(panel(ethbtc, t2, b2, 25, 72, [30, 40, 50, 60, 70],
                   lambda v: f"{v/1000:.03f}", "c2",
                   f"ETH/BTC  {ethbtc[0]/1000:.5f} → {ethbtc[-1]/1000:.5f} "
                   f"({ethbtc[-1]/ethbtc[0]-1:+.0%})",
                   "ETH/BTC ratio"))

    for i in month_ticks(months, 6):
        p.append(f'<text x="{px(i):.1f}" y="{b2+20:.1f}" class="ax" '
                 f'text-anchor="middle">{months[i]}</text>')
    p.append(xtitle("Month", y=b2 + 44, x=l + pw / 2))

    p.append(_statbox(None, r - 300, t1 + 8, 300, []) if False else "")
    p.append(f'<rect x="{r-296}" y="{t1+6}" width="296" height="52" rx="5" class="box"/>')
    p.append(f'<text x="{r-286}" y="{t1+26}" class="monob">'
             'corr(ΔAPR, ETH/BTC return) = -0.046</text>')
    p.append(f'<text x="{r-286}" y="{t1+43}" class="mono">'
             'p = 0.77, n = 42 monthly changes</text>')

    p.append(note("Both series decline over the window, which is what a dual-axis chart "
                  "would dramatise. In monthly changes the relationship is zero: the "
                  "co-movement is shared time, not a shared cause.",
                  y=b2 + 62, x=l))
    return svg("".join(p), h=h)


# ---------------------------- chart 10: the regressions, levels vs changes scatter
def chart_regression():
    data = series()
    apr = [d[2] for d in data]
    px_ = [d[3] for d in data]
    ethbtc = [d[3] / d[4] for d in data]

    lv = OLS([a * 100 for a in apr], [v * 1000 for v in ethbtc], "levels")
    ch = OLS([d * 10_000 for d in diffs(apr)], [r * 100 for r in rets(px_)], "changes")

    h = 500
    t, b = 96, 380
    pw = 336
    lx, rx = L, L + pw + 92                # two panels side by side

    p = [f'<text x="{L}" y="26" class="ti">The correlation people quote is a trend, '
         f'not a relationship</text>',
         f'<text x="{L}" y="45" class="sub">Left: the naive regression on levels, which '
         f'looks strong and is spurious. Right: the same question asked in monthly '
         f'changes, which is the version that identifies anything.</text>',
         f'<text x="{L}" y="66" class="sub">Each dot is one month, Jan 2023 - Jul 2026. '
         f'Shaded band is the 95% confidence interval of the fitted line.</text>']

    def scatter(reg, x0, y0, x1, y1, xt, yt, ticks_x, ticks_y, fx, fy,
                left, cls, title, box, zero=False):
        pxf = lambda v: left + (v - x0) / (x1 - x0) * pw
        pyf = lambda v: b - (v - y0) / (y1 - y0) * (b - t)
        o = [f'<text x="{left}" y="{t-14}" class="lab" fill="var(--ink)">{esc(title)}</text>']
        for v in ticks_y:
            o.append(f'<line x1="{left}" y1="{pyf(v):.1f}" x2="{left+pw}" '
                     f'y2="{pyf(v):.1f}" class="grid"/>')
            o.append(f'<text x="{left-10}" y="{pyf(v)+4:.1f}" class="ax" '
                     f'text-anchor="end">{fy(v)}</text>')
        for v in ticks_x:
            o.append(f'<text x="{pxf(v):.1f}" y="{b+20:.1f}" class="ax" '
                     f'text-anchor="middle">{fx(v)}</text>')
        if zero:
            o.append(f'<line x1="{pxf(0):.1f}" y1="{t}" x2="{pxf(0):.1f}" '
                     f'y2="{b}" class="zero"/>')
            o.append(f'<line x1="{left}" y1="{pyf(0):.1f}" x2="{left+pw}" '
                     f'y2="{pyf(0):.1f}" class="zero"/>')
        # Clip the fit and its band to the panel: on levels both run off the top.
        cid = f"clip{int(left)}"
        o.append(f'<clipPath id="{cid}"><rect x="{left}" y="{t}" width="{pw}" '
                 f'height="{b-t}"/></clipPath>')
        o.append(f'<g class="{cls}" clip-path="url(#{cid})">'
                 f'<path d="{_fit_band(reg, x0, x1, pxf, pyf)}" class="band"/>')
        o.append(f'<path d="M{pxf(x0):.1f},{pyf(reg.intercept+reg.slope*x0):.1f}'
                 f'L{pxf(x1):.1f},{pyf(reg.intercept+reg.slope*x1):.1f}" class="fit"/>')
        for u, v in zip(reg.x, reg.y):
            o.append(f'<circle cx="{pxf(u):.1f}" cy="{pyf(v):.1f}" r="4" class="pt"/>')
        o.append("</g>")
        o.append(xtitle(xt, y=b + 42, x=left + pw / 2))
        o.append(ytitle(yt, x=left - 62, top=t, bot=b))
        o.append(_statbox(reg, left + 8, t + 8, 214, box))
        return "".join(o)

    p.append(scatter(
        lv, 2.4, 25, 4.1, 72,
        "Consensus staking APR (%)", "ETH/BTC ratio",
        [2.5, 3.0, 3.5, 4.0], [30, 40, 50, 60, 70],
        lambda v: f"{v:.1f}%", lambda v: f"{v/1000:.03f}",
        lx, "c1", "LEVELS  —  do not publish",
        [("R² = 0.70   r = +0.835", True),
         ("slope +0.0335 ETH/BTC", False),
         ("  per 1pp of APR,  p < 0.001", False),
         ("Durbin-Watson 0.27  → spurious", True)]))

    p.append(scatter(
        ch, -14, -46, 14, 46,
        "Change in staking APR (basis points)", "ETH monthly return (%)",
        [-10, -5, 0, 5, 10], [-40, -20, 0, 20, 40],
        lambda v: f"{v:+.0f}", lambda v: f"{v:+.0f}%",
        rx, "c2", "CHANGES  —  the honest test",
        [("R² = 0.003   r = -0.055", True),
         ("slope -0.18 pp per bp", False),
         ("95% CI [-1.23, +0.87]", False),
         ("p = 0.73  → zero", True)], zero=True))

    p.append(note("Durbin-Watson near zero means the level regression's residuals are almost perfectly "
                  "autocorrelated: it has fitted a shared downtrend, not a relationship. In changes the "
                  "slope is a third of its own standard error and the 95% interval straddles zero. "
                  "APR = 166.28/√S is a deterministic function of the staked balance, so the level series "
                  "is near-monotone and carries almost no independent variation to regress against.",
                  y=b + 64, x=L))
    return svg("".join(p), h=h)


# --------------- chart 11: the stake-rate / yield identity (the mathematical answer)
def chart_rate_vs_yield():
    data = series()
    staked = [d[1] for d in data]
    apr = [d[2] * 100 for d in data]
    lo, hi = 8_000_000, 60_250_000
    ymax = 6.0
    h = 510
    ph = h - T - 100                       # taller canvas: the footnote needs two lines
    pxf = lambda s: L + (s - lo) / (hi - lo) * PW
    pyf = lambda v: T + ph - v / ymax * ph

    p = [head("Stake rate and staking yield are the same variable",
              "The consensus yield is not correlated with the staked balance — it is a "
              "function of it. Every month since 2023 sits exactly on the curve.")]
    for v in (0, 1.5, 3.0, 4.5, 6.0):
        p.append(f'<line x1="{L}" y1="{pyf(v):.1f}" x2="{L+PW}" y2="{pyf(v):.1f}" class="grid"/>')
        p.append(f'<text x="{L-10}" y="{pyf(v)+4:.1f}" class="ax" text-anchor="end">'
                 f'{v:.1f}%</text>')
    for s in range(10_000_000, hi + 1, 10_000_000):
        p.append(f'<text x="{pxf(s):.1f}" y="{T+ph+20:.1f}" class="ax" '
                 f'text-anchor="middle">{s/1e6:.0f}M</text>')
        p.append(f'<text x="{pxf(s):.1f}" y="{T+ph+35:.1f}" class="note" '
                 f'text-anchor="middle">{s/SUPPLY*100:.0f}% of supply</text>')

    curve = "M" + "L".join(
        f"{pxf(s):.1f},{pyf(K_ISSUANCE / math.sqrt(s) * 100):.1f}"
        for s in range(lo, hi + 1, 250_000))
    p.append(f'<g class="c1"><path d="{curve}" class="ln"/></g>')
    for s, a in zip(staked, apr):
        p.append(f'<g class="c2"><circle cx="{pxf(s):.1f}" cy="{pyf(a):.1f}" r="4.5" '
                 f'class="pt"/></g>')

    p.append(f'<g class="c1"><text x="{pxf(20_000_000):.1f}" '
             f'y="{pyf(K_ISSUANCE/math.sqrt(20e6)*100)-14:.1f}" class="lab txt" '
             f'text-anchor="middle">APR(S) = 166.28 / √S</text></g>')
    p.append(f'<g class="c2"><text x="{pxf(41_000_000):.1f}" y="{pyf(2.05):.1f}" '
             f'class="lab txt" text-anchor="start">43 observed months, '
             f'Jan 2023 – Jul 2026</text></g>')

    p.append(_statbox(None, L + PW - 300, T + 8, 300, [
        ("log APR = log(166.28) - 0.500 * log S", True),
        ("fitted slope   -0.5000   (theory -0.5)", False),
        ("R² = 1.0000   n = 43", False),
        ("elasticity: +1% stake → -0.5% yield", True),
    ]))

    p.append(xtitle("ETH staked (millions of ETH)", y=T + ph + 54))
    p.append(ytitle("Consensus staking APR (%)"))
    p.append(note("Ethereum pays I(S) = 166.28√S ETH a year, so the yield per staked "
                  "ETH is I(S)/S = 166.28/√S. Doubling the stake cuts the yield 29.3%; "
                  "quadrupling it halves the yield. There is nothing here to estimate — "
                  "the relationship is protocol arithmetic.", y=T + ph + 72))
    return svg("".join(p), h=h)


# ------------------------------ chart 12: coefficient plot, every tested hypothesis
def chart_coefficients():
    data = series()
    staked = [d[1] for d in data]
    apr = [d[2] for d in data]
    px_ = [d[3] for d in data]
    ethbtc = [d[3] / d[4] for d in data]

    d_apr = [d * 10_000 for d in diffs(apr)]
    r_eth = [r * 100 for r in rets(px_)]
    r_eb = [r * 100 for r in rets(ethbtc)]
    g_stk = [r * 100 for r in rets(staked)]

    def sd(v):
        m = sum(v) / len(v)
        return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))

    tests = [
        ("ΔAPR → ETH return", d_apr, r_eth),
        ("ΔAPR → ETH/BTC return", d_apr, r_eb),
        ("ETH return → staked growth (same month)", r_eth, g_stk),
        ("ETH return t → staked growth t+1", r_eth[:-1], g_stk[1:]),
        ("staked growth t → ETH return t+1", g_stk[:-1], r_eth[1:]),
    ]
    rows = []
    for name, x, y in tests:
        reg = OLS(x, y, name)
        k = sd(x) / sd(y)                       # standardise: sd of y per sd of x
        rows.append((name, reg.slope * k, reg.ci[0] * k, reg.ci[1] * k, reg.p, reg.r2))

    h = 410
    t, b = 108, 300
    l = 268                                 # wide left margin: the row labels are long
    pw = W - l - 78                         # right gutter holds the p-values
    lim = 0.55
    pxf = lambda v: l + (v + lim) / (2 * lim) * pw
    rowh = (b - t) / len(rows)

    p = [f'<text x="{L}" y="26" class="ti">Every price-and-yield channel tested, and '
         f'every one of them is zero</text>',
         f'<text x="{L}" y="45" class="sub">Standardised OLS slopes with 95% confidence '
         f'intervals. Units are standard deviations of the outcome per standard '
         f'deviation of the driver,</text>',
         f'<text x="{L}" y="63" class="sub">so the five tests are directly comparable. '
         f'An interval that crosses the dashed zero line cannot reject "no effect". '
         f'All five cross it.</text>']

    for v in (-0.5, -0.25, 0.0, 0.25, 0.5):
        cls = "zero" if v == 0 else "grid"
        p.append(f'<line x1="{pxf(v):.1f}" y1="{t-8}" x2="{pxf(v):.1f}" y2="{b+8}" '
                 f'class="{cls}"/>')
        p.append(f'<text x="{pxf(v):.1f}" y="{b+28:.1f}" class="ax" '
                 f'text-anchor="middle">{v:+.2f}</text>')

    for i, (name, bta, lo, hi, pv, r2) in enumerate(rows):
        cy = t + rowh * (i + 0.5)
        p.append(f'<text x="{l-14}" y="{cy+4:.1f}" class="ax" text-anchor="end">'
                 f'{esc(name)}</text>')
        p.append(f'<g class="c1"><line x1="{pxf(lo):.1f}" y1="{cy:.1f}" '
                 f'x2="{pxf(hi):.1f}" y2="{cy:.1f}" stroke="var(--c)" stroke-width="2.4" '
                 f'stroke-linecap="round" opacity=".55"/>'
                 f'<line x1="{pxf(lo):.1f}" y1="{cy-6:.1f}" x2="{pxf(lo):.1f}" '
                 f'y2="{cy+6:.1f}" stroke="var(--c)" stroke-width="2"/>'
                 f'<line x1="{pxf(hi):.1f}" y1="{cy-6:.1f}" x2="{pxf(hi):.1f}" '
                 f'y2="{cy+6:.1f}" stroke="var(--c)" stroke-width="2"/>'
                 f'<circle cx="{pxf(bta):.1f}" cy="{cy:.1f}" r="5" class="dot"/></g>')
        p.append(f'<text x="{l+pw+10}" y="{cy+4:.1f}" class="mono">'
                 f'p={pv:.2f}</text>')

    p.append(xtitle("Standardised slope (sd of outcome per sd of driver)",
                    y=b + 52, x=l + pw / 2))
    p.append(note("Reading: the widest interval spans "
                  f"{min(r[2] for r in rows):+.2f} to {max(r[3] for r in rows):+.2f} standard "
                  "deviations. Monthly data cannot rule out a small yield effect; what it rules "
                  "out is a large one, which is the claim EIP-8363's opponents are making. "
                  "n = 42 monthly changes (41 for the lead and lag tests), Jan 2023 - Jul 2026.",
                  y=b + 76, x=L))
    return svg("".join(p), h=h)


CHARTS = (
    ("burn-collapse", chart_burn),
    ("issuance-vs-burn", chart_issuance_vs_burn),
    ("staked-eth-history", chart_staked_history),
    ("staking-apr-split", chart_apr_split),
    ("issuance-curves", chart_issuance),
    ("staking-equilibrium", chart_equilibrium),
    ("lst-share", chart_lst_share),
    ("lst-collateral", chart_lst_collateral),
    ("yield-vs-price-panels", chart_yield_price_panels),
    ("yield-price-regression", chart_regression),
    ("stake-rate-vs-yield", chart_rate_vs_yield),
    ("regression-coefficients", chart_coefficients),
)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in CHARTS:
        with open(f"{OUT}/{name}.svg", "w") as f:
            f.write(fn())
        print(f"wrote {OUT}/{name}.svg")
