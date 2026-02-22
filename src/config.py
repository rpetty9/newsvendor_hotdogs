# src/config.py
# control panel, handles all the input, their distributions, and parameters

# =========================
# Model Parameters
# =========================

# Baseline hot dog consumption rate per attendee (r)
R_BASE = 0.30

# -------------------------
# Attendance statistical parameters
# -------------------------
BASE_FILL_RATE = 0.86   # typical % of seats filled (regular game)
A_STD_FRAC = 0.12       # std dev as % of mean
MIN_STD = 2000          # avoid tiny std for small stadiums

# -------------------------
# Noise factor (epsilon)
# -------------------------
# EPS_SIGMA is the log-space standard deviation (sigma_ln) for lognormal epsilon.
EPS_SIGMA = 0.10


# =========================
# Economic Parameters (Newsvendor)
# =========================
P_DEFAULT = 6.00
C_DEFAULT = 1.50
S_DEFAULT = 0.25

P_MIN, P_MAX = 0.01, 50.0
C_MIN, C_MAX = 0.00, 50.0
S_MIN, S_MAX = 0.00, 50.0

FIXED_COST_PER_GAME = 0.0


# =========================
# Attendance drivers (multipliers)
# =========================

PROMO_BOOST = 1.03        # +3%
PLAYOFF_BOOST = 1.20      # +20%

TEMP_IDEAL_F = 65
TEMP_PENALTY_PER_10F = 0.02   # 2% penalty per 10°F away from ideal

RAIN_PENALTY = 0.90
SNOW_PENALTY = 0.95

TEAM_WIN_BOOST_AT_1 = 1.10
OPPONENT_WIN_BOOST_AT_1 = 1.05


# =========================
# UI input ranges (for sliders/radios)
# =========================

CAPACITY_MIN = 25_000
CAPACITY_MAX = 100_000
CAPACITY_STEP = 500
CAPACITY_DEFAULT = 60_000

TEMP_MIN_F = 0
TEMP_MAX_F = 100
TEMP_DEFAULT_F = TEMP_IDEAL_F

WINS_MIN = 0
LOSSES_MIN = 0
SEASON_GAMES = 20
WINS_MAX = SEASON_GAMES
LOSSES_MAX = SEASON_GAMES


# =========================
# Simulation limits (UI + safety)
# =========================

REPS_MIN = 100
REPS_MAX = 100_000
REPS_DEFAULT = 10_000
REPS_STEP = 500


# =========================
# Defaults (used by Scenario)
# =========================

STADIUM_CAPACITY = CAPACITY_DEFAULT


# ============================
# Q (order quantity) limits
# ============================

Q_MIN = 0
Q_MAX = 100_000
MAX_GRID_POINTS = 500