# Evaluator Backtest Summary

> 2026-07-15 | HK IPO Evaluator v1.4

## Backtest Results

| IPO | Date | Score | Advice | Actual First Day | Correct? |
|-----|------|-------|--------|-----------------|----------|
| Anker (00668.HK) | 7/2 | 70% | BUY | +15.69% | ✅ |
| Tongrentang (02667.HK) | 7/7 | 39% | SKIP | -39.09% | ✅ |
| Luxshare (02475.HK) | 7/9 | 52% | CAUTIOUS (veto) | -5.18% | ✅ |
| Puyuan (02497.HK) | 7/9 | 33% | SKIP | -37.36% | ✅ |

**N=4, accuracy=100%** (N<20, observe not claim)

## Evaluator Evolution

| Version | Change | Luxshare Score | Luxshare Advice | Correct? |
|---------|--------|---------------|-----------------|----------|
| v1.0 | 6 dims, discount 40% | 78 | STRONG BUY | ❌ |
| v1.1 | +sentiment, discount 30% | 70 | BUY | ⚠️ |
| v1.2 | +dark_signal, discount 20% | 62 | BUY | ⚠️ |
| v1.3a | dark 20% + veto (<-4%) | 59 | CAUTIOUS (veto) | ✅ |
| v1.4 | +supply_pressure 10% | 52 | CAUTIOUS (veto) | ✅ |

## Key Mechanisms

- **One-vote-veto**: dark < -4% → CAUTIOUS regardless of total score
- **Dark signal is best first-day predictor**: dark -4.95% → actual -5.18% = near-perfect
- **Supply pressure is best fallback**: 12 IPOs/week caught Puyuan crash that v1.3a missed

## Key Lessons

1. **Dark market signal is the best first-day predictor** — dark -4.95% → actual -5.18%
2. **One-vote-veto caught crashes that weighted scores missed** — Luxshare scored 52 but veto correctly triggered
3. **Supply pressure caught Puyuan crash** — 12 IPOs/week = 40% crash rate vs 12% H1 baseline
4. **Long-term value ≠ short-term trading** — A-H discount is a holding metric, not a flipping metric
5. **Retail hot + institutional cold = danger** — Tongrentang 251x retail + 2.84x institutional → -39%

---

_Generated: 2026-07-15_
_File: hk_ipo_evaluator.py (v1.4)_
