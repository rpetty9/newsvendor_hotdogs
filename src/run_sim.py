# src/run_sim.py

from __future__ import annotations

import argparse
import random
from statistics import mean, pstdev
from typing import Iterable

from . import game, config
from .scenario import Scenario


def simulate_many(
    Q: int,
    sc: Scenario,
    n: int | None = None,
    seed: int | None = None,
    return_traces: bool = False,
) -> dict:
    """
    Run N simulated games for a single order quantity Q under a Scenario.

    - n defaults to sc.replications
    - seed defaults to sc.seed
    - return_traces=True includes per-game series for plotting, including epsilon
    """
    sc.validate()

    n = sc.replications if n is None else n
    seed = sc.seed if seed is None else seed

    if n <= 0:
        raise ValueError("n/replications must be > 0")
    if Q < 0:
        raise ValueError("Q must be >= 0")

    rng = random.Random(seed)

    profits = []
    demands = []
    solds = []
    leftovers = []
    attendances = []
    epsilons = []
    stockouts = 0

    for _ in range(n):
        D, a, eps = game.sample_demand(rng, sc)  # <-- sample_demand must return eps now
        res = game.profit_for_game(Q, D, a, sc)

        profits.append(res.profit)
        demands.append(res.D)
        solds.append(res.sold)
        leftovers.append(res.leftover)
        attendances.append(res.attendance)
        epsilons.append(eps)

        if res.D > Q:
            stockouts += 1

    out = {
        "Q": Q,
        "n games": n,
        "seed": seed,
        "avg_profit": mean(profits),
        "sd_profit": pstdev(profits),
        "min_profit": min(profits),
        "max_profit": max(profits),
        "avg_attendance": mean(attendances),
        "avg_demand": mean(demands),
        "avg_sold": mean(solds),
        "avg_leftover": mean(leftovers),
        "stockout_rate": stockouts / n,
    }

    out.update({
    "price": sc.price,
    "cost": sc.cost,
    "salvage": sc.salvage,
    "fixed_cost_per_game": getattr(sc, "fixed_cost_per_game", getattr(config, "FIXED_COST_PER_GAME", 0.0)),
    })

    if return_traces:
        out["traces"] = {
            "profit": profits,
            "demand": demands,
            "attendance": attendances,
            "eps": epsilons,
        }

    return out


def evaluate_grid(
    Q_values: Iterable[int],
    sc: Scenario,
    n: int | None = None,
    seed: int | None = None,
) -> list[dict]:
    """
    Evaluate multiple Q values under the same Scenario.

    Note: using the SAME seed for each Q gives 'common random numbers' (fair comparisons).
    """
    return [simulate_many(Q=Q, sc=sc, n=n, seed=seed) for Q in Q_values]


def print_summary(summary: dict) -> None:
    print("\n=== Monte Carlo Summary ===")
    print(f"Q:              {summary['Q']}")
    print(f"n games:        {summary['n games']}")
    print(f"seed:           {summary['seed']}")
    print("----------------------------")
    print(f"avg_profit:     {summary['avg_profit']:.2f}")
    print(f"sd_profit:      {summary['sd_profit']:.2f}")
    print(f"min_profit:     {summary['min_profit']:.2f}")
    print(f"max_profit:     {summary['max_profit']:.2f}")
    print("----------------------------")
    print(f"avg_attendance: {summary['avg_attendance']:.1f}")
    print(f"avg_demand:     {summary['avg_demand']:.1f}")
    print(f"avg_sold:       {summary['avg_sold']:.1f}")
    print(f"avg_leftover:   {summary['avg_leftover']:.1f}")
    print(f"stockout_rate:  {summary['stockout_rate']:.3f}")
    print()


