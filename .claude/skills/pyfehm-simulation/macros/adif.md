# adif - Air-Water Vapor Diffusion

**Status**: Optional

## Purpose

Enable air-water vapor diffusion. The air-water diffusion equation is given as Equation (21) of the "Models and Methods Summary" of the FEHM Application (Zyvoloski et al. 1999).

## Input Format

```
adif
TORT
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| TORT | real | Tortuosity for air-water vapor diffusion |

## Tortuosity Interpretation

| Condition | Behavior |
|-----------|----------|
| TORT > 0 | τ of equation 21 |
| TORT < 0 | abs(τφS_v) of the same equation |
| TORT > 1 | Water-vapor diffusion coefficient set to value specified for first vapor species in `trac` macro |

## Example

```
adif
    0.8

```

Sets tortuosity (τ) for vapor diffusion to 0.8.

## Notes

- Typically used with air-water or multiphase simulations
- Requires appropriate phase conditions to be meaningful
- Works in conjunction with `trac` macro for species transport
