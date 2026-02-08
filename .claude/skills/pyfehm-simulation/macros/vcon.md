# vcon - Variable Thermal Conductivity

**Status**: Optional

## Purpose

Define variable thermal conductivity as a function of temperature or saturation. Useful for modeling salt formations and other materials with temperature-dependent thermal properties.

## Input Format

```
vcon
IVCON  VC1F  VC2F  VC3F
...
(blank line to end Group 1)
JA  JB  JC  IVCND
...
(blank line to end Group 2)
```

## Parameters

### Group 1 - Model Definition

| Variable | Format | Description |
|----------|--------|-------------|
| IVCON | integer | Conductivity model type |
| VC1F | real | Model parameter 1 (depends on IVCON) |
| VC2F | real | Model parameter 2 (depends on IVCON) |
| VC3F | real | Model parameter 3 (depends on IVCON) |

### Group 2 - Node Assignment

| Variable | Format | Description |
|----------|--------|-------------|
| JA | integer | First node (or -zone_number) |
| JB | integer | Last node |
| JC | integer | Node increment |
| IVCND | integer | Model number (from Group 1 sequence) |

## Thermal Conductivity Models

### Model 1: Linear Temperature Variation

Thermal conductivity varies linearly with temperature:

λ = VC1F + VC2F × (T - VC3F)

| Parameter | Description |
|-----------|-------------|
| VC1F | Reference conductivity at T = VC3F (W/m·K) |
| VC2F | Temperature coefficient (W/m·K·°C) |
| VC3F | Reference temperature (°C) |

### Model 2: Square Root Saturation Variation

Thermal conductivity varies with square root of liquid saturation:

λ = VC1F × √(Sl)

| Parameter | Description |
|-----------|-------------|
| VC1F | Fully saturated conductivity (W/m·K) |
| VC2F | Not used |
| VC3F | Not used |

### Salt Formation Models

For intact and crushed salt, FEHM implements specialized formulas:

**Intact salt:**
λ_IS = λ_IS,300 × (300/T)^γ₁

**Crushed salt:**
λ_CS = λ_CS,300 × (300/T)^γ₁

where:
λ_CS,300 = 1.08 × (α₄φ⁴ + α₃φ³ + α₂φ² + α₁φ + α₀)

Parameters include λ_IS,300, γ₁, γ₂, α₄, α₃, α₂, α₁, α₀, and specific heat of salt.

## Example: Linear Temperature Dependence

```
vcon
    1       2.5      -0.003      25.0

    1        100          1          1

```

In this example:
- Model 1 (linear with temperature)
- Reference conductivity 2.5 W/m·K at 25°C
- Conductivity decreases 0.003 W/m·K per degree
- Applied to nodes 1-100

## Example: Saturation Dependence

```
vcon
    2       3.0       0.0        0.0

   -1          0          0          1

```

In this example:
- Model 2 (square root of saturation)
- Fully saturated conductivity 3.0 W/m·K
- Applied to zone 1

## Example: Multiple Models

```
vcon
    1       2.5      -0.003      25.0
    2       3.5       0.0        0.0

    1         50          1          1
   51        100          1          2

```

This example:
- Model 1 for nodes 1-50 (temperature-dependent)
- Model 2 for nodes 51-100 (saturation-dependent)

## Notes

- Model numbers are assigned sequentially as Group 1 lines are read
- Group 1 is terminated by a blank line
- The vcon macro modifies the thermal conductivity assigned in the **cond** macro
- For most problems, constant conductivity from **cond** is sufficient
- Temperature-dependent conductivity is important for salt formations
- Saturation-dependent conductivity captures wet/dry thermal contrasts
- Zone-based assignment uses negative JA values

