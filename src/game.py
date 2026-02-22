# src/game.py

from __future__ import annotations

from dataclasses import dataclass
import random

from . import config
from .scenario import Scenario


@dataclass(frozen=True)
class GameResult:
    """Outputs from a single simulated game."""
    Q: int
    D: int
    sold: int
    leftover: int
    revenue: float
    cost: float
    salvage: float
    profit: float
    attendance: int


# =========================
# Helpers
# =========================

def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(x, hi))


def _win_pct_multiplier(win_pct: float, boost_at_1: float, min_mult: float = 0.80) -> float:
    """
    Centered scaling around 0.500 so bad teams can reduce attendance, good teams increase it.

    - win_pct = 1.0 -> multiplier = boost_at_1
    - win_pct = 0.5 -> multiplier = 1.0
    - win_pct = 0.0 -> multiplier = 2 - boost_at_1  (then clamped by min_mult)

    This matches intuition better than always-positive effects.
    """
    slope = boost_at_1 - 1.0
    m = 1.0 + (win_pct - 0.5) * 2.0 * slope
    return max(min_mult, m)


def attendance_multiplier(sc: Scenario) -> float:
    """
    Multiplicative attendance effects from the scenario (promo/playoff/weather/records).
    """
    m = 1.0

    if sc.promo:
        m *= config.PROMO_BOOST
    if sc.playoff:
        m *= config.PLAYOFF_BOOST

    # Precipitation: if you later want separate snow penalty, add SNOW_PENALTY to config
    # Weather effects (ignored if indoor)
    if not sc.indoor:

        # Precipitation
        if sc.rain:
            m *= config.RAIN_PENALTY
        if sc.snow:
            m *= getattr(config, "SNOW_PENALTY", config.RAIN_PENALTY)

        # Temperature discomfort penalty
        dist = abs(sc.temp_f - config.TEMP_IDEAL_F)
        tens = dist / 10.0
        temp_mult = 1.0 - config.TEMP_PENALTY_PER_10F * tens
        temp_mult = max(0.70, temp_mult)
        m *= temp_mult

        # Team + opponent performance (wins/losses -> win_pct computed in Scenario)
        m *= _win_pct_multiplier(sc.team_win_pct, config.TEAM_WIN_BOOST_AT_1)
        m *= _win_pct_multiplier(sc.opp_win_pct, config.OPPONENT_WIN_BOOST_AT_1, min_mult=0.90)

    return m


# =========================
# Random draws
# =========================

def sample_epsilon(rng: random.Random) -> float:
    """
    Multiplicative noise factor epsilon with mean ~ 1.0.
    lognormal with sigma in log-space (EPS_SIGMA).
    """
    sigma = config.EPS_SIGMA
    mu = -0.5 * sigma * sigma  # so E[epsilon] ≈ 1
    return rng.lognormvariate(mu, sigma)


def sample_attendance(rng: random.Random, sc: Scenario) -> int:
    """
    Attendance model:
      1) baseline mean = capacity * BASE_FILL_RATE
      2) baseline sigma = max(MIN_STD, mean * A_STD_FRAC)
      3) adjust mean by attendance_multiplier(scenario)
      4) sample Normal(mean_adj, sigma)
      5) clamp to [0, capacity]
    """
    sc.validate()

    cap = float(sc.stadium_capacity)

    mu0 = cap * config.BASE_FILL_RATE
    sigma0 = max(float(config.MIN_STD), mu0 * config.A_STD_FRAC)

    mu = mu0 * attendance_multiplier(sc)

    a = rng.gauss(mu, sigma0)
    a = _clip(a, 0.0, cap)

    return int(round(a))


def sample_demand(rng: random.Random, sc: Scenario) -> tuple[int, int, float]:
    """
    Demand model:
      D = round( attendance * R_BASE * epsilon )

    Returns (D, attendance) so downstream reporting can include attendance.
    """
    a = sample_attendance(rng, sc)
    eps = sample_epsilon(rng)

    d = a * config.R_BASE * eps
    d = max(0.0, d)
    return int(round(d)), a, eps


# =========================
# Profit Function
# =========================

def profit_for_game(Q: int, D: int, attendance: int, sc: Scenario) -> GameResult:
    """
    Newsvendor profit:
      profit = p*min(Q,D) - c*Q + s*max(Q-D, 0) - fixed_cost
    """
    if Q < 0:
        raise ValueError("Q must be >= 0")
    if D < 0:
        raise ValueError("D must be >= 0")

    sold = min(Q, D)
    leftover = max(Q - D, 0)

    p = float(sc.price)
    c = float(sc.cost)
    s = float(sc.salvage)
    fixed = float(getattr(sc, "fixed_cost_per_game", getattr(config, "FIXED_COST_PER_GAME", 0.0)))

    revenue = p * sold
    cost = c * Q
    salvage = s * leftover
    profit = revenue - cost + salvage - fixed

    return GameResult(
        Q=Q, D=D, sold=sold, leftover=leftover,
        revenue=revenue, cost=cost, salvage=salvage, profit=profit,
        attendance=attendance,
    )


def simulate_one_game(Q: int, sc: Scenario, seed: int | None = None) -> GameResult:
    """
    Convenience wrapper: simulate one game under a scenario and compute profit.
    If seed is provided, it overrides sc.seed for this single call.
    """
    rng = random.Random(sc.seed if seed is None else seed)
    D, a, _ = sample_demand(rng, sc)
    return profit_for_game(Q, D, a, sc)


if __name__ == "__main__":
    # Quick smoke test (uses Scenario defaults)
    sc = Scenario()
    res = simulate_one_game(Q=20000, sc=sc, seed=42)
    print(res)