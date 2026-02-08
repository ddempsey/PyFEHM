# eos - Equation of State

**Status**: Optional

## Purpose

Provide the code with alternate thermodynamic properties for the liquid and/or vapor phases. This allows simulation of nonisothermal single-phase air or making comparisons with analytical solutions using different equations of state.

## Input Format

```
eos
IIEOSD  IPSAT  ITSAT
EW1  EW2  EW3  EW4  EW5  EW6  EW7  EW8  EW9  EW10  EW11
EV1  EV2  EV3  EV4  EV5  EV6  EV7  EV8  EV9  EV10  EV11
```

## Parameters

### Group 1 - Control

| Variable | Format | Description |
|----------|--------|-------------|
| IIEOSD | integer | Equation of state reference: 1 or 2 = use built-in high/low pressure data, other = use user-defined Groups 2 and 3 |
| IPSAT | integer | Vapor pressure control: 0 = calculate, ≠0 = set to zero |
| ITSAT | integer | Saturation temperature control: <0 = set to -1000°C, >0 = set to 1000°C, 0 = calculate |

### Group 2 - Liquid Properties (EW1-EW11)

| Variable | Description |
|----------|-------------|
| EW1 | Reference pressure (MPa) |
| EW2 | Reference temperature (°C) |
| EW3 | Reference density (kg/m³) |
| EW4 | Derivative of density with respect to pressure at reference conditions |
| EW5 | Derivative of density with respect to temperature at reference conditions |
| EW6 | Reference enthalpy (MJ/kg) |
| EW7 | Derivative of enthalpy with respect to pressure at reference conditions |
| EW8 | Derivative of enthalpy with respect to temperature at reference conditions |
| EW9 | Reference viscosity (Pa·s) |
| EW10 | Derivative of viscosity with respect to pressure at reference conditions |
| EW11 | Derivative of viscosity with respect to temperature at reference conditions |

### Group 3 - Vapor Properties (EV1-EV11)

Same structure as Group 2, but for vapor phase. Note: EV4 and EV5 are not used (density from ideal gas law).

## Physics

For simplified thermodynamic equations, the data generates first-order equations:
- Property uses a 1/T term for liquid viscosity
- Vapor density and derivatives use ideal gas law
- Properties are linearized around reference conditions

## Example

```
eos
    3        0        0
  0.1       20.      998.        0.       -0.2       0.8        0.     4.2e-03     9.e-04        0.        0.
  0.1       20.      1.29        0         0        2.5        0.       0.1       2.e-4        0.        0.

```

In this example:
- User-defined equation of state (IIEOSD=3)
- Calculate vapor pressure and saturation temperature
- Liquid at reference: P=0.1 MPa, T=20°C, ρ=998 kg/m³, dρ/dT=-0.2 kg/m³/°C
- Liquid enthalpy: h=0.8 MJ/kg, dh/dT=4.2e-3 MJ/kg/°C
- Liquid viscosity: μ=9.e-4 Pa·s
- Vapor at reference: P=0.1 MPa, T=20°C, ρ=1.29 kg/m³
- Vapor enthalpy: h=2.5 MJ/kg, dh/dT=0.1 MJ/kg/°C
- Vapor viscosity: μ=2.e-4 Pa·s

## Notes

- IIEOSD = 1 or 2 use FEHM's built-in steam tables
- User-defined EOS useful for non-water fluids or simplified physics
- Setting IPSAT ≠ 0 eliminates phase change (single-phase only)
- ITSAT can force single-phase liquid (<0) or vapor (>0)
- Linearized properties are accurate only near reference conditions
- For CO₂ simulations, use **carb** macro instead
