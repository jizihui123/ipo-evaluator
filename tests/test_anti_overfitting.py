#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for anti-overfitting mechanisms.

Run: python tests/test_anti_overfitting.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anti_overfitting import (
    FROZEN_CASES, assert_case_frozen, is_holdout_case,
    EconomicLogicChecker, DirectionMetrics, FailedCaseTracker,
    SimplicityAudit, verify_structural_constraints, run_full_audit,
)


def test_frozen_cases():
    """Frozen cases should be detected and blocked."""
    assert assert_case_frozen("Luxshare") == True, "Luxshare should be frozen"
    assert assert_case_frozen("Anker") == True, "Anker should be frozen"
    assert assert_case_frozen("Nasen") == True, "Nasen should be frozen"
    print("✅ test_frozen_cases passed")


def test_holdout_case():
    """New cases should be identified as holdout."""
    assert is_holdout_case("Junzheng") == True, "Junzheng should be holdout"
    assert is_holdout_case("SHEIN") == True, "SHEIN should be holdout"
    assert is_holdout_case("Luxshare") == False, "Luxshare should NOT be holdout"
    print("✅ test_holdout_case passed")


def test_frozen_case_count():
    """Should have 16 frozen cases (excluding Anker duplicate)."""
    assert len(FROZEN_CASES) == 16, f"Expected 16 frozen cases, got {len(FROZEN_CASES)}"
    print("✅ test_frozen_case_count passed")


def test_economic_logic_approved():
    """Approved economic logic should pass validation."""
    r = EconomicLogicChecker.validate(
        "dark_veto", "dark_signal_predictor: dark market predicts listing day",
        triggered_by_case=None
    )
    assert r["approved"] == True, "dark_signal_predictor should be approved"
    print("✅ test_economic_logic_approved passed")


def test_economic_logic_rejected():
    """Rejected patterns should fail validation."""
    r = EconomicLogicChecker.validate(
        "case_multiplier", "case_specific_multiplier: if name==X then *1.5",
        triggered_by_case=None
    )
    assert r["approved"] == False, "case_specific_multiplier should be rejected"
    assert r["rejected_pattern"] == "case_specific_multiplier"
    print("✅ test_economic_logic_rejected passed")


def test_economic_logic_frozen_violation():
    """Parameter change on frozen case should trigger warning."""
    r = EconomicLogicChecker.validate(
        "some_param", "supply_demand: more IPOs = lower prices",
        triggered_by_case="Luxshare"
    )
    assert r["approved"] == True, "supply_demand is valid logic"
    assert r["frozen_case_violation"] == True, "Should flag frozen case violation"
    print("✅ test_economic_logic_frozen_violation passed")


def test_direction_buy():
    """BUY advice with positive return = correct direction."""
    r = DirectionMetrics.evaluate("BUY +", 5.0)
    assert r["direction_correct"] == True
    print("✅ test_direction_buy passed")


def test_direction_skip():
    """SKIP advice with negative return = correct direction."""
    r = DirectionMetrics.evaluate("SKIP -", -10.0)
    assert r["direction_correct"] == True
    print("✅ test_direction_skip passed")


def test_direction_buy_wrong():
    """BUY advice with negative return = wrong direction."""
    r = DirectionMetrics.evaluate("BUY +", -5.0)
    assert r["direction_correct"] == False
    print("✅ test_direction_buy_wrong passed")


def test_direction_cautious():
    """CAUTIOUS advice with marginal return = correct."""
    r = DirectionMetrics.evaluate("CAUTIOUS ?", 2.0)
    assert r["direction_correct"] == True, "CAUTIOUS +2% should be correct"
    r2 = DirectionMetrics.evaluate("CAUTIOUS ?", -3.0)
    assert r2["direction_correct"] == True, "CAUTIOUS -3% should be correct"
    r3 = DirectionMetrics.evaluate("CAUTIOUS ?", -15.0)
    assert r3["direction_correct"] == False, "CAUTIOUS -15% should be wrong"
    print("✅ test_direction_cautious passed")


def test_direction_aggregate():
    """Aggregate metrics should compute correctly."""
    results = [
        {"advice": "BUY +", "actual": 5.0, "has_dark": True},
        {"advice": "SKIP -", "actual": -10.0, "has_dark": True},
        {"advice": "BUY +", "actual": -3.0, "has_dark": False},
    ]
    # Evaluate each
    evals = []
    for r in results:
        e = DirectionMetrics.evaluate(r["advice"], r["actual"])
        e["has_dark"] = r["has_dark"]
        evals.append(e)
    
    agg = DirectionMetrics.aggregate(evals)
    assert "2/3 = 67%" in agg["direction_accuracy"]
    assert "2/2 = 100%" in agg["with_dark"]
    assert "0/1 = 0%" in agg["without_dark"]
    print("✅ test_direction_aggregate passed")


def test_failed_case_tracker():
    """Failed case tracker should record and report failures."""
    FailedCaseTracker.clear()
    FailedCaseTracker.record("TestFail", "00001.HK", "SKIP -", 1.5, "false negative")
    failures = FailedCaseTracker.get_all()
    assert len(failures) == 1
    assert failures[0]["case"] == "TestFail"
    FailedCaseTracker.clear()
    print("✅ test_failed_case_tracker passed")


def test_simplicity_audit():
    """Simplicity audit should return model complexity metrics."""
    audit = SimplicityAudit.audit()
    assert audit["scoring_dimensions"] == 9
    assert audit["uses_integer_scoring"] == True
    assert audit["uses_continuous_optimization"] == False
    assert audit["simplicity_score"] in ["HIGH", "MEDIUM", "LOW"]
    print("✅ test_simplicity_audit passed")


def test_structural_constraints():
    """Structural constraints should have zero degrees of freedom."""
    struct = verify_structural_constraints()
    assert struct["total_constraints"] == 4
    assert struct["total_degrees_of_freedom"] == 0
    assert struct["anti_overfitting_strength"] == "MAXIMUM"
    print("✅ test_structural_constraints passed")


def test_full_audit():
    """Full audit should run without errors."""
    result = run_full_audit()
    assert "structural_constraints" in result
    assert "simplicity" in result
    print("✅ test_full_audit passed")


if __name__ == "__main__":
    test_frozen_cases()
    test_holdout_case()
    test_frozen_case_count()
    test_economic_logic_approved()
    test_economic_logic_rejected()
    test_economic_logic_frozen_violation()
    test_direction_buy()
    test_direction_skip()
    test_direction_buy_wrong()
    test_direction_cautious()
    test_direction_aggregate()
    test_failed_case_tracker()
    test_simplicity_audit()
    test_structural_constraints()
    test_full_audit()
    print(f"\n{'=' * 55}")
    print("  All 15 anti-overfitting tests passed! ✅")
    print(f"{'=' * 55}")
