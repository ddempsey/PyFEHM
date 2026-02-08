# anpe - Anisotropic Permeability (Cross Terms)

**Status**: Optional

## Purpose

Add cross terms to the permeability tensor. Enables full anisotropic permeability specification beyond the diagonal terms defined in `perm` macro.

## Restrictions

Do NOT use with:
- `dpdp` macro (double porosity/double permeability)
- `gdkm` macro (generalized dual permeability)
- Multiple porosity models

## Input Format

```
anpe
JA  JB  JC  ANXY  ANXZ  ANYZ
...
(blank line to end)
```

## Parameters

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA | integer | - | First node (or -zone) |
| JB | integer | - | Last node |
| JC | integer | - | Node increment |
| ANXY | real | 1.e-30 | Permeability in xy-direction (m²) |
| ANXZ | real | 1.e-30 | Permeability in xz-direction (m²) |
| ANYZ | real | 1.e-30 | Permeability in yz-direction (m²) |

## Full Permeability Tensor

Combined with `perm` macro, the full permeability tensor becomes:

```
     | kx   kxy  kxz |
K =  | kxy  ky   kyz |
     | kxz  kyz  kz  |
```

Where:
- `kx`, `ky`, `kz` from `perm` macro (diagonal)
- `kxy`, `kxz`, `kyz` from `anpe` macro (off-diagonal)

## Example

```
anpe
    1     100       1     1.e-14      1.e-15      0.0

```

Assigns nodes 1-100:
- kxy = 1.e-14 m²
- kxz = 1.e-15 m²
- kyz = 0 m²

## Notes

- Use for fractured media with oriented fracture sets
- Cross terms create flow coupling between coordinate directions
- Default (1.e-30) effectively zero
- Zone assignment supported with negative JA
