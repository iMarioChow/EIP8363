# EIP-8363: Ethereum's Issuance Decision

**First version — 13 August 2026.**

EIP-8363 proposes burning a rising share of validator rewards as the staking ratio
climbs, reaching a 100% burn at 50% of supply staked. This note models what the proposal
does to issuance, yield and the staking equilibrium; tests whether ETH's yield has ever
explained its price; sizes what in the on-chain economy genuinely depends on that yield;
and sets out where we land.

Everything here is built from on-chain data and the EIP text. The model is independent
and reproduces published third-party figures to within 2%
([§9](#9-cross-check-against-blockworks-and-messari)); sources and reproduction steps
are in [§10](#10-how-to-verify).

**In brief:** the fee burn is dead, which leaves issuance as the only lever Ethereum
still has over ETH's supply. The proposal halves issuance at today's staking level
rather than zeroing it, and it is self-limiting — at any plausible staker hurdle rate
the system settles at 27–35% of supply staked and 0.3–0.5%/yr issuance. Meanwhile the
yield it cuts shows no detectable relationship to ETH's price. Full argument in
[§7](#7-conclusion).

**Fastest read:** [§0](#0-where-this-starts-the-burn-has-stopped-working),
[§3c](#3c-equilibrium--the-number-that-actually-settles-the-argument),
[§7](#7-conclusion).

---

## 0. Where this starts: the burn has stopped working

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

This reframes the debate. EIP-8363 is usually argued as a *choice* between staking yield
and monetary scarcity. It is better understood as something narrower and more forced:
**issuance policy is now the only remaining lever Ethereum has over ETH's supply**,
because the demand-driven one stopped working. Every supply question now routes through
the issuance schedule, whether or not anyone legislates it.

Blockworks reached the same conclusion independently on 5 Aug ("Demand, Not Issuance,
Sets ETH's Monetary Path"), and their per-day figures match ours to within rounding —
see [§9](#9-cross-check-against-blockworks-and-messari).

---

## 1. What EIP-8363 actually does

Most commentary skips the mechanism, which makes the magnitudes impossible to judge.
From the spec:

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

Two consequences are routinely misstated:

1. **Issuance does not go to zero.** At today's 41.9M staked, `b = 58%`. Zero issuance
   requires 60.25M ETH staked — 44% above today's record. The accurate headline is
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
the whole debate, and it is rarely stated.

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

The mechanism is self-limiting by construction. That is the most interesting property of
the design, and the one least discussed.

---

## 4. Does staking yield explain ETH's price?

### 4a. First, the question behind the question: are stake rate and yield correlated?

**Yes — perfectly, and by definition, not by observation.** This has to be settled before
any correlation work, because it determines what the data can and cannot show.

The protocol pays a fixed total reward pool that scales with the square root of the
staked balance, so per-ETH yield is a closed form:

```
issuance(S) = 940.9 · √(S/32)  ETH/yr        APR(S) = issuance(S)/S = 166.28 / √S
```

More stake divides the same pool among more coins. Correlation between stake rate and
issuance yield is **−1 by construction**. Plotting one against the other is plotting an
identity — it can look like a discovery, and it is arithmetic.

![Staking yield against ETH staked. A smooth declining curve is the protocol's reward formula, with independently reported yield observations sitting slightly above it; the gap between observation and curve is fee income, which narrows to almost nothing by 2026](charts/yield-identity.svg)

The curve above is not fitted to anything — it is the formula. The dots are yields
reported independently (Blockworks, and the press figure for native APR), deliberately
*not* our reconstructed series, which is derived from the same formula and would make
the fit circular.

Two things follow, and the second is the useful one:

1. **Blockworks' stake-rate-vs-yield chart is showing an identity.** Their yield fell
   5.8% → 2.6% while the stake rate rose 11.5% → 34.1%. That is what the formula
   requires. It is not evidence of anything beyond "more people staked."
2. **The only free variable is the gap between the dots and the curve — fee income.**
   It was ~1.34pp in 2022 and is 0.03–0.21pp today. Everything genuinely uncertain about
   ETH's staking yield lives in that wedge, and the wedge has collapsed along with the
   burn (§0). This is the sharper way to state the whole argument: *issuance yield is
   administered, fee yield is earned, and the earned part has gone to almost nothing.*

### 4b. The correlation itself

**Answer: there isn't one.** (`yield_price_analysis.py`, `yield_price_regression.py`;
43 months, Jan-2023 → Jul-2026.)

| Test | Pearson | Spearman |
|---|---|---|
| Levels: APR vs ETH price | −0.410 | −0.360 |
| Levels: APR vs ETH/BTC | +0.835 | +0.824 |
| **Changes: ΔAPR vs ETH monthly return** | **−0.055** | −0.154 |
| **Changes: ΔAPR vs ETH/BTC monthly return** | **−0.046** | −0.134 |
| ETH return(t) → staked growth(t+1) | +0.038 | |
| staked growth(t) → ETH return(t+1) | −0.066 | |

### 4c. Regression output

| | Levels: ETH price ~ APR | Changes: ETH return ~ ΔAPR |
|---|---|---|
| slope | −$871 per pp | −0.180 % per bp |
| 95% CI | — | [−1.233, +0.873] |
| t | −2.88 | −0.35 |
| **p** | **0.006** | **0.73** |
| **R²** | **0.168** | **0.003** |
| Durbin–Watson | **0.40** | 1.75 |
| n | 43 | 42 |

![Scatter of month-end ETH price against staking APR with an OLS fit; the fit looks strong but the residuals are heavily autocorrelated](charts/regression-levels.svg)

The levels regression is "significant" at p = 0.006 — and it is worthless. Durbin–Watson
of **0.40** says the residuals are heavily serially correlated, which is the textbook
signature of a spurious regression between two trending series. Both variables trend, so
they correlate; the standard errors are understated and the p-value is not usable.
**Do not publish this chart as evidence.** It is in the pack precisely so nobody
reproduces it in good faith.

![Scatter of ETH monthly return against the same month's change in staking APR, with a flat OLS fit and a wide residual band](charts/regression-changes.svg)

Differencing kills the trend and the relationship disappears: p = 0.73, R² = 0.003.
Durbin–Watson is 1.75, so this specification is clean. The 95% confidence interval spans
zero comfortably in both directions — the data cannot even sign the effect, let alone
size it.

![Rolling 12-month correlation between changes in staking yield and ETH returns, oscillating around zero and mostly inside a band where it is indistinguishable from zero](charts/regression-rolling.svg)

And it is not a stable relationship hiding inside a noisy average — the rolling
correlation crosses zero repeatedly and spends most of its life inside the band where it
cannot be distinguished from zero.

In changes, then, the relationship is **statistically indistinguishable from zero in both
directions**. Yield changes do not move price; price changes do not move staking flows.

Stated plainly:

> Between January 2023 and July 2026, ETH's staking yield fell from 3.98% to 2.50% and
> ETH/BTC fell 57%. Over the same window, the month-to-month correlation between changes
> in staking yield and ETH's return was −0.05. The yield was there the whole way down.
> It did not defend the price, and its compression did not cause the decline. If a
> 37% cut in yield delivered by the existing reward curve had no detectable price
> effect, the burden of proof is on anyone claiming a further cut will.

Caveat to state: the staking series is reconstructed from on-chain flows (§8) and lands
5.4% above the reported 41.9M; direction and shape are reliable, the level is not exact.

---

## 5. How exposed is the on-chain economy to ETH yield?

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

![Horizontal bars showing liquid-staking tokens as a share of TVL: SparkLend 68.6%, Aave V3 35.0%, Morpho Blue 10.1%, all three combined 32.0%](charts/defi-exposure.svg)

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
the bear case. The pool-level ETH-vs-stablecoin split remains an open number.

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
  post-8363 yield that spread is negative in most rate environments. The exact break-even
  needs the current Aave WETH borrow APR; the DefiLlama yields endpoint did not return
  clean borrow rates, so this stays an open number ([§10](#10-how-to-verify)).

**The part of the economy that unwinds is the leveraged one, not the collateral one.**
That is a smaller and far more defensible claim than "the ecosystem depends on
inflationary subsidies", which is how the bear case is usually put.

---

## 6. Arguments in this debate that don't survive scrutiny

Both sides of the EIP-8363 argument lean on claims that break under inspection. Ranked
by how much damage each does to whoever makes it.

**1. "Reducing issuance is quantitative tightening — it removes liquidity."**
A category error, and the most common one. QT shrinks a central bank's balance sheet:
existing base money is withdrawn from circulation. EIP-8363 withdraws nothing. Every ETH
in existence the day it ships is still in existence the day after. What changes is the
*growth rate of the float*, from 0.87%/yr to roughly 0.37%/yr. The right central-bank
analogy is **tapering QE, not tightening** — and that is not a weaker claim, because
markets price the flow, not the level.

There *is* a real flow being removed and it is worth stating precisely: ~624k ETH/yr,
1,711/day, ~$3.2M/day of newly minted ETH that stops arriving in stakers' hands. The
load-bearing assumption is what share of that would have been sold — compounding stakers
and auto-compounding LSTs never sell it. That share is measurable from exchange inflows
traced to withdrawal addresses, and it is the first thing a sceptic should attack.

**2. "The ecosystem depends on inflationary subsidies."**
A subsidy comes from outside the system. Issuance does not: it is a dilution tax levied
on non-stakers and paid to stakers. No external value enters. The LST, restaking and
leverage complex is built on **monetising a wealth transfer**, not on receiving one.

The distinction changes who bears the cost. Under "subsidy", cutting it reads as
austerity — the pie shrinks and everyone is poorer. Under "transfer", cutting it reads as
ending a redistribution: stakers and their intermediaries lose, every other holder gains
by exactly the same amount, and ETH holders in aggregate are flat. Strongly
redistributive, not contractionary. The subsidy framing quietly contradicts the very
thesis it is usually deployed to support.

**3. "Bitcoin proves an asset doesn't need yield."**
True and insufficient, for two reasons. First, a level-versus-change confusion: Bitcoin
shows that an asset which has *never* paid a yield can become collateral. It says nothing
about removing a yield that already exists and around which ~$30B of infrastructure is
priced and levered. Second, the security half of the comparison cuts the other way —
Bitcoin's security is *also* issuance-funded, and its unresolved long-run problem is
precisely a subsidy trending to zero with no equilibrium mechanism. EIP-8363 is Ethereum
installing the mechanism Bitcoin lacks. That is the stronger argument, and it is almost
never the one made.

**4. The security case is usually argued against the wrong attack.**
The standard list — censorship, reordering, reorgs, double-spends — omits the cheapest
meaningful attack: **a ⅓ stake stalls finality**. No merchant, no external counterparty,
no coordination, a third of the capital of the attacks usually named. This does not
overturn the conclusion that security has diminishing returns (⅓ of even a 25M-ETH stake
is ~$16B), but omitting it makes the argument look reverse-engineered.

The EIP's own security rationale is also worth engaging, because it is not about quantity
at all: the authors defend the 50% saturation point as the threshold beyond which a
rescue coalition drawn from stakers would constitute an economic majority.

**5. "The market overrated ETH's yield" is usually asserted, not tested.**
[§4](#4-does-staking-yield-explain-eths-price) tests it. Over 43 months the correlation
between changes in staking yield and ETH's return is −0.05, and price does not drive
staking flows either. The claim survives the test — but it should be published *with* the
test, not in place of it.

**6. The strongest objection is Messari's, and it deserves a direct answer.**
They call the proposal *"a solution in search of a problem"* — issuance is only ~0.85%/yr
— and note that *"the impact addresses nominal yield, when real yield from the demand
side remains the core problem."* That partly agrees with the pro-8363 case and then asks
why it matters. Two answers, both from the data above: the dilution removed (0.52% of
market cap per year) is larger than Ethereum's entire fee economy (~0.2%/yr); and if fee
demand is not returning — which the 99% burn collapse suggests — then issuance is the
only variable left. Messari reads the smallness of issuance as grounds for indifference;
read against a dead burn, the same fact makes it the only available lever.

**7. Three things missing from most treatments.**
- **Staked ETH ETFs and treasury companies.** The one demand channel that is explicitly
  yield-marketed, and therefore the one that plausibly shrinks with issuance. Sizing it
  is an open item ([§10](#10-how-to-verify)).
- **What the yield actually becomes.** Post-8363 the residual is execution-layer income,
  ~0.21% and falling 66% y/y. This strengthens rather than weakens the institutional
  objection that the yield becomes unpredictable: today's yield is a smooth deterministic
  function of the staked balance; the post-8363 residual is a volatile fee-driven number.
- **Transition reflexivity.** Over the 18-month taper, exiting stakers reduce `D`, which
  lowers `b`, which raises the yield for everyone who stayed. That is a stabiliser, and
  the best available answer to "the exit queue will cascade."

---

## 7. Conclusion

**The proposal is directionally right, and both camps are overstating its magnitude.**

Start with what is no longer in doubt. Ethereum's fee burn has fallen 99% since 2022 and
now offsets 2.6% of issuance. Whatever one thinks of EIP-8363, the mechanism that was
supposed to make ETH's supply demand-responsive has stopped functioning, and no plausible
recovery in L1 fees brings it back at current blob economics. Ethereum's monetary policy
is on autopilot, and issuance is the only steering left. That is the fact that forces
the question, and it is independent of anyone's view on staking.

**On magnitude, the honest numbers sit between the two campaigns.** At today's 41.9M
staked the proposal cuts issuance 58% and staking APR 54% — not to zero, which would need
60.25M staked, 44% above the record. And the mechanism is self-limiting: because exits
lower both the staked balance and the burn fraction, at a 2% staker hurdle the system
settles near 27% of supply staked with issuance around 0.47%/yr, and at 1.25% it settles
near today's level. Supporters promising the end of ETH issuance and critics warning of a
staking collapse are both describing states the mechanism does not reach. What it
delivers is roughly half the dilution, at a staking ratio somewhere in the high twenties
to mid thirties.

**On whether that dilution matters, the numbers are better than the rhetoric.** 624k
ETH/yr is $1.18B at current prices, or 0.52% of market cap annually — larger than
Ethereum's entire execution-layer fee economy, which runs at roughly 0.2%/yr. For an
asset whose fee income has collapsed, removing half a point of structural dilution is not
a rounding error. It is the largest lever available.

**On the cost side, the exposure is real but narrower than headline numbers suggest.**
A third of collateral in the three largest Ethereum lending markets is a staking-yield
derivative, and SparkLend is 69% wstETH. But exposure is not dependency: wstETH remains
strictly better collateral than plain WETH at any positive yield. What breaks at 1.29% is
the *levered* staking loop, which needs the staking yield to clear the ETH borrow rate.
The complex that unwinds is the leveraged one, not the collateral one — and the direct
protocol revenue at risk is modest, on the order of $27M/yr for Lido, about half its take.

**And on the central empirical question, the market has already answered.** Across 43
months, changes in staking yield show no detectable relationship to ETH's return
(p = 0.73, R² = 0.003), and the relationship does not run the other way either. Staking
yield fell from 3.98% to 2.50% while ETH/BTC fell 57%. The yield was there the whole way
down. It did not defend the price, and its compression did not cause the decline. If a
37% cut in yield delivered by the existing reward curve had no measurable price effect,
the burden of proof sits with anyone claiming a further cut will.

**Where we land.** The case for EIP-8363 is not the one usually made. It is not that
scarcity beats yield — it is that the yield is an administered number that no longer buys
what it is assumed to buy, sitting on top of a fee economy too small to matter, at a
moment when the only other supply lever has stopped working. The proposal converts an
unexamined default into a deliberate policy, and it does so with a self-correcting
mechanism rather than a cliff.

The strongest case against it is not the DeFi bear case, which the data shrinks. It is
Messari's: that this addresses nominal yield while real, demand-side yield remains
Ethereum's actual problem. That objection is correct on its own terms. It is simply not
an argument for leaving the one working lever untouched.

**What would change our mind.** Evidence that a large share of issuance is compounded
rather than sold, which would shrink the flow argument in §6.1. A staked-ETF and
treasury-company bid large enough that a yield cut removes real marginal demand. Or a
credible path back to L1 fee income — if the burn revives, the case for legislating
issuance weakens considerably, because the demand-driven mechanism would be working
again.

**On odds.** Messari rates passage low, and we see no reason to disagree. A proposal that
takes ~$1.2B/yr from the most organised constituency in the ecosystem, in exchange for a
diffuse benefit to every holder, is a hard governance problem regardless of whether the
economics are right. Being right and not passing is the most likely outcome here.

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

**Eight are built and embedded above.** `make_charts.py` renders five (burn collapse §0,
issuance curves §3a, equilibrium §3c, yield identity §4a, DeFi exposure §5c);
`yield_price_regression.py` renders the three regression figures in §4c. Both are pure
standard library — no matplotlib, no numpy — so they rebuild anywhere.

The equilibrium chart (§3c) and the yield-identity chart (§4a) are the two that have no
published equivalent elsewhere in this debate.

One production note. Blockworks' stake-rate-vs-yield chart puts two different measures on
two y-axes, which lets the reader infer whatever relationship the axis scaling implies.
Worse, as [§4a](#4a-first-the-question-behind-the-question-are-stake-rate-and-yield-correlated)
shows, those two series are related by an identity — the chart cannot help but look
meaningful. Stacked panels on a shared x-axis show the same data without the implication.

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
say which of the two they mean. Our 92.5%/7.5% split is network-level and should always
be labelled as such.

Their measured stake-rate-and-yield series (11.5% → 34.1% stake rate, 5.8% → 2.6% yield,
Sep 2022 → Aug 2026) is also better than our reconstruction, which lands 5.4% high on the
level. Ours is used for shape and for the correlation test only. Note their 2.6% yield
against the 2.78% quoted in the press — the gap is almost certainly consensus-layer-only
versus including execution-layer income. This note uses 2.78% as the total and states the
2.57% consensus-only figure separately throughout.

Their third chart — DEX volume and active addresses against ETH price, r = 0.87 and 0.69
on monthly levels — is a useful companion to §4: on-chain activity tracks price, not
yield. (Same level-correlation caveat applies, as their own footnote concedes.)

**Messari's position, and why it matters more than agreement would.** Messari calls
EIP-8363 *"a solution in search of a problem"* — issuance is already only ~0.85%/yr, so
the dilution being removed is small — and rates its odds of passing **low**. Their sharper
point: *"the impact addresses nominal yield, when real yield from the demand side remains
the core problem ETH faces."*

This is the best objection in the debate and it needs a direct answer, because it is not
a defence of the status quo — it partly agrees with the pro-8363 case and then asks why
it matters. Two answers from the data above:

1. **The magnitude is not trivial relative to what ETH actually earns.** 624k ETH/yr of
   dilution removed is 0.52% of market cap annually. Against an asset whose entire
   execution-layer income is ~0.2%/yr, removing half a point of dilution is larger than
   the network's whole fee economy.
2. **"Demand-side real yield is the real problem" is precisely §0's point, and it cuts
   toward the proposal, not away from it.** If fee demand is not coming back — and the
   99% burn collapse says it has not — then issuance is the only variable left. Messari
   treats the smallness of issuance as a reason for indifference; the same fact read
   against a dead burn makes it the only lever there is.

We report their low-probability call as-is and agree with it — see
[§7](#7-conclusion).

---

## 10. How to verify

**Scripts** (all in `research/eip8363/`, no dependencies beyond the stdlib):

| File | Purpose |
|---|---|
| `issuance_model.py` | Issuance, burn fraction, yields, equilibrium solver → `model_output.txt` |
| `staking_history.py` | Reconstructs staked ETH from on-chain flows → `staked_eth_reconstructed.csv` |
| `yield_price_analysis.py` | Correlation tests → `correlation_output.txt` |
| `yield_price_regression.py` | OLS with t / p / R² / Durbin–Watson, plus the three §4c figures |
| `make_charts.py` | Renders the other five charts → `charts/*.svg` |

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
   This sets where the levered staking loop turns negative, the single most load-bearing
   number in the bear case.
2. Pendle's ETH-yield vs stablecoin-yield split at pool level (§5d).
3. Staked-ETH ETF and treasury-company AUM, to size the yield-driven institutional bid
   ([§6.7](#6-arguments-in-this-debate-that-dont-survive-scrutiny)).
4. The validator-revenue fee-share conflict with Blockworks (§9) — needs the MEV-boost
   proposer-payment series to settle. Ours is a residual, theirs is per-proposer, and
   the two are ~3x apart.
