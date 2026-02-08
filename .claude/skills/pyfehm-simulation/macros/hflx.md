# hflx - Heat Flow Boundary Conditions

**Status**: Optional

## Purpose

Heat flow input. Specifies heat flow boundary conditions at nodes.

## Input Format

```
hflx
JA  JB  JC  QFLUX  QFLXM
...
(blank line to end)
```

## Parameters

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop |
| QFLUX | real | 0. | Heat flow (MW) if QFLXM=0, or temperature (°C) if QFLXM≠0 |
| QFLXM | real | 0. | Multiplier for heat flow equation (MW/°C) |

A negative heat flow indicates heat flow **into** the reservoir.

## Physics

### Case 1: QFLXM = 0 (Specified Heat Flow)
```
QH = QFLUX  (MW)
```

### Case 2: QFLXM > 0 (Temperature-Dependent Heat Flow)
Heat flow calculated according to:
```
QH = QFLXM × (T - QFLUX)  (MW)
```
This must be large for large temperature gradients or when a constant temperature must be maintained.

### Case 3: QFLXM < 0 (Fixed Saturation)
QFLUX is interpreted as a fixed saturation and:
```
QH = ABS(QFLXM) × (Sl - QFLUX)  (MW)
```

## Example

```
hflx
  401       410        1     -0.001       0.0

```

In this example:
- Nodes 401 to 410 (every node, JC=1)
- Heat flow of 0.001 MW = 1 kW is being **injected** into the model (negative sign)
- Direct heat flow specification (QFLXM = 0)

## Notes

- Use for specifying basal heat flux, surface heat loss, or heat sources
- For temperature-dependent heat flow, QFLXM acts as a thermal impedance
- Large QFLXM values effectively hold temperature constant
- Sign convention: negative = heat in, positive = heat out
- Heat flow units are MW (megawatts), not W
- For typical geothermal basal heat flux (~60-80 mW/m²), calculate total MW for boundary area
