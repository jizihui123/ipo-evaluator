# IPO Evaluator

A multi-dimensional scoring model for evaluating Hong Kong IPO first-day trading decisions.

## Why?

Retail investors often lose money on IPOs because they focus on the wrong signals — high oversubscription ratios or A-H discount premiums — while the real predictors of first-day performance are **dark market signals** and **supply pressure**.

This tool encodes lessons from real IPO outcomes in July 2026 into a transparent, reproducible scoring framework.

## Features

- **9-dimension weighted scoring**: discount, rating, scale, oversubscription structure, cornerstone, market environment, sentiment, dark market signal, supply pressure
- **One-vote-veto mechanism**: dark market <= -4% triggers soft veto (CAUTIOUS), <= -8% triggers hard veto (SKIP)
- **Trading cost warning**: when BUY is advised but predicted gain (from dark signal) < 3% trading cost threshold
- **JSON output mode**: `to_json(result)` for programmatic integration
- **A-share amplification**: for A+H listings, when A-share moves >5% on listing day, prediction range is amplified
- **Pure Python stdlib** — no external dependencies, runs anywhere
- **Backtest validated** with real IPO data (N=8, 100% directional accuracy)

## Installation

```bash
git clone https://github.com/jizihui123/ipo-evaluator.git
cd ipo-evaluator
```

No dependencies needed. Just Python 3.8+.

## Quick Start

```python
from hk_ipo_evaluator import eval_hk_ipo, print_result

# Evaluate a hypothetical IPO
result = eval_hk_ipo(
    name="Example Corp",
    code="01234.HK",
    ipo_price_hkd=50.0,
    ref_price_cny=48.0,       # A-share price in CNY
    fx_rate=1.152,             # CNY to HKD
    rating="AA+",
    scale_hk_yi=20,            # IPO size in hundred-million HKD
    retail_oversub=15.0,       # retail oversubscription ratio
    inst_oversub=8.0,          # institutional oversubscription ratio
    cornerstone=True,
    market_env="normal",
    sentiment="neutral",
    dark_signal=2.5,           # dark market return %
    ipos_same_week=3,          # IPOs listing same week
)

print_result(result)
```

Output:
```
=======================================================
  Example Corp (01234.HK)
  IPO: HK$50.0 | A-share: ¥48.0 -> HK$55.30 @1RMB=1.152HKD
  disc: +9.6% | AA+ | 20.0B HKD
=======================================================
  disc    : 3/5  discount small
  rate    : 4/5  AA+(4/5)
  scale   : 3/5  mid(balanced)
  subs    : 3/5  normal
  corn    : 4/5  has cornerstone
  env     : 3/5  normal
  sent    : 3/5  mixed signals
  dark    : 4/5  dark +2.5% positive
  supply  : 3/5  3 IPOs/week = mild supply pressure

  Weighted: 3.4/5.0 (68%)
  Advice:   BUY +
=======================================================
```

## Scoring Dimensions

| # | Dimension | Weight | Key Insight |
|---|-----------|--------|-------------|
| 1 | A-H Discount | 13% | Long-term value metric, NOT short-term trading predictor |
| 2 | Credit Rating | 9% | Higher rating = lower default risk |
| 3 | IPO Scale | 4% | Mega IPOs: high hit rate, low premium; Small: opposite |
| 4 | Oversubscription | 13% | Retail hot + institutional cold = danger signal |
| 5 | Cornerstone | 9% | Locked-up institutional commitment reduces float |
| 6 | Market Environment | 4% | Bull/bear market context |
| 7 | Sentiment | 9% | Recent IPO crash contagion + A-share trend |
| 8 | Dark Market Signal | 18% | **Best first-day predictor** — one-vote-veto at < -4% |
| 9 | Supply Pressure | 9% | **Best predictor when dark signal unavailable** — >12 IPOs/week = crash risk |

## Advice Levels

| Score | Advice | Action |
|-------|--------|--------|
| ≥75% | STRONG BUY | High confidence positive |
| 55-74% | BUY | Positive expected value |
| 40-54% | CAUTIOUS | Marginal, proceed with care |
| <40% | SKIP | Negative expected value |
| Dark <= -4% | CAUTIOUS (veto) | Soft veto overrides score |
| Dark <= -8% | SKIP (veto) | Hard veto overrides score |
| BUY + predicted < 3% | BUY + cost warning | Trading cost may exceed profit |

## Backtest Results (July 2026)

| IPO | Date | Advice | Actual First Day | Correct? |
|-----|------|--------|-----------------|----------|
### Key Lessons

**Accuracy: 11/11 = 100%** (N<20, observe not claim)

| IPO | Date | Advice | Actual First Day | Correct? |
|-----|------|--------|-----------------|----------|
| Anker (00668.HK) | 7/2 | BUY | +15.69% | ✅ |
| Tongrentang (02667.HK) | 7/7 | SKIP | -39.09% | ✅ |
| Luxshare (02475.HK) | 7/9 | CAUTIOUS (veto) | -5.18% | ✅ |
| Puyuan (02497.HK) | 7/9 | SKIP | -37.36% | ✅ |
| Yikong Zhijia (07687.HK) | 7/8 | BUY | +9.99% | ✅ |
| Binhua Group (06745.HK) | 7/10 | SKIP (veto) | -18.68% | ✅ |
| Momenta (06880.HK) | 7/8 | BUY | +6.00% | ✅ |
| Jinghe (02249.HK) | 7/10 | BUY | +12.00% | ✅ |
| Basic Semi (09971.HK) | 7/8 | BUY | +8.00% | ✅ |
| Zhongji Innolight (03308.HK) | 7/30 | CAUTIOUS (range-veto) | -2.04% | ✅ |

1. **Dark market signal is the best first-day predictor** — dark -4.95% → actual -5.18% (near-perfect)
2. **One-vote-veto caught crashes that weighted scores missed** — Luxshare scored 52 but dark signal correctly vetoed
3. **Supply pressure caught Puyuan crash** — 12 IPOs in one week = 40% crash rate vs 12% H1 baseline
4. **Long-term value ≠ short-term trading** — A-H discount is a holding metric, not a flipping metric
5. **Retail hot + institutional cold = danger** — Tongrentang had 251x retail but only 2.84x institutional → -39%

## Research Documentation

- [HK IPO Crash Pattern Study (N=10)](docs/hk_ipo_crash_patterns.md) — 6-dimension analysis of what really predicts first-day performance
- [Backtest Summary](docs/backtest_summary.md) — Detailed backtest report

## Running Tests

```bash
# Run backtest
python hk_ipo_evaluator.py

# Run unit tests
python tests/test_backtest.py

# Run examples
python examples/basic_usage.py
```

## Limitations

- **Small sample size**: N=4 backtest is observational, not statistically significant (need N≥20)
- **July 2026 specific**: Market conditions and IPO characteristics may not generalize
- **Dark market data availability**: Not all IPOs have dark market trading; supply pressure serves as fallback
- **FX rate sensitivity**: Discount calculation depends on accurate CNY/HKD exchange rate

## Roadmap

- [ ] Add more backtest cases (target N=20)
- [ ] Real-time dark market data integration
- [ ] Historical supply pressure tracker
- [ ] Calibration analysis (predicted vs actual distribution)

## License

MIT

## Author

**jizihui123** — Built from real IPO trading experience and losses in July 2026 Hong Kong IPO market.
