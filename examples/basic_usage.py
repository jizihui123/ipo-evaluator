#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic usage example for HK IPO Evaluator.

Demonstrates:
  1. Evaluating an IPO with full data (including dark market signal)
  2. Evaluating an IPO without A-share reference
  3. Evaluating an IPO with supply pressure focus (no dark signal)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hk_ipo_evaluator import eval_hk_ipo, print_result


# Example 1: Full data evaluation with dark market signal
print("=" * 60)
print("  Example 1: Full evaluation with dark market signal")
print("=" * 60)

result = eval_hk_ipo(
    name="TechCorp HK",
    code="09988.HK",
    ipo_price_hkd=80.0,
    ref_price_cny=75.0,
    fx_rate=1.152,
    rating="AA+",
    scale_hk_yi=30,
    retail_oversub=20.0,
    inst_oversub=12.0,
    cornerstone=True,
    market_env="normal",
    sector="technology",
    sentiment="positive",
    dark_signal=3.5,
    ipos_same_week=4,
)
print_result(result)


# Example 2: No A-share reference (standalone HK listing)
print("\n" + "=" * 60)
print("  Example 2: Standalone HK listing (no A-share ref)")
print("=" * 60)

result = eval_hk_ipo(
    name="BioTech HK",
    code="02121.HK",
    ipo_price_hkd=12.5,
    ref_price_cny=None,
    rating="AA",
    scale_hk_yi=8,
    retail_oversub=5.0,
    inst_oversub=3.0,
    cornerstone=False,
    market_env="normal",
    sector="biotech",
    sentiment="neutral",
    ipos_same_week=2,
)
print_result(result)


# Example 3: Supply pressure focus (no dark signal available)
print("\n" + "=" * 60)
print("  Example 3: High supply pressure scenario (no dark signal)")
print("=" * 60)

result = eval_hk_ipo(
    name="ConsumerCo HK",
    code="01500.HK",
    ipo_price_hkd=6.8,
    ref_price_cny=None,
    rating="A+",
    scale_hk_yi=3,
    retail_oversub=1.5,
    inst_oversub=0.8,
    cornerstone=False,
    market_env="bear",
    sector="consumer",
    sentiment="crash",
    dark_signal=None,
    ipos_same_week=15,
)
print_result(result)
print("\n  Note: 15 IPOs same week -> supply pressure = 0 (extreme)")
print("  This is what caught the Puyuan -37.36% crash in backtest")
