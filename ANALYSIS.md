# EIP-8363 — data pack and editorial review

Companion to the draft *"EIP-8363: Ethereum's Most Courageous Monetary Experiment."*
Fills the two `[TODO: Need data analysis]` blocks, builds the charts, cross-checks the
model against Blockworks and Messari, and sets out where the argument needs fixing.

Data pulled 13 Aug 2026. Sources and reproduction steps in [§10](#10-how-to-verify).

**Fastest read:** [§0](#0-the-one-thing-that-changes-the-whole-article) (the burn is
dead), [§3c](#3c-equilibrium--the-number-that-actually-settles-the-argument) (the
mechanism is self-limiting), [§7](#7-where-momirs-framework-is-questionable) (what to
fix before publishing).

---

## 0. The one thing that changes the whole article

**The burn is gone.** EIP-1559 destroyed 1.48M ETH in 2022. Over the last twelve
months it destroyed **27,545 ETH** — a 98% collapse — and the current run-rate is
lower still (1,133 ETH in July 2026, ~13.7k/yr annualised).

![EIP-1559 fee burn per day by year, collapsing from 8,844 ETH/day in 2021 to 60 ETH/day in 2026, far below both the current issuance line and the maximum issuance line under EIP-8363](charts/burn-collapse.svg)

| Year | ETH burned | ETH/day |
|---|---|---|
| 2021 (from 5 Aug) | 1,317,700 | 8,844 |
| 2022 | 1,482,912 | 4,063 |
| 2023 | 1,093,504 | 2,996 |
| 2024 | 634,265 | 1,733 |
| 2025 | 91,175 | 250 |
| 2026 YTD (to 31 Jul) | 12,638 | 60 |

Against gross issuance of ~1.08M ETH/yr, the burn now offsets **2.6%** of new supply.
"Ultrasound money" is over as a mechanism. L2 migration and blob scaling moved the fee
base off L1 — L1 gas *used* actually doubled over the period (3.4bn → 6.7bn units/month)
while base fees collapsed, so this is a price effect, not a demand effect.

This matters because it reframes the entire debate. The draft presents EIP-8363 as a
*choice* between yield and scarcity. The stronger framing: **issuance policy is now the
only remaining lever Ethereum has over ETH's supply**, because the demand-driven one
stopped working. That should be near the top of the piece.

Blockworks published the same finding independently on 5 Aug ("Demand, Not Issuance,
Sets ETH's Monetary Path"), and their per-day figures match ours to within rounding —
see [§9](#9-cross-check-against-blockworks-and-messari). Two things follow. The
observation is solid enough to build on. It is also no longer proprietary, so the
article's edge has to come from what we do with it, not from stating it.

---

## 1. What EIP-8363 actually does

The draft never states the mechanism, which makes it impossible for a reader to judge
the magnitudes. From the spec:

| Parameter | Value |
|---|---|
| Burn fraction | `b = (D / D_sat)^1.5`, clamped at 1 |
| `SATURATION_BALANCE` (`D_sat`) | 60,250,000 ETH (~50% of supply) |
| `TRANSITION_BASE_REWARD_FACTOR` | 128 (2× standard) |
| `TRANSITION_DURATION_EPOCHS` | 123,300 (~18 months) |
| `BASE_REWARD_FACTOR` (terminal) | 64 |

Rewards are still *earned* in full; a fraction `b` of the **idealised** reward for each
duty (attestation, proposal, sync committee) is then burned. Sizing the deduction on
idealised rather than actual performance keeps per-duty marginal incentives intact —
an offline validator is not penalised twice. Attestation burns pause during an
inactivity leak. Execution-layer income (priority fees + MEV) is **untouched**.

Two consequences the draft gets wrong or omits:

1. **Issuance does not go to zero.** At today's 41.9M staked, `b = 58%`. Zero issuance
   requires 60.25M ETH staked — 44% above today's record. The honest headline is
   "roughly halves issuance at current staking levels", not "cuts issuance to zero."
2. **The 18-month transition is nearly neutral on day one.** Doubling the base reward
   factor to 128 offsets most of a 58% burn: net issuance at launch is ~0.84× today's,
   then decays to 0.42× as the factor tapers back to 64. The pain is spread, not
   instant. That is a meaningful answer to the "shock to DeFi" objection.

---

## 2. Baseline: where Ethereum actually is

| Metric | Value | As of |
|---|---|---|
| ETH price | $1,896 | 13 Aug 2026 |
| ETH market cap | $228.8B | |
| ETH circulating supply | 120,681,993 | |
| Drawdown from ATH ($4,946) | −61.7% | |
| BTC price / mcap | $63,701 / $1.279T | |
| **ETH/BTC** | **0.0298** (−57% since Jan 2023) | |
| ETH staked | 41.9M ETH (34.7% of supply) — record high | Aug 2026 |
| Active validators | ~897k | |
| Reported staking APR | 2.78% | |
| Ethereum DeFi TVL | $41.3B (of $75.3B all chains) | |

### Supply dynamics

| Flow | ETH/yr | % of supply |
|---|---|---|
| Gross consensus-layer issuance | 1,076,652 | 0.892% |
| EIP-1559 burn (trailing 12m) | 27,545 | 0.023% |
| **Net supply growth** | **1,049,107** | **0.869%** |
| Value of gross issuance | **$2.04B/yr** | |

Issuance is modelled as `I(S) = 940.9 · √(S/32)` ETH/yr, the protocol's own reward
curve. At S = 41.9M this gives a consensus-layer APR of 2.57%; the reported 2.78%
implies **~0.21% from execution-layer rewards**, i.e. ~88k ETH/yr of priority fees plus
MEV. Measured priority fees alone are 39k ETH/yr, so MEV is ~49k ETH/yr. Both are
falling fast: priority fees are down 66% year-on-year (9,697 ETH in Aug-2024 → 3,262
ETH in Jul-2026).

**Validator income is now ~92.5% issuance and ~7.5% fees.** That ratio is the crux of
the whole debate and it is not in the draft.

---

## 3. Modelling EIP-8363 (`issuance_model.py`)

### 3a. Applied at today's staking level, no behavioural response

| | Net issuance | % supply/yr | Staking APR |
|---|---|---|---|
| Today | 1,076,652 | 0.892% | 2.78% |
| Phase-in start (BRF 128) | 904,510 | 0.749% | 2.37% |
| Fully phased in (BRF 64) | 452,255 | 0.375% | **1.29%** |

Issuance cut: **−58%**. Staking APR cut: **−54%**. Dilution removed: **624k ETH/yr =
$1.18B/yr = 0.52% of ETH market cap per year.**

![Annual ETH issuance as a share of supply against staking ratio: today's curve rises steadily, the EIP-8363 launch curve peaks near 1.0% at 20% staked, and the permanent curve peaks near 0.5%, both falling to zero at 50% staked](charts/issuance-curves.svg)

### 3b. The full curve (fully phased in)

| Staked | % supply | b | Net issuance | % supply/yr | Post-8363 APR | Today's APR |
|---|---|---|---|---|---|---|
| 10M | 8.3% | 6.8% | 490,413 | 0.406% | 5.78% | 6.14% |
| 20M | 16.6% | 19.1% | 601,583 | 0.498% | 3.45% | 4.16% |
| 25M | 20.7% | 26.7% | **609,360** | **0.505%** | 2.79% | 3.68% |
| 30M | 24.9% | 35.1% | 590,930 | 0.490% | 2.26% | 3.33% |
| 40M | 33.1% | 54.1% | 482,905 | 0.400% | 1.43% | 2.85% |
| 50M | 41.4% | 75.6% | 286,979 | 0.238% | 0.75% | 2.53% |
| 60M | 49.7% | 99.4% | 8,011 | 0.007% | 0.16% | 2.29% |

Issuance peaks at ~0.505% of supply around 25M staked, then declines — matching the
EIP's own claim.

### 3c. Equilibrium — the number that actually settles the argument

Stakers are not passive. If yield falls below their required return they exit, which
raises gross APR *and* lowers `b`. Solving for the fixed point:

![Total staking yield against ETH staked, under today's rules and under EIP-8363. The EIP-8363 curve crosses a 2% hurdle at 32.9M staked and a 1.25% hurdle at 42.5M](charts/staking-equilibrium.svg)

| Marginal staker's required return | Equilibrium stake | % of supply | Net issuance | % supply/yr |
|---|---|---|---|---|
| 0.50% | 54.1M ETH | 44.8% | 182,493 | 0.151% |
| 1.00% | 46.1M ETH | 38.2% | 373,156 | 0.309% |
| **1.25%** | **42.5M ETH** | **35.2%** | 442,697 | 0.367% |
| 1.50% | 39.0M ETH | 32.3% | 497,392 | 0.412% |
| 2.00% | 32.9M ETH | 27.2% | 569,357 | 0.472% |
| 2.50% | 27.6M ETH | 22.9% | 602,777 | 0.499% |

Read this against the two loudest claims in the debate:

- **"Issuance goes to zero."** Only if the marginal staker will work for ~0.5%. At any
  plausible required return, ETH still inflates 0.3–0.5%/yr. Supporters are overselling.
- **"Staking collapses."** At a 2% hurdle the staking ratio settles at 27% — below
  today's 34.7% but above where it sat through most of 2024. Critics are overselling too.

The mechanism is self-limiting by construction, and the piece should say so. That is
the genuinely interesting design point and it is currently missing.

---

## 4. `[TODO]` #1 — correlation between ETH price and staking yield

**Answer: there isn't one.** (`yield_price_analysis.py`, 43 months, Jan-2023 → Jul-2026.)

| Test | Pearson | Spearman |
|---|---|---|
| Levels: APR vs ETH price | −0.410 | −0.360 |
| Levels: APR vs ETH/BTC | +0.835 | +0.824 |
| **Changes: ΔAPR vs ETH monthly return** | **−0.055** | −0.154 |
| **Changes: ΔAPR vs ETH/BTC monthly return** | **−0.046** | −0.134 |
| ETH return(t) → staked growth(t+1) | +0.038 | |
| staked growth(t) → ETH return(t+1) | −0.066 | |

Do **not** publish the level correlations. Consensus APR is a deterministic function of
the staked balance (`APR = 166.28/√S`), so it is a near-monotone series — it fell in 34
of 42 months, from 3.98% to 2.50%. Correlating that with a round-tripping price measures
the trend and nothing else. The +0.835 against ETH/BTC would let someone argue "falling
yield caused ETH/BTC to fall", which is exactly the kind of spurious result that gets a
research piece torn apart.

In changes, the relationship is **statistically indistinguishable from zero in both
directions**. Yield changes do not move price; price changes do not move staking flows.

The usable version of this for the article, which supports the author's thesis:

> Between January 2023 and July 2026, ETH's staking yield fell from 3.98% to 2.50% and
> ETH/BTC fell 57%. Over the same window, the month-to-month correlation between changes
> in staking yield and ETH's return was −0.05. The yield was there the whole way down.
> It did not defend the price, and its compression did not cause the decline. If a
> 37% cut in yield delivered by the existing reward curve had no detectable price
> effect, the burden of proof is on anyone claiming a further cut will.

Caveat to state: the staking series is reconstructed from on-chain flows (§8) and lands
5.4% above the reported 41.9M; direction and shape are reliable, the level is not exact.

---

## 5. `[TODO]` #2 — how exposed is the on-chain economy to ETH yield?

### 5a. Liquid staking

| Protocol | TVL | Share of staked ETH ($79.4B) |
|---|---|---|
| Lido | $17.94B | 22.6% |
| Binance staked ETH | $7.04B | 8.9% |
| ether.fi | $3.31B | 4.2% |
| Rocket Pool | $1.00B | 1.3% |
| Coinbase cbETH | $0.35B | 0.4% |
| **Top 5** | **$29.6B** | **37.3%** |

Lido alone is **43% of Ethereum's entire $41.3B DeFi TVL**. Any claim that "DeFi will be
fine" has to survive that number.

### 5b. Restaking

EigenLayer: **$5.05B** (DefiLlama) vs **$2.87B** (Surf) — see the data-conflict note in
§8. Kelp $0.87B. stETH deposited directly into EigenLayer: $525M.

### 5c. LSTs as lending collateral — the real dependency

| Protocol | Total TVL | wstETH | weETH | LST share |
|---|---|---|---|---|
| Aave V3 | $14.19B | $2.46B | $2.51B | **35.0%** |
| SparkLend | $3.57B | $2.37B | $0.08B | **68.6%** |
| Morpho Blue | $7.97B | $0.56B | $0.25B | 10.1% |
| Compound V3 | — | $0.21B | — | — |
| Fluid Lending | — | $0.15B | — | — |

Across the three largest Ethereum lending markets, **~$8.2B of ~$25.7B (32%) of
collateral is a staking-yield derivative.** SparkLend is a single-point-of-failure case:
more than two-thirds of it is wstETH.

Total LST/LRT deployed as DeFi collateral: **~$9.5–10B**, roughly a third of all
tokenised staked ETH.

### 5d. Yield trading

Pendle: $1.19B total, $698M on Ethereum. Note that a large share of Pendle's book has
migrated to stablecoin and non-ETH yield (Plasma $151M, Monad $163M, Arbitrum $132M) —
**Pendle is materially less ETH-yield-dependent than it was in 2024**, which cuts against
the bear case. Pool-level ETH-vs-stablecoin split is the one number I could not cleanly
resolve; worth a manual check before publishing.

### 5e. Protocol revenue at risk

Lido intermediates ~$535M/yr of gross staking rewards and keeps a 10% fee (~$53.5M/yr).
A 58% issuance cut removes 624k ETH/yr of rewards; Lido's 22.6% share of that is
**~$27M/yr of lost fee revenue** — about half its take. Meaningful for Lido, immaterial
for Ethereum.

### 5f. The honest answer to "what percentage of DeFi TVL depends on staked ETH?"

**Roughly 45–50% of Ethereum DeFi TVL is staking-linked, but the number is inflated by
double-counting and the *dependency* is weaker than the *exposure*.**

- Double-counting: DefiLlama books Lido's staked ETH once as Lido TVL and again when
  wstETH is deposited into Aave. The gross overlap is ~$10B.
- Exposure ≠ dependency. wstETH is used as collateral because it is liquid ETH exposure
  that pays *something*, not because it pays 2.78% specifically. A cut to 1.29% narrows
  the carry on leverage loops; it does not make wstETH a worse collateral asset than raw
  ETH — wstETH still strictly dominates WETH for any borrower who wants ETH exposure.
- What genuinely breaks is the **leveraged staking loop** (deposit wstETH → borrow ETH →
  restake), which only works while staking yield exceeds the ETH borrow rate. At a 1.29%
  post-8363 yield that spread is negative in most rate environments. Getting the current
  Aave WETH borrow APR into the piece would let you state the exact break-even; the
  DefiLlama yields endpoint did not return clean borrow rates and this is worth one
  manual lookup.

So: the ecosystem that unwinds is the leveraged one, not the collateral one. That is a
smaller and more defensible claim than the draft's "the ecosystem depends on
inflationary subsidies", and it is the version I would publish.

---

## 6. Editorial review

### What's strong and should stay

- The security-input-vs-security-outcome distinction is correct and well framed.
- The diminishing-returns-on-security-budget argument is right, and the EIP's own
  rationale agrees with you.
- The instinct that yield-driven demand was overrated now has data behind it (§4).

### What needs fixing

**1. The QT analogy is wrong.** Quantitative tightening withdraws existing base money
from the system. Reducing ETH issuance removes nothing — it slows the growth of the
float. No liquidity is drained; no balance sheet shrinks. The correct analogy is a lower
dividend or a lower money-growth rate, not QT. As written, "It removes liquidity from
the system" is simply false, and a sharp reader will stop there. I'd cut the section
heading and rebuild it around the actual mechanism below.

**2. Issuance is a transfer, not a subsidy.** New ETH does not enter the ecosystem from
outside — it is a dilution tax on non-stakers paid to stakers. So the ecosystem is not
"subsidised by emissions"; it is **built on redistributing dilution**. That is a sharper
and more damaging version of your own point, and it survives scrutiny in a way
"inflationary subsidy" does not. It also explains why the burn is the neutral mechanism:
burning a staker's reward is a transfer *back* to all holders, not a destruction of
aggregate purchasing power.

**3. The Bitcoin comparison does too much work.** Two problems:
   - *Level vs change.* Bitcoin proves an asset that has *never* paid a yield can be
     money. It says nothing about the effect of *removing* a yield that already exists
     and around which $30B of infrastructure has been priced. Those are different claims.
   - *The security budget point cuts the other way.* Bitcoin's security is also paid by
     issuance, and its unsolved long-run problem is exactly that the subsidy goes to zero
     with no equilibrium mechanism. EIP-8363 is Ethereum choosing a floor mechanism
     deliberately. That is a *better* argument than "Bitcoin proves you don't need
     yield" — use it instead.

**4. The attack-surface list understates the threat.** You list censorship, reordering,
reorgs, double-spends. The cheapest meaningful attack is missing: **a ⅓ stake can
prevent finality** — no double-spend required, no external counterparty required, no
coordination with a merchant. That is the liveness attack, it is a third of the cost of
your framing, and omitting it is the kind of gap a critic will use to dismiss the whole
security section. It doesn't damage your conclusion — ⅓ of even a 25M-ETH stake is
~$16B — but you have to name it.

**5. The carry-trade section is currently assertion.** Replace with §4. Also drop the
rhetorical "How many BTC holders pivoted to ETH because of the yield element?" — it
invites the answer "the ETH treasury companies and the staked ETFs, and here they are."
Which brings us to:

**6. Missing counter-argument: staked ETH ETFs and ETH treasury companies.** This is the
strongest live objection to your thesis and the draft doesn't engage it. These vehicles
market a *yield* on ETH to allocators who cannot access it otherwise. Their bid is
explicitly yield-driven and is the one demand channel that plausibly does shrink with
issuance. You need a paragraph on it, even if the conclusion is "small relative to the
0.52%/yr of dilution removed."

**7. Missing: what staking yield actually becomes.** Post-8363 the residual is execution
-layer income — priority fees and MEV — currently ~0.21% and falling 66% y/y. Stani
Kulechov's "institutions can't predict the yield" objection gets *stronger* under this
lens, not weaker: today's yield is a smooth deterministic function of the staked balance,
whereas the post-8363 residual is a volatile fee-driven number. If you want to rebut him,
rebut that, not the strawman that yields become low.

**8. Missing: transition reflexivity.** Over the 18-month taper, exiting stakers reduce
`D`, which lowers `b`, which raises the yield for everyone who stayed. That is a
stabiliser, and it is the best available answer to "the exit queue will cascade." Worth
a paragraph; it is the kind of second-order point that distinguishes a fund's note from
a newsletter.

### Structural suggestion

The draft's spine is "yield vs scarcity." The data suggests a stronger one:

> Ethereum's supply policy has been running on autopilot since the burn stopped working.
> Net issuance is 0.87%/yr, 97% of it flowing to stakers, offset by a fee burn that has
> collapsed 98% since 2022. EIP-8363 is not a choice between yield and scarcity — it is
> the first deliberate decision about ETH's money supply since 1559, forced by the fact
> that 1559 no longer does anything. And the market has already told us the yield was
> not what people were paying for.

---

## 7. Where Momir's framework is questionable

Section 6 lists fixes. This section is narrower and blunter: the load-bearing pieces of
the argument that would not survive a hostile reading. Ranked by how much damage each
does if a critic finds it first.

**1. "Reducing ETH issuance is economically similar to quantitative tightening. It
removes liquidity from the system." — this is the one that has to go.**
It is not a loose analogy, it is a category error, and it is the piece a rival analyst
would quote to dismiss the rest. QT shrinks a central bank's balance sheet: existing
base money is withdrawn from circulation. EIP-8363 withdraws nothing. Every ETH in
existence on the day it ships is still in existence the day after. What changes is the
*rate of growth of the float*, from 0.87%/yr to roughly 0.37%/yr. Nothing is drained,
no liquidity leaves the system, no balance sheet contracts. The whole "QT → weak
businesses fail → healthy discipline" passage is built on this and inherits the error.
The mechanism the section is reaching for is real — marginal activity that only pencils
at a 2.78% risk-free rate stops pencilling at 1.29% — but that is a hurdle-rate
argument, not a liquidity argument, and it needs to be written as one.

**2. "Ethereum's economy depends on inflationary subsidies" mislabels a transfer as a
subsidy.** A subsidy is paid from outside the system. Issuance is not: it is a dilution
tax levied on non-stakers and paid to stakers. No external value enters. Once that is
clear, the article's own bear case gets sharper *and* smaller — what the LST/restaking/
leverage complex is built on is the redistribution of dilution, and burning a staker's
reward is a transfer back to all holders rather than a destruction of purchasing power.
Momir's instinct is right; the label is wrong, and the wrong label is what makes the
bear case sound more dramatic than the numbers support.

**3. The Bitcoin comparison is doing load-bearing work it cannot support.** The article
uses it twice, and both uses have the same defect — a level-versus-change confusion.
Bitcoin demonstrates that an asset which has *never* paid a yield can become collateral.
It says nothing about what happens when you remove a yield that already exists and
around which ~$30B of infrastructure has been priced and levered. Worse, the security
half of the comparison cuts the other way: Bitcoin's security is also paid for by
issuance, and its unresolved long-run problem is precisely that the subsidy trends to
zero with no equilibrium mechanism. EIP-8363 is Ethereum installing the mechanism
Bitcoin lacks. That is a genuinely strong argument and it is sitting right there
unused, while the weaker version ("Bitcoin proves you don't need yield") is the one on
the page.

**4. The security section wins against an opponent who isn't there.** "ETH security
should not be measured by the amount of ETH staked" is correct, and the
input-versus-outcome distinction is the best thinking in the draft. But the attack list
— censor, reorder, reorg, double-spend — omits the cheapest real attack: a ⅓ stake
stalls finality. No merchant, no external counterparty, no coordination, a third of the
capital. Leaving it out is not fatal to the conclusion (a third of even a 25M-ETH stake
is ~$16B) but it is the first thing a protocol researcher will notice, and it makes the
section look like it was written to reach a conclusion rather than to test one. Then
engage the EIP's *own* security argument, which is not about quantity at all: the
authors defend the 50% threshold as the point beyond which a rescue coalition drawn
from stakers would constitute an economic majority. The draft never mentions it.

**5. "The market may have overestimated the importance of ETH yield" is asserted where
it could be demonstrated.** This is the thesis sentence of the whole piece and it
currently rests on a rhetorical question about BTC whales. [§4](#4-todo-1--correlation-between-eth-price-and-staking-yield)
supplies the evidence, and the evidence supports him. Publishing the claim without it,
when the test is this cheap to run, is the difference between a view and a finding.

**6. An unexamined assumption: that scarcity and yield trade off against each other at
all.** The framing "should ETH maximise economic activity around staking, or optimise
for becoming a stronger monetary asset" presumes the two compete for the same resource.
The equilibrium result in [§3c](#3c-equilibrium--the-number-that-actually-settles-the-argument)
says they mostly don't — the mechanism self-corrects, so you get a lower issuance rate
*and* a staking ratio in the high 20s to mid 30s, not one or the other. The article's
central tension may be softer than it is presented, which is a more interesting finding
than the tension itself.

**7. A framing risk worth naming: the piece is directionally long the proposal, and the
data mostly agrees, which is exactly when to be careful.** Everything in §0–§5 supports
Momir's side. That is a reason to state the strongest opposing case in the article's
own voice rather than in summary — specifically Messari's "solution in search of a
problem" ([§9](#9-cross-check-against-blockworks-and-messari)) and the staked-ETF /
treasury-company demand channel, which is the one bid that is explicitly yield-driven
and which the draft does not mention at all.

**What is not questionable.** The security input/output distinction, the diminishing
returns on security budget, and the core intuition that yield-driven demand was
overrated — these hold up, and §4 strengthens the third. The problems above are in the
scaffolding, not the thesis.

---

## 8. Chart list

| # | Chart | Data |
|---|---|---|
| 1 | Monthly ETH burn, Aug-2021 → Jul-2026, log scale — *the 98% collapse* | `eth_supply_monthly.csv`, `burn_history.csv` |
| 2 | Gross issuance vs burn vs net issuance, annual | §2 + `burn_history.csv` |
| 3 | Staked ETH and staking ratio, 2021 → 2026 | `staked_eth_reconstructed.csv` |
| 4 | Staking APR: consensus vs execution layer, stacked | §2, `eth_supply_monthly.csv` |
| 5 | **Yield curve under EIP-8363 vs status quo, x = staked ETH** — the money chart | §3b |
| 6 | **Equilibrium staking ratio vs required return** | §3c |
| 7 | LST share of staked ETH (Lido dominance over time) | §5a |
| 8 | LST collateral as % of TVL, by lending protocol | §5c |
| 9 | ETH/BTC and staking APR, **two stacked panels sharing an x-axis**, with the Δ-correlation stated on the chart | §4 |

Three are built and embedded above (`charts/*.svg`, regenerate with `make_charts.py`):
the burn collapse (§0), the issuance curves (§3a) and the equilibrium curve (§3c). The
equilibrium chart is the one nobody else in this debate has published — lead with it.

One production note. Blockworks' stake-rate-vs-yield chart puts two different measures
on two y-axes, which lets the reader infer whatever relationship the axis scaling
implies — and here it implies a tight inverse link that [§4](#4-todo-1--correlation-between-eth-price-and-staking-yield)
shows is not there in changes. Don't reproduce that. Stacked panels on a shared x-axis
show the same two series honestly.

---

## 9. Cross-check against Blockworks and Messari

Both houses published on EIP-8363 in the week of 5 Aug. Our model was built independently
and reproduces their published figures closely, which is the strongest available evidence
that the method in §3 is sound.

| Quantity | This model | Blockworks | Δ |
|---|---|---|---|
| Fee burn, 2022 avg | 4,063 ETH/day | 4,063 | 0.0% |
| Fee burn, 2023 avg | 2,996 ETH/day | 2,996 | 0.0% |
| Fee burn, 2024 avg | 1,733 ETH/day | 1,740 | −0.4% |
| Fee burn, 2025 avg | 250 ETH/day | 255 | −2.0% |
| Fee burn, 2026 YTD | 60 ETH/day | 59 | +1.7% |
| Issuance at today's stake | 2,950 ETH/day | 2,878 | +2.5% |
| **Max net issuance under EIP-8363** | **1,669 ETH/day** | **1,636** | **+2.0%** |
| Permanent-curve peak issuance | 0.505% of supply | ~0.51% | — |
| Peak located at | 20.7% staked | ~20% | — |

The small positive bias on issuance is expected: our formula is the theoretical maximum
at 100% participation, and the burn series is base fees only where Blockworks includes
blob fees.

**What Blockworks adds that we could not measure.** Their "Validator Operator Revenue"
chart splits proposer income into priority fees, builder priority fees, tips and
issuance, and puts the fee share at roughly 20–25% in recent quarters. Our network-level
figure is ~7.5%. **These do not reconcile and I could not close the gap** — the Dune
`mev_boost` schema was unavailable, so our MEV number is a residual. The likely
explanation is that their series is per-proposer (a block proposer's own issuance reward
is a small slice of total network issuance, so fees loom much larger in that view) while
ours is network-wide. Anyone quoting a "fees are X% of validator income" number needs to
say which of the two they mean. Treat our 92.5%/7.5% split as network-level and flag it
as such; do not put it in the article next to a Blockworks chart without the distinction.

Their measured stake-rate-and-yield series (11.5% → 34.1% stake rate, 5.8% → 2.6% yield,
Sep 2022 → Aug 2026) is also better than our reconstruction, which lands 5.4% high on the
level. **Use their series for any published chart**; ours is for shape and for the
correlation test. Note their 2.6% yield versus the 2.78% in the press — the gap is almost
certainly consensus-layer-only versus including execution-layer income, and the article
should pick one definition and state it.

Their third chart — DEX volume and active addresses against ETH price, r = 0.87 and 0.69
on monthly levels — is a useful companion to §4: on-chain activity tracks price, not
yield. (Same level-correlation caveat applies, as their own footnote concedes.)

**Messari's position, and why it matters more than agreement would.** Messari calls
EIP-8363 *"a solution in search of a problem"* — issuance is already only ~0.85%/yr, so
the dilution being removed is small — and rates its odds of passing **low**. Their sharper
point: *"the impact addresses nominal yield, when real yield from the demand side remains
the core problem ETH faces."*

This is the best objection in the debate and the article must answer it directly, because
it is not a defence of the status quo — it partly agrees with Momir and then asks why he
cares. Two answers are available from our data:

1. **The magnitude is not trivial relative to what ETH actually earns.** 624k ETH/yr of
   dilution removed is 0.52% of market cap annually. Against an asset whose entire
   execution-layer income is ~0.2%/yr, removing half a point of dilution is larger than
   the network's whole fee economy.
2. **"Demand-side real yield is the real problem" is precisely §0's point, and it cuts
   toward the proposal, not away from it.** If fee demand is not coming back — and the
   99% burn collapse says it has not — then issuance is the only variable left. Messari
   treats the smallness of issuance as a reason for indifference; the same fact read
   against a dead burn makes it the only lever there is.

Their low-probability call should be reported as-is. A piece that says "this probably
won't pass, and here is why it should" is more credible than one that quietly implies
adoption.

---

## 10. How to verify

**Scripts** (all in `research/eip8363/`, no dependencies beyond the stdlib):

| File | Purpose |
|---|---|
| `issuance_model.py` | Issuance, burn fraction, yields, equilibrium solver → `model_output.txt` |
| `staking_history.py` | Reconstructs staked ETH from on-chain flows → `staked_eth_reconstructed.csv` |
| `yield_price_analysis.py` | Correlation tests → `correlation_output.txt` |
| `make_charts.py` | Renders the three embedded charts → `charts/*.svg` |

**Dune SQL** (paste at https://dune.com/queries):

```sql
-- EIP-1559 burn, monthly
SELECT date_trunc('month', time) AS mo,
       SUM(base_fee_per_gas * gas_used) / 1e18 AS eth_burned
FROM ethereum.blocks WHERE time >= TIMESTAMP '2021-08-01' GROUP BY 1 ORDER BY 1;

-- priority fees to proposers, monthly
SELECT date_trunc('month', block_time) AS mo,
       SUM(CAST(priority_fee_per_gas AS double) * CAST(gas_used AS double))/1e18 AS priority_fees_eth
FROM ethereum.transactions WHERE block_time >= TIMESTAMP '2024-08-01' GROUP BY 1 ORDER BY 1;

-- beacon deposits, monthly
SELECT date_trunc('month', block_time) AS mo, SUM(CAST(value AS double))/1e18 AS eth_deposited
FROM ethereum.traces
WHERE to = 0x00000000219ab540356cbb839cbe05303d7705fa
  AND value > CAST(0 AS uint256) AND tx_success AND success
GROUP BY 1 ORDER BY 1;

-- consensus withdrawals + validator count, monthly
SELECT date_trunc('month', block_time) AS mo,
       approx_distinct(validator_index) AS validators,
       SUM(CAST(amount AS double))/1e9 AS eth_withdrawn
FROM ethereum.withdrawals GROUP BY 1 ORDER BY 1;
```

**Third-party sources cited in §9:** Blockworks Research charts dated 5 Aug 2026
("EIP-8363 Issuance Transition", "Stake Rate vs. Staking Yield", "Price Cycles Pull
Activity Onchain", "Validator Operator Revenue", "Demand, Not Issuance, Sets ETH's
Monetary Path"); Messari, *EIP-8363: Tapered Issuance Burn*,
`https://messari.io/report/eip-8363`.

**Other sources:** CoinGecko (`/en/coins/ethereum`) for price, supply, ATH. DefiLlama
(`/protocol/{lido,aave-v3,sparklend,morpho-blue,eigenlayer,pendle}` and the wstETH /
weETH / stETH token pages) for TVL and collateral placement. EIP text:
`github.com/ethereum/EIPs/blob/master/EIPS/eip-8363.md`. Staked-ETH and APR headline
figures cross-checked against press reporting of the 41.9M record and 2.78% APR.

### Methodology notes

- **Issuance formula.** `I(S) = 940.9·√(S/32)` ETH/yr, derived from
  `base_reward_per_increment = 64e9/√(total_active_balance_gwei)` at 82,181 epochs/yr.
  This is the theoretical maximum; realised issuance is marginally lower at <100%
  participation.
- **MEV is a residual,** not measured. The Dune `mev_boost` schema was unavailable, so
  execution-layer income is inferred as `(reported 2.78% APR − modelled 2.57% CL APR) ×
  staked`. Priority fees within it *are* measured directly.
- **Staked-ETH reconstruction** uses `balance(t) = balance(t−1) + deposits − withdrawals
  + issuance`, iterating monthly from Nov-2020. It lands at 44.2M for Jul-2026 vs 41.9M
  reported — **+5.4%**, most likely activation-queue lag and sub-100% participation. Use
  it for shape, not levels; all headline numbers in this note are anchored to the
  reported 41.9M.
- **Validator counts are not a proxy for staked ETH post-Pectra.** Count peaked at 1.14M
  (Aug-2025) and is now ~883k, a 22% fall, while staked ETH hit a record — consolidation
  into 0x02 credentials (up to 2048 ETH per validator) explains the divergence. Anyone
  quoting "validators are leaving" is misreading this.

### Data conflicts

| Metric | Source A | Source B | Likely cause |
|---|---|---|---|
| EigenLayer TVL | $5.05B (DefiLlama) | $2.87B (Surf) | DefiLlama likely counts restaked LSTs at both layers; Surf nets them |
| Lido TVL | $17.94B (DefiLlama) | $17.81B (Surf) | 0.7%, timing — immaterial |
| Staked ETH | 41.41M (4 Aug) / 41.9M (record) | 44.2M (reconstructed) | activation queue + participation, see above |

### Gaps worth closing before publishing

1. Aave WETH borrow APR — needed for the exact leverage-loop break-even (§5f).
2. Pendle's ETH-yield vs stablecoin-yield split at pool level (§5d).
3. Staked-ETH ETF and treasury-company AUM, to size the yield-driven institutional bid
   (§6.6, §7.7).
4. The validator-revenue fee-share conflict with Blockworks (§9) — needs the MEV-boost
   proposer-payment series to settle. Ours is a residual, theirs is per-proposer, and
   the two are ~3x apart.
