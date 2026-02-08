# impf - Timestep Control by Variable Change

**Status**: Optional

## Purpose

Time step control based on maximum allowed variable change. The timestep is increased if all variable changes are below these limits.

## Input Format

```
impf
DELPT  DELTT  DELST  DELAT
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| DELPT | real | Maximum allowable pressure change for which time step will be increased (MPa) |
| DELTT | real | Maximum allowable temperature change for which time step will be increased (°C) |
| DELST | real | Maximum allowable saturation change for which time step will be increased (0-1) |
| DELAT | real | Maximum allowable air pressure change for which time step will be increased (MPa) |

## Example

```
impf
   0.5       20.0       0.1      0.05

```

In this example:
- Pressure changes limited to 0.5 MPa
- Temperature changes limited to 20°C
- Saturation changes limited to 0.1
- Air pressure changes limited to 0.05 MPa

If all changes are below these limits during a timestep, the timestep can be increased (according to **ctrl** parameters).

## Notes

- This macro provides additional control over time stepping beyond basic **ctrl** parameters
- Large changes indicate rapidly varying conditions that may need smaller timesteps
- Setting appropriate limits prevents numerical instabilities from large variable jumps
- For steady-state problems, these limits can be relaxed
- For transient problems with sharp fronts, tighter limits improve accuracy
- If not specified, FEHM uses internal criteria based on convergence
