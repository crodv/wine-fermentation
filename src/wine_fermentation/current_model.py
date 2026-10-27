"""Exact current seven-state equations, copied for migration checks only.

No calibration, new constraints, state removals or gas simplifications are applied.
Functions and constants were extracted statically from the recorded source revision.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import math
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

FULL15 = (
    "mu0",
    "sN",
    "qN",
    "qXG",
    "qXF",
    "betaG0",
    "sG",
    "betaF0",
    "sF",
    "qEG",
    "qEF",
    "iG",
    "iE",
    "Kd0",
    "m0",
)


GLYCEROL_PARAMETERS = ("gammaG0", "gammaF0")


FULL17 = FULL15 + GLYCEROL_PARAMETERS


REDUCED11 = ("mu0", "qN", "betaG0", "betaF0", "qEG", "qEF", "iG", "iE", "Kd0", "gammaG0", "gammaF0")


STATE_NAMES = ("X", "Xd", "N", "G", "F", "E", "Gly")


INPUT_CHANNELS = ("N", "G", "F", "E", "X")


DEFAULT_THETA = {
    "mu0": 0.18,
    "sN": 18.0,
    "qN": 0.18 / 19.69,
    "qXG": 0.18 / 1.60,
    "qXF": 0.18 / 1.60,
    "betaG0": 0.225,
    "sG": 0.225 / 7.5,
    "betaF0": 0.225,
    "sF": 0.225 / 7.5,
    "qEG": 0.225 / 0.49,
    "qEF": 0.225 / 0.49,
    "iG": 0.02,
    "iE": 1.0 / 40.0,
    "Kd0": 0.00044,
    "m0": 0.01,
    "gammaG0": 0.024,
    "gammaF0": 0.024,
}


FIXED_CONSTANTS = {
    "Cde": 0.0415,
    "Etd": 130000.0,
    "R": 8.314,
    "Eac": 59453.0,
    "Eafe": 11000.0,
    "EaKn": 46055.0,
    "EaKg": 46055.0,
    "EaKf": 46055.0,
    "EaKig": 46055.0,
    "EaKie": 46055.0,
    "Eam": 37681.0,
}


MEASUREMENT_ERROR_FLOOR = {
    "X": 0.06,
    "Xd": 0.06,
    "N": 0.012,
    "G": 2.5,
    "F": 2.5,
    "E": 2.0,
    "Gly": 0.35,
}


MEASUREMENT_ERROR_REL = {
    "X": 0.08,
    "Xd": 0.12,
    "N": 0.08,
    "G": 0.025,
    "F": 0.025,
    "E": 0.025,
    "Gly": 0.05,
}


STATE_COLUMNS = {
    "X": "X_viable_kg_m3",
    "Xd": "X_dead_kg_m3",
    "N": "N_kg_m3",
    "G": "G_g_l",
    "F": "F_g_l",
    "E": "E_g_l",
    "Gly": "glycerol_g_l",
}


STATE_BOUNDS = {
    "X": (0.0, 20.0),
    "Xd": (0.0, 30.0),
    "N": (0.0, 5.0),
    "G": (0.0, 350.0),
    "F": (0.0, 350.0),
    "E": (0.0, 220.0),
    "Gly": (0.0, 30.0),
}


MAINTENANCE_SUGAR_CUTOFF_KG_M3 = 1.0


@dataclass(frozen=True)
class BatchData:
    medium: str
    batch: str
    time: np.ndarray
    temperature_c: np.ndarray
    pulses: dict[str, tuple[tuple[float, float], ...]]
    observations: dict[str, np.ndarray]
    initials: dict[str, float]

    @property
    def label(self) -> str:
        return f"{self.medium}/{self.batch}"


@dataclass(frozen=True)
class FutureDesign:
    name: str
    family: str
    medium: str
    horizon_h: float
    initials: dict[str, float]
    temperature_segments: tuple[float, ...]
    pulses: dict[str, tuple[tuple[float, float], ...]]
    rationale: str


def _first_finite(values: Iterable[float], default: float) -> float:
    arr = pd.to_numeric(pd.Series(list(values)), errors="coerce").dropna()
    if arr.empty:
        return float(default)
    return float(arr.iloc[0])


def _initials_from_group(group: pd.DataFrame) -> dict[str, float]:
    g0 = _first_finite(group["G_g_l"], 80.0)
    f0 = _first_finite(group["F_g_l"], 80.0)
    return {
        "X": _first_finite(group["X_viable_kg_m3"], 0.45),
        "Xd": _first_finite(group["X_dead_kg_m3"], 0.0),
        "N": _first_finite(group["N_kg_m3"], 0.18),
        "G": g0,
        "F": f0,
        "E": _first_finite(group["E_g_l"], 0.0),
        "Gly": _first_finite(group["glycerol_g_l"], 0.0),
    }


def make_batches(data: pd.DataFrame) -> list[BatchData]:
    batches: list[BatchData] = []
    for (medium, batch), group in data.groupby(["medium", "batch"], sort=True):
        group = group.sort_values("time_h").drop_duplicates("time_h").reset_index(drop=True)
        time = group["time_h"].to_numpy(dtype=float)
        if len(time) < 3 or not np.all(np.diff(time) > 0.0):
            continue
        temperature = group["temperature_c"].interpolate(limit_direction="both").fillna(18.0).to_numpy(dtype=float)
        pulse_rows = group[["time_h", "N_pulse_kg_m3"]].dropna()
        pulses = {
            "N": tuple((float(row.time_h), float(row.N_pulse_kg_m3)) for row in pulse_rows.itertuples() if float(row.N_pulse_kg_m3) > 0.0),
            "G": tuple(),
            "F": tuple(),
            "E": tuple(),
            "X": tuple(),
        }
        observations = {}
        for state, col in STATE_COLUMNS.items():
            values = group[col].to_numpy(dtype=float)
            if state in STATE_BOUNDS:
                lb, _ub = STATE_BOUNDS[state]
                values = np.where(np.isfinite(values), np.maximum(values, lb), values)
            observations[state] = values
        batches.append(
            BatchData(
                medium=str(medium),
                batch=str(batch),
                time=time,
                temperature_c=temperature,
                pulses=pulses,
                observations=observations,
                initials=_initials_from_group(group),
            )
        )
    return batches


def temperature_at(batch: BatchData | FutureDesign, t: float) -> float:
    if isinstance(batch, BatchData):
        return float(np.interp(float(t), batch.time, batch.temperature_c))
    edges = np.linspace(0.0, float(batch.horizon_h), len(batch.temperature_segments) + 1)
    idx = int(np.searchsorted(edges[1:-1], float(t), side="right"))
    return float(batch.temperature_segments[min(max(idx, 0), len(batch.temperature_segments) - 1)])


def kinetic_terms(theta: dict[str, float], temperature_c: float, x: float, n: float, g: float, f: float, e: float) -> dict[str, float]:
    x = max(float(x), 0.0)
    n = max(float(n), 0.0)
    g = max(float(g), 0.0)
    f = max(float(f), 0.0)
    e = max(float(e), 0.0)
    temp_k = float(temperature_c) + 273.15
    constants = FIXED_CONSTANTS
    eps = 1e-8
    r = constants["R"]
    a_mu = math.exp(constants["Eac"] * (temp_k - 300.0) / (300.0 * r * temp_k))
    a_beta = math.exp(constants["Eafe"] * (temp_k - 296.15) / (296.15 * r * temp_k))
    a_kn = math.exp(constants["EaKn"] * (temp_k - 293.15) / (293.15 * r * temp_k))
    a_kg = math.exp(constants["EaKg"] * (temp_k - 293.15) / (293.15 * r * temp_k))
    a_kf = math.exp(constants["EaKf"] * (temp_k - 293.15) / (293.15 * r * temp_k))
    a_kig = math.exp(constants["EaKig"] * (temp_k - 293.15) / (293.15 * r * temp_k))
    a_kie = math.exp(constants["EaKie"] * (temp_k - 293.15) / (293.15 * r * temp_k))
    kn = (theta["mu0"] / theta["sN"]) * a_kn
    kg = (theta["betaG0"] / theta["sG"]) * a_kg
    kf = (theta["betaF0"] / theta["sF"]) * a_kf
    i_g = theta["iG"] / (a_kig + eps)
    i_e = theta["iE"] / (a_kie + eps)
    n_lim = n / (n + kn + eps)
    g_lim = g / (g + kg + eps)
    f_lim = f / (f + kf + eps)
    e_inhib = 1.0 / (1.0 + i_e * e)
    g_inhib_for_f = 1.0 / (1.0 + i_g * g)
    growth_factor = a_mu * n_lim
    glucose_ferm_factor = a_beta * g_lim * e_inhib
    fructose_ferm_factor = a_beta * f_lim * g_inhib_for_f * e_inhib
    mu = theta["mu0"] * growth_factor
    beta_g = theta["betaG0"] * glucose_ferm_factor
    beta_f = theta["betaF0"] * fructose_ferm_factor
    maintenance = theta["m0"] * math.exp(constants["Eam"] * (temp_k - 293.3) / (293.3 * r * temp_k))
    td = -0.0001 * e**3 + 0.0049 * e**2 - 0.1279 * e + 315.89
    if temp_k >= td:
        kd = theta["Kd0"] * math.exp(
            (constants["Cde"] * e) + (constants["Etd"] * (temp_k - 305.65)) / (305.65 * r * temp_k)
        )
    else:
        kd = 0.0
    sugar_total = g + f + eps
    maintenance_availability = sugar_total / (sugar_total + MAINTENANCE_SUGAR_CUTOFF_KG_M3)
    return {
        "x": x,
        "growth_factor": growth_factor,
        "glucose_ferm_factor": glucose_ferm_factor,
        "fructose_ferm_factor": fructose_ferm_factor,
        "mu": mu,
        "kd": kd,
        "beta_g": beta_g,
        "beta_f": beta_f,
        "maintenance": maintenance,
        "maintenance_availability": maintenance_availability,
        "sugar_total": sugar_total,
    }


def rhs(t: float, y: np.ndarray, theta: dict[str, float], batch: BatchData | FutureDesign) -> list[float]:
    x, xd, n, g, f, e, gly = [max(0.0, float(value)) for value in y]
    terms = kinetic_terms(theta, temperature_at(batch, t), x, n, g, f, e)
    sugar_total = terms["sugar_total"]
    growth_factor = terms["growth_factor"]
    glucose_ferm_factor = terms["glucose_ferm_factor"]
    fructose_ferm_factor = terms["fructose_ferm_factor"]
    maintenance_flux = terms["maintenance"] * terms["maintenance_availability"]
    dx = (terms["mu"] - terms["kd"]) * x
    dxd = terms["kd"] * x
    dn = -theta["qN"] * growth_factor * x
    dg = -(
        theta["qXG"] * growth_factor
        + theta["qEG"] * glucose_ferm_factor
        + maintenance_flux * (g / sugar_total)
    ) * x
    df = -(
        theta["qXF"] * growth_factor
        + theta["qEF"] * fructose_ferm_factor
        + maintenance_flux * (f / sugar_total)
    ) * x
    de = (terms["beta_g"] + terms["beta_f"]) * x
    dgly = (theta["gammaG0"] * glucose_ferm_factor + theta["gammaF0"] * fructose_ferm_factor) * x
    return [dx, dxd, dn, dg, df, de, dgly]


def initial_vector(batch: BatchData | FutureDesign) -> np.ndarray:
    return np.array([float(batch.initials[state]) for state in STATE_NAMES], dtype=float)


def _pulse_events(
    batch: BatchData | FutureDesign,
    t0: float,
    tf: float,
) -> dict[float, np.ndarray]:
    events: dict[float, np.ndarray] = {}
    state_index = {state: index for index, state in enumerate(STATE_NAMES)}
    for channel in INPUT_CHANNELS:
        for event_time, amount in batch.pulses.get(channel, tuple()):
            event_time = float(event_time)
            amount = float(amount)
            if not np.isfinite(event_time) or not np.isfinite(amount) or amount < 0.0:
                raise ValueError("Pulse times and amounts must be finite; amounts must be nonnegative")
            if amount == 0.0 or event_time < t0 - 1e-12 or event_time > tf + 1e-12:
                continue
            delta = events.setdefault(event_time, np.zeros(len(STATE_NAMES), dtype=float))
            delta[state_index[channel]] += amount
    return events


def simulate(
    batch: BatchData | FutureDesign,
    theta: dict[str, float],
    output_time: np.ndarray | None = None,
    *,
    sample_event_order: str = "sample_before_action",
    integration_max_step_h: float = 2.0,
) -> pd.DataFrame | None:
    """Integrate continuous dynamics between events and apply exact pulse jumps.

    ``sample_event_order`` controls the state returned when a requested sample
    shares a timestamp with an action. Pilot 2026 approves
    ``sample_before_action``: the recorded state is pre-jump and the complete
    dose is applied immediately afterward. The alternate convention remains
    available for explicit numerical tests.
    """

    if sample_event_order not in {"sample_before_action", "action_before_sample"}:
        raise ValueError("sample_event_order must be sample_before_action or action_before_sample")
    if not np.isfinite(integration_max_step_h) or integration_max_step_h <= 0.0:
        raise ValueError("integration_max_step_h must be finite and positive")
    if output_time is None:
        if isinstance(batch, BatchData):
            output_time = batch.time
        else:
            output_time = operational_sample_times(batch.horizon_h)
    output_time = np.asarray(sorted(set(float(t) for t in output_time)), dtype=float)
    if len(output_time) == 0:
        return None
    t0 = float(output_time[0])
    tf = float(output_time[-1])
    if isinstance(batch, BatchData):
        y0 = initial_vector(batch)
        if abs(float(batch.time[0]) - t0) > 1e-9:
            t0 = float(batch.time[0])
            output_time = np.asarray(sorted(set([t0] + [float(t) for t in output_time])), dtype=float)
    else:
        y0 = initial_vector(batch)
        if t0 > 0.0:
            output_time = np.asarray(sorted(set([0.0] + [float(t) for t in output_time])), dtype=float)
            t0 = 0.0
    if tf < t0:
        return None
    try:
        events = _pulse_events(batch, t0, tf)
    except ValueError:
        raise
    output_set = set(float(value) for value in output_time)
    timeline = sorted(output_set | set(events))
    current_time = float(t0)
    current_state = np.asarray(y0, dtype=float).copy()
    records: dict[float, np.ndarray] = {}
    try:
        for time_h in timeline:
            if time_h < current_time - 1e-12:
                continue
            if time_h > current_time + 1e-12:
                sol = solve_ivp(
                    lambda t, y: rhs(t, y, theta, batch),
                    (current_time, time_h),
                    current_state,
                    t_eval=[time_h],
                    method="LSODA",
                    rtol=1e-6,
                    atol=1e-8,
                    max_step=float(integration_max_step_h),
                )
                if not sol.success or sol.y.shape[1] != 1:
                    return None
                current_state = np.asarray(sol.y[:, -1], dtype=float)
                current_time = float(time_h)
            delta = events.get(float(time_h))
            if delta is not None and sample_event_order == "sample_before_action":
                if float(time_h) in output_set:
                    records[float(time_h)] = current_state.copy()
                current_state = current_state + delta
            elif delta is not None:
                current_state = current_state + delta
                if float(time_h) in output_set:
                    records[float(time_h)] = current_state.copy()
            elif float(time_h) in output_set:
                records[float(time_h)] = current_state.copy()
    except Exception:
        return None
    if any(float(time_h) not in records for time_h in output_time):
        return None
    values = np.vstack([records[float(time_h)] for time_h in output_time])
    for idx, state in enumerate(STATE_NAMES):
        lb, ub = STATE_BOUNDS[state]
        values[:, idx] = np.clip(values[:, idx], lb, ub)
    return pd.DataFrame(values, index=output_time, columns=STATE_NAMES)


def sigma_for_state(state: str, observed_or_simulated: np.ndarray | float) -> np.ndarray:
    arr = np.asarray(observed_or_simulated, dtype=float)
    floor = float(MEASUREMENT_ERROR_FLOOR[state])
    rel = float(MEASUREMENT_ERROR_REL[state])
    return np.maximum(floor, rel * np.maximum(np.abs(arr), floor))


def operational_sample_times(
    horizon_h: float,
    start: str = "2026-06-15 08:00",
    policy: str = "front_loaded",
) -> np.ndarray:
    start_dt = datetime.fromisoformat(start)
    horizon = float(horizon_h)
    points: list[float] = []
    process_day = 0
    current_day = start_dt.date()
    while True:
        day_start = datetime.combine(current_day, datetime.min.time())
        if (day_start - start_dt).total_seconds() / 3600.0 > horizon + 24.0:
            break
        if day_start.weekday() < 5:
            if policy == "balanced":
                hours = (10, 12, 14, 16)
            elif policy == "two_per_day":
                hours = (10, 16)
            else:
                hours = (10, 12, 14, 16) if process_day <= 2 else (10, 16)
            for hour in hours:
                dt = datetime.combine(current_day, datetime.min.time()) + timedelta(hours=hour)
                t = (dt - start_dt).total_seconds() / 3600.0
                if 0.0 < t <= horizon:
                    points.append(float(t))
            process_day += 1
        current_day = current_day + timedelta(days=1)
    return np.array(sorted(set(round(t, 8) for t in points)), dtype=float)
