# conv - Head to Pressure Conversion

**Status**: Optional

## Purpose

Convert input from head to pressure. Often used when converting a head-based isothermal model to a heat and mass simulation with pressure and temperature variables.

## Physics Note

This is an approximate method. Since density is a nonlinear function of pressure and temperature, this method gives slightly different answers than a calculation allowing a water column to come to thermal and mechanical equilibrium.

## Input Format

```
conv HEAD0
NCONV
ZONE_CONV  ICONVF  CONV1  CONV2  CORDC  IDIRC  VARC
...
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| HEAD0 | real | Reference head (m) - entered on macro line |
| NCONV | integer | Number of zones for variable conversion |
| ZONE_CONV | integer | Zone for variable conversion |
| ICONVF | integer | Conversion type: 1=initial conditions, 2=boundary (fixed head) |
| CONV1 | real | Reference pressure (MPa) |
| CONV2 | real | Reference temperature (°C) |
| CORDC | real | Reference coordinate (m) |
| IDIRC | integer | Coordinate direction: 1=X, 2=Y, 3=Z |
| VARC | real | Temperature gradient (°C/m) |

## Calculation Method

1. Reference head (HEAD0) is converted to pressure
2. This pressure is added to reference pressure (CONV1)
3. Combined with reference temperature (CONV2) to calculate density
4. This density converts head to pressure for the identified zone

## Example

```
conv  1000.
    1
   45        1        0.1       80.        0.        0        0.0

```

Converts head to pressure with:
- Reference head: 1000 m
- 1 zone to convert (zone 45)
- Conversion for initial conditions (ICONVF=1)
- Reference pressure: 0.1 MPa
- Reference temperature: 80°C
- No coordinate-dependent temperature gradient

## Notes

- Used to bridge isothermal head models to non-isothermal pressure models
- Temperature gradient (VARC) allows depth-dependent temperature conversion
- Density calculated from reference P,T conditions
