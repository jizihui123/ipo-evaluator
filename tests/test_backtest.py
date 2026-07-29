#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for HK IPO Evaluator backtest cases.

Run: python tests/test_backtest.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hk_ipo_evaluator import eval_hk_ipo


# ====== Original 4 cases ======

def test_anker_buy():
    """Anker (7/2): BUY -> actual +15.69%"""
    r = eval_hk_ipo(
        "Anker", "00668.HK", 99.32,
        ref_price_cny=100.4, fx_rate=1.152,
        rating="AA+", scale_hk_yi=56,
        retail_oversub=27.57, inst_oversub=10.24,
        cornerstone=True, market_env="normal", sector="consumer",
        sentiment="positive", ipos_same_week=8,
    )
    assert "BUY" in r['advice'], f"Expected BUY, got {r['advice']}"
    print("✅ test_anker_buy passed")


def test_tongrentang_skip():
    """Tongrentang (7/7): SKIP -> actual -39.09%"""
    r = eval_hk_ipo(
        "Tongrentang", "02667.HK", 5.50,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=5.3,
        retail_oversub=251.74, inst_oversub=2.84,
        cornerstone=True, market_env="normal", sector="pharma",
        sentiment="negative", ipos_same_week=6,
    )
    assert "SKIP" in r['advice'] or "CAUTIOUS" in r['advice'], \
        f"Expected SKIP/CAUTIOUS, got {r['advice']}"
    print("✅ test_tongrentang_skip passed")


def test_luxshare_cautious_veto():
    """Luxshare (7/9): CAUTIOUS(veto) -> actual -5.18%"""
    r = eval_hk_ipo(
        "Luxshare", "02475.HK", 63.28,
        ref_price_cny=62.47, fx_rate=1.152,
        rating="AA+", scale_hk_yi=242,
        retail_oversub=3.81, inst_oversub=15,
        cornerstone=True, market_env="normal", sector="electronics",
        sentiment="negative", dark_signal=-4.95, ipos_same_week=12,
    )
    assert "CAUTIOUS" in r['advice'], f"Expected CAUTIOUS (veto), got {r['advice']}"
    assert 'veto' in r, "Expected veto reason in result"
    print("✅ test_luxshare_cautious_veto passed")


def test_puyuan_skip_supply():
    """Puyuan (7/9): SKIP (supply pressure) -> actual -37.36%"""
    r = eval_hk_ipo(
        "Puyuan", "02497.HK", 7.80,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=15,
        retail_oversub=0.45, inst_oversub=0.12,
        cornerstone=False, market_env="normal", sector="biotech",
        sentiment="negative", dark_signal=None, ipos_same_week=12,
    )
    assert "SKIP" in r['advice'] or "CAUTIOUS" in r['advice'], \
        f"Expected SKIP/CAUTIOUS, got {r['advice']}"
    print("✅ test_puyuan_skip_supply passed")


def test_dark_hard_veto():
    """Dark signal <= -8% triggers hard veto (SKIP)"""
    r = eval_hk_ipo(
        "TestCrash", "00001.HK", 10.0,
        ref_price_cny=10.0, fx_rate=1.152,
        rating="AAA", scale_hk_yi=5,
        retail_oversub=30, inst_oversub=20,
        cornerstone=True, market_env="bull", sector="tech",
        sentiment="positive", dark_signal=-10.0, ipos_same_week=1,
    )
    assert "SKIP" in r['advice'], f"Expected SKIP (hard veto), got {r['advice']}"
    assert 'veto' in r, "Expected hard veto reason"
    print("✅ test_dark_hard_veto passed")


def test_dark_soft_veto():
    """Dark signal <= -4% triggers soft veto (CAUTIOUS)"""
    r = eval_hk_ipo(
        "TestSoft", "00002.HK", 10.0,
        ref_price_cny=10.0, fx_rate=1.152,
        rating="AAA", scale_hk_yi=5,
        retail_oversub=30, inst_oversub=20,
        cornerstone=True, market_env="bull", sector="tech",
        sentiment="positive", dark_signal=-5.0, ipos_same_week=1,
    )
    assert "CAUTIOUS" in r['advice'], f"Expected CAUTIOUS (soft veto), got {r['advice']}"
    print("✅ test_dark_soft_veto passed")


# ====== New cases (v1.5) ======

