# init - Initial Conditions

**Status**: REQUIRED if macro **pres** not used

## Purpose

Set initial pressure and temperature at all nodes. Provides a way to specify spatially varying initial conditions using temperature gradients.

Note that the macro **pres** may overwrite some values set by **init**.

## Input Format

```
init
PEIN  TIN  TIN1  GRAD1  DEPTH  TIN2  GRAD2  QUAD
```

All parameters on a single line.

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| PEIN | real | Initial value of pressure (MPa). If gravity is present, this is the pressure at node 1 and other nodal pressures are adjusted by hydraulic head. Pressure as a function of depth is calculated with TIN < 0. |
| TIN | real | Initial value of temperature (°C). If TIN ≤ 0, initial temperatures are calculated using the temperature gradient formulas below. |
| TIN1 | real | Temperature at surface for shallow depths (°C) |
| GRAD1 | real | Temperature gradient for shallow depths (°C/m) |
| DEPTH | real | Depth at which gradient changes (m) |
| TIN2 | real | Temperature at DEPTH (°C) |
| GRAD2 | real | Temperature gradient for deep depths (°C/m) |
| QUAD | real | Quadratic temperature term for deep depths (°C/m²) |

## Temperature Gradient Formulas

For nodes at depth Z:

### Shallow Region (0 ≤ Z ≤ DEPTH):
```
T = TIN1 + GRAD1 × Z
```

### Deep Region (Z > DEPTH):
```
T = TIN2 + GRAD2 × Z + QUAD × Z²
```

## Examples

### Example 1: Uniform Initial Conditions
```
init
   3.6       0.0      240.        0.        0.      240.        0.        0.

```
- Initial pressure: 3.6 MPa
- Initial temperature: 240°C (uniform, since TIN=0, TIN1=240, GRAD1=0)
- No depth-dependent gradient

### Example 2: Temperature Gradient
```
init
   5.0       0.0       20.       0.3     2500.       20.       0.3        0.

```
- Initial pressure: 5.0 MPa
- Initial temperature defined by gradient:
  - Surface temperature: 20°C
  - Gradient: 0.3°C/m (30°C/km)
  - For depths 0-2500 m: T = 20 + 0.3×Z
  - For depths > 2500 m: T = 20 + 0.3×Z (same gradient continues)

## Notes

- Use **init** for simple uniform or gradient initial conditions
- Use **pres** for node-by-node or zone-based initial conditions
- If both **init** and **pres** are used, **pres** values supersede **init**
- Temperature gradient is commonly 25-30°C/km in continental crust
- Pressure gradient for hydrostatic conditions is ~9.8 kPa/m or 0.0098 MPa/m
- The QUAD term allows for nonlinear temperature profiles at depth
- Initial values from restart file override **init** values
