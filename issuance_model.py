"""
EIP-8363 (Tapered Issuance Burn) — issuance, yield and staking-equilibrium model.

Sources for the empirical inputs are documented in ANALYSIS.md.
All ETH-denominated flows are annualised.
"""
import math

# ---------------------------------------------------------------- constants
SUPPLY          = 120_681_993      # ETH circulating supply (CoinGecko, 2026-08-13)
STAKED          = 41_900_000       # ETH staked (record high, Aug 2026)
D_SAT           = 60_250_000       # EIP-8363 SATURATION_BALANCE
PRICE           = 1_896.17         # ETH/USD (CoinGecko, 2026-08-13)

# Consensus-layer issuance:  I(S) = 940.9 * sqrt(S/32)  ETH/yr  ==  166.28 * sqrt(S)
#   derived from base_reward_per_increment = 64e9 / sqrt(total_active_balance_gwei)
K_ISSUANCE      = 940.9 / math.sqrt(32)          # = 166.28

# Execution-layer rewards (priority fees + MEV), ETH/yr.
#  - priority fees measured on-chain: 3,262 ETH in Jul-2026  ->  39.1k ETH/yr
#  - MEV taken as the residual between the reported 2.78% APR and modelled CL APR
EL_PRIORITY_FEES = 39_150
EL_TOTAL         = 88_000          # priority fees + MEV, see ANALYSIS.md
BURN_ANNUAL      = 27_545          # EIP-1559 burn, trailing 12m (Aug-25..Jul-26).
                                   # Current run-rate is lower still: 13.7k ETH/yr.


def issuance(staked: float) -> float:
    """Gross consensus-layer issuance, ETH/yr, under today's rules."""
    return K_ISSUANCE * math.sqrt(staked)


def burn_fraction(staked: float) -> float:
    """EIP-8363 burn fraction b = (D / D_sat)^1.5, clamped at 1."""
    return min(1.0, (staked / D_SAT) ** 1.5)


def net_issuance_8363(staked: float, base_reward_factor: float = 64.0) -> float:
    """Issuance surviving the tapered burn. BRF=128 during the 18-month phase-in."""
    return issuance(staked) * (base_reward_factor / 64.0) * (1 - burn_fraction(staked))


def yields(staked: float, brf: float = 64.0):
    """Return (cl_apr, el_apr, total_apr) as decimals, post-8363."""
    cl = net_issuance_8363(staked, brf) / staked
    el = EL_TOTAL / staked
    return cl, el, cl + el


def status_quo_yields(staked: float):
    cl = issuance(staked) / staked
    el = EL_TOTAL / staked
    return cl, el, cl + el


def equilibrium_stake(required_return: float) -> float:
    """Staked ETH at which post-8363 total yield equals the required return."""
    lo, hi = 1_000_000.0, D_SAT
    for _ in range(200):
        mid = (lo + hi) / 2
        if yields(mid)[2] > required_return:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def pct(x):  return f"{x*100:.2f}%"
def mm(x):   return f"{x/1e6:.2f}M"


