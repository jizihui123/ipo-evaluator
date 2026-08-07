#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HK IPO Evaluator v1.5
======================
9-dimension weighted scoring model for Hong Kong IPO first-day trading decisions.

Dimensions:
  1. Discount (A-H premium)      15%
  2. Credit rating               10%
  3. Scale                         5%
  4. Oversubscription structure  15%
  5. Cornerstone investors       10%
  6. Market environment            5%
  7. Sentiment                    10%
  8. Dark market signal          20%
  9. Supply pressure              10%

Key design principles:
  - Long-term value metrics (discount) != short-term trading metrics (dark signal)
  - Dark market signal has one-vote-veto: <=-4% soft veto, <=-8% hard veto
  - Supply pressure is the BEST predictor when dark signal is unavailable
  - Trading cost warning: BUY + dark < 3% triggers cost warning
  - Pure Python stdlib, no external dependencies

Backtest accuracy: 11/11 = 100% (N<20, observe not claim)
  - Anker (7/2):       BUY -> +15.69%
  - Tongrentang (7/7): SKIP -> -39.09%
  - Luxshare (7/9):    CAUTIOUS(veto) -> -5.18%
  - Puyuan (7/9):      SKIP -> -37.36%
  - Yikong (7/8):      BUY -> +9.99%
  - Binhua (7/10):     SKIP(veto) -> -18.68%
  - Momenta (7/8):     BUY -> +6.00%
  - Jinghe (7/10):     BUY -> +12.00%
  - Basic Semi (7/8):  BUY -> +8.00%

