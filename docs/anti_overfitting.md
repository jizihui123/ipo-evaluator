# Overfitting Analysis & Anti-Overfitting Mechanisms

> 2026-08-19 | Honest self-assessment of model reliability

## Overview

This document provides a transparent analysis of overfitting risk in the IPO Evaluator, and describes the mechanisms designed to mitigate it. **This project takes overfitting seriously** — the goal is not to achieve 100% backtest accuracy, but to build a model that generalizes to unseen IPOs.

## Overfitting Risk Assessment

### What is Overfitting?

Overfitting occurs when a model fits training data noise rather than underlying patterns. Signs include: perfect backtest accuracy that fails on new data, case-specific parameters, and no holdout validation set.

### This Project's Risk Level: ⚠️ Moderate-High (Acknowledged)

| Risk Factor | This Project | Benchmark | Status |
|-------------|-------------|-----------|--------|
| Parameters / samples ratio | 71 params / 16 cases = 4.4x | <0.1x ideal | ⚠️ High |
| Train/test split | No holdout set | 80/20 split | ⚠️ Critical |
| Case-specific tuning | 8/16 cases have fitted params | 0 | ⚠️ High |
| Sample diversity | All July 2026 | Multiple periods | ⚠️ High |
| Model not perfectly fit | 94% (1 false negative) | <100% | ✅ Good |
| Economic logic behind params | Yes, all params have reasoning | — | ✅ Good |
| Simple core mechanism | Dark signal veto (binary) | — | ✅ Good |

### Honest Accuracy Assessment

- **Backtest accuracy (in-sample): 94%** — likely inflated by parameter fitting
- **Estimated true out-of-sample accuracy: 70-85%** — based on overfitting analysis
- **The model will perform differently on new IPOs** — this is expected and normal

## Anti-Overfitting Mechanisms

### 1. Structural Constraints Over Parameter Tuning

The model prioritizes **structural constraints** (hard rules) over continuous parameter optimization:

| Mechanism | Type | Description |
|-----------|------|-------------|
| Bear veto | Binary rule | dark ≤ -8% → SKIP, regardless of score |
| Soft veto | Binary rule | dark ≤ -4% → CAUTIOUS, regardless of score |
| Range veto | Binary rule | dark < 0% + BUY → CAUTIOUS |
| Bull veto | Binary rule | dark ≥ +20% → BUY |
| Cost warning | Threshold | dark < 3% + BUY → cost warning |

**Why this helps:** Binary rules have fewer degrees of freedom than continuous parameters. The dark signal veto is either triggered or not — no fine-tuning possible. This is the project's strongest anti-overfitting feature.

### 2. Economic Logic Requirement

Every parameter change must have an **economic explanation**, not just a data-fitting justification:

| Parameter | Economic Logic | Accepted? |
|-----------|---------------|-----------|
| Dark signal veto | Dark market = real money trading, directly predicts listing day | ✅ Yes |
| Supply pressure | More IPOs = more capital competition = lower prices | ✅ Yes |
| A-share amplification | A+H linked, A-share moves affect HK sentiment | ✅ Yes |
| Danger zone (dark -10 to -15 + same-day) | Moderate dark hasn't priced in supply yet | ✅ Yes |
| Mean reversion for extreme dark | Extreme signals overreact, market corrects | ✅ Yes |
| Market temperature | Recent break rate = market risk appetite | ✅ Yes |

**Parameters rejected** (would have improved backtest but lacked logic):
- ❌ Case-specific multipliers (e.g., "if name==X then *1.5")
- ❌ Date-specific adjustments
- ❌ Sector-specific weights (too few cases per sector)

### 3. Direction Over Magnitude

The model prioritizes **direction accuracy** (BUY/CAUTIOUS/SKIP) over **magnitude accuracy** (predicted range). Direction is more robust to overfitting because:

- Direction is binary (up/down/flat) — harder to overfit
- Magnitude requires precise parameter calibration — easier to overfit
- For trading decisions, direction matters more than exact percentage

### 4. Failed Cases Are Kept (Not Hidden)

The model does not hide failures:

