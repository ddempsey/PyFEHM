# flow - Flow Boundary Conditions

**Status**: REQUIRED for flow problems (either **boun** or **flow**)

## Purpose

Flow data. Source and sink parameters are input and may be used to apply boundary conditions. Note that alternative definitions for isothermal models apply when **flow** is used in conjunction with control statement **airwater**.

## Input Format

```
flow
JA  JB  JC  SKD  EFLOW  AIPED
...
(blank line to end)
```

## Parameters

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop (JA, JB, JC - defined on page 33) |
| SKD | real | 0. | See physics table below |
| EFLOW | real | 0. | See physics table below |
| AIPED | real | 0. | Impedance parameter - see physics table below |

## Non-Isothermal Model

| AIPED | SKD ≥ 0 | SKD < 0 | EFLOW ≥ 0 | EFLOW < 0 |
|-------|---------|---------|-----------|-----------|
| > 0 | Flowing wellbore pressure (MPa) | Flowing wellbore pressure (MPa) - injection into rock | Enthalpy (MJ/kg) | Temperature (°C) |
| = 0 | Flow rate (kg/s), Heat only (MJ/s) | Flow rate (kg/s), Heat only (MJ/s) - injection into rock | Enthalpy (MJ/kg) | Temperature (°C) |
| < 0 | Flowing wellbore pressure (MPa) - outflow only | N/A | N/A | N/A |

If EFLOW < 0, then ABS(EFLOW) is interpreted as temperature (°C) and enthalpy is calculated assuming water only. For heat-only problems with EFLOW < 0, the node is in contact with a large heat pipe that supplies heat through impedance AIPED to maintain temperature near ABS(EFLOW). Large AIPED values (~1000) recommended.

## Isothermal Model (with airwater macro)

### Case 1: AIPED = 0 (Constant Mass Rate)

| SKD | EFLOW | Description |
|-----|-------|-------------|
| + | ≥ 0 | SKD = mass source (kg/s), EFLOW = source liquid saturation, Qw = SKD·EFLOW, Qa = SKD·(1-EFLOW) |
| + | < 0 | SKD = mass source (kg/s), ABS(EFLOW) = source air pressure (MPa), Qw = SKD, Qa = 1.0·(Pa - ABS(EFLOW)) |
| - | any | Injection into rock mass |

### Case 2: AIPED > 0 (Constant Pressure)

| SKD | EFLOW | Description |
|-----|-------|-------------|
| any | < 0 | Air only source: Qa = AIPED·(Pa - SKD) |
| any | 0 < EFLOW < 1 | Two-phase source at specified saturation |
| any | = 1 | Water only source: Qw = AIPED·(Pl - SKD) |
| < 0 | any | Water only source (Qa = 0) |

### Case 3: AIPED < 0 (Outflow Only)

| Condition | Description |
|-----------|-------------|
| Pl > SKD | Outflow occurs: Qw = ABS(AIPED)·Rl/μl·(Pl - SKD) |

where Rl is water relative permeability and μl is water viscosity.

## Examples

### Example 1: Non-isothermal
```
flow
   88        88        1      0.050      -25.0         0.
   14       140       14      3.600     -160.0         1.

```
- Node 88: mass flow 0.05 kg/s withdrawn at 25°C (in-place temperature used)
- Nodes 14 to 140 (every 14th): pressure 3.6 MPa held constant at 160°C

### Example 2: Isothermal air-water
```
airwater
    2
 20.0         0.1
flow
   26        52       26     -2.e-3       1.0         0.
    1        27       26       0.1      -0.2       1.e2

```
- Isothermal air-water at 20°C, reference pressure 0.1 MPa
- Nodes 26 and 52: water injected at 2.e-3 kg/s, 100% water saturation
- Nodes 1 and 27: air only source at pressure 0.1 MPa with impedance 100

## Notes

- The parameter interpretation depends heavily on sign combinations
- For constant pressure boundaries, use large AIPED values (10² - 10⁶)
- For heat-only problems, if porosity = 0, only temperature solution exists
- The **boun** macro provides time-dependent boundary conditions
- Multiple flow macro entries can be used in the same input file
