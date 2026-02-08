# rlp - Relative Permeability

**Status**: REQUIRED for two-phase problems

## Purpose

Define relative permeability and capillary pressure models for multiphase flow. Several models are available, selected by the IRLP parameter.

## Input Format

```
rlp
IRLP  RP1  RP2  RP3  ...  (model-dependent parameters)
...
(blank line to end Group 1)
JA  JB  JC  I
...
(blank line to end Group 2)
```

## Parameters

### Group 1 - Model Definition

| Variable | Format | Description |
|----------|--------|-------------|
| IRLP | integer | Relative permeability model type (see models below) |
| RP1-RP16 | real | Model parameters (number depends on IRLP value) |

### Group 2 - Node Assignment

| Variable | Format | Description |
|----------|--------|-------------|
| JA | integer | First node (or -zone_number) |
| JB | integer | Last node |
| JC | integer | Node increment |
| I | integer | Model number (from Group 1 sequence) |

## Available Models

### Model -1: Constant Relative Permeability, Linear Capillary Pressure (4 parameters)

| Parameter | Description |
|-----------|-------------|
| RP1 | Liquid relative permeability (constant, m²) |
| RP2 | Vapor relative permeability (constant, m²) |
| RP3 | Capillary pressure at zero saturation (MPa) |
| RP4 | Saturation at which capillary pressure goes to zero |

### Model 1: Linear Relative Permeability, Linear Capillary Pressure (6 parameters)

| Parameter | Description |
|-----------|-------------|
| RP1 | Residual liquid saturation |
| RP2 | Residual vapor saturation |
| RP3 | Maximum liquid saturation |
| RP4 | Maximum vapor saturation |
| RP5 | Capillary pressure at zero saturation (MPa) |
| RP6 | Saturation at which capillary pressure goes to zero |

### Model 2: Corey Relative Permeability, Linear Capillary Pressure (4 parameters)

| Parameter | Description |
|-----------|-------------|
| RP1 | Residual liquid saturation |
| RP2 | Residual vapor saturation |
| RP3 | Capillary pressure at zero saturation (MPa) |
| RP4 | Saturation at which capillary pressure goes to zero |

### Model 3: van Genuchten Relative Permeability and Capillary Pressure (6 parameters)

Permeabilities represented as function of capillary pressure [rlp(h)].

| Parameter | Description |
|-----------|-------------|
| RP1 | Residual liquid saturation |
| RP2 | Maximum liquid saturation |
| RP3 | Inverse of air entry head, αG (1/m) |
| RP4 | Power n in van Genuchten formula |
| RP5 | Low saturation fitting parameter (multiple of cutoff Pcap) |
| RP6 | Cutoff saturation (must be > RP1) |

### Model 4: van Genuchten, Effective Continuum (15 parameters)

For fracture-matrix effective continuum. Includes separate parameters for matrix (RP1-RP6) and fracture (RP7-RP12), plus permeabilities (RP13-RP15).

### Model 5: van Genuchten [rlp(S)] (6 parameters)

Same as Model 3 but permeabilities are function of saturation rather than capillary pressure.

### Model 6: van Genuchten Effective Continuum [rlp(S)] (15 parameters)

Same as Model 4 but permeabilities as function of saturation.

### Model 7: van Genuchten Effective Continuum with Fracture Interaction (16 parameters)

Same as Model 6 with additional fracture-matrix interaction term (RP16).

### Model 10: Linear with Minimum Relative Permeability (8 parameters)

| Parameter | Description |
|-----------|-------------|
| RP1 | Residual liquid saturation |
| RP2 | Residual vapor saturation |
| RP3 | Maximum liquid saturation |
| RP4 | Maximum vapor saturation |
| RP5 | Minimum liquid permeability (m²) |
| RP6 | Minimum vapor permeability (m²) |
| RP7 | Capillary pressure at zero saturation (MPa) |
| RP8 | Saturation at which capillary pressure goes to zero |

## Example: Corey Model

```
rlp
    2        0.3        0.1        2.0        1.

    1        140          1          1

```

In this example:
- Model 2 (Corey) with residual liquid saturation 0.3, residual vapor saturation 0.1
- Base capillary pressure 2.0 MPa, goes to zero at saturation 1.0
- Applied to nodes 1-140

## Notes

- For models 4, 6, and 7, permeability is isotropic and overwrites **perm** macro input
- Use **fper** macro to introduce anisotropy with models 4, 6, and 7
- The **rlpm** macro provides an alternative, more flexible input format
- van Genuchten parameters often require careful calibration
- Capillary pressure fitting parameters (RP5, RP6) control behavior near zero saturation
- Group 1 is ended with a blank line; model number i is incremented each time a Group 1 line is read
