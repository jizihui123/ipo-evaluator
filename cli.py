#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI interface for HK IPO Evaluator.

Usage examples:
  # Evaluate with all data
  python cli.py --name "Anker" --code "00668.HK" --price 99.32 \\
    --ref-cny 100.4 --rating "AA+" --scale 56 \\
    --retail 27.57 --inst 10.24 --cornerstone \\
    --sentiment positive --ipos-week 8

  # Evaluate with minimal data
  python cli.py --name "Mystery" --code "00001.HK" --price 10.0

  # Evaluate with dark market signal
  python cli.py --name "Luxshare" --code "02475.HK" --price 63.28 \\
    --ref-cny 62.47 --rating "AA+" --scale 242 \\
    --retail 3.81 --inst 15 --cornerstone \\
    --sentiment negative --dark -4.95 --ipos-week 12

  # Output as JSON
  python cli.py --name "Anker" --code "00668.HK" --price 99.32 \\
    --rating "AA+" --scale 56 --json

  # Run backtest
  python cli.py --backtest
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hk_ipo_evaluator import eval_hk_ipo, print_result, to_json, run_backtest


def main():
    parser = argparse.ArgumentParser(
        description="HK IPO Evaluator v1.5 - 9-dimension scoring model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full evaluation
  python cli.py -n "Anker" -c "00668.HK" -p 99.32 --ref-cny 100.4 \\
    --rating "AA+" --scale 56 --retail 27.57 --inst 10.24 \\
    --cornerstone --sentiment positive --ipos-week 8

  # With dark market signal
  python cli.py -n "Luxshare" -c "02475.HK" -p 63.32 --ref-cny 62.47 \\
    --rating "AA+" --scale 242 --retail 3.81 --inst 15 \\
    --cornerstone --sentiment negative --dark -4.95 --ipos-week 12

  # JSON output
  python cli.py -n "Test" -c "00001.HK" -p 10.0 --json

  # Run backtest suite
  python cli.py --backtest
        """,
    )

    parser.add_argument("--backtest", action="store_true",
                        help="Run backtest suite (N=10)")

    parser.add_argument("-n", "--name", type=str, help="Company name")
    parser.add_argument("-c", "--code", type=str, help="Stock code (e.g. 00668.HK)")
    parser.add_argument("-p", "--price", type=float, help="IPO offer price in HKD")

    parser.add_argument("--ref-cny", type=float, default=None,
                        help="A-share reference price in CNY")
    parser.add_argument("--fx-rate", type=float, default=1.152,
                        help="CNY to HKD conversion rate (default: 1.152)")
    parser.add_argument("--rating", type=str, default="",
                        help="Credit rating: AAA, AA+, AA, A+, A")
    parser.add_argument("--scale", type=float, default=0,
                        help="IPO size in hundred-million HKD (yi)")

    parser.add_argument("--retail", type=float, default=None,
                        help="Retail oversubscription ratio")
    parser.add_argument("--inst", type=float, default=None,
                        help="Institutional oversubscription ratio")
    parser.add_argument("--cornerstone", action="store_true", default=None,
                        help="Has cornerstone investors")
    parser.add_argument("--no-cornerstone", action="store_false",
                        dest="cornerstone", help="No cornerstone investors")

    parser.add_argument("--market-env", type=str, default="normal",
                        choices=["bull", "normal", "bear"],
                        help="Market environment (default: normal)")
    parser.add_argument("--sentiment", type=str, default="neutral",
                        choices=["positive", "neutral", "negative", "crash"],
                        help="Market sentiment (default: neutral)")

    parser.add_argument("--dark", type=float, default=None,
                        help="Dark market return in percent (e.g. -4.95)")
    parser.add_argument("--ipos-week", type=int, default=1,
                        help="Number of IPOs listing same week (default: 1)")
    parser.add_argument("--ipos-day", type=int, default=1,
                        help="Number of IPOs listing same DAY (default: 1)")
    parser.add_argument("--market-temp", type=float, default=None,
                        help="Recent IPO first-day break rate 0-1 (e.g. 0.40 = 40% break rate)")
    parser.add_argument("--a-share", type=float, default=None,
                        help="A-share real-time change %% (for A+H listings, amplification effect)")
    parser.add_argument("--cost-threshold", type=float, default=3.0,
                        help="Trading cost threshold %% for cost warning (default: 3.0)")

    parser.add_argument("--json", action="store_true",
                        help="Output as JSON instead of text")

    args = parser.parse_args()

    if args.backtest:
        run_backtest()
        return

    if not args.name or not args.code or not args.price:
        parser.error("--name, --code, and --price are required (or use --backtest)")

    result = eval_hk_ipo(
        name=args.name,
        code=args.code,
        ipo_price_hkd=args.price,
        ref_price_cny=args.ref_cny,
        fx_rate=args.fx_rate,
        rating=args.rating,
        scale_hk_yi=args.scale,
        retail_oversub=args.retail,
        inst_oversub=args.inst,
        cornerstone=args.cornerstone,
        market_env=args.market_env,
        sentiment=args.sentiment,
        dark_signal=args.dark,
        ipos_same_week=args.ipos_week,
        ipos_same_day=args.ipos_day,
        cost_threshold_pct=args.cost_threshold,
        market_temp=args.market_temp,
        a_share_change=args.a_share,
    )

    if args.json:
        print(to_json(result))
    else:
        print_result(result)


if __name__ == "__main__":
    main()
