# bous - Boussinesq Approximation

**Status**: Optional

## Purpose

Enable constant density and viscosity for flow terms (Boussinesq approximation). This simplification is useful for problems where density variations are small but buoyancy effects are still important.

## Input Format

```
bous
ICONS
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| ICONS | integer | Enable/disable flag |

## Flag Values

| ICONS | Effect |
|-------|--------|
| ≠ 0 | Boussinesq approximation enabled |
| = 0 | Boussinesq approximation disabled (default) |

## Physics

When enabled:
- Density and viscosity are held constant in flow equations
- Gravity term in air phase is set to zero
- Density variations only affect buoyancy term
- Simplifies equations and can improve convergence

## Example

```
bous
    1

```

Enables the Boussinesq approximation.

## Notes

- Useful for natural convection problems with small temperature variations
- Can improve solver stability for certain problem types
- Not appropriate when density variations are large
- Commonly used in geothermal applications
