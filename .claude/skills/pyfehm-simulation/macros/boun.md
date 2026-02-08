# boun - Boundary Conditions (Time-Dependent)

**Status**: REQUIRED for flow problems (if macro `flow` is not used)

## Purpose

Implement boundary conditions and sources/sinks with time-dependent and cyclic capabilities. More flexible than `flow` macro for complex boundary condition scenarios.

## Input Format

```
boun
model [N]
KEYWORD_TIME
  NTIMES  TIME(1) TIME(2) ... TIME(NTIMES)
KEYWORD_VAR
  VAR(1) VAR(2) ... VAR(NTIMES)
...
end
JA  JB  JC  MODEL_NUMBER
...
(blank line to end)
```

## Time Keywords

| Keyword | Description |
|---------|-------------|
| `ti` | Time sequence (days) - step function changes |
| `ti_linear` | Time sequence - linear interpolation between times |
| `cy` | Cyclic time sequence - step function, repeats |
| `cy_linear` | Cyclic time sequence - linear interpolation |
| `sec` | Time input in seconds |
| `min` | Time input in minutes |
| `day` | Time input in days (default) |
| `year` | Time input in years |
| `tran` | Activate only after steady state |

## Variable Keywords

### Source/Sink Terms
| Keyword | Description | Units |
|---------|-------------|-------|
| `sw` | Water source rate | kg/s |
| `sa` | Air source rate | kg/s |
| `se` | Enthalpy source | MW |
| `dsw` | Distributed water source | kg/s |
| `dsa` | Distributed air source | kg/s |
| `dse` | Distributed enthalpy source | MW |

### Fixed Value Conditions
| Keyword | Description | Units |
|---------|-------------|-------|
| `pw` | Fixed water pressure | MPa |
| `pa` | Fixed air pressure | MPa |
| `t` | Fixed temperature | °C |
| `en` | Fixed enthalpy | MW |
| `s` | Fixed saturation | - |
| `hd` | Fixed hydraulic head | m |
| `ft` | Fixed flowing temperature | °C |

### Outflow-Only Conditions
| Keyword | Description | Units |
|---------|-------------|-------|
| `pwo` | Fixed pressure (outflow only) | MPa |
| `pao` | Fixed air pressure (outflow only) | MPa |
| `hdo` | Fixed head (outflow only) | m |

### Other
| Keyword | Description | Units |
|---------|-------------|-------|
| `sf` | Seepage face pressure | MPa |
| `sfh` | Seepage face head | m |
| `kx`, `ky`, `kz` | Fixed permeability | m² |
| `if` | Impedance factor | - |
| `ts` | Timestep at time change | days |
| `end` | End of model definition | - |

### Weighting Options for Distributed Sources
| Keyword | Description |
|---------|-------------|
| `wgt` | Weight by nodal control volume |
| `wgtx/y/z` | Weight by control volume / length scale |
| `wgtp` | Weight by volume × permeability |
| `wgtr` | Weight by volume × permeability × relative perm |

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| NTIMES | integer | Number of time changes |
| TIME | real | Times for changes (in specified units) |
| VARIABLE | real | Values at each time |
| MODEL_NUMBER | integer | Model number to assign to nodes |

## Example 1: Cyclic Water Injection

```
boun
model 1
cy
    4         0.0         1.e1        1.e2        1.e5
sw
    -1.e-4    -1.e-5      -1.e-3      -1.e-4
ft
    20.0      50.0        50.0        20.0
model 2
ti
    2         0.0         1.e20
pw
    0.1       0.1
ft
    20.0      20.0
end
   26        26          1           1
   27        27          1           2

```

- Model 1: Cyclic water injection with varying rate and temperature
- Model 2: Fixed pressure boundary at 0.1 MPa
- Node 26 uses model 1, node 27 uses model 2

## Example 2: Distributed Source with Timestep Control

```
boun
model 1
ti
    4         0.0         91.325      182.625     273.9375
ts
    1.0       1.0         1.0         1.0
dsw
    29.248    0.0         29.248      0.
kz
    8e-12     2e-12       8e-12       2e-12
end
  -100       0           0           1

```

- Distributed water source applied to zone 100
- Timestep reset to 1.0 days at each time change
- Permeability also varies with time
