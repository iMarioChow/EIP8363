# EIP-8363 research pack

Supporting data and analysis for the article *"EIP-8363: Ethereum's Most Courageous
Monetary Experiment."*

- **`ANALYSIS.md`** — start here. Data pack, model results, correlation tests, and an
  editorial review of the draft.

| File | What it is |
|---|---|
| `issuance_model.py` | Issuance / burn-fraction / yield / staking-equilibrium model |
| `staking_history.py` | Reconstructs staked ETH month by month from on-chain flows |
| `yield_price_analysis.py` | Tests whether staking yield explains ETH's price |
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
