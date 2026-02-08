# cond - Thermal Conductivity

**Status**: REQUIRED (for non-isothermal problems)

## Purpose

Assign thermal conductivities of the rock matrix. Required for any simulation involving heat transfer.

## Input Format

```
cond
JA  JB  JC  THXD  THYD  THZD
...
(blank line to end)
```

## Parameters

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA | integer | - | First node to be assigned properties |
| JB | integer | - | Last node to be assigned properties |
| JC | integer | - | Loop increment for assigning properties |
| THXD | real | 1.e-30 | Thermal conductivity in x-direction (W/m/K) |
| THYD | real | 1.e-30 | Thermal conductivity in y-direction (W/m/K) |
| THZD | real | 1.e-30 | Thermal conductivity in z-direction (W/m/K) |

## Zone Assignment

Use negative JA to assign by zone:
- `JA = -zone_number` assigns to all nodes in that zone
- JB and JC must still be provided but are ignored

## Notes

- Default value (1.e-30) effectively means no conduction
- Units are W/(m·K)
- Anisotropic conductivity supported via different x, y, z values
- For isotropic materials, set THXD = THYD = THZD

## Typical Values

| Material | Conductivity (W/m/K) |
|----------|---------------------|
| Sandstone | 2.0 - 4.0 |
| Shale | 1.5 - 2.5 |
| Limestone | 2.5 - 3.5 |
| Granite | 2.5 - 3.5 |
| Water | 0.6 |
| Air | 0.025 |

## Example

```
cond
    1     140       1     1.00e+00     1.00e+00     0.00e+00

```

Assigns all nodes 1-140 thermal conductivity of 1 W/m/K in X and Y directions, 0 in Z direction.

### Zone-based Example

```
cond
   -1       0       0     2.5          2.5          2.5
   -2       0       0     1.8          1.8          1.8

```

Assigns zone 1 conductivity of 2.5 W/m/K (isotropic), zone 2 gets 1.8 W/m/K.
