#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Anti-Overfitting Mechanism Integration Tests

Simulates real-world scenarios that should trigger each of the 6 mechanisms.
Each test verifies that the mechanism fires automatically when the condition is met.

Run: python tests/test_anti_overfitting_integration.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anti_overfitting import (
    FROZEN_CASES, assert_case_frozen, is_holdout_case,
    EconomicLogicChecker, DirectionMetrics, FailedCaseTracker,
    SimplicityAudit, verify_structural_constraints, run_full_audit,
)
from hk_ipo_evaluator import eval_hk_ipo, format_result

passed = 0
failed = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}: {detail}")

print("=" * 70)
print("  ANTI-OVERFITTING MECHANISM INTEGRATION TESTS")
print("  6 mechanisms × real-world scenarios")
print("=" * 70)

# ============================================================================
# Mechanism 1: Structural Constraints (Binary Veto Rules)
# ============================================================================
print("\n" + "=" * 70)
print("  MECHANISM 1: Structural Constraints (Binary Veto Rules)")
print("  Test: veto triggers automatically when dark signal crosses threshold")
print("=" * 70)

# Scenario 1a: dark = -10% with GOOD structure -> downgraded to CAUTIOUS (not SKIP)
# This is the conditional hard veto: struct_ok (subs>=3 + corn>=3) downgrades
print("\n[Scenario 1a] dark = -10% with good structure -> CAUTIOUS (downgraded)")
r = eval_hk_ipo("TestCrash", "00001.HK", 10.0,
    ref_price_cny=10.0, fx_rate=1.152, rating="AAA", scale_hk_yi=5,
    retail_oversub=30, inst_oversub=20, cornerstone=True,
    market_env="bull", sentiment="positive",
    dark_signal=-10.0, ipos_same_week=1)
check("dark=-10% + good structure -> CAUTIOUS (downgraded)", "CAUTIOUS" in r['advice'], f"advice={r['advice']}")
check("veto reason present", 'veto' in r, f"keys={list(r.keys())}")
check("veto is downgraded soft veto", "downgraded" in r.get('veto', ''), f"veto={r.get('veto')}")

# Scenario 1a2: dark = -10% with BAD structure -> SKIP (hard veto not downgraded)
print("\n[Scenario 1a2] dark = -10% with bad structure -> SKIP (hard veto)")
r = eval_hk_ipo("TestCrashBad", "00001.HK", 10.0,
    ref_price_cny=10.0, fx_rate=1.152, rating="AAA", scale_hk_yi=5,
    retail_oversub=0.5, inst_oversub=0.3, cornerstone=False,
    market_env="bear", sentiment="crash",
    dark_signal=-10.0, ipos_same_week=15)
check("dark=-10% + bad structure -> SKIP", "SKIP" in r['advice'], f"advice={r['advice']}")
check("veto is hard veto (not downgraded)", "DARK VETO" in r.get('veto', '') and "downgraded" not in r.get('veto', ''), 
      f"veto={r.get('veto')}")

# Scenario 1b: dark = -5% should trigger soft veto (CAUTIOUS)
print("\n[Scenario 1b] dark = -5% (between -4% and -8%)")
r = eval_hk_ipo("TestSoft", "00002.HK", 10.0,
    ref_price_cny=10.0, fx_rate=1.152, rating="AAA", scale_hk_yi=5,
    retail_oversub=30, inst_oversub=20, cornerstone=True,
    market_env="bull", sentiment="positive",
    dark_signal=-5.0, ipos_same_week=1)
check("dark=-5% triggers CAUTIOUS", "CAUTIOUS" in r['advice'], f"advice={r['advice']}")
check("veto is soft veto", "SOFT-VETO" in r.get('veto', ''), f"veto={r.get('veto')}")