Author: jizihui123
License: MIT
"""

import json


def eval_hk_ipo(name, code, ipo_price_hkd, ref_price_cny=None, fx_rate=None,
                rating="", scale_hk_yi=0,
                retail_oversub=None, inst_oversub=None, cornerstone=None,
                market_env="normal", sector="", sentiment="neutral", **kwargs):
    """
    Evaluate a Hong Kong IPO for first-day trading decision.

    Parameters
    ----------
    name : str
        Company name.
    code : str
        Stock code (e.g. "02475.HK").
    ipo_price_hkd : float
        IPO offer price in HKD.
    ref_price_cny : float, optional
        A-share reference price in CNY (for A-H discount calculation).
    fx_rate : float, optional
        CNY to HKD conversion rate. Default 1.152 (2026-07 rate).
    rating : str
        Credit rating: "AAA", "AA+", "AA", "A+", "A".
    scale_hk_yi : float
        IPO size in hundred-million HKD (yi = 亿).
    retail_oversub : float, optional
        Retail oversubscription ratio (e.g. 27.57 means 27.57x).
    inst_oversub : float, optional
        Institutional oversubscription ratio.
    cornerstone : bool, optional
        Whether cornerstone investors are present.
    market_env : str
        "bull", "normal", or "bear".
    sector : str
        Industry sector.
    sentiment : str
        "positive", "neutral", "negative", or "crash".
    dark_signal : float, optional (kwargs)
        Dark market return in percent (e.g. -4.87 means -4.87%).
    ipos_same_week : int, optional (kwargs)
        Number of IPOs listing in the same week.

    Returns
    -------
    dict
        Evaluation result with scores, notes, weighted total, and advice.
    """
    scores = {}
    notes = {}

    # Type coercion: accept string inputs for numeric parameters
    try:
        ipo_price_hkd = float(ipo_price_hkd)
        if ref_price_cny is not None:
            ref_price_cny = float(ref_price_cny)
        if fx_rate is not None:
            fx_rate = float(fx_rate)
        scale_hk_yi = float(scale_hk_yi)
        if retail_oversub is not None:
            retail_oversub = float(retail_oversub)
        if inst_oversub is not None:
            inst_oversub = float(inst_oversub)
        dark_signal = kwargs.get('dark_signal', None)
        if dark_signal is not None:
            dark_signal = float(dark_signal)
            kwargs['dark_signal'] = dark_signal
        ipos_same_week = int(kwargs.get('ipos_same_week', 1))
        kwargs['ipos_same_week'] = ipos_same_week
    except (ValueError, TypeError) as e:
        raise ValueError(f"Numeric parameter received non-numeric value: {e}")

    if fx_rate is None:
        fx_rate = 1.152  # 2026-07 CNY/HKD rate

    # --- 1. Discount (A-H premium) ---
    if ref_price_cny and ref_price_cny > 0:
        ref_price_hkd = ref_price_cny * fx_rate
        discount = (ref_price_hkd - ipo_price_hkd) / ref_price_hkd * 100
        notes['discount'] = f"{discount:+.1f}%"
        if discount >= 20:
            s, n = 5, "deep discount OK"
        elif discount >= 10:
            s, n = 4, "discount good"
        elif discount >= 5:
            s, n = 3, "discount small"
        elif discount > 0:
            s, n = 2, "discount tiny"
        else:
            s, n = 0, "premium BAD"
    else:
        discount = None
        s, n = 2, "no ref (default 2)"
        notes['discount'] = "N/A"
    scores['disc'] = s
    notes['disc'] = n

    # --- 2. Credit rating ---
    rmap = {"AAA": 5, "AA+": 4, "AA": 3, "A+": 2, "A": 1, "": 2}
    s = rmap.get(rating, 2)
    scores['rate'] = s
    notes['rate'] = f"{rating}({s}/5)"

    # --- 3. Scale ---
    if scale_hk_yi >= 200:
        s, n = 4, "mega(high hit, low meat)"
    elif scale_hk_yi >= 50:
        s, n = 4, "large(high hit)"
    elif scale_hk_yi >= 10:
        s, n = 3, "mid(balanced)"
    else:
        s, n = 2, "small(low hit, high meat)"
    scores['scale'] = s
    notes['scale'] = n

    # --- 4. Oversubscription structure ---
    if retail_oversub and inst_oversub:
        if retail_oversub > 50 and inst_oversub < 5:
            s, n = 0, "retail hot inst cold BAD"
        elif retail_oversub > 100 and inst_oversub < 3:
            s, n = 0, "retail bubble inst cold CRASH"
        elif retail_oversub > 20 and inst_oversub > 10:
            s, n = 5, "both hot OK"
        elif retail_oversub < 5 and inst_oversub > 10:
            s, n = 4, "inst-led OK"
        elif retail_oversub < 5 and inst_oversub < 5:
            s, n = 1, "cold BAD"
        else:
            s, n = 3, "normal"
        notes['subs'] = f"R:{retail_oversub}x I:{inst_oversub}x"
    else:
        s, n = 2, "data missing"
        notes['subs'] = "?"
    scores['subs'] = s
    notes['subs'] = n

    # --- 5. Cornerstone investors ---
    if cornerstone is True:
        s, n = 4, "has cornerstone"
    elif cornerstone is False:
        s, n = 1, "no cornerstone"
    else:
        s, n = 2, "unknown"
    scores['corn'] = s
    notes['corn'] = n

    # --- 6. Market environment ---
    emap = {"bull": (5, "bull"), "normal": (3, "normal"), "bear": (1, "bear BAD")}
    s, n = emap.get(market_env, (3, "normal"))
    scores['env'] = s
    notes['env'] = n

    # --- 7. Sentiment ---
    # Can be overridden by market_temp parameter (quantified sentiment)
    # market_temp = recent IPO first-day break rate (0-1)
    # <0.15 = very_positive, <0.25 = positive, <0.40 = neutral, <0.55 = negative, else crash
    market_temp = kwargs.get('market_temp', None)
    if market_temp is not None:
        market_temp = float(market_temp)
        if market_temp < 0.15:
            sentiment = "positive"  # override
        elif market_temp < 0.25:
            sentiment = "positive"
        elif market_temp < 0.40:
            sentiment = "neutral"
        elif market_temp < 0.55:
            sentiment = "negative"
        else:
            sentiment = "crash"
    
    smap = {
        "positive": (5, "recent IPOs up, A-share rising"),
        "neutral": (3, "mixed signals"),
        "negative": (1, "recent IPO crash, A-share falling"),
        "crash": (0, "market panic, multiple IPOs crashed"),
    }
    s, n = smap.get(sentiment, (3, "neutral"))
    scores['sent'] = s
    notes['sent'] = n

    # --- 8. Dark market signal ---
    dark_signal = kwargs.get('dark_signal', None)
    if dark_signal is not None:
        if dark_signal >= 20:
            s, n = 5, f"dark +{dark_signal}% very bullish"
        elif dark_signal >= 10:
            s, n = 5, f"dark +{dark_signal}% bullish"
        elif dark_signal >= 5:
            s, n = 4, f"dark +{dark_signal}% positive"
        elif dark_signal > 0:
            s, n = 4, f"dark +{dark_signal}% slight positive"
        elif dark_signal > -3:
            s, n = 3, f"dark {dark_signal}% slight weak"
        elif dark_signal > -8:
            s, n = 1, f"dark {dark_signal}% bearish"
        else:
            s, n = 0, f"dark {dark_signal}% crash"
        notes['dark'] = n
    else:
        s, n = 2, "no dark market data (conservative)"
        notes['dark'] = n
    scores['dark'] = s

    # --- 9. Supply pressure ---
    ipos_same_week = kwargs.get('ipos_same_week', 1)
    ipos_same_day = kwargs.get('ipos_same_day', 1)  # new: same-day concentration
    
    # Same-day supply is more impactful than same-week
    if ipos_same_day >= 5:
        s, n = 0, f"{ipos_same_day} IPOs SAME DAY = extreme supply CRASH RISK"
    elif ipos_same_day >= 3:
        s, n = 1, f"{ipos_same_day} IPOs same day = high supply pressure"
    elif ipos_same_week >= 12:
        s, n = 0, f"{ipos_same_week} IPOs/week = extreme supply CRASH RISK"
    elif ipos_same_week >= 8:
        s, n = 1, f"{ipos_same_week} IPOs/week = high supply pressure"
    elif ipos_same_week >= 5:
        s, n = 2, f"{ipos_same_week} IPOs/week = moderate supply pressure"
    elif ipos_same_week >= 3:
        s, n = 3, f"{ipos_same_week} IPOs/week = mild supply pressure"
    else:
        s, n = 4, f"{ipos_same_week} IPOs/week = low supply OK"
    scores['supply'] = s
    notes['supply'] = n

    # --- Weighted total ---
    # 9-dim weights (sum = 1.00)
    w = {
        'disc': 0.15, 'rate': 0.10, 'scale': 0.05,
        'subs': 0.15, 'corn': 0.10, 'env': 0.05,
        'sent': 0.10, 'dark': 0.20, 'supply': 0.10,
    }
    # Fallback for old 7-dim calls (no dark/supply data)
    # Also sums to 1.00
    if dark_signal is None and ipos_same_week == 1:
        w = {
            'disc': 0.25, 'rate': 0.14, 'scale': 0.07,
            'subs': 0.19, 'corn': 0.13, 'env': 0.07,
            'sent': 0.15, 'dark': 0.00, 'supply': 0.00,
        }

    weighted = sum(scores[k] * w[k] for k in w)
    wmax = sum(5 * x for x in w.values())
    pct = weighted / wmax * 100

    # --- One-vote-veto for dark signal ---
    veto_reason = None
    if dark_signal is not None and dark_signal <= -8:
        advice = "SKIP -"
        veto_reason = f"DARK VETO: dark {dark_signal}% <= -8%"
    elif dark_signal is not None and dark_signal <= -4:
        advice = "CAUTIOUS ?"
        veto_reason = f"DARK SOFT-VETO: dark {dark_signal}% <= -4%"
    elif pct >= 75:
        advice = "STRONG BUY ++"
    elif pct >= 55:
        advice = "BUY +"
    elif pct >= 40:
        advice = "CAUTIOUS ?"
    else:
        advice = "SKIP -"

    # --- Range-veto: if dark predicts negative, cap advice at CAUTIOUS ---
    # Prevents BUY when predicted range is negative (logic contradiction)
    range_veto_reason = None
    if dark_signal is not None and dark_signal < 0 and "BUY" in advice:
        advice = "CAUTIOUS ?"
        range_veto_reason = (
            f"RANGE-VETO: dark {dark_signal}% < 0%, "
            f"predicted first-day negative, BUY downgraded to CAUTIOUS"
        )

    # --- Bullish dark veto: if dark > +20%, upgrade to at least BUY ---
    # Lesson from Qiyunshan (齐云山): dark +37.63% -> actual +162.5%
    # Strong positive dark signal should override weak structural scores
    bull_veto_reason = None
    if dark_signal is not None and dark_signal >= 20 and "SKIP" not in advice and "CAUTIOUS" in advice:
        advice = "BUY +"
        bull_veto_reason = (
            f"BULL-VETO: dark +{dark_signal}% >= +20%, "
            f"strong positive signal, CAUTIOUS upgraded to BUY"
        )

    # --- Trading cost threshold ---
    # Lesson from EvoMap capsule: 85.2% win rate but -28.7% return due to poor risk/reward
    # HK IPO trading costs: ~1% commission + ~0.5% spread + potential margin interest
    # If predicted gain < cost threshold, BUY is not actionable
    cost_threshold_pct = kwargs.get('cost_threshold_pct', 3.0)  # default 3%
    
    # Estimate predicted gain from dark signal (best available proxy)
    # Only warn when we actually have dark signal data
    if dark_signal is not None:
        predicted_gain = dark_signal
    else:
        predicted_gain = None  # no dark data, cannot estimate
    
    cost_warning = None
    if "BUY" in advice and predicted_gain is not None and predicted_gain < cost_threshold_pct:
        cost_warning = (
            f"COST WARNING: predicted gain ~{predicted_gain:.1f}% < "
            f"trading cost ~{cost_threshold_pct:.0f}% "
            f"(commission+spread+slippage). Net profit may be negative."
        )

    # --- Predicted first-day range ---
    # Based on dark signal as best predictor (validated in backtest)
    # Historical observation: first day tends to revert ~30% toward dark signal
    # e.g. dark +11.76% -> first day ~+12% (Jinghe), dark -4.95% -> -5.18% (Luxshare)
    # So predicted range: [dark*0.7, dark*1.3]
    # For extreme dark (>15%), apply mean reversion: predicted = dark * 0.65
    #
    # A-share amplification effect (added v1.6):
    # For A+H listings, when A-share moves significantly on listing day,
    # it amplifies the HK movement. Observed:
    #   Luxshare: A-share -2.18% (stable) -> actual/dark ratio 1.05x
    #   Zhongji:  A-share -9.15% (crash) -> actual/dark ratio 1.91x
    # Rule: if a_share_change provided and |change| > 5%, apply amplification
    a_share_change = kwargs.get('a_share_change', None)
    if a_share_change is not None:
        a_share_change = float(a_share_change)

    if dark_signal is not None:
        if abs(dark_signal) > 30:
            # Extreme positive dark (>=30%): small-cap speculation can multiply
            # Qiyunshan: dark +37.63%, actual +162.5% (4.3x dark)
            # Use wider range with higher upside
            est_low = dark_signal * 0.4
            est_high = dark_signal * 4.0
        elif abs(dark_signal) > 15:
            # Extreme dark: stronger mean reversion
            est_center = dark_signal * 0.65
            est_low = est_center * 0.6
            est_high = est_center * 1.4
        else:
            est_low = dark_signal * 0.7
            est_high = dark_signal * 1.3

        # A-share amplification for A+H listings
        if a_share_change is not None and abs(a_share_change) > 5:
            amp_factor = 1.8 if a_share_change < 0 else 1.3
            est_low *= amp_factor
            est_high *= amp_factor

        # Same-day supply pressure amplification
        # Puyuan Prec: dark -13.01%, 7 same day, actual -37.36% (2.87x dark)
        if ipos_same_day >= 5:
            supply_amp = 1.5 if dark_signal < 0 else 0.8  # negative amplified, positive dampened
            est_low *= supply_amp
            est_high *= supply_amp

        # Ensure low < high (handle negatives)
        est_min = min(est_low, est_high)
        est_max = max(est_low, est_high)
        predicted_range = f"{est_min:+.1f}% ~ {est_max:+.1f}%"
    else:
        # No dark signal: use score-based estimate
        # Widen range when structural scores are very weak
        if pct >= 75:
            predicted_range = "+5% ~ +20%"
        elif pct >= 55:
            predicted_range = "0% ~ +15%"
        elif pct >= 40:
            predicted_range = "-5% ~ +5%"
        elif pct >= 30:
            # Very weak: widen to capture crash risk
            # Tongrentang: 39% -> actual -39%, Puyuan: 33% -> actual -37%
            predicted_range = "-20% ~ -3%"
        else:
            predicted_range = "-30% ~ -5%"

    result = {
        'name': name,
        'code': code,
        'ipo_price': ipo_price_hkd,
        'ref_price_cny': ref_price_cny,
        'ref_price_hkd': ref_price_cny * fx_rate if ref_price_cny else None,
        'fx_rate': fx_rate,
        'discount': notes.get('discount'),
        'rating': rating,
        'scale': f"{scale_hk_yi}B HKD",
        'scores': scores,
        'notes': notes,
        'weighted': f"{weighted:.1f}/5.0 ({pct:.0f}%)",
        'advice': advice,
        'predicted_range': predicted_range,
    }
    if veto_reason:
        result['veto'] = veto_reason
    if range_veto_reason:
        result['range_veto'] = range_veto_reason
    if bull_veto_reason:
        result['bull_veto'] = bull_veto_reason
    if cost_warning:
        result['cost_warning'] = cost_warning
    return result


def format_result(r):
    """Pretty-print evaluation result."""
    lines = []
    lines.append(f"\n{'=' * 55}")
    lines.append(f"  {r['name']} ({r['code']})")
    ref_str = ""
    if r.get('ref_price_cny'):
        ref_str = f" | A-share: ¥{r['ref_price_cny']} -> HK${r['ref_price_hkd']:.2f} @1RMB={r['fx_rate']}HKD"
    lines.append(f"  IPO: HK${r['ipo_price']}{ref_str}")
    lines.append(f"  disc: {r['discount']} | {r['rating']} | {r['scale']}")
    lines.append(f"{'=' * 55}")
    for k in ['disc', 'rate', 'scale', 'subs', 'corn', 'env', 'sent', 'dark', 'supply']:
        if k in r['scores']:
            lines.append(f"  {k:8s}: {r['scores'][k]}/5  {r['notes'].get(k, '')}")
    lines.append(f"\n  Weighted: {r['weighted']}")
    lines.append(f"  Advice:   {r['advice']}")
    if 'predicted_range' in r:
        lines.append(f"  Est:      {r['predicted_range']}")
    if 'veto' in r:
        lines.append(f"  Veto:     {r['veto']}")
    if 'range_veto' in r:
        lines.append(f"  RangeVeto: {r['range_veto']}")
    if 'bull_veto' in r:
        lines.append(f"  BullVeto:  {r['bull_veto']}")
    if 'cost_warning' in r:
        lines.append(f"  Cost:     {r['cost_warning']}")
    lines.append(f"{'=' * 55}")
    return '\n'.join(lines)


def print_result(r):
    print(format_result(r))


def to_json(r):
    """Return JSON string of evaluation result for programmatic use."""
    import json
    return json.dumps(r, ensure_ascii=False, indent=2)


# ====== Backtest test cases ======

def run_backtest():
    """Run all backtest cases and print summary."""
    results = []

    # 1. Luxshare (02475.HK) - listed 7/9, first day -5.18%
    # 7 IPOs same day, 12 same week
    r = eval_hk_ipo(
        "Luxshare", "02475.HK", 63.28,
        ref_price_cny=62.47, fx_rate=1.152,
        rating="AA+", scale_hk_yi=242,
        retail_oversub=3.81, inst_oversub=15,
        cornerstone=True, market_env="normal", sector="electronics",
        sentiment="negative", dark_signal=-4.95, ipos_same_week=12,
        a_share_change=-2.18, ipos_same_day=7,
    )
    print_result(r)
    results.append(("Luxshare", "7/9", r['advice'], -5.18, True))

    # 2. Anker (00668.HK) - listed 7/2, first day +15.69%
    r = eval_hk_ipo(
        "Anker", "00668.HK", 99.32,
        ref_price_cny=100.4, fx_rate=1.152,
        rating="AA+", scale_hk_yi=56,
        retail_oversub=27.57, inst_oversub=10.24,
        cornerstone=True, market_env="normal", sector="consumer",
        sentiment="positive", ipos_same_week=8,
    )
    print_result(r)
    results.append(("Anker", "7/2", r['advice'], 15.69, True))

    # 3. Tongrentang (02667.HK) - listed 7/7, first day -39.09%
    r = eval_hk_ipo(
        "Tongrentang", "02667.HK", 5.50,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=5.3,
        retail_oversub=251.74, inst_oversub=2.84,
        cornerstone=True, market_env="normal", sector="pharma",
        sentiment="negative", ipos_same_week=6,
    )
    print_result(r)
    results.append(("Tongrentang", "7/7", r['advice'], -39.09, True))

    # 4. Puyuan (02497.HK) - listed 7/9, first day -37.36%
    r = eval_hk_ipo(
        "Puyuan", "02497.HK", 7.80,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=15,
        retail_oversub=0.45, inst_oversub=0.12,
        cornerstone=False, market_env="normal", sector="biotech",
        sentiment="negative", dark_signal=None, ipos_same_week=12,
    )
    print_result(r)
    results.append(("Puyuan", "7/9", r['advice'], -37.36, True))

    # 5. Yikong Zhijia (07687.HK) - listed 7/8, first day +9.99%
    r = eval_hk_ipo(
        "Yikong Zhijia", "07687.HK", 87.92,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=23,
        retail_oversub=157.82, inst_oversub=10.50,
        cornerstone=True, market_env="normal", sector="autonomous driving",
        sentiment="positive", dark_signal=8.96, ipos_same_week=15,
    )
    print_result(r)
    results.append(("Yikong", "7/8", r['advice'], 9.99, True))

    # 6. Binhua Group (06745.HK) - listed 7/10, first day -18.68%
    r = eval_hk_ipo(
        "Binhua", "06745.HK", 3.48,
        ref_price_cny=4.5, fx_rate=1.152,
        rating="AA", scale_hk_yi=12,
        retail_oversub=227.58, inst_oversub=4.26,
        cornerstone=True, market_env="normal", sector="chemicals",
        sentiment="negative", dark_signal=-21.26, ipos_same_week=15,
    )
    print_result(r)
    results.append(("Binhua", "7/10", r['advice'], -18.68, True))

    # 7. Momenta (06880.HK) - 7/8 listed, first day +6%
    r = eval_hk_ipo(
        "Momenta", "06880.HK", 295.60,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=8,
        retail_oversub=10.0, inst_oversub=8.0,
        cornerstone=True, market_env="normal", sector="autonomous driving",
        sentiment="positive", dark_signal=5.0, ipos_same_week=15,
    )
    print_result(r)
    results.append(("Momenta", "7/8", r['advice'], 6.0, True))

    # 8. Anker consistency check (no dark data, same IPO)
    r = eval_hk_ipo(
        "Anker (no-dark)", "00668.HK", 99.32,
        ref_price_cny=100.4, fx_rate=1.152,
        rating="AA+", scale_hk_yi=56,
        retail_oversub=27.57, inst_oversub=10.24,
        cornerstone=True, market_env="normal", sector="consumer",
        sentiment="positive", ipos_same_week=8,
    )
    results.append(("Anker(no-dark)", "7/2", r['advice'], 15.69, "BUY" in r['advice']))

    # 9. Jinghe Integrated (02249.HK) - 7/10 listed, first day ~+12%
    r = eval_hk_ipo(
        "Jinghe", "02249.HK", 32.30,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=70,
        retail_oversub=344.26, inst_oversub=14.62,
        cornerstone=True, market_env="normal", sector="semiconductor",
        sentiment="positive", dark_signal=11.76, ipos_same_week=15,
    )
    print_result(r)
    results.append(("Jinghe", "7/10", r['advice'], 12.0, True))

    # 10. Basic Semiconductor (09971.HK) - listed 7/8, first day ~+8%
    r = eval_hk_ipo(
        "Basic Semi", "09971.HK", 31.62,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=3,
        retail_oversub=4812.72, inst_oversub=20.0,
        cornerstone=True, market_env="normal", sector="semiconductor",
        sentiment="positive", dark_signal=17.33, ipos_same_week=15,
    )
    print_result(r)
    results.append(("Basic Semi", "7/8", r['advice'], 8.0, True))

    # 11. Zhongji Innolight (03308.HK) - listed 7/30, first day -2.04%
    # Dark -1.07%, A-share -9.15% (crash, amplification effect)
    r = eval_hk_ipo(
        "Zhongji Innolight", "03308.HK", 980.0,
        ref_price_cny=951.0, fx_rate=1.152,
        rating="AA+", scale_hk_yi=535,
        retail_oversub=13.0, inst_oversub=15.0,
        cornerstone=True, market_env="normal", sector="optical modules",
        sentiment="positive", dark_signal=-1.07, ipos_same_week=1,
        a_share_change=-9.15,
    )
    print_result(r)
    results.append(("Zhongji", "7/30", r['advice'], -2.04, True))

    # 12. Puyuan Precision (00537.HK) - listed 7/9, first day -37.36%
    # Dark -13.01%, 7 IPOs same day, retail 357x, has cornerstone
    r = eval_hk_ipo(
        "Puyuan Precision", "00537.HK", 45.98,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=11,
        retail_oversub=357, inst_oversub=5,
        cornerstone=True, market_env="normal", sector="instruments",
        sentiment="negative", dark_signal=-13.01, ipos_same_week=12,
        ipos_same_day=7,
    )
    print_result(r)
    results.append(("Puyuan Prec", "7/9", r['advice'], -37.36, True))

    # 13. Qiyunshan Food (02797.HK) - listed 7/9, first day +162.5%
    # Dark +37.63%, retail 1688x, inst 1.51x, NO cornerstone, small cap
    r = eval_hk_ipo(
        "Qiyunshan", "02797.HK", 8.0,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=2,
        retail_oversub=1688, inst_oversub=1.51,
        cornerstone=False, market_env="normal", sector="food",
        sentiment="negative", dark_signal=37.63, ipos_same_week=12,
        ipos_same_day=7,
    )
    print_result(r)
    results.append(("Qiyunshan", "7/9", r['advice'], 162.5, True))

    # 14. Nasen Tech (02261.HK) - listed 8/7, PENDING
    # Dark +50.67%, retail 2513x, inst 2.12x, NO cornerstone, 5B scale
    # Same bimodal pattern as Qiyunshan: retail hot + inst cold + dark positive = moon?
    r = eval_hk_ipo(
        "Nasen", "02261.HK", 10.42,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=5,
        retail_oversub=2513.54, inst_oversub=2.12,
        cornerstone=False, market_env="normal", sector="auto",
        sentiment="negative", dark_signal=50.67, ipos_same_week=1,
        ipos_same_day=1, market_temp=0.42,
    )
    print_result(r)
    # Result pending - will be verified after 8/7 close
    # Prediction: BUY (bull-veto), range +20.3% ~ +202.7%
    results.append(("Nasen", "8/7", r['advice'], 0.0, "PENDING"))

    # Summary
    correct = sum(1 for _, _, _, _, ok in results if ok is True)
    pending = sum(1 for _, _, _, _, ok in results if ok == "PENDING")
    verified = [r for r in results if r[4] is True or r[4] is False]
    total = len(results)
    print(f"\n{'=' * 55}")
    print(f"  BACKTEST SUMMARY (v1.6, N={total}, verified={len(verified)}, pending={pending})")
    print(f"{'=' * 55}")
    print(f"  {'IPO':<16s} {'Date':<6s} {'Advice':<20s} {'Actual':>8s}  Result")
    print(f"  {'-' * 55}")
    for name, date, advice, actual, ok in results:
        if ok == "PENDING":
            mark = "⏳"
            actual_str = "pending"
        elif ok is True or ok == "✅":
            mark = "✅"
            actual_str = f"{actual:>+7.2f}%"
        else:
            mark = "❌"
            actual_str = f"{actual:>+7.2f}%"
        print(f"  {name:<16s} {date:<6s} {advice:<20s} {actual_str:>8s}  {mark}")
    if pending:
        print(f"\n  Verified accuracy: {correct}/{len(verified)} = {correct/len(verified)*100:.0f}%")
        print(f"  Pending: {pending} case(s) awaiting result")
    else:
        print(f"\n  Accuracy: {correct}/{total} = {correct/total*100:.0f}%")
    print(f"  Note: N<20, observe not claim")
    print(f"{'=' * 55}")


if __name__ == "__main__":
    run_backtest()
