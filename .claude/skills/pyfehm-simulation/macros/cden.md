# cden - Concentration-Dependent Density

**Status**: Optional

## Purpose

Enable concentration-dependent density for flow calculations. The fluid density becomes a function of solute concentration.

## Restrictions

1. Cannot be used with `head` macro (assumes constant density)
2. Density updating is explicit (based on previous timestep)
3. Requires small timesteps for accuracy
4. Heat and mass transfer solution must remain on during entire simulation

## Input Format

```
cden
ISPCDEN
FACTCDEN
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| ISPCDEN | integer | Chemical component number in `trac` for density dependence |
| FACTCDEN | real | Factor for density relationship (kg/m³) |

## Density Relationship

```
density = density_water + FACTCDEN × C
```

Where:
- `density_water` = density of pure water (kg/m³)
- `C` = concentration of chemical component ISPCDEN

## Example

```
cden
    1
  100.

```

Uses component 1 from `trac` macro. For concentrations of order 1, the density correction would be 100 kg/m³, which is ~10% of nominal water density (1000 kg/m³).

## Notes

- Verify convergence by testing with smaller timesteps
- Keep fluid flow timesteps small enough that concentration changes are small between steps
- Useful for brine/saltwater intrusion problems
- Component number refers to species defined in `trac` macro