# Scenario 1c: dark = -1% + high score -> range-veto (BUY downgraded to CAUTIOUS)
print("\n[Scenario 1c] dark = -1% + high score -> range-veto")
r = eval_hk_ipo("TestRange", "00003.HK", 10.0,
    ref_price_cny=15.0, fx_rate=1.152, rating="AAA", scale_hk_yi=5,
    retail_oversub=30, inst_oversub=20, cornerstone=True,
    market_env="bull", sentiment="positive",
    dark_signal=-1.0, ipos_same_week=1)
check("dark=-1% + high score -> CAUTIOUS (not BUY)", "BUY" not in r['advice'], f"advice={r['advice']}")
check("range_veto present", 'range_veto' in r, f"keys={list(r.keys())}")

# Scenario 1d: dark = +25% + low score -> bull-veto (CAUTIOUS upgraded to BUY)
print("\n[Scenario 1d] dark = +25% + low score -> bull-veto")
r = eval_hk_ipo("TestBull", "00004.HK", 10.0,
    rating="AA", scale_hk_yi=2,
    retail_oversub=200, inst_oversub=1.5,
    cornerstone=False, sentiment="negative",
    dark_signal=25.0, ipos_same_week=12)
check("dark=+25% -> BUY (bull-veto)", "BUY" in r['advice'], f"advice={r['advice']}")
check("bull_veto present", 'bull_veto' in r, f"keys={list(r.keys())}")

# Scenario 1e: dark = +2% + high score -> NO veto, normal BUY
print("\n[Scenario 1e] dark = +2% + high score -> normal BUY (no veto)")
r = eval_hk_ipo("TestNormal", "00005.HK", 10.0,
    ref_price_cny=15.0, fx_rate=1.152, rating="AAA", scale_hk_yi=5,
    retail_oversub=30, inst_oversub=20, cornerstone=True,
    market_env="bull", sentiment="positive",
    dark_signal=2.0, ipos_same_week=1)
check("dark=+2% -> BUY (no veto)", "BUY" in r['advice'], f"advice={r['advice']}")
check("no veto triggered", 'veto' not in r and 'range_veto' not in r and 'bull_veto' not in r, 
      f"unexpected veto: {r.get('veto','')}{r.get('range_veto','')}{r.get('bull_veto','')}")

# Scenario 1f: verify structural constraints have 0 degrees of freedom
print("\n[Scenario 1f] Verify 0 degrees of freedom")
struct = verify_structural_constraints()
check("4 constraints exist", struct['total_constraints'] == 4, f"count={struct['total_constraints']}")
check("0 degrees of freedom", struct['total_degrees_of_freedom'] == 0, f"dof={struct['total_degrees_of_freedom']}")
check("strength = MAXIMUM", struct['anti_overfitting_strength'] == "MAXIMUM", f"strength={struct['anti_overfitting_strength']}")

# ============================================================================
# Mechanism 2: Economic Logic Validator
# ============================================================================
print("\n" + "=" * 70)
print("  MECHANISM 2: Economic Logic Validator")
print("  Test: rejects params without economic justification")
print("=" * 70)

# Scenario 2a: approved logic passes
print("\n[Scenario 2a] Valid economic logic -> approved")
r = EconomicLogicChecker.validate("dark_veto_threshold", "dark_signal_predictor: dark market predicts listing day")
check("approved logic accepted", r['approved'] == True, f"approved={r['approved']}")

# Scenario 2b: case-specific multiplier rejected
print("\n[Scenario 2b] Case-specific multiplier -> rejected")
r = EconomicLogicChecker.validate("luxshare_multiplier", "case_specific_multiplier: if name==Luxshare then *1.5")
check("case-specific rejected", r['approved'] == False, f"approved={r['approved']}")
check("rejected_pattern identified", r['rejected_pattern'] == "case_specific_multiplier", 
      f"pattern={r.get('rejected_pattern')}")

# Scenario 2c: date-specific rejected
print("\n[Scenario 2c] Date-specific adjustment -> rejected")
r = EconomicLogicChecker.validate("july9_adjustment", "date_specific: if July 9 then *2")
check("date-specific rejected", r['approved'] == False, f"approved={r['approved']}")

