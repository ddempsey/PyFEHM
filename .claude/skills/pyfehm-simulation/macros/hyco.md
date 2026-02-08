# hyco - Hydraulic Conductivity

**Status**: REQUIRED if macro **perm** not used

## Purpose

Hydraulic conductivity input. Alternative to specifying permeability directly. Hydraulic conductivity is related to permeability by K = k·ρg/μ where k is permeability, ρ is fluid density, g is gravity, and μ is viscosity.

## Input Format

```
hyco
JA  JB  JC  PNX  PNY  PNZ
...
(blank line to end)
```

## Parameters

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop |
| PNX | real | 1.e-30 | Hydraulic conductivity in the x-direction (m/s) |
| PNY | real | 1.e-30 | Hydraulic conductivity in the y-direction (m/s) |
| PNZ | real | 1.e-30 | Hydraulic conductivity in the z-direction (m/s) |

## Example

```
hyco
    1       140        1    1.00e-05    1.00e-05    0.00e-00

```

In this example:
- Nodes 1 through 140 are specified
- Hydraulic conductivities of 1.0e-5 m/s in X and Y directions
- No conductivity (0.0 m/s) in Z direction

## Conversion to Permeability

For water at standard conditions (20°C, 0.1 MPa):
- ρ ≈ 998 kg/m³
- μ ≈ 1.0e-3 Pa·s
- g = 9.81 m/s²

Therefore:
```
k (m²) ≈ K (m/s) × 1.02e-7
```

Or approximately:
```
K = 1e-5 m/s  →  k ≈ 1e-12 m²
K = 1e-7 m/s  →  k ≈ 1e-14 m²
```

## Notes

- Use either **hyco** or **perm**, not both
- Hydraulic conductivity is commonly used in groundwater applications
- FEHM internally converts to permeability for calculations
- Units are m/s (SI), not m/day or ft/day
- Default value (1.e-30) effectively means impermeable
- For anisotropic hydraulic conductivity, specify different values for each direction
