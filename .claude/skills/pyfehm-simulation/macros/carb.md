# carb - CO2 Simulation Input

**Status**: Optional

## Purpose

Set up CO2 problems including CO2-water, CO2 only, and CO2-water-air systems. Supports multiple problem types with varying degrees of freedom.

## Input Format

```
carb
IPRTYPE
KEYWORD
  (keyword-specific data)
...
end carb
```

## Problem Types (IPRTYPE)

| Value | Description | DOFs |
|-------|-------------|------|
| 1 | Water only problem | 2 |
| 2 | CO2 only problem | 2 |
| 3 | CO2-water problem, no solubility | 3 |
| 4 | CO2-water problem, with solubility | 4 |
| 5 | CO2-water-air with solubility | 5 |

## Sub-Keywords

### co2pres - Initial Pressure Conditions
```
co2pres
JA  JB  JC  PHICO2  TCO2  ICES
...
(blank line)
```

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| PHICO2 | real | 0 | Initial CO2 pressure (MPa) |
| TCO2 | real | 0 | Initial CO2 temperature (°C) |
| ICES | integer | 0 | Phase state guess: 1=liquid, 2=two-phase, 3=vapor, 4=supercritical |

### co2flow - CO2 Flow Boundary Conditions
```
co2flow
JA  JB  JC  SKTMP  ESKTMP  AIPED  IFLG_FLOWMAC
...
(blank line)
```

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| SKTMP | real | 0 | CO2 flowing pressure (MPa) or mass rate (kg/s) |
| ESKTMP | real | 0 | Enthalpy (MJ/kg) or temperature (°C) or saturation |
| AIPED | real | 0 | Impedance parameter or mass rate |
| IFLG_FLOWMAC | integer | 0 | Boundary condition type (1-9) |

### IFLG_FLOWMAC Options

| Value | Description |
|-------|-------------|
| 1 | Constant pressure BC, inflow/outflow allowed, user AIPED |
| 2 | Constant pressure BC, outflow only, user AIPED |
| 3 | Constant pressure BC, AIPED calculated from geometry |
| 4 | Constant pressure + saturation, user AIPED |
| 5 | Constant pressure + saturation, AIPED from geometry |
| 6 | Constant free-phase CO2 mass flow rate |
| 7 | CO2 flow rate with saturation |
| 8 | Constant water source with CO2 mass fraction (kg/s) |
| 9 | Partial explicit update, CO2 constant pressure |

### co2diff - CO2 Diffusion
```
co2diff
JA  JB  JC  DIFF  TORTCO2
...
```

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| DIFF | real | 0 | Diffusion coefficient |
| TORTCO2 | real | 0 | Tortuosity for CO2-water vapor diffusion |

### co2frac - Initial CO2 Fractions
```
co2frac
JA  JB  JC  FW  FL  YC  CSALT  INICO2FLG
...
```

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| FW | real | 0 | Water-rich liquid saturation (volume fraction) |
| FL | real | 0 | CO2-rich supercritical/liquid saturation |
| YC | real | 0 | Mass fraction of CO2 in CO2-rich phase |
| CSALT | real | 0 | Salt concentration (ppm) - if "brine" keyword used |
| INICO2FLG | integer | 0 | Override restart file fractions (1=yes) |

### userprop - User-Defined Properties
```
userprop
DENC DENCP DENCT ENC ENCP ENCT VISC VISCP VISCT
DENW DENWP DENWT ENW ENWP ENWT VISW VISWP VISWT
```

For specifying constant CO2 and brine properties with derivatives.

### brine
```
brine
```
Enables salt-concentration dependent CO2 solubility.

## Example

```
carb
    4
co2pres
    1       0       0        3.        20.        4
   -1       0       0       13         20.        4
   -2       0       0        .6        20.        4

co2frac
    1       0       0        1.0       0.0        0     100000     0
   -1       0       0        0.9465    .0535      0        0.       0.

co2flow
   -2       0       0        0        -20.       -1.e-1      3
   -1       0       0       -0.0001   -20.        0.         6
end carb

```

This example:
- IPRTYPE=4: CO2-water with solubility
- Zone 1: Initial CO2 pressure 3 MPa, 20°C, supercritical
- Zone -1: Pressure 13 MPa
- Zone -2: Pressure 0.6 MPa
- CO2 fractions and flow conditions specified by zone