def test_yikong_buy():
    """Yikong Zhijia (7/8): BUY -> actual +9.99%"""
    r = eval_hk_ipo(
        "Yikong", "07687.HK", 87.92,
        ref_price_cny=None,
        rating="AA", scale_hk_yi=23,
        retail_oversub=157.82, inst_oversub=10.50,
        cornerstone=True, market_env="normal", sector="autonomous driving",
        sentiment="positive", dark_signal=8.96, ipos_same_week=15,
    )
    assert "BUY" in r['advice'], f"Expected BUY, got {r['advice']}"
    print("✅ test_yikong_buy passed")


def test_binhua_skip_veto():
    """Binhua (7/10): SKIP (hard veto) -> actual -18.68%"""
    r = eval_hk_ipo(
        "Binhua", "06745.HK", 3.48,
        ref_price_cny=4.5, fx_rate=1.152,
        rating="AA", scale_hk_yi=12,
        retail_oversub=227.58, inst_oversub=4.26,
        cornerstone=True, market_env="normal", sector="chemicals",
        sentiment="negative", dark_signal=-21.26, ipos_same_week=15,
    )
    assert "SKIP" in r['advice'], f"Expected SKIP (hard veto), got {r['advice']}"
    assert 'veto' in r, "Expected hard veto"
    print("✅ test_binhua_skip_veto passed")


def test_cost_warning():
    """BUY with low predicted gain should trigger cost warning"""
    r = eval_hk_ipo(
        "LowGain", "00003.HK", 10.0,
        ref_price_cny=10.0, fx_rate=1.152,
        rating="AA+", scale_hk_yi=10,
        retail_oversub=15, inst_oversub=8,
        cornerstone=True, market_env="normal", sentiment="neutral",
        dark_signal=1.0, ipos_same_week=2,  # dark +1% < 3% cost threshold
    )
    if "BUY" in r['advice']:
        assert 'cost_warning' in r, \
            f"Expected cost_warning for low-gain BUY, got advice={r['advice']}"
        print("✅ test_cost_warning passed")
    else:
        print("✅ test_cost_warning passed (advice not BUY, no warning needed)")


def test_json_output():
    """to_json() should produce valid JSON"""
    from hk_ipo_evaluator import to_json
    import json
    r = eval_hk_ipo(
        "JSONTest", "00004.HK", 10.0,
        ref_price_cny=10.0, fx_rate=1.152,
        rating="AA+", scale_hk_yi=10,
        retail_oversub=15, inst_oversub=8,
        cornerstone=True, dark_signal=2.0, ipos_same_week=3,
    )
    j = to_json(r)
    parsed = json.loads(j)
    assert parsed['name'] == "JSONTest"
    assert 'scores' in parsed
    assert 'advice' in parsed
    print("✅ test_json_output passed")


def test_range_veto():
    """Dark < 0% should cap advice at CAUTIOUS (range-veto)"""
    r = eval_hk_ipo(
        "RangeVeto", "00005.HK", 10.0,
        ref_price_cny=12.0, fx_rate=1.152,  # big discount to push score up
        rating="AA+", scale_hk_yi=50,
        retail_oversub=15, inst_oversub=8,
        cornerstone=True, market_env="normal", sentiment="positive",
        dark_signal=-1.0, ipos_same_week=1,  # dark negative but above veto threshold
    )
    assert "BUY" not in r['advice'], \
        f"Expected CAUTIOUS (range-veto), got {r['advice']}"
    assert 'range_veto' in r, "Expected range_veto in result"
    print("✅ test_range_veto passed")


def test_predicted_range_with_dark():
    """predicted_range should be in output when dark signal is available"""
    r = eval_hk_ipo(
        "RangeTest", "00006.HK", 10.0,
        ref_price_cny=10.0, fx_rate=1.152,
        rating="AA+", scale_hk_yi=20,
        retail_oversub=15, inst_oversub=8,
        cornerstone=True, dark_signal=5.0, ipos_same_week=2,
    )
    assert 'predicted_range' in r, "Missing predicted_range"
    assert '%' in r['predicted_range'], f"Bad range format: {r['predicted_range']}"
    print("✅ test_predicted_range_with_dark passed")


if __name__ == "__main__":
    test_anker_buy()
    test_tongrentang_skip()
    test_luxshare_cautious_veto()
    test_puyuan_skip_supply()
    test_dark_hard_veto()
    test_dark_soft_veto()
    test_yikong_buy()
    test_binhua_skip_veto()
    test_cost_warning()
    test_json_output()
    test_range_veto()
    test_predicted_range_with_dark()
    print(f"\n{'=' * 55}")
    print("  All 12 tests passed! ✅")
    print(f"{'=' * 55}")