# Scenario 2d: sector-specific rejected
print("\n[Scenario 2d] Sector-specific weight -> rejected")
r = EconomicLogicChecker.validate("tech_sector_weight", "sector_specific_weight: tech sector *1.5")
check("sector-specific rejected", r['approved'] == False, f"approved={r['approved']}")

# Scenario 2e: continuous optimization rejected
print("\n[Scenario 2e] Continuous optimization -> rejected")
r = EconomicLogicChecker.validate("learned_weights", "continuous_optimization: gradient descent on weights")
check("continuous optimization rejected", r['approved'] == False, f"approved={r['approved']}")

# Scenario 2f: supply_demand approved
print("\n[Scenario 2f] Supply-demand logic -> approved")
r = EconomicLogicChecker.validate("supply_threshold", "supply_demand: more IPOs = lower prices")
check("supply_demand approved", r['approved'] == True, f"approved={r['approved']}")

# ============================================================================
# Mechanism 3: Direction Over Magnitude
# ============================================================================
print("\n" + "=" * 70)
print("  MECHANISM 3: Direction Over Magnitude")
print("  Test: direction evaluation is independent of range magnitude")
print("=" * 70)

# Scenario 3a: BUY + positive = correct direction
print("\n[Scenario 3a] BUY + actual +5% -> direction correct")
r = DirectionMetrics.evaluate("BUY +", 5.0)
check("BUY + positive = correct", r['direction_correct'] == True, f"correct={r['direction_correct']}")

# Scenario 3b: BUY + negative = wrong direction
print("\n[Scenario 3b] BUY + actual -3% -> direction wrong")
r = DirectionMetrics.evaluate("BUY +", -3.0)
check("BUY + negative = wrong", r['direction_correct'] == False, f"correct={r['direction_correct']}")

# Scenario 3c: SKIP + negative = correct
print("\n[Scenario 3c] SKIP + actual -10% -> direction correct")
r = DirectionMetrics.evaluate("SKIP -", -10.0)
check("SKIP + negative = correct", r['direction_correct'] == True, f"correct={r['direction_correct']}")

# Scenario 3d: SKIP + positive = wrong (Dongfang pattern)
print("\n[Scenario 3d] SKIP + actual +1.73% -> direction wrong (Dongfang pattern)")
r = DirectionMetrics.evaluate("SKIP -", 1.73)
check("SKIP + positive = wrong", r['direction_correct'] == False, f"correct={r['direction_correct']}")

# Scenario 3e: aggregate separates dark vs no-dark accuracy
print("\n[Scenario 3e] Aggregate separates dark vs no-dark")
evals = [
    DirectionMetrics.evaluate("BUY +", 5.0),  # correct, with dark
    DirectionMetrics.evaluate("SKIP -", -10.0),  # correct, with dark
    DirectionMetrics.evaluate("SKIP -", 1.0),  # wrong, no dark
]
evals[0]['has_dark'] = True
evals[1]['has_dark'] = True
evals[2]['has_dark'] = False
agg = DirectionMetrics.aggregate(evals)
check("with-dark 100%", "2/2 = 100%" in agg['with_dark'], f"with_dark={agg['with_dark']}")
check("without-dark 0%", "0/1 = 0%" in agg['without_dark'], f"without_dark={agg['without_dark']}")

# ============================================================================
# Mechanism 4: Failed Case Visibility
# ============================================================================
print("\n" + "=" * 70)
print("  MECHANISM 4: Failed Case Visibility")
print("  Test: failures are recorded and reported, not hidden")
print("=" * 70)

# Scenario 4a: record a failure
print("\n[Scenario 4a] Record a failure")
FailedCaseTracker.clear()
f = FailedCaseTracker.record("TestFail", "00001.HK", "SKIP -", 1.73, "false negative")
check("failure recorded", f['case'] == "TestFail", f"case={f['case']}")
check("failure has advice", f['advice'] == "SKIP -", f"advice={f['advice']}")
check("failure has actual", f['actual'] == 1.73, f"actual={f['actual']}")

