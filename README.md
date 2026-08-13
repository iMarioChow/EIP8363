# EIP-8363 research pack

Supporting data and analysis for the article *"EIP-8363: Ethereum's Most Courageous
Monetary Experiment."*

- **`ANALYSIS.md`** — start here. Data pack, model results, regressions, twelve charts,
  and an editorial review of the draft.
- **`ANALYSIS-charts-embedded.md`** — the same document with every chart inlined, for
  sending to someone outside the repo.

| File | What it is |
|---|---|
| `issuance_model.py` | Issuance / burn-fraction / yield / staking-equilibrium model |
| `staking_history.py` | Reconstructs staked ETH month by month from on-chain flows |
| `yield_price_analysis.py` | Correlation tests: does staking yield explain ETH's price? |
| `regression_analysis.py` | The same question as regressions — slopes, HAC errors, Durbin-Watson, power |
| `make_charts.py` | Renders all twelve charts |
| `embed_charts.py` | Builds the self-contained `ANALYSIS-charts-embedded.md` |
| `charts/*.svg` | Twelve charts, light/dark aware, both axes named |
| `model_output.txt` | Output of `issuance_model.py` |
| `staking_history_output.txt` | Output of `staking_history.py` |
| `correlation_output.txt` | Output of `yield_price_analysis.py` |
| `regression_output.txt` | Output of `regression_analysis.py` |
| `staked_eth_reconstructed.csv` | Monthly staked ETH, consensus APR, annualised issuance |
| `eth_supply_monthly.csv` | Monthly EIP-1559 burn and priority fees (Dune) |
| `burn_history.csv` | Annual ETH burned, 2021–2026 |
| `eth_monthly.csv` | Month-end ETH/USD (CoinGecko) |
| `btc_monthly.csv` | Month-end BTC/USD (CoinGecko), for the ETH/BTC tests |

Everything runs on a bare Python 3 install — no numpy, no scipy, no matplotlib. OLS, the
Student-t tail, Newey-West standard errors and the SVG renderer are all in-tree.

```bash
python3 issuance_model.py     > model_output.txt
python3 staking_history.py    > staking_history_output.txt
python3 yield_price_analysis.py > correlation_output.txt
python3 regression_analysis.py  > regression_output.txt
python3 make_charts.py        # -> charts/*.svg
python3 embed_charts.py       # -> ANALYSIS-charts-embedded.md
```

Data as of 13 Aug 2026.
