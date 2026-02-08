# perm - Permeability

**Status**: REQUIRED if macro **hyco** not used

## Purpose

Assign permeabilities of the rock. Permeabilities represent average values of a volume associated with a node. Note that using **rlp** models 4 or 6 to describe relative permeabilities causes these values to be overwritten.

Permeabilities may be entered as log values.

## Input Format

```
perm
JA  JB  JC  PNXD  PNYD  PNZD
...
(blank line to end)
```

## Parameters

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop |
| PNXD | real | 1.e-30 | Permeability in the x-direction (m²) |
| PNYD | real | 1.e-30 | Permeability in the y-direction (m²) |
| PNZD | real | 1.e-30 | Permeability in the z-direction (m²) |

## Example

```
perm
    1       140        1    2.50e-14    2.50e-14    0.00e-00

```

In this example:
- Nodes 1 through 140 are specified
- Permeabilities of 2.5e-14 m² in X and Y directions
- No permeability (0.0 m²) in Z direction (impermeable in Z)

## Permeability Values Reference

| Material | Permeability (m²) | Permeability (mD) |
|----------|-------------------|-------------------|
| Gravel | 1e-9 to 1e-7 | 10⁶ to 10⁸ |
| Clean sand | 1e-12 to 1e-10 | 10³ to 10⁵ |
| Silty sand | 1e-14 to 1e-12 | 10 to 10³ |
| Silt | 1e-16 to 1e-14 | 0.1 to 10 |
| Clay | 1e-20 to 1e-16 | 10⁻⁵ to 0.1 |
| Fractured rock | 1e-14 to 1e-10 | 10 to 10⁵ |
| Unfractured rock | 1e-20 to 1e-16 | 10⁻⁵ to 0.1 |

## Unit Conversions

- 1 Darcy = 9.87e-13 m²
- 1 millidarcy (mD) = 9.87e-16 m²
- 1 m² ≈ 1.01e12 Darcy

## Notes

- Use either **perm** or **hyco**, not both
- Default value (1.e-30 m²) effectively means impermeable
- Permeability can be isotropic (same in all directions) or anisotropic
- For fully anisotropic permeability (off-diagonal terms), use **anpe** macro
- Values can be assigned by zone using negative JA (e.g., JA = -5 for zone 5)
- **rlp** models 4 and 6 calculate permeability from relative permeability functions
- Use **fper** macro to apply scaling factors to permeability
- Very low permeability (< 1e-20 m²) can cause numerical issues