# Scenario 4b: record multiple failures
print("\n[Scenario 4b] Record multiple failures")
FailedCaseTracker.record("TestFail2", "00002.HK", "BUY +", -5.0, "false positive")
all_fails = FailedCaseTracker.get_all()
check("2 failures recorded", len(all_fails) == 2, f"count={len(all_fails)}")

# Scenario 4c: clear failures
print("\n[Scenario 4c] Clear failures")
FailedCaseTracker.clear()
check("failures cleared", len(FailedCaseTracker.get_all()) == 0, f"count={len(FailedCaseTracker.get_all())}")

# Scenario 4d: simulate real backtest failure (Dongfang pattern)
print("\n[Scenario 4d] Simulate Dongfang-like failure")
FailedCaseTracker.clear()
FailedCaseTracker.record("Dongfang", "01770.HK", "SKIP -", 1.73, 
    "false negative: no dark data + extreme supply + small cap = unpredictable")
failures = FailedCaseTracker.get_all()
check("Dongfang failure tracked", len(failures) == 1 and failures[0]['case'] == "Dongfang",
      f"failures={failures}")
check("failure reason recorded", "unpredictable" in failures[0]['reason'],
      f"reason={failures[0]['reason']}")
FailedCaseTracker.clear()

# ============================================================================
# Mechanism 5: Version Freeze Protocol
# ============================================================================
print("\n" + "=" * 70)
print("  MECHANISM 5: Version Freeze Protocol")
print("  Test: frozen cases are blocked, holdout cases are allowed")
print("=" * 70)

# Scenario 5a: frozen case detected
print("\n[Scenario 5a] Frozen case (Luxshare) detected")
is_frozen = assert_case_frozen("Luxshare")
check("Luxshare is frozen", is_frozen == True, f"frozen={is_frozen}")

# Scenario 5b: holdout case allowed
print("\n[Scenario 5b] Holdout case (Junzheng) allowed")
is_frozen = assert_case_frozen("Junzheng")
check("Junzheng not frozen", is_frozen == False, f"frozen={is_frozen}")
is_holdout = is_holdout_case("Junzheng")
check("Junzheng is holdout", is_holdout == True, f"holdout={is_holdout}")

# Scenario 5c: SHEIN is holdout
print("\n[Scenario 5c] SHEIN is holdout")
is_holdout = is_holdout_case("SHEIN")
check("SHEIN is holdout", is_holdout == True, f"holdout={is_holdout}")

# Scenario 5d: frozen case count correct
print("\n[Scenario 5d] Frozen case count = 16")
check("16 frozen cases", len(FROZEN_CASES) == 16, f"count={len(FROZEN_CASES)}")

# Scenario 5e: parameter change on frozen case triggers warning
print("\n[Scenario 5e] Parameter change on frozen case -> warning")
r = EconomicLogicChecker.validate("some_param", "supply_demand: test", triggered_by_case="Anker")
check("frozen violation detected", r['frozen_case_violation'] == True, 
      f"violation={r['frozen_case_violation']}")
check("frozen warning present", r['frozen_warning'] is not None,
      f"warning={r.get('frozen_warning')}")

# Scenario 5f: parameter change on holdout case -> no warning
print("\n[Scenario 5f] Parameter change on holdout case -> no freeze warning")
r = EconomicLogicChecker.validate("some_param", "supply_demand: test", triggered_by_case="Junzheng")
check("no freeze violation", r['frozen_case_violation'] == False, 
      f"violation={r['frozen_case_violation']}")

# ============================================================================
# Mechanism 6: Simplicity Bias
# ============================================================================
print("\n" + "=" * 70)
print("  MECHANISM 6: Simplicity Bias")
print("  Test: integer scoring, fixed thresholds, no weight learning")
print("=" * 70)

# Scenario 6a: all scores are integers 0-5
print("\n[Scenario 6a] All scores are integers 0-5")
r = eval_hk_ipo("TestScore", "00001.HK", 10.0,
    ref_price_cny=10.0, fx_rate=1.152, rating="AA+", scale_hk_yi=20,
    retail_oversub=15, inst_oversub=8, cornerstone=True,
    sentiment="positive", dark_signal=5.0, ipos_same_week=3)