| Case | Advice | Actual | Result |
|------|--------|--------|--------|
| Dongfang (01770) | SKIP | +1.73% | ❌ False negative |
| Dingtai (01377) | CAUTIOUS | -1.79% | ✅ (but range miss) |
| Puyuan Prec (00537) | CAUTIOUS | -37.36% | ✅ (but should be SKIP) |

**Why this helps:** Hiding failures would make the model look better but hide overfitting. Keeping them visible allows honest assessment.

### 5. Version Freeze Protocol (New)

Starting from v1.8, the following protocol is enforced:

```
EXISTING CASES (N=17): No parameter changes allowed
NEW CASES: Evaluate only, no tuning
TARGET: N=20+ with zero parameter changes
```

**Rules:**
1. The 17 existing backtest cases are **frozen** — no parameter changes to improve their accuracy
2. New IPOs (Junzheng 8/25, SHEIN 8/28, etc.) serve as **true holdout set**
3. If new cases show accuracy < 70%, the model is confirmed overfit → simplify
4. If new cases show accuracy > 80%, the model has genuine predictive power
5. Parameter changes only allowed if economic logic is independently validated

### 6. Simplicity Bias

The model uses **integer scores (0-5)** and **fixed thresholds** rather than continuous optimization:

- Scores: 0, 1, 2, 3, 4, 5 (6 levels per dimension)
- Thresholds: fixed cutpoints with economic meaning (e.g., -4%, -8%, +20%)
- Weights: fixed percentages, not learned

**Why this helps:** Discrete scoring has far fewer possible states than continuous parameters, reducing the parameter space from ~71 effective to ~20 meaningful configurations.

## Parameter Audit

### Case-Specific Parameters (Acknowledged Risk)

These parameters were added to fit specific cases but have general economic logic:

| Parameter | Triggered By | General Pattern | Risk Level |
|-----------|-------------|-----------------|------------|
| Danger zone 2.5x | Puyuan Prec | Moderate dark + supply = underpriced risk | Medium |
| Bull-veto skip dampening | Qiyunshan | Extreme positive dark = supply irrelevant | Low |
| A-share positive shrink | Dingtai | A-share rise supports HK price | Low |
| Structural amplification 3.7x | Tongrentang | Multiple weaknesses = nonlinear crash | Medium |
| No-dark upper bound +2% | Dongfang | Small cap + extreme retail = surprise potential | Medium |

### Parameters NOT Added (Rejected)

| Rejected Parameter | Why Rejected |
|-------------------|-------------|
| Per-case multipliers | No generalization possible |
| Sector-specific weights | <3 cases per sector, unreliable |
| Date-specific adjustments | No economic logic |
| Continuous weight optimization | Would perfectly fit training data |
| Rating-specific veto thresholds | Too few cases per rating level |

## Validation Plan

### Phase 1: Holdout Validation (In Progress)

| IPO | Date | Status | Rule |
|-----|------|--------|------|
| Junzheng (03223) | 8/25 | Pending | No param changes |
| SHEIN | 8/28 | Pending | No param changes |
| Future IPOs | TBD | TBD | No param changes |

**Success criteria:** ≥80% direction accuracy on 5+ new cases without parameter changes.

**Failure criteria:** <70% direction accuracy → model overfit → simplify by removing case-specific params.

### Phase 2: Cross-Period Validation (Future)

Collect IPOs from different market conditions:
- Normal market (break rate <25%)
- Bull market (break rate <15%)
- Different sectors

**Success criteria:** Model works across market regimes without regime-specific parameters.

## Summary

This project acknowledges that:

1. **The 94% backtest accuracy is likely inflated** by parameter fitting on 17 cases
2. **The true out-of-sample accuracy is probably 70-85%**
3. **The dark signal veto mechanism is the most robust feature** (simple, binary, 100% direction)
4. **The model will fail on some new IPOs** — this is expected and honest
5. **Parameter changes on existing cases are now frozen** to enable honest holdout validation

The goal is not a perfect model, but a **transparent and honest** one. Users should treat the evaluator as a decision-support tool, not an oracle.

---

_Last updated: 2026-08-19_
_Validation status: Phase 1 holdout in progress (2 cases pending)_
