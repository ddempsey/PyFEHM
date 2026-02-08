# pres - Initial Pressure/Temperature/Saturation

**Status**: REQUIRED if macro **init** not used

## Purpose

Set initial pressure, temperature, and/or saturation on a node-by-node or zone basis. Values defined in **pres** supersede all others.

Note: The term "saturated" in IEOSD refers to thermodynamic state (vapor and liquid coexist), **not** the groundwater definition (fraction of pore space filled with water).

## Input Format

```
pres
JA  JB  JC  PHRD  TIND  IEOSD
...
(blank line to end)
```

## Parameters

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop. Use negative JA for zone assignment. |
| PHRD | real | PEIN | Initial pressure (MPa) |
| TIND | real | | Initial temperature (°C) if IEOSD = 1 or 3; Initial saturation if IEOSD = 2 |
| IEOSD | integer | 1 | Thermodynamic region parameter (see table) |

## IEOSD Values - Thermodynamic Region

| IEOSD | Region | TIND Meaning |
|-------|--------|--------------|
| 1 | Compressed liquid | Temperature (°C) |
| 2 | Saturation (two-phase) | Liquid saturation (0-1) |
| 3 | Superheated vapor | Temperature (°C) |
| -1, -2, -3 | Same as above | Values of PHRD and TIND are **fixed** throughout simulation |

The negative IEOSD values fix the boundary condition (constant pressure and temperature/saturation).

## Thermodynamic Regions

- **Compressed liquid (IEOSD=1)**: T < Tsat(P), liquid only, saturation = 1
- **Saturation (IEOSD=2)**: T = Tsat(P), vapor and liquid coexist
- **Superheated (IEOSD=3)**: T > Tsat(P), vapor only, saturation = 0

## Example

```
pres
   -1         0        1       0.1       0.1        2
   -2         0        1       0.1       0.1        2
   -3         0        1       0.1     0.003        2
   -4         0        1       0.1       0.1        2
   -5         0        1       0.1      0.11        2
   -6         0        1       0.1      0.11       -2
    1       800        1       0.1       0.5        2

```

In this example:
- Zones 1, 2, 3, 4, 5: Initial pressure 0.1 MPa, in saturation region (IEOSD=2)
  - Zones 1, 2, 4: saturation = 0.1
  - Zone 3: saturation = 0.003
  - Zone 5: saturation = 0.11
- Zone 6: Same as zone 5 but **fixed** (IEOSD=-2 means constant P and saturation)
- Nodes 1-800: Initial pressure 0.1 MPa, saturation 0.5, in saturation region

## Notes

- **pres** values supersede **init** values where both are specified
- Use negative IEOSD for fixed boundary conditions (Dirichlet)
- For isothermal simulations, TIND is typically saturation
- For non-isothermal single-phase, use IEOSD = 1 (compressed liquid) or 3 (superheated)
- Zone assignment uses negative JA (e.g., JA = -5 for zone 5)
- Multiple pres statements can be used; later values override earlier ones
- Pressure should be above saturation pressure for IEOSD=1
- Saturation temperature at 0.1 MPa ≈ 100°C, at 1 MPa ≈ 180°C