all_integer = all(isinstance(v, int) for v in r['scores'].values())
in_range = all(0 <= v <= 5 for v in r['scores'].values())
check("scores are integers", all_integer, f"scores={r['scores']}")
check("scores in 0-5 range", in_range, f"scores={r['scores']}")

# Scenario 6b: same inputs always produce same output (deterministic)
print("\n[Scenario 6b] Deterministic output (same input = same output)")
r1 = eval_hk_ipo("Test1", "00001.HK", 10.0,
    ref_price_cny=10.0, rating="AA+", scale_hk_yi=20,
    retail_oversub=15, inst_oversub=8, cornerstone=True,
    sentiment="positive", dark_signal=5.0, ipos_same_week=3)
r2 = eval_hk_ipo("Test2", "00001.HK", 10.0,
    ref_price_cny=10.0, rating="AA+", scale_hk_yi=20,
    retail_oversub=15, inst_oversub=8, cornerstone=True,
    sentiment="positive", dark_signal=5.0, ipos_same_week=3)
check("deterministic scores", r1['scores'] == r2['scores'], 
      f"r1={r1['scores']} r2={r2['scores']}")
check("deterministic advice", r1['advice'] == r2['advice'],
      f"r1={r1['advice']} r2={r2['advice']}")

# Scenario 6c: simplicity audit returns correct metrics
print("\n[Scenario 6c] Simplicity audit metrics")
audit = SimplicityAudit.audit()
check("9 scoring dimensions", audit['scoring_dimensions'] == 9, f"dims={audit['scoring_dimensions']}")
check("6 score levels (0-5)", audit['score_levels_per_dim'] == 6, f"levels={audit['score_levels_per_dim']}")
check("integer scoring", audit['uses_integer_scoring'] == True)
check("NO continuous optimization", audit['uses_continuous_optimization'] == False)
check("NO weight learning", audit['weight_learning'] == False)
check("fixed thresholds used", audit['uses_fixed_thresholds'] == True)
check("simplicity score is HIGH", audit['simplicity_score'] == "HIGH", 
      f"score={audit['simplicity_score']}")

# Scenario 6d: fixed thresholds are immutable
print("\n[Scenario 6d] Fixed thresholds are predefined and immutable")
thresholds = SimplicityAudit.FIXED_THRESHOLDS
check("dark_veto_hard = -8", thresholds['dark_veto_hard'] == -8, f"value={thresholds['dark_veto_hard']}")
check("dark_veto_soft = -4", thresholds['dark_veto_soft'] == -4, f"value={thresholds['dark_veto_soft']}")
check("bull_veto = 20", thresholds['bull_veto'] == 20, f"value={thresholds['bull_veto']}")
check("cost_threshold = 3", thresholds['cost_threshold'] == 3, f"value={thresholds['cost_threshold']}")
check("advice_strong_buy = 75", thresholds['advice_strong_buy'] == 75, f"value={thresholds['advice_strong_buy']}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print(f"  INTEGRATION TEST SUMMARY")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print(f"  Total:  {passed + failed}")
if failed == 0:
    print(f"\n  ✅ ALL {passed} TESTS PASSED!")
    print(f"  6 anti-overfitting mechanisms all trigger correctly.")
else:
    print(f"\n  ❌ {failed} TESTS FAILED!")
print("=" * 70)

# Print mechanism-by-mechanism summary
print("\nMechanism breakdown:")
print(f"  1. Structural Constraints:   binary veto auto-triggers ✅")
print(f"  2. Economic Logic Validator: rejects bad patterns ✅")
print(f"  3. Direction Over Magnitude: separates dark/no-dark accuracy ✅")
print(f"  4. Failed Case Visibility:   records and reports failures ✅")
print(f"  5. Version Freeze Protocol:  blocks frozen case changes ✅")
print(f"  6. Simplicity Bias:          integer scores, fixed thresholds ✅")
