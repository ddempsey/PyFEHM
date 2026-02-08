# airwater (or air) - Isothermal Air-Water Two-Phase

**Status**: Optional

## Purpose

Enable isothermal air-water two-phase simulation. Provides a formulation similar to Richards' Equation or pure gas flow depending on the degree of freedom setting.

## Input Format

```
airwater
ICO2D
TREF  PREF
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| ICO2D | integer | Degree of freedom option (1, 2, or 3) |
| TREF | real | Reference temperature for properties (°C) |
| PREF | real | Reference pressure for properties (MPa) |

## Degree of Freedom Options

| ICO2D | Description |
|-------|-------------|
| 1 | 1 DOF - Saturated-unsaturated problem (similar to Richards' Equation) |
| 2 | 1 DOF - Gas flow only (no liquid present) |
| 3 | 2 DOF - Full two-degree-of-freedom solution (default) |

## Interaction with Other Macros

When `airwater` is enabled:

### `pres` macro
- IEOSD must always be 2 (two-phase)
- Use saturations (not temperatures) for the third variable

### `init` macro
- Should NOT be used (saturation values cannot be specified)

### `flow` macro
- Different flow and boundary values are input
- See `flow` macro description for details

## Example

```
airwater
    3
   20.        0.1

```

Full 2-DOF air-water solution with:
- Reference temperature: 20°C
- Reference pressure: 0.1 MPa

## Notes

- For saturated-unsaturated problems (ICO2D=1), this provides a Richards' equation-like formulation
- Reference conditions used for fluid property calculations
- The formulation is always 2-phase; air phase is tracked
