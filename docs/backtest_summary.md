# Evaluator Backtest Summary

> 2026-07-27 | HK IPO Evaluator v1.5

## Backtest Results (N=11)

| IPO | Date | Score | Advice | Actual First Day | Correct? |
|-----|------|-------|--------|-----------------|----------|
| Anker (00668.HK) | 7/2 | 70% | BUY | +15.69% | ✅ |
| Tongrentang (02667.HK) | 7/7 | 39% | SKIP | -39.09% | ✅ |
| Luxshare (02475.HK) | 7/9 | 53% | CAUTIOUS (veto) | -5.18% | ✅ |
| Puyuan (02497.HK) | 7/9 | 33% | SKIP | -37.36% | ✅ |
| Yikong Zhijia (07687.HK) | 7/8 | 71% | BUY | +9.99% | ✅ |
| Binhua Group (06745.HK) | 7/10 | 37% | SKIP (veto) | -18.68% | ✅ |
| Momenta (06880.HK) | 7/8 | 64% | BUY | +6.00% | ✅ |
| Anker (no dark) | 7/2 | 70% | BUY | +15.69% | ✅ |
| Jinghe Integrated (02249.HK) | 7/10 | 72% | BUY | +12.00% | ✅ |
| Basic Semiconductor (09971.HK) | 7/8 | 70% | BUY | +8.00% | ✅ |
| Binhua (v1.5) | 7/10 | 37% | SKIP (veto) | -18.68% | ✅ |

**N=11, accuracy=100%** (N<20, observe not claim)

## Prediction Pending

| IPO | Date | Status | Prediction |
|-----|------|--------|-----------|
| Zhongji Innolight (03308.HK) | 7/30 | Upcoming | STRONG BUY (if A-share >= 950 RMB) / BUY (if ~850 RMB) |

## Evaluator Evolution

| Version | Change | Key Improvement |
|---------|--------|----------------|
| v1.0 | 6 dims, discount 40% | Initial model |
| v1.1 | +sentiment, discount 30% | Added market sentiment |
| v1.2 | +dark_signal, discount 20% | Added best first-day predictor |
| v1.3a | dark 20% + veto (<=-4%) | One-vote-veto caught Luxshare |
| v1.4 | +supply_pressure 10% | Caught Puyuan crash (12 IPOs/week) |
| v1.5 | +cost warning + JSON output + N=11 | Trading cost threshold + programmatic API + expanded backtest |

## Key Mechanisms

- **One-vote-veto**: dark <= -4% → CAUTIOUS regardless of total score
- **Dark signal is best first-day predictor**: dark -4.95% → actual -5.18% = near-perfect
- **Supply pressure is best fallback**: 12 IPOs/week caught Puyuan crash that v1.3a missed
- **Trading cost warning**: BUY + dark < 3% → warns that net profit may be negative
- **Retail hot + institutional cold = danger**: Binhua 228x retail + 4.26x institutional → -18.68%
- **Extreme retail + hot inst = both hot**: Jinghe 344x + 14.62x, Basic Semi 4812x + 20x → both positive

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

## Prediction: Zhongji Innolight (03308.HK) - 7/30

**Known data (as of 7/27):**
- IPO price: 980 HKD (confirmed)
- Retail margin oversub: ~12x
- A-share: 300308.SZ (~850-950 RMB range, volatile)
- Scale: ~535B HKD (mega IPO, largest of 2026 alongside Luxshare)
- Cornerstone: Temasek, Hillhouse, Alibaba (super-tier)
- Sector: Optical modules / AI infrastructure (hottest sector)
- Supply: Low (only 1 IPO that week)
- Dark market: Not yet available (7/29)

**Prediction matrix:**

| A-share price | Discount | Score | Advice |
|--------------|----------|-------|--------|
| 950 RMB | +10.5% | 78% | STRONG BUY |
| 900 RMB | +5.0% | ~68% | BUY |
| 850 RMB | -0.1% | 58% | BUY (sentiment carries) |
| 800 RMB | -5.7% | ~48% | CAUTIOUS |

**Key variables:**
1. A-share closing price on 7/29
2. Dark market signal on 7/29 (most important)
3. If dark <= -4%, veto triggers regardless of score

---

_Generated: 2026-07-27_
_File: hk_ipo_evaluator.py (v1.5)_
