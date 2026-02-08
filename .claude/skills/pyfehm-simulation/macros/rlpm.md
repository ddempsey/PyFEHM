# rlpm - Relative Permeability (Alternative Input)

**Status**: Optional (alternative to rlp)

## Purpose

Alternative input format for relative permeability and capillary pressure. Provides a more flexible, keyword-based input structure compared to the **rlp** macro.

## Input Format

```
rlpm
group  IGROUP
PHASE  MODEL  [parameters...]
...
cap  COUPLING  MODEL  [parameters...]
end
JA  JB  JC  IGROUP
...
(blank line to end)
```

## Keywords

### Phase Keywords

| PHASE | Description |
|-------|-------------|
| water | Liquid water phase |
| vapor | Steam/vapor phase |
| air | Air phase |
| fracture | Fracture continuum (for dual permeability) |

### Relative Permeability Models

| MODEL | Parameters | Description |
|-------|------------|-------------|
| linear | SLR, SLM | Linear model: residual saturation, max saturation |
| corey | SLR, SGR | Corey model: liquid residual, gas residual saturation |
| same | (none) | Same as previous phase |
| vg_cap | SLR, SLM, ALPHA, N, PMAX | van Genuchten as function of capillary pressure |
| vg_sat | SLR, SLM, ALPHA, N | van Genuchten as function of saturation |

### Capillary Pressure Models

| MODEL | Parameters | Description |
|-------|------------|-------------|
| linear | SLC, PCMAX | Linear: saturation cutoff, max capillary pressure |
| linear_for | SLC, PCMAX | Linear with forced drainage |
| vg_cap | SLR, SLM, ALPHA, N, PMAX, SLC, [PCMAX] | van Genuchten |

### Phase Coupling (cap keyword)

| COUPLING | Description |
|----------|-------------|
| air/water | Air-water system |
| water/co2_liquid | Water-liquid CO2 |
| water/co2_gas | Water-gaseous CO2 |
| co2_liquid/co2_gas | Liquid CO2-gaseous CO2 |
| water/vapor | Water-steam |
| air/vapor | Air-steam |

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| IGROUP | integer | Group number for this model set |
| SLR | real | Residual liquid saturation |
| SGR | real | Residual gas saturation |
| SLM | real | Maximum liquid saturation |
| ALPHA | real | van Genuchten alpha parameter (1/m) |
| N | real | van Genuchten n parameter |
| PMAX | real | Maximum capillary pressure (MPa) |
| SLC | real | Saturation cutoff for capillary pressure |
| PCMAX | real | Capillary pressure at zero saturation (MPa) |

## Example: Corey Model

```
rlpm
group       1
water       corey       0.3        0.1
vapor       same
end
    1        140          1          1

```

This example uses Corey relative permeability with residual liquid saturation 0.3 and residual gas saturation 0.1, applied to nodes 1-140.

## Example: Linear Model with Capillary Pressure

```
rlpm
group       1
water       linear      0.3        1.0
air         linear      0.3        1.0
cap         air/water   linear_for   93.6      100.
end
    1          0          0          1

```

## Example: van Genuchten with Fracture

```
rlpm
group       1
water       vg_cap      0.0212     1.0      0.00715    1.62
fracture                0.03       1.0     12.05       3.00      4.06e-09   2.04e-18   2.93e-04   0.
air         same
cap         air/water   vg_cap     0.0212   1.0        0.00715   1.62       2.         0.0312
fracture                0.03       1.0     12.05       3.00      20.0       0.0001
end
   -1          0          0          1

```

## Example: Table Input

```
rlpm
group       1
water       corey       0.3        0.1
vapor       same
group       2
table       1           4          water      vapor      water/vapor
file
input/doe_rlpm.table
end
    1        140          1          2

```

The table file contains saturation vs relative permeability and capillary pressure data.

## Notes

- The **rlpm** macro is more readable than **rlp** for complex models
- Multiple groups can be defined in one macro call
- The "fracture" keyword enables dual permeability models
- Use "same" to apply identical parameters to multiple phases
- Table input allows arbitrary saturation functions from external files
- Zone assignment uses standard JA/JB/JC format (negative JA for zones)
- The "end" keyword terminates the group definitions