if __name__ == "__main__":
    print("=" * 78)
    print("1. TODAY  (status quo)")
    print("=" * 78)
    cl, el, tot = status_quo_yields(STAKED)
    gross = issuance(STAKED)
    print(f"  staked                 {mm(STAKED)} ETH  ({STAKED/SUPPLY*100:.1f}% of supply)")
    print(f"  gross CL issuance      {gross:,.0f} ETH/yr  ({gross/SUPPLY*100:.3f}% of supply)")
    print(f"  EIP-1559 burn          {BURN_ANNUAL:,.0f} ETH/yr  ({BURN_ANNUAL/SUPPLY*100:.3f}% of supply)")
    print(f"  net supply growth      {(gross-BURN_ANNUAL)/SUPPLY*100:.3f}% /yr")
    print(f"  burn offsets           {BURN_ANNUAL/gross*100:.1f}% of issuance")
    print(f"  staking APR  CL {pct(cl)}  + EL {pct(el)}  = {pct(tot)}")
    print(f"  USD value of issuance  ${gross*PRICE/1e9:.2f}B /yr")

    print()
    print("=" * 78)
    print("2. EIP-8363 APPLIED AT TODAY'S STAKING LEVEL (no behavioural response)")
    print("=" * 78)
    b = burn_fraction(STAKED)
    print(f"  burn fraction b        {pct(b)}")
    for label, brf in (("phase-in start (BRF=128)", 128.0), ("fully phased in (BRF=64)", 64.0)):
        ni = net_issuance_8363(STAKED, brf)
        c, e, t = yields(STAKED, brf)
        print(f"  {label:26s} net issuance {ni:>10,.0f} ETH/yr "
              f"({ni/SUPPLY*100:5.3f}% supply)  APR {pct(t)}")
    ni = net_issuance_8363(STAKED)
    print(f"  -> issuance cut        {(1-ni/gross)*100:.1f}%")
    print(f"  -> staking APR cut     {(1-yields(STAKED)[2]/tot)*100:.1f}%")

    print()
    print("=" * 78)
    print("3. YIELD / ISSUANCE CURVE ACROSS STAKING LEVELS (fully phased in)")
    print("=" * 78)
    print(f"  {'staked':>8} {'% supply':>9} {'b':>7} {'net iss ETH/yr':>15} "
          f"{'% supply/yr':>12} {'CL APR':>8} {'EL APR':>8} {'total':>8} {'today APR':>10}")
    for s in range(10_000_000, 60_250_001, 5_000_000):
        c, e, t = yields(s)
        _, _, t0 = status_quo_yields(s)
        print(f"  {mm(s):>8} {s/SUPPLY*100:8.1f}% {burn_fraction(s):6.1%} "
              f"{net_issuance_8363(s):15,.0f} {net_issuance_8363(s)/SUPPLY*100:11.3f}% "
              f"{pct(c):>8} {pct(e):>8} {pct(t):>8} {pct(t0):>10}")

    print()
    print("=" * 78)
    print("4. EQUILIBRIUM STAKE FOR A GIVEN REQUIRED RETURN (post-8363)")
    print("=" * 78)
    print(f"  {'required':>9} {'equilibrium stake':>19} {'% supply':>10} "
          f"{'net issuance':>14} {'% supply/yr':>12}")
    for r in (0.005, 0.0075, 0.010, 0.0125, 0.015, 0.020, 0.025):
        s = equilibrium_stake(r)
        print(f"  {pct(r):>9} {mm(s)+' ETH':>19} {s/SUPPLY*100:9.1f}% "
              f"{net_issuance_8363(s):14,.0f} {net_issuance_8363(s)/SUPPLY*100:11.3f}%")

    print()
    print("=" * 78)
    print("5. WHAT THE ISSUANCE CUT IS WORTH, AND WHAT IT COSTS")
    print("=" * 78)
    saved = gross - net_issuance_8363(STAKED)
    print(f"  issuance removed       {saved:,.0f} ETH/yr = ${saved*PRICE/1e9:.2f}B/yr at ${PRICE:,.0f}")
    print(f"  as % of ETH mcap       {saved*PRICE/(SUPPLY*PRICE)*100:.3f}% /yr")
    # Lido custodies $17.94B of the $79.4B staked -> 22.6% of the removed issuance
    # would have been Lido's, of which the protocol keeps a 10% fee.
    lido_share = 17_944_614_912 / (STAKED * PRICE)
    print(f"  Lido share of stake    {lido_share*100:.1f}%")
    print(f"  Lido fee revenue lost  ${saved*PRICE*lido_share*0.10/1e6:.0f}M/yr "
          f"(vs ~${1_466_555*365/1e6:.0f}M/yr gross staking rewards it intermediates today)")
