# grad - Gradient Initial Conditions

**Status**: Optional

## Purpose

Gradient model input. Allows specification of initial conditions (pressure, temperature, saturation, etc.) that vary linearly with a coordinate direction.

## Input Format

```
grad
NGRAD
IZONE_GRAD  CORDG  IDIRG  IGRADF  VAR0  GRAD1
...
```

Group 2 is repeated NGRAD times for each gradient model being defined.

## Parameters

### Group 1

| Variable | Format | Description |
|----------|--------|-------------|
| NGRAD | integer | Number of gradient models |

### Group 2 (repeated NGRAD times)

| Variable | Format | Description |
|----------|--------|-------------|
| IZONE_GRAD | integer | Zone associated with ith model |
| CORDG | real | Reference coordinate of gradient equation (m) |
| IDIRG | integer | Coordinate direction of gradient (1=X, 2=Y, 3=Z) |
| IGRADF | integer | Variable to which gradient is applied (see table) |
| VAR0 | real | Value of variable at reference point |
| GRAD1 | real | Gradient with distance |

## IGRADF Values

| IGRADF | Variable | Units for GRAD1 |
|--------|----------|-----------------|
| 1 | Pressure | MPa/m |
| 2 | Temperature | °C/m |
| 3 | Saturation | 1/m |
| 4 | Fixed boundary pressure | MPa/m |
| 5 | Fixed boundary temperature | °C/m |
| -5 | Fixed boundary temperature (for inflow nodes) | °C/m |
| 6 | Methane pressure | MPa/m |
| 7 | Fixed Methane boundary pressure | MPa/m |
| 8 | Fixed boundary heat flow | MW/m |
| 9 | CO₂ pressure | MPa/m |
| 10 | Fixed CO₂ boundary pressure | MPa/m |
| 11 | Pressure for matrix in gdkm or gdpm model | MPa/m |
| 12 | Temperature for matrix in gdkm or gdpm model | °C/m |

## Calculation

The variable at any point is calculated as:

```
Variable = VAR0 + GRAD1 × (coordinate - CORDG)
```

where `coordinate` is the value in the direction specified by IDIRG.

## Example

```
grad
    1
    1         0.        2        2       10.     -150.

```

In this example:
- 1 gradient model
- Applied to zone 1
- Reference coordinate is 0 in Y direction (IDIRG=2)
- Applying a temperature gradient (IGRADF=2)
- Reference temperature VAR0=10°C at Y=0
- Gradient GRAD1=-150°C/m (temperature decreases with Y)

So temperature at any point = 10 - 150×Y (°C)

## Notes

- Multiple gradient models can be defined for different zones and variables
- Gradients are applied during initialization
- Can be combined with **pres** or **init** macros (grad values may override)
- Useful for establishing geothermal gradients, hydrostatic pressure profiles
- For typical geothermal gradient: GRAD1 ≈ 0.025-0.030 °C/m (25-30°C/km)
- For hydrostatic pressure gradient in water: GRAD1 ≈ 0.0098 MPa/m
