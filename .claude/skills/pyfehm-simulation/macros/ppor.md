# ppor - Pressure-Dependent Porosity

**Status**: Optional

## Purpose

Model pressure-dependent porosity. Provides three models for relating porosity changes to pressure and/or temperature changes.

## Input Format

```
ppor
IPOROS
JA  JB  JC  POR1  POR2  POR3  POR4
...
(blank line to end)
```

## Parameters

### Group 1

| Variable | Format | Description |
|----------|--------|-------------|
| IPOROS | integer | Model type (see table) |

### Group 2

| Variable | Format | Description |
|----------|--------|-------------|
| JA, JB, JC | integer | Standard node loop |
| POR1-POR4 | real | Model-dependent parameters (see below) |

## Model Types

### Model 1: IPOROS = 1 (Aquifer Compressibility)

Porosity varies with pressure:
```
φ = φ₀ + αₐ(P - P₀)
```

| Parameter | Description |
|-----------|-------------|
| POR1 | Aquifer compressibility αₐ (MPa⁻¹) |

### Model -1: IPOROS = -1 (Specific Storage)

For isothermal conditions, specific storage model:
```
Sₛ = ρg(αₐ + φβ)
```

where:
- ρ = liquid density (kg/m³)
- g = gravity (m/s²)
- αₐ = aquifer compressibility (MPa⁻¹)
- φ = porosity
- β = liquid compressibility (MPa⁻¹)

| Parameter | Description |
|-----------|-------------|
| POR1 | Specific storage Sₛ (m⁻¹) |

### Model -2: IPOROS = -2 (Gangi Model)

"Bed of nails" model for fracture compressibility with stress and temperature effects:
```
φ = φ₀[1 - (Pc/Px)^m]
Pc = σ - P - αE(T - T₀)
```

and permeability varies as:
```
k = k₀(φ/φ₀)³
```

| Parameter | Description |
|-----------|-------------|
| POR1 | Exponent m in Gangi equation |
| POR2 | Px parameter (MPa) |
| POR3 | σ, in-situ stress (MPa) |
| POR4 | αE, product of thermal expansion coefficient and Young's modulus (MPa/°C) |

Note: For isothermal simulations, the thermal term (POR4) does not apply.

## Example

```
ppor
    1
    1         0        0      1.e-2

```

In this example:
- Aquifer compressibility model (IPOROS=1)
- All nodes (JA=1, JB=0, JC=0 shortcut)
- Compressibility of 1.e-2 MPa⁻¹

## Notes

- Model 1 is common for confined aquifer simulations
- Model -1 (specific storage) is standard groundwater formulation
- Model -2 (Gangi) is for fractured rock with stress-dependent aperture
- Porosity changes affect storage and can affect permeability
- For Gangi model, permeability decreases with increasing effective stress
- Specific storage values typically range from 1e-6 to 1e-4 m⁻¹
- Aquifer compressibility typically ranges from 1e-4 to 1e-2 MPa⁻¹
