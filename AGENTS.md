# Confirmed CO2 instrumentation

Before discussing or editing CO2 measurement, conversion or Kalman measurement
uncertainty, read `configs/co2_instrument.json`.

The user explicitly confirmed on 2026-11-05:

- Instrument range: **0–50 SCCM**.
- Calibration gas: **air**.
- CO2 conversion factor: **0.74**, confirmed correct for this setup.

Treat these as established user-provided facts. Do not ask the user to confirm
them again, and do not mark them as pending in reports or notebooks. Revisit
them only if the user reports an instrumentation change or contradictory new
evidence requires investigation. This confirmation does not supply a standard
deviation for R or resolve the manufacturer's unspecified basis for the ±4%
gas-conversion accuracy.
