"""
Render the three charts embedded in ANALYSIS.md as standalone, theme-aware SVGs.

No dependencies. Colours are the validated categorical slots 1-3 (blue / orange /
aqua), stepped separately for the light and dark surfaces; every series is direct-
labelled so identity never rests on colour alone.

    python3 make_charts.py        # writes charts/*.svg
"""
import math, os
from issuance_model import (SUPPLY, STAKED, D_SAT, issuance, burn_fraction,
                            net_issuance_8363, yields, status_quo_yields,
                            equilibrium_stake, EL_TOTAL)

OUT = "charts"
W, H = 880, 470
L, R, T, B = 68, 30, 58, 62          # plot margins
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

    p.append(f'<text x="{L}" y="{T+PH+52:.0f}" class="note">'
             'Base-fee burn measured from every Ethereum block (Dune). '
             '2021 dates from the 5 Aug London fork; 2026 through 31 Jul. '
             'Latest month, Jul 2026: 37 ETH/day.</text>')
    p.append(f'<text x="{L}" y="{y(0):.0f}" class="base" />')
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
    p.append(f'<text x="{L+PW/2:.0f}" y="{T+PH+42:.0f}" class="axt" text-anchor="middle">'
             'Share of ETH supply staked</text>')

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
    p.append(f'<text x="{L+PW/2:.0f}" y="{T+PH+42:.0f}" class="axt" text-anchor="middle">'
             'ETH staked</text>')

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
    p.append(f'<text x="{L}" y="{T+PH+58:.0f}" class="note">'
             'Execution-layer income (priority fees + MEV, ~88k ETH/yr) is untouched by the '
             'proposal and sets the floor. Yield is capped at 6% for legibility.</text>')
    return svg("".join(p))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("burn-collapse", chart_burn),
                     ("issuance-curves", chart_issuance),
                     ("staking-equilibrium", chart_equilibrium)):
        with open(f"{OUT}/{name}.svg", "w") as f:
            f.write(fn())
        print(f"wrote {OUT}/{name}.svg")
