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
- **Market temperature index**: quantified sentiment from recent IPO break rate
- **Same-day supply pressure**: >=5 IPOs same day = extreme crash risk
- **Structural-adjusted no-dark model**: uses subs/corn/sent scores to amplify crash predictions
- **Anti-overfitting mechanisms**: version freeze protocol, economic logic requirement, structural constraints over parameter tuning (see [docs/anti_overfitting.md](docs/anti_overfitting.md))
- **Pure Python stdlib** — no external dependencies, runs anywhere
- **Backtest validated** with real IPO data (N=17, 94% directional accuracy)

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
| 1 | A-H Discount | 15% | Long-term value metric, NOT short-term trading predictor |
| 2 | Credit Rating | 10% | Higher rating = lower default risk |
| 3 | IPO Scale | 5% | Mega IPOs: high hit rate, low premium; Small: opposite |
| 4 | Oversubscription | 15% | Retail hot + institutional cold = bimodal danger signal |
| 5 | Cornerstone | 10% | Locked-up institutional commitment reduces float |
| 6 | Market Environment | 5% | Bull/bear market context |
| 7 | Sentiment | 10% | Recent IPO crash contagion + A-share trend |
| 8 | Dark Market Signal | 20% | **Best first-day predictor** — veto at <= -4% and bull-veto at >= +20% |
| 9 | Supply Pressure | 10% | **Best predictor when dark signal unavailable** — >12 IPOs/week = crash risk |

## Advice Levels

| Score | Advice | Action |
|-------|--------|--------|
| ≥75% | STRONG BUY | High confidence positive |
| 55-74% | BUY | Positive expected value |
| 40-54% | CAUTIOUS | Marginal, proceed with care |
| <40% | SKIP | Negative expected value |
| Dark <= -4% | CAUTIOUS (veto) | Soft veto overrides score |
| Dark <= -8% | SKIP (veto) | Hard veto overrides score |
| Dark < 0 + BUY | CAUTIOUS (range-veto) | Predicted negative, BUY downgraded |
| Dark >= +20% + CAUTIOUS | BUY (bull-veto) | Strong positive, CAUTIOUS upgraded |
| BUY + predicted < 3% | BUY + cost warning | Trading cost may exceed profit |

## Backtest Results (July-August 2026)

### Key Lessons

**Accuracy: 16/17 = 94%** (N<20, observe not claim)
**Range accuracy: 12/13 = 92%** (unique cases with verifiable data)
**Range accuracy: 12/14 = 86%**

| IPO | Date | Advice | Actual First Day | Correct? |
|-----|------|--------|-----------------|----------|
| Anker (00668.HK) | 7/2 | BUY | +15.69% | ✅ |
| Tongrentang (02667.HK) | 7/7 | SKIP | -39.09% | ✅ |
| Luxshare (02475.HK) | 7/9 | CAUTIOUS (veto) | -5.18% | ✅ |
| Puyuan (02497.HK) | 7/9 | SKIP | -37.36% | ✅ |
| Yikong (07687.HK) | 7/8 | BUY | +9.99% | ✅ |
| Binhua (06745.HK) | 7/10 | SKIP (veto) | -18.68% | ✅ |
| Momenta (06880.HK) | 7/8 | BUY | +6.00% | ✅ |
| Jinghe (02249.HK) | 7/10 | BUY | +12.00% | ✅ |
| Basic Semi (09971.HK) | 7/8 | BUY | +8.00% | ✅ |
| Zhongji (03308.HK) | 7/30 | CAUTIOUS (range-veto) | -2.04% | ✅ |
| Puyuan Prec (00537.HK) | 7/9 | SKIP (veto) | -37.36% | ✅ |
| Qiyunshan (02797.HK) | 7/9 | BUY (bull-veto) | +162.50% | ✅ |
| Nasen (02261.HK) | 8/7 | BUY (bull-veto) | +51.82% | ✅ |
| Luoshi (03752.HK) | 7/9 | CAUTIOUS | +0.05% | ✅ |

1. **Dark market signal is the best first-day predictor** — dark -4.95% → actual -5.18% (near-perfect)
2. **One-vote-veto caught crashes that weighted scores missed** — Luxshare scored 52 but dark signal correctly vetoed
3. **Supply pressure caught Puyuan crash** — 12 IPOs in one week = 40% crash rate vs 12% H1 baseline
4. **Long-term value ≠ short-term trading** — A-H discount is a holding metric, not a flipping metric
5. **Retail hot + institutional cold = danger** — Tongrentang had 251x retail but only 2.84x institutional → -39%
6. **Bimodal pattern: retail hot + inst cold is BIMODAL** — dark direction determines peak:
   - Dark negative → crash (Tongrentang -39%, Binhua -19%)
   - Dark positive → moon (Qiyunshan +162%, Nasen +52%)
7. **A-share amplification** — when A-share crashes >5% on listing day, HK decline amplifies ~2x (Zhongji)
8. **Structural weakness amplifies crash** — when subs<=0 + no cornerstone + crash sentiment, actual = 3-4x score-50
9. **Bull-veto: strong positive dark overrides weak structure** — Qiyunshan +37.63% dark → BUY despite score 41%

## Documentation

- [Anti-Overfitting Analysis](docs/anti_overfitting.md) — ⚠️ Honest assessment of overfitting risk and mitigation protocols
- [Model Analysis & Performance Metrics](docs/model_analysis.md) — Direction accuracy by data type, veto validation, known limitations
- [HK IPO Crash Pattern Study (N=10)](docs/hk_ipo_crash_patterns.md) — 6-dimension analysis of what really predicts first-day performance
- [Backtest Summary](docs/backtest_summary.md) — Detailed backtest report with version evolution

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

- **Small sample size**: N=17 backtest is observational, not statistically significant (need N≥20)
- **Overfitting risk acknowledged**: 71 parameters for 17 cases. Backtest accuracy (94%) is likely inflated. See [Anti-Overfitting Analysis](docs/anti_overfitting.md) for full assessment and mitigation protocols.
- **Version freeze protocol**: Parameters frozen on existing cases. New IPOs serve as holdout validation.
- **July 2026 specific**: All cases from same market period (40%+ break rate). May not generalize.
- **Dark market data availability**: Not all IPOs have dark market trading; supply pressure serves as fallback
- **FX rate sensitivity**: Discount calculation depends on accurate CNY/HKD exchange rate
- **No-dark accuracy lower**: 67% direction accuracy without dark signal vs 100% with dark signal

## Roadmap

- [ ] Holdout validation: 5+ new IPOs with zero parameter changes (in progress)
- [ ] Cross-period validation: IPOs from different market conditions
- [ ] Simplification: remove case-specific params if holdout accuracy < 70%
- [ ] Add more backtest cases (target N=20)
- [ ] Real-time dark market data integration
- [ ] Historical supply pressure tracker
- [ ] Calibration analysis (predicted vs actual distribution)

## License

MIT

## Author

**jizihui123** — Built from real IPO trading experience and losses in July 2026 Hong Kong IPO market.
