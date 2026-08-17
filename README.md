# EIP-8363: Ethereum's Issuance Decision

First-version research on EIP-8363 (Tapered Issuance Burn) — what it does to ETH
issuance, staking yield and the staking equilibrium, whether staking yield has ever
explained ETH's price, and what in the on-chain economy actually depends on it.

- **`ANALYSIS.md`** — the research note. Start here.
- **`ANALYSIS-charts-embedded.md`** — same note with the charts embedded in the file,
  for reading outside the repo.

| File | What it is |
|---|---|
| `issuance_model.py` | Issuance / burn-fraction / yield / staking-equilibrium model |
| `staking_history.py` | Reconstructs staked ETH month by month from on-chain flows |
| `yield_price_analysis.py` | Tests whether staking yield explains ETH's price |
| `yield_price_regression.py` | OLS diagnostics (t, p, R², Durbin–Watson) + the regression charts |
| `btc_monthly.csv` | Month-end BTC/USD (CoinGecko), for the ETH/BTC ratio |
| `regression_output.txt` | Output of `yield_price_regression.py` |
| `make_charts.py` | Renders the three charts embedded in ANALYSIS.md |
| `charts/*.svg` | Burn collapse, issuance curves, staking equilibrium (light/dark aware) |
| `model_output.txt` | Output of `issuance_model.py` |
| `staking_history_output.txt` | Output of `staking_history.py` |
| `correlation_output.txt` | Output of `yield_price_analysis.py` |
| `staked_eth_reconstructed.csv` | Monthly staked ETH, consensus APR, annualised issuance |
| `eth_supply_monthly.csv` | Monthly EIP-1559 burn and priority fees (Dune) |
| `burn_history.csv` | Annual ETH burned, 2021–2026 |
| `eth_monthly.csv` | Month-end ETH/USD (CoinGecko) |

`yield_price_analysis.py` reads the raw CoinGecko price dumps from the session's tool-
results cache; the derived series are checked in as CSV so the conclusions stay
reproducible without it. Data as of 13 Aug 2026.
