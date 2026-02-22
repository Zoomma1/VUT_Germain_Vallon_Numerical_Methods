from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from solvers import ALL_SOLVERS
from comparison import ALL_SCIPY_SOLVERS
from problems import ALL_PROBLEMS
from utils import (
    absolute_error,
    relative_error_percent,
    format_table,
    format_float,
)


DEFAULT_STEP_SIZES = [0.5, 0.25, 0.1]
SCIPY_METHODS_TO_COMPARE = ["SciPy RK45", "SciPy DOP853", "SciPy Radau"]


def run_benchmark(
    problems_indices: list[int] | None = None,
    step_sizes: list[float] | None = None,
    verbose: bool = True,
) -> dict:
    if step_sizes is None:
        step_sizes = DEFAULT_STEP_SIZES
    problems = (
        [ALL_PROBLEMS[i] for i in problems_indices]
        if problems_indices
        else ALL_PROBLEMS
    )
    all_solvers = ALL_SOLVERS + ALL_SCIPY_SOLVERS

    results: dict = {}

    for ivp in problems:
        if verbose:
            print(f"\n{'='*72}")
            print(f"Problem: {ivp.name}")
            print(f"  {ivp.description}")
            print(f"  x ∈ [{ivp.x0}, {ivp.x_end}],  y({ivp.x0}) = {ivp.y0}")
            if ivp.exact is not None:
                print(f"  Exact at x_end: {format_float(ivp.exact(ivp.x_end))}")
            print()

        results[ivp.name] = {}

        for h in step_sizes:
            results[ivp.name][h] = {}

            headers = ["Method", "y_final", "|error|", "rel err (%)"]
            rows = []

            exact_y = ivp.exact_at(ivp.x_end)

            for solver in all_solvers:
                try:
                    result = solver.solve(
                        ivp.f, ivp.x0, ivp.y0, ivp.x_end, h
                    )
                    y_final = result.final_value()
                    results[ivp.name][h][solver.name] = result

                    if exact_y is not None:
                        abs_err = absolute_error(y_final, exact_y)
                        rel_err = relative_error_percent(y_final, exact_y)
                        rows.append([
                            solver.name,
                            format_float(y_final),
                            format_float(abs_err),
                            f"{rel_err:.4f}",
                        ])
                    else:
                        rows.append([
                            solver.name,
                            format_float(y_final),
                            "N/A",
                            "N/A",
                        ])

                except Exception as exc:
                    results[ivp.name][h][solver.name] = None
                    rows.append([solver.name, "ERROR", str(exc)[:40], ""])

            if verbose:
                print(f"  Step size h = {h}")
                print(format_table(headers, rows, col_widths=[28, 14, 14, 12]))
                print()

    return results


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--step", nargs="+", type=float, default=DEFAULT_STEP_SIZES,
        metavar="H", help="Step size(s) to use (default: 0.5 0.25 0.1)"
    )
    parser.add_argument(
        "--problem", nargs="+", type=int, default=None,
        metavar="IDX", help="Problem indices to run (default: all)"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available problems and exit"
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if args.list:
        print("\nAvailable problems:")
        print(format_table(
            ["Index", "Name", "x_end", "Has exact?"],
            [
                [i, ivp.name, ivp.x_end, "Yes" if ivp.exact else "No"]
                for i, ivp in enumerate(ALL_PROBLEMS)
            ],
            col_widths=[5, 35, 6, 10],
        ))
        return

    print("Solver Comparison")
    print("Implemented methods: " + ", ".join(s.name for s in ALL_SOLVERS))
    print("SciPy references:    " + ", ".join(s.name for s in ALL_SCIPY_SOLVERS))

    run_benchmark(
        problems_indices=args.problem,
        step_sizes=args.step,
        verbose=True,
    )

if __name__ == "__main__":
    main()
