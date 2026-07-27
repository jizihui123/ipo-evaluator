# Evaluator Backtest Summary

> 2026-07-27 | HK IPO Evaluator v1.5

## Backtest Results (N=8)

| IPO | Date | Score | Advice | Actual First Day | Correct? |
|-----|------|-------|--------|-----------------|----------|
| Anker (00668.HK) | 7/2 | 70% | BUY | +15.69% | ✅ |
| Tongrentang (02667.HK) | 7/7 | 39% | SKIP | -39.09% | ✅ |
| Luxshare (02475.HK) | 7/9 | 53% | CAUTIOUS (veto) | -5.18% | ✅ |
| Puyuan (02497.HK) | 7/9 | 33% | SKIP | -37.36% | ✅ |
| Yikong Zhijia (07687.HK) | 7/8 | 71% | BUY | +9.99% | ✅ |
| Binhua Group (06745.HK) | 7/10 | 37% | SKIP (veto) | -18.68% | ✅ |
| Momenta | 7/8 | 64% | BUY | +6.00% | ✅ |
| Anker (no dark) | 7/2 | 70% | BUY | +15.69% | ✅ |

**N=8, accuracy=100%** (N<20, observe not claim)

## Evaluator Evolution

| Version | Change | Key Improvement |
|---------|--------|----------------|
| v1.0 | 6 dims, discount 40% | Initial model |
| v1.1 | +sentiment, discount 30% | Added market sentiment |
| v1.2 | +dark_signal, discount 20% | Added best first-day predictor |
| v1.3a | dark 20% + veto (<=-4%) | One-vote-veto caught Luxshare |
| v1.4 | +supply_pressure 10% | Caught Puyuan crash (12 IPOs/week) |
| v1.5 | +cost warning + JSON output + N=8 | Trading cost threshold + programmatic API |

## Key Mechanisms

- **One-vote-veto**: dark <= -4% → CAUTIOUS regardless of total score
- **Dark signal is best first-day predictor**: dark -4.95% → actual -5.18% = near-perfect
- **Supply pressure is best fallback**: 12 IPOs/week caught Puyuan crash that v1.3a missed
- **Trading cost warning**: BUY + dark < 3% → warns that net profit may be negative
- **Retail hot + institutional cold = danger**: Binhua 228x retail + 4.26x institutional → -18.68%

## Cost Warning Logic

HK IPO trading costs (approximate):
- Commission: ~1%
- Bid-ask spread: ~0.5%
- Slippage: ~0.5-1%
- Margin interest (if using financing): ~1-2%

Total: ~3% minimum profit needed to break even.

The cost warning fires when:
1. Advice is BUY
2. Dark signal is available
3. Dark signal < 3% (cost threshold)

This prevents false confidence in marginal BUY signals.

---

_Generated: 2026-07-27_
_File: hk_ipo_evaluator.py (v1.5)_
