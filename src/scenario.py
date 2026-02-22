# src/scenario.py
#user inputs

from __future__ import annotations
from dataclasses import dataclass

from . import config


@dataclass(frozen=True)
class Scenario:
    """
    Scenario = user-controlled inputs (sliders/radios) for a simulation run.

    Keep model coefficients/assumptions in config.py.
    Keep one run's inputs here, with validation so the UI can't break the model.
    """

    # ---- simulation controls ----
    seed: int = 123
    replications: int = getattr(config, "REPS_DEFAULT", 10_000)

    # ---- user inputs (game context) ----
    stadium_capacity: int = config.STADIUM_CAPACITY
    temp_f: float = config.TEMP_IDEAL_F

    # ---- economics (newsvendor) ----
    price: float = getattr(config, "P_DEFAULT", 6.00)
    cost: float = getattr(config, "C_DEFAULT", 1.50)
    salvage: float = getattr(config, "S_DEFAULT", 0.25)
    fixed_cost_per_game: float = getattr(config, "FIXED_COST_PER_GAME", 0.0)

    team_wins: int = 9
    team_losses: int = 8
    opp_wins: int = 9
    opp_losses: int = 8

    indoor: bool = False
    rain: bool = False
    snow: bool = False
    promo: bool = False
    playoff: bool = False

    def validate(self) -> None:
        # -------------------------
        # Simulation controls
        # -------------------------
        reps_min = getattr(config, "REPS_MIN", None)
        reps_max = getattr(config, "REPS_MAX", None)

        if reps_min is not None and reps_max is not None:
            if not (reps_min <= self.replications <= reps_max):
                raise ValueError(
                    f"replications must be between {reps_min} and {reps_max}"
                )
        else:
            if self.replications <= 0:
                raise ValueError("replications must be > 0")
        # seed can be any int; no strict constraint needed

        # -------------------------
        # Capacity
        # -------------------------
        cap_min = getattr(config, "CAPACITY_MIN", None)
        cap_max = getattr(config, "CAPACITY_MAX", None)

        if cap_min is not None and cap_max is not None:
            if not (cap_min <= self.stadium_capacity <= cap_max):
                raise ValueError(
                    f"stadium_capacity must be between {cap_min} and {cap_max}"
                )
        elif self.stadium_capacity <= 0:
            raise ValueError("stadium_capacity must be > 0")

        # -------------------------
        # Temperature
        # -------------------------
        temp_min = getattr(config, "TEMP_MIN_F", None)
        temp_max = getattr(config, "TEMP_MAX_F", None)

        if temp_min is not None and temp_max is not None:
            if not (temp_min <= self.temp_f <= temp_max):
                raise ValueError(f"temp_f must be between {temp_min} and {temp_max}")

        # -------------------------
        # Economics (newsvendor)
        # -------------------------
        p_min, p_max = getattr(config, "P_MIN", None), getattr(config, "P_MAX", None)
        c_min, c_max = getattr(config, "C_MIN", None), getattr(config, "C_MAX", None)
        s_min, s_max = getattr(config, "S_MIN", None), getattr(config, "S_MAX", None)

        if p_min is not None and p_max is not None:
            if not (p_min <= self.price <= p_max):
                raise ValueError(f"price must be between {p_min} and {p_max}")
        else:
            if self.price <= 0:
                raise ValueError("price must be > 0")

        if c_min is not None and c_max is not None:
            if not (c_min <= self.cost <= c_max):
                raise ValueError(f"cost must be between {c_min} and {c_max}")
        else:
            if self.cost < 0:
                raise ValueError("cost must be >= 0")

        if s_min is not None and s_max is not None:
            if not (s_min <= self.salvage <= s_max):
                raise ValueError(f"salvage must be between {s_min} and {s_max}")
        else:
            if self.salvage < 0:
                raise ValueError("salvage must be >= 0")

        # sanity relationships
        if self.salvage > self.cost:
            raise ValueError("salvage cannot exceed cost (would create weird incentives).")

        if self.price <= self.cost:
            # don't hard fail if you want, but it's usually a mistake
            raise ValueError("price should be greater than cost (otherwise margin <= 0).")

        if self.fixed_cost_per_game < 0:
            raise ValueError("fixed_cost_per_game must be >= 0")

        # -------------------------
        # Records (wins/losses)
        # -------------------------
        season_games = getattr(config, "SEASON_GAMES", 20)

        for name, w, l in [
            ("team", self.team_wins, self.team_losses),
            ("opp", self.opp_wins, self.opp_losses),
        ]:
            if w < 0 or l < 0:
                raise ValueError(f"{name} wins/losses must be >= 0")
            if w > season_games or l > season_games:
                raise ValueError(f"{name} wins/losses must be <= {season_games}")
            if w + l > season_games:
                raise ValueError(f"{name} wins+losses cannot exceed {season_games}")

        # -------------------------
        # Weather sanity
        # -------------------------
        if self.rain and self.snow:
            raise ValueError("rain and snow cannot both be True (pick one).")
        # Indoor overrides weather
        if self.indoor and (self.rain or self.snow):
            raise ValueError("Indoor stadium cannot have rain or snow.")

    @property
    def team_win_pct(self) -> float:
        games = self.team_wins + self.team_losses
        return self.team_wins / games if games > 0 else 0.5

    @property
    def opp_win_pct(self) -> float:
        games = self.opp_wins + self.opp_losses
        return self.opp_wins / games if games > 0 else 0.5