def build_scenario_from_args(args: argparse.Namespace) -> Scenario:
    """
    Create Scenario from CLI args, falling back to Scenario defaults where not provided.
    """
    base = Scenario()

    return Scenario(
        seed=base.seed if args.seed is None else args.seed,
        replications=base.replications if args.n is None else args.n,

        stadium_capacity=base.stadium_capacity if args.capacity is None else args.capacity,
        temp_f=base.temp_f if args.temp is None else args.temp,

        team_wins=base.team_wins if args.team_wins is None else args.team_wins,
        team_losses=base.team_losses if args.team_losses is None else args.team_losses,

        opp_wins=base.opp_wins if args.opp_wins is None else args.opp_wins,
        opp_losses=base.opp_losses if args.opp_losses is None else args.opp_losses,

        rain=args.rain,
        snow=args.snow,
        promo=args.promo,
        playoff=args.playoff,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run hot dog Monte Carlo simulation.")

    # Decision variable
    parser.add_argument("--Q", type=int, default=20000, help="Order quantity (hot dogs).")

    # Scenario / simulation controls
    parser.add_argument("--seed", type=int, default=None, help="Random seed.")
    parser.add_argument("--n", type=int, default=None, help="Number of replications (simulated games).")

    parser.add_argument("--capacity", type=int, default=None, help="Stadium capacity.")
    parser.add_argument("--temp", type=float, default=None, help="Temperature (°F).")

    parser.add_argument("--team_wins", type=int, default=None)
    parser.add_argument("--team_losses", type=int, default=None)
    parser.add_argument("--opp_wins", type=int, default=None)
    parser.add_argument("--opp_losses", type=int, default=None)

    # Flags (store_true makes them boolean toggles)
    parser.add_argument("--rain", action="store_true", help="Enable rain.")
    parser.add_argument("--snow", action="store_true", help="Enable snow.")
    parser.add_argument("--promo", action="store_true", help="Enable promotion.")
    parser.add_argument("--playoff", action="store_true", help="Enable playoff game.")

    # Grid
    parser.add_argument("--grid", action="store_true", help="Evaluate a grid of Q values.")
    parser.add_argument("--Qmin", type=int, default=15000, help="Grid: minimum Q.")
    parser.add_argument("--Qmax", type=int, default=30000, help="Grid: maximum Q (inclusive).")
    parser.add_argument("--step", type=int, default=500, help="Grid: step size.")

    # Optional refinement
    parser.add_argument("--refine", action="store_true", help="Refine around best Q from coarse grid.")
    parser.add_argument("--refine_width", type=int, default=2000, help="Refine: half-width around best Q.")
    parser.add_argument("--refine_step", type=int, default=100, help="Refine: step size.")

    args = parser.parse_args()

    sc = build_scenario_from_args(args)
    sc.validate()

    # Single-Q mode
    if not args.grid:
        summary = simulate_many(Q=args.Q, sc=sc)
        print_summary(summary)
        return

    # Grid mode validation
    if args.step <= 0:
        raise ValueError("--step must be > 0")
    if args.Qmax < args.Qmin:
        raise ValueError("--Qmax must be >= --Qmin")

    Q_values = list(range(args.Qmin, args.Qmax + 1, args.step))
    results = evaluate_grid(Q_values, sc=sc)

    best = max(results, key=lambda r: r["avg_profit"])

    print("\n=== Grid Search Results (top 10 by avg_profit) ===")
    top10 = sorted(results, key=lambda r: r["avg_profit"], reverse=True)[:10]
    for r in top10:
        print(
            f"Q={r['Q']:>6} | avg_profit={r['avg_profit']:>10.2f} | "
            f"stockout_rate={r['stockout_rate']:.3f} | avg_leftover={r['avg_leftover']:.1f}"
        )

    print("\n=== Best Q by avg_profit (coarse grid) ===")
    print_summary(best)

    if args.refine:
        if args.refine_width < 0:
            raise ValueError("--refine_width must be >= 0")
        if args.refine_step <= 0:
            raise ValueError("--refine_step must be > 0")

        q_center = best["Q"]
        q_lo = max(args.Qmin, q_center - args.refine_width)
        q_hi = min(args.Qmax, q_center + args.refine_width)

        refined_Qs = list(range(q_lo, q_hi + 1, args.refine_step))
        refined_results = evaluate_grid(refined_Qs, sc=sc)
        best_refined = max(refined_results, key=lambda r: r["avg_profit"])

        print(f"\n=== Refined Search (best±{args.refine_width} by {args.refine_step}) ===")
        print_summary(best_refined)


if __name__ == "__main__":
    main()