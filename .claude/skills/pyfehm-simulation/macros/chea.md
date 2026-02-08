# chea - Convert Output to Head

**Status**: Optional

## Purpose

Convert output from pressure to head for non-head problems. The reference temperature and pressure are used to calculate density for the head calculation.

## Input Format

All values on the macro line:

```
chea HEAD0 TEMP0 PRES0 SAT_ICH HEAD_ID
```

## Parameters

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| HEAD0 | real | 0 | Reference head (m) |
| TEMP0 | real | 20 | Reference temperature (°C) |
| PRES0 | real | 0.1 | Reference pressure (MPa) |
| SAT_ICH | real | 0 | Saturation adjustment after variable switch |
| HEAD_ID | real | 0 | Output head identification for small saturations |

## Notes

- If any values are omitted, all five must be entered to override defaults
- Used when running pressure-based simulations but head output is desired
- Head calculation: h = P/(ρg) + z, where ρ is calculated at reference T and P

## Example

```
chea 0. 25. 1. 0. 0.

```

Convert pressures to heads using:
- Reference head: 0 m
- Reference temperature: 25°C
- Reference pressure: 1 MPa
- No saturation adjustment
- No special head identification

## Use Case

Useful when:
- Model is solved in terms of pressure (non-head problem)
- Output is needed in terms of hydraulic head for comparison with field data
- Working with well data that reports head/water levels
