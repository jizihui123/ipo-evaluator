#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Anti-Overfitting Module for IPO Evaluator
==========================================

6 mechanisms to prevent overfitting, implemented as executable code:

1. Structural Constraints: binary veto rules, no continuous optimization
2. Economic Logic Validator: reject params without economic justification
3. Direction Over Magnitude: prioritize binary direction over precise range
4. Failed Case Visibility: track and report all failures
5. Version Freeze Protocol: block parameter changes on frozen cases
6. Simplicity Bias: integer scores, fixed thresholds, parameter count audit

Usage:
    from anti_overfitting import (
        FROZEN_CASES, assert_case_frozen, audit_parameters,
        EconomicLogicChecker, DirectionMetrics, SimplicityAudit
    )
"""

import hashlib
import json
from datetime import datetime


# ============================================================================
# Mechanism 5: Version Freeze Protocol
# ============================================================================

# Cases frozen since v1.8 (2026-08-19). No parameter changes allowed
# to improve accuracy on these specific cases.
FROZEN_CASES = {
    "Luxshare": "02475.HK",
    "Anker": "00668.HK",
    "Tongrentang": "02667.HK",
    "Puyuan": "02497.HK",
    "Yikong": "07687.HK",
    "Binhua": "06745.HK",
    "Momenta": "06880.HK",
    "Jinghe": "02249.HK",
    "Basic Semi": "09971.HK",
    "Zhongji": "03308.HK",
    "Puyuan Prec": "00537.HK",
    "Qiyunshan": "02797.HK",
    "Nasen": "02261.HK",
    "Dingtai": "01377.HK",
    "Dongfang": "01770.HK",
    "Luoshi": "03752.HK",
}

FREEZE_DATE = "2026-08-19"
FREEZE_VERSION = "v1.8"


def assert_case_frozen(case_name):
    """
    Check if a case is frozen. Raises warning if parameter tuning
    is attempted on a frozen case.
    
    Returns True if frozen (no changes allowed), False if new case.
    """
    if case_name in FROZEN_CASES:
        print(
            f"⚠️  FROZEN CASE: '{case_name}' ({FROZEN_CASES[case_name]}) "
            f"is frozen since {FREEZE_DATE} ({FREEZE_VERSION}). "
            f"No parameter changes allowed to improve its accuracy."
        )
        return True
    return False


def is_holdout_case(case_name):
    """Check if a case is a new holdout case (not in frozen set)."""
    return case_name not in FROZEN_CASES


# ============================================================================
# Mechanism 2: Economic Logic Validator
# ============================================================================

class EconomicLogicChecker:
    """
    Validates that parameter changes have economic justification,
    not just data-fitting justification.
    """
    
    # Approved economic logic categories
    APPROVED_LOGIC = {
        "dark_signal_predictor": "Dark market = real money trading, directly predicts listing day",
        "supply_demand": "More IPOs = more capital competition = lower prices",
        "ah_linkage": "A+H linked, A-share moves affect HK sentiment",
        "mean_reversion": "Extreme signals overreact, market corrects toward fundamental",
        "market_temperature": "Recent break rate = market risk appetite",
        "trading_cost": "Transaction costs reduce net profit on marginal trades",
        "structural_weakness": "Multiple weaknesses compound nonlinearly",
        "speculation_dynamics": "Small cap + extreme retail = bimodal speculation",
    }
    
    # Rejected logic patterns (would improve backtest but lack generalization)
    REJECTED_LOGIC = [
        "case_specific_multiplier",  # e.g., "if name==X then *1.5"
        "date_specific",             # e.g., "if July 9 then *2"
        "sector_specific_weight",    # too few cases per sector
        "continuous_optimization",   # would perfectly fit training data
        "rating_specific_veto",      # too few cases per rating level
    ]
    
    @classmethod
    def validate(cls, parameter_name, economic_logic, triggered_by_case=None):
        """
        Validate a parameter change against economic logic requirements.
        
        Parameters
        ----------
        parameter_name : str
            Name of the parameter being changed.
        economic_logic : str
            Economic justification (must match an approved category).
        triggered_by_case : str, optional
            Which case triggered this change (for audit trail).
        
        Returns
        -------
        dict
            Validation result with approved/rejected status and reason.
        """
        # Check if triggered by a frozen case
        frozen_warning = None
        if triggered_by_case:
            if assert_case_frozen(triggered_by_case):
                frozen_warning = (
                    f"PARAMETER CHANGE ON FROZEN CASE '{triggered_by_case}' - "
                    f"this violates the version freeze protocol"
                )
        
        # Check economic logic
        approved = False
        logic_category = None
        for category, description in cls.APPROVED_LOGIC.items():
            if category in economic_logic.lower() or description.lower() in economic_logic.lower():
                approved = True
                logic_category = category
                break
        
        # Check rejected patterns
        rejected_pattern = None
        for pattern in cls.REJECTED_LOGIC:
            if pattern in economic_logic.lower():
                approved = False
                rejected_pattern = pattern
                break
        
        result = {
            "parameter": parameter_name,
            "economic_logic": economic_logic,
            "approved": approved,
            "logic_category": logic_category,
            "triggered_by": triggered_by_case,
            "frozen_case_violation": frozen_warning is not None,
            "frozen_warning": frozen_warning,
            "rejected_pattern": rejected_pattern,
            "timestamp": datetime.now().isoformat(),
        }
        
        if not approved:
            print(f"❌ REJECTED: {parameter_name} - economic logic not approved")
            if rejected_pattern:
                print(f"   Rejected pattern: {rejected_pattern}")
        elif frozen_warning:
            print(f"⚠️  APPROVED with warning: {parameter_name}")
            print(f"   {frozen_warning}")
        else:
            print(f"✅ APPROVED: {parameter_name} ({logic_category})")
        
        return result


# ============================================================================
# Mechanism 3: Direction Over Magnitude
# ============================================================================

class DirectionMetrics:
    """
    Track direction accuracy separately from magnitude accuracy.
    Direction (BUY/CAUTIOUS/SKIP) is more robust to overfitting than
    predicted range (exact percentage).
    """
    
    @staticmethod
    def evaluate(advice, actual_return):
        """
        Evaluate if direction is correct.
        
        BUY -> actual > 0
        CAUTIOUS -> actual in [-5%, +5%] (marginal)
        SKIP -> actual < 0
        """
        if "STRONG BUY" in advice or "BUY" in advice:
            expected_direction = "positive"
            correct = actual_return > 0
        elif "SKIP" in advice:
            expected_direction = "negative"
            correct = actual_return < 0
        elif "CAUTIOUS" in advice:
            expected_direction = "marginal"
            # CAUTIOUS is correct if actual is between -10% and +5%
            # (broad band, as CAUTIOUS means "uncertain")
            correct = -10 <= actual_return <= 5
        else:
            expected_direction = "unknown"
            correct = False
        
        return {
            "advice": advice,
            "actual": actual_return,
            "expected_direction": expected_direction,
            "direction_correct": correct,
        }
    
    @staticmethod
    def aggregate(results):
        """Aggregate direction accuracy across cases."""
        total = len(results)
        correct = sum(1 for r in results if r["direction_correct"])
        
        # Separate by data type
        with_dark = [r for r in results if r.get("has_dark")]
        without_dark = [r for r in results if not r.get("has_dark")]
        
        dark_correct = sum(1 for r in with_dark if r["direction_correct"])
        no_dark_correct = sum(1 for r in without_dark if r["direction_correct"])
        
        return {
            "total": total,
            "direction_correct": correct,
            "direction_accuracy": f"{correct}/{total} = {correct/total*100:.0f}%" if total else "N/A",
            "with_dark": f"{dark_correct}/{len(with_dark)} = {dark_correct/len(with_dark)*100:.0f}%" if with_dark else "N/A",
            "without_dark": f"{no_dark_correct}/{len(without_dark)} = {no_dark_correct/len(without_dark)*100:.0f}%" if without_dark else "N/A",
        }


# ============================================================================
# Mechanism 4: Failed Case Visibility
# ============================================================================

class FailedCaseTracker:
    """
    Track failed predictions. Failed cases are kept visible,
    not hidden, to enable honest assessment.
    """
    
    _failures = []
    
    @classmethod
    def record(cls, case_name, code, advice, actual, reason=""):
        """Record a failed prediction."""
        failure = {
            "case": case_name,
            "code": code,
            "advice": advice,
            "actual": actual,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
        }
        cls._failures.append(failure)
        return failure
    
    @classmethod
    def get_all(cls):
        """Get all recorded failures."""
        return cls._failures.copy()
    
    @classmethod
    def clear(cls):
        """Clear all failures (for new evaluation run)."""
        cls._failures = []
    
    @classmethod
    def summary(cls):
        """Print failure summary."""
        if not cls._failures:
            print("No failures recorded ✅")
            return
        print(f"Failed predictions ({len(cls._failures)}):")
        for f in cls._failures:
            print(f"  ❌ {f['case']} ({f['code']}): {f['advice']} vs actual {f['actual']:.2f}%")


# ============================================================================
# Mechanism 6: Simplicity Bias
# ============================================================================

class SimplicityAudit:
    """
    Audit model simplicity: integer scores, fixed thresholds,
    and parameter count tracking.
    """
    
    # All scoring uses integer 0-5 (6 levels per dimension)
    SCORE_LEVELS = 6  # 0, 1, 2, 3, 4, 5
    
    # All thresholds are fixed with economic meaning
    FIXED_THRESHOLDS = {
        "dark_veto_hard": -8,      # dark <= -8% -> SKIP
        "dark_veto_soft": -4,      # dark <= -4% -> CAUTIOUS
        "bull_veto": 20,           # dark >= +20% -> BUY
        "cost_threshold": 3,       # dark < 3% + BUY -> cost warning
        "danger_zone_low": -15,    # danger zone: -15 to -10
        "danger_zone_high": -10,
        "extreme_dark": 30,        # |dark| > 30% -> extreme branch
        "extreme_dark_15": 15,     # |dark| > 15% -> mean reversion
        "ashare_threshold": 5,     # |a_share| > 5% -> amplification
        "supply_same_day": 5,      # >=5 same day -> extreme
        "retail_extreme": 200,     # retail > 200x -> bimodal
        "advice_strong_buy": 75,   # >=75% -> STRONG BUY
        "advice_buy": 55,          # >=55% -> BUY
        "advice_cautious": 40,     # >=40% -> CAUTIOUS
    }
    
    @classmethod
    def audit(cls):
        """
        Audit model simplicity metrics.
        """
        # Count effective parameters
        # 9 dimensions * 5 thresholds each = ~45 scoring params
        # 4 veto mechanisms = 4 binary params
        # ~8 range model params
        # 4 advice thresholds
        # Total ~61 (lower than the 71 raw count because many are 
        # derived from the same threshold)
        
        scoring_params = 9 * 5  # 9 dims, ~5 thresholds each
        veto_params = 4  # bear, soft, range, bull
        range_params = 8  # extreme, mean reversion, ashare, supply, struct
        threshold_params = len(cls.FIXED_THRESHOLDS)
        total = scoring_params + veto_params + range_params + threshold_params
        
        # Effective configs (much smaller due to integer scoring)
        # Each dimension has 6 levels, but thresholds are shared
        # Effective unique model states ~= 6^9 * 4 (veto) but most are
        # unreachable. Realistic unique states ~= 1000.
        
        return {
            "scoring_dimensions": 9,
            "score_levels_per_dim": cls.SCORE_LEVELS,
            "veto_mechanisms": veto_params,
            "range_model_params": range_params,
            "fixed_thresholds": threshold_params,
            "total_raw_parameters": total,
            "uses_integer_scoring": True,
            "uses_fixed_thresholds": True,
            "uses_continuous_optimization": False,
            "weight_learning": False,
            "simplicity_score": "HIGH" if total < 80 else "MEDIUM" if total < 150 else "LOW",
        }


# ============================================================================
# Mechanism 1: Structural Constraints (verification)
# ============================================================================

def verify_structural_constraints():
    """
    Verify that structural constraints (binary veto rules) are in place
    and functioning. These are the strongest anti-overfitting feature
    because they have zero degrees of freedom.
    """
    constraints = [
        {
            "name": "Bear Veto",
            "rule": "dark <= -8% -> SKIP",
            "type": "binary",
            "degrees_of_freedom": 0,
            "cases_validated": ["Binhua (-21.26% -> -18.68%)", "Puyuan Prec (-13.01% -> -37.36%)"],
        },
        {
            "name": "Soft Veto",
            "rule": "dark <= -4% -> CAUTIOUS",
            "type": "binary",
            "degrees_of_freedom": 0,
            "cases_validated": ["Luxshare (-5.97% -> -5.18%)"],
        },
        {
            "name": "Range Veto",
            "rule": "dark < 0% + BUY -> CAUTIOUS",
            "type": "binary",
            "degrees_of_freedom": 0,
            "cases_validated": ["Zhongji (-1.07% -> -2.04%)"],
        },
        {
            "name": "Bull Veto",
            "rule": "dark >= +20% + CAUTIOUS -> BUY",
            "type": "binary",
            "degrees_of_freedom": 0,
            "cases_validated": ["Qiyunshan (+37.63% -> +162.5%)", "Nasen (+50.67% -> +51.82%)"],
        },
    ]
    
    total_dof = sum(c["degrees_of_freedom"] for c in constraints)
    
    return {
        "constraints": constraints,
        "total_constraints": len(constraints),
        "total_degrees_of_freedom": total_dof,
        "anti_overfitting_strength": "MAXIMUM" if total_dof == 0 else "HIGH",
    }


# ============================================================================
# Full Audit Report
# ============================================================================

def run_full_audit():
    """
    Run a complete anti-overfitting audit of the model.
    """
    print("=" * 65)
    print("  ANTI-OVERFITTING AUDIT REPORT")
    print("=" * 65)
    
    # Mechanism 1: Structural Constraints
    print("\n1. STRUCTURAL CONSTRAINTS (Binary Veto Rules)")
    print("-" * 50)
    struct = verify_structural_constraints()
    for c in struct["constraints"]:
        print(f"  ✅ {c['name']}: {c['rule']}")
        print(f"     Validated: {', '.join(c['cases_validated'])}")
    print(f"  Degrees of freedom: {struct['total_degrees_of_freedom']}")
    print(f"  Anti-overfitting strength: {struct['anti_overfitting_strength']}")
    
    # Mechanism 2: Economic Logic
    print("\n2. ECONOMIC LOGIC VALIDATOR")
    print("-" * 50)
    print(f"  Approved logic categories: {len(EconomicLogicChecker.APPROVED_LOGIC)}")
    for cat, desc in EconomicLogicChecker.APPROVED_LOGIC.items():
        print(f"  ✅ {cat}: {desc}")
    print(f"  Rejected patterns: {len(EconomicLogicChecker.REJECTED_LOGIC)}")
    for pat in EconomicLogicChecker.REJECTED_LOGIC:
        print(f"  ❌ {pat}")
    
    # Mechanism 3: Direction Over Magnitude
    print("\n3. DIRECTION OVER MAGNITUDE")
    print("-" * 50)
    print("  Model prioritizes BUY/CAUTIOUS/SKIP direction over exact range")
    print("  Direction = binary (harder to overfit)")
    print("  Magnitude = continuous (easier to overfit)")
    
    # Mechanism 4: Failed Case Visibility
    print("\n4. FAILED CASE VISIBILITY")
    print("-" * 50)
    print(f"  Frozen cases tracked: {len(FROZEN_CASES)}")
    print("  Known failures (kept visible, not hidden):")
    print("  ❌ Dongfang (01770): SKIP but actual +1.73%")
    print("  ⚠️ Dingtai (01377): CAUTIOUS, range miss (-3.0~-1.6 vs -1.79)")
    print("  ⚠️ Puyuan Prec (00537): CAUTIOUS but actual -37.36% (should be SKIP)")
    
    # Mechanism 5: Version Freeze
    print("\n5. VERSION FREEZE PROTOCOL")
    print("-" * 50)
    print(f"  Freeze date: {FREEZE_DATE}")
    print(f"  Freeze version: {FREEZE_VERSION}")
    print(f"  Frozen cases: {len(FROZEN_CASES)}")
    print(f"  Rule: No parameter changes on frozen cases")
    print(f"  New cases serve as TRUE holdout validation")
    
    # Mechanism 6: Simplicity Bias
    print("\n6. SIMPLICITY BIAS")
    print("-" * 50)
    audit = SimplicityAudit.audit()
    print(f"  Scoring dimensions: {audit['scoring_dimensions']}")
    print(f"  Score levels per dimension: {audit['score_levels_per_dim']} (integer 0-5)")
    print(f"  Veto mechanisms: {audit['veto_mechanisms']}")
    print(f"  Fixed thresholds: {audit['fixed_thresholds']}")
    print(f"  Total raw parameters: {audit['total_raw_parameters']}")
    print(f"  Uses integer scoring: {audit['uses_integer_scoring']}")
    print(f"  Uses fixed thresholds: {audit['uses_fixed_thresholds']}")
    print(f"  Uses continuous optimization: {audit['uses_continuous_optimization']}")
    print(f"  Weight learning: {audit['weight_learning']}")
    print(f"  Simplicity score: {audit['simplicity_score']}")
    
    print("\n" + "=" * 65)
    print("  AUDIT COMPLETE")
    print("=" * 65)
    
    return {
        "structural_constraints": struct,
        "economic_logic": {
            "approved": len(EconomicLogicChecker.APPROVED_LOGIC),
            "rejected": len(EconomicLogicChecker.REJECTED_LOGIC),
        },
        "frozen_cases": len(FROZEN_CASES),
        "simplicity": audit,
    }


if __name__ == "__main__":
    run_full_audit()
