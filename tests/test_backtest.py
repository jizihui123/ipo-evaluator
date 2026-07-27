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


def test_anker_strong_buy():
    """Anker (7/2): STRONG BUY -> actual +15.69%"""
    r = eval_hk_ipo(
        "Anker", "00668.HK", 99.32,
        ref_price_cny=100.4, fx_rate=1.152,
        rating="AA+", scale_hk_yi=56,
        retail_oversub=27.57, inst_oversub=10.24,
        cornerstone=True, market_env="normal", sector="consumer",
        sentiment="positive", ipos_same_week=8,
    )
    assert "STRONG BUY" in r['advice'] or "BUY" in r['advice'], \
        f"Expected BUY/STRONG BUY, got {r['advice']}"
    print("✅ test_anker_strong_buy passed")


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
    assert "CAUTIOUS" in r['advice'], \
        f"Expected CAUTIOUS (veto), got {r['advice']}"
    assert 'veto' in r, "Expected veto reason in result"
    print("✅ test_luxshare_cautious_veto passed")


def test_puyuan_skip_supply_pressure():
    """Puyuan (7/9): SKIP (v1.4 supply pressure) -> actual -37.36%"""
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
    print("✅ test_puyuan_skip_supply_pressure passed")


def test_dark_veto_hard():
    """Dark signal < -8% should trigger hard veto (SKIP)"""
    r = eval_hk_ipo(
        "TestCrash", "00001.HK", 10.0,
        ref_price_cny=10.0, fx_rate=1.152,
        rating="AAA", scale_hk_yi=5,
        retail_oversub=30, inst_oversub=20,
        cornerstone=True, market_env="bull", sector="tech",
        sentiment="positive", dark_signal=-10.0, ipos_same_week=1,
    )
    assert "SKIP" in r['advice'], \
        f"Expected SKIP (hard veto), got {r['advice']}"
    assert 'veto' in r, "Expected hard veto reason"
    print("✅ test_dark_veto_hard passed")


def test_dark_veto_soft():
    """Dark signal < -4% should trigger soft veto (CAUTIOUS)"""
    r = eval_hk_ipo(
        "TestSoft", "00002.HK", 10.0,
        ref_price_cny=10.0, fx_rate=1.152,
        rating="AAA", scale_hk_yi=5,
        retail_oversub=30, inst_oversub=20,
        cornerstone=True, market_env="bull", sector="tech",
        sentiment="positive", dark_signal=-5.0, ipos_same_week=1,
    )
    assert "CAUTIOUS" in r['advice'], \
        f"Expected CAUTIOUS (soft veto), got {r['advice']}"
    print("✅ test_dark_veto_soft passed")


if __name__ == "__main__":
    test_anker_strong_buy()
    test_tongrentang_skip()
    test_luxshare_cautious_veto()
    test_puyuan_skip_supply_pressure()
    test_dark_veto_hard()
    test_dark_veto_soft()
    print(f"\n{'=' * 55}")
    print("  All 6 tests passed! ✅")
    print(f"{'=' * 55}")
