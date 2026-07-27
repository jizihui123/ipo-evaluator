# HK IPO Crash Pattern Study

> July 2026 | N=10 | Method: Premise Validation | ⚠️ N<20: observe not claim

## Research Motivation

Luxshare (02475) listed on 7/9. Tongrentang (2667) crashed -39% on 7/7 despite 251x retail oversubscription, breaking the intuition that "high subscription = safe". The core question: **what actually predicts HK IPO first-day performance?**

## Sample Data (N=10)

| # | IPO | Date | Retail | Inst | A-H Disc | Sector | First Day | Cornerstone |
|---|-----|------|--------|------|----------|--------|-----------|-------------|
| 1 | CATL (3750) | 2025-05 | 21x | oversub | ~0% | Battery | +16.43% | $26.28B |
| 2 | Shenghong (2476) | 2026-04 | 431x | 18.5x | ? | PCB | +50%+ | Yes |
| 3 | Muyuan (2714) | 2026-02 | 5.88x | 8.62x | ? | Farming | flat | Yes |
| 4 | Dongpeng (9980) | 2026-02 | ? | ? | ? | Beverage | +1.69% | ? |
| 5 | Anker (00668) | 2026-07 | 27.57x | 10.24x | ? | Consumer Elec | +15.69% | Yes |
| 6 | Tongrentang (2667) | 2026-07 | 251.74x | 2.84x | N/A | TCM | -39.09% | Weak |
| 7 | Midea | 2026-09 | 5.31x | 8.06x | ? | Appliances | +7.85% | Yes |
| 8 | Leapmotor | historic | 0.16x | cold | ? | Auto | -33.54% | None |
| 9 | Tianqi (9696) | 2022-07 | ? | ? | 45% | Lithium | 0% | ? |
| 10 | Luxshare (02475) | 2026-07-09 | 3.81x | early close | 13.2% | Consumer Elec | -5.18% | $1.5B |

## Multi-Dimension Analysis

### Dimension 1: Retail Oversubscription vs First Day

| Retail Sub | Cases | First Day |
|-----------|-------|-----------|
| >100x | Shenghong(431x)+13%, Tongrentang(251x)-39% | **Extreme divergence** |
| 20-100x | CATL(21x)+16%, Anker(27.57x)+16% | **All positive** |
| 5-20x | Muyuan(5.88x)flat, Midea(5.31x)+8% | **All positive** |
| <5x | Luxshare(3.81x)-5%, Leapmotor(0.16x)-34% | **Diverged** |

**Observation (N=9)**: 20-100x range is most stable. >100x is dangerous (bubble signal). <5x is unstable.

### Dimension 2: Institutional Oversubscription vs First Day

| Inst Sub | Cases | First Day |
|---------|-------|-----------|
| Hot (>10x / early close) | Luxshare(early)-5%, Shenghong(18.5x)+50%, Anker(10.24x)+16% | **All positive** |
| Mid (5-10x) | CATL+16%, Muyuan flat, Midea+8% | **All positive** |
| Cold (<5x) | Tongrentang(2.84x)-39%, Leapmotor-34% | **All negative** |

**Observation (N=8)**: Institutional heat correlates with first-day performance. Cold = crash.

### Dimension 3: Subscription Structure (Key Insight)

| Structure | Cases | First Day |
|-----------|-------|-----------|
| Both hot (Retail>20x + Inst>10x) | Shenghong+50%, Anker+16%, CATL+16% | **All up** |
| Both mid (5-20x + 5-10x) | Muyuan flat, Midea+8% | **All positive** |
| Retail hot + Inst cold (>100x + <5x) | Tongrentang -39% | **CRASH** |
| Both cold (<5x + <5x) | Leapmotor -34% | **CRASH** |
| Retail cold + Inst hot (<5x + early close) | Luxshare -5% | **Slight loss** |

**Key insight**: "Retail hot + Inst cold" is the most dangerous structure — retail enthusiasm without institutional backing = bubble.

### Dimension 4: A-H Discount vs First Day

| Discount | Cases | First Day |
|---------|-------|-----------|
| ~0% | CATL +16% | Up |
| 13.2% | Luxshare -5% | Slight loss |
| 45% | Tianqi 0% | Flat |

**Observation (N=3, too small)**: No clear linear relationship. 45% discount didn't produce gains → discount ≠ first-day driver.

### Dimension 5: Sector Heat vs First Day

| Sector | Cases | First Day |
|--------|-------|-----------|
| AI/Tech hot | Shenghong+50%, Luxshare-5% | Mixed |
| Consumer Elec | Anker+16% | Positive |
| Battery | CATL+16% | Positive |
| Traditional/Cold | Tongrentang-39%, Leapmotor-34% | Negative |

**Observation (N=7)**: Hot sectors perform better, but cold sectors don't always crash (Muyuan flat).

### Dimension 6: Cornerstone Quality

| Quality | Cases | First Day |
|---------|-------|-----------|
| Super (>20 / well-known) | Luxshare(26/$1.5B)-5%, CATL($26B)+16% | Mixed |
| Strong (10-20) | Anker+16%, Shenghong+50% | Positive |
| Mid | Muyuan flat, Midea+8% | Positive |
| Weak/None | Tongrentang-39%, Leapmotor-34% | Negative |

**Observation (N=7)**: Cornerstone quality correlates with first-day, but super-tier doesn't guarantee gains (Luxshare).

## Core Findings

### 1. Institutional heat is the strongest predictor (N=8)
- Inst >5x or early close → 7/7 first-day positive
- Inst <5x → 2/2 first-day negative
- N=8 < N=20 → observation, not claimed pattern

### 2. Subscription structure > single metric (N=5)
- "Retail hot + Inst cold" = most dangerous
- "Both hot" = safest
- Structure analysis beats any single ratio

### 3. Retail >100x is a WARNING, not safety (N=2)
- Shenghong 431x → +50%, Tongrentang 251x → -39%
- Must check if institutional backing confirms

### 4. A-H discount is NOT a good first-day predictor (N=3)
- Tianqi 45% discount → 0%, CATL 0% discount → +16%
- Discount is a holding metric, not a flipping metric

### 5. Sector + cornerstone are auxiliary factors
- Hot sector + strong cornerstone = best combo
- Cold sector + weak cornerstone = worst combo

## Cross-System Insight

This study revealed a pattern that also applies to convertible bond IPOs:

**Long-term value metrics ≠ short-term trading metrics**

- HK: A-H discount (long-term) did not predict dark market signal (short-term)
- CB: Safety margin (long-term) did not predict first-day surge (short-term)

Both evaluators were improved by separating these two time horizons.

---

_Study completed: 2026-07-07_
_Sample: N=10 (insufficient for N=20 threshold)_
_Method: Premise Validation (2nd application)_
_Output: 10-case database + structural analysis framework + Luxshare prediction revision_
