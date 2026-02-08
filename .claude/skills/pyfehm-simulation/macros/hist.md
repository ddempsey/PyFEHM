# hist - History Output

**Status**: Optional

## Purpose

History data output selection, output timestep intervals, and time intervals. Parameters will be output for nodes specified in the **node** or **nod2** macro in individual files for each parameter selected. If output zones are defined (**node** macro), the output will be a volume weighted average for the zone.

History files are named using the root portion of the history file name (*root_name*.his) provided as input.

## Input Format

Several formats available:

### Simple Keyword Format
```
hist
CHDUM
...
end hist
```

### With Time Control
```
hist
CHDUM  NHIST  HISTIME
...
end hist
```

### Multiple Keywords
```
hist
CHDUM  CHDUM1  ...  CHDUMn
...
end hist
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| CHDUM | character*80 | Keyword specifying output type (see tables below) |
| NHIST | integer | Optional: Output every NHIST timesteps (default=1) |
| HISTIME | real | Optional: Output at time intervals of HISTIME (units from time keyword) |
| CHDUM1...n | character*80 | Optional additional keywords (up to 3) |

## File Format Keywords

| Keyword | Description |
|---------|-------------|
| tecplot | Output using tecplot style headers and format |
| csv / surfer | Output as comma-separated values |

## Time Unit Keywords

| Keyword | Description |
|---------|-------------|
| years | Output time in years |
| days | Output time in days (default) |
| hrs | Output time in hours |
| seconds | Output time in seconds |

## Output Variable Keywords

| Keyword | Output Variable | Units |
|---------|-----------------|-------|
| mpa / pressure | Pressure | MPa |
| deg / temperature | Temperature | °C |
| head / meters | Hydraulic head | m |
| feet | Hydraulic head | ft |
| saturation | Saturation | - |
| wco | Water content | - |
| flow / kgs | Flow rate | kg/s |
| enthalpy | Enthalpy | MJ/kg |
| efl / mjs | Enthalpy flow | MJ/s |
| density | Density | kg/m³ |
| humidity | Relative humidity | - |
| viscosity | Viscosity | Pa·s |
| zflux | Zone fluxes | - |
| concentration | Species concentration | (separate file per species) |
| wt | Water table elevation | m |
| co2s | CO₂ saturations | - |
| co2m | CO₂ mass (total, free, dissolved) | kg |
| cfluxz | CO₂ zone fluxes | - |
| displacements | Displacements | m |
| stress | Stresses | MPa |
| strain | Strain | - |
| rel | Relative permeability table | - |
| global | Global mass/energy balances | - |

## Pressure Sub-Keywords (with mpa/pressure)

| Sub-Keyword | Description |
|-------------|-------------|
| total / water | Total or water pressure |
| air | Air pressure |
| capillary | Capillary pressure |
| co2 | CO₂ pressure |

## Density/Viscosity Sub-Keywords

| Sub-Keyword | Description |
|-------------|-------------|
| water | Water density/viscosity |
| air | Air/vapor density/viscosity |
| co2 | CO₂ density/viscosity |

## Global Sub-Keywords

| Sub-Keyword | Description |
|-------------|-------------|
| mass | Mass balances only (excluding steam) |
| water | Water balances only (excluding steam) |
| steam | Mass/water balance including steam |
| air | Air/vapor balances |
| energy | Energy balances |

## Examples

### Example 1: Time in Years
```
hist
years      100000       50.
deg
end

```
- Output time in years
- Write every 100000 timesteps OR at 50-year intervals
- Output temperature in °C

### Example 2: Multiple Outputs
```
hist
mpa        total        air
deg
global     mass
end

```
- Output pressure (total and air)
- Output temperature
- Output global mass balance
- Data written each timestep, time in days (default)

## Notes

- Keywords must start in column 1
- Keywords are case insensitive
- If no time keyword specified, time output in days
- If no optional keywords used with primary keyword, code determines output based on problem input
- History output named: *root_name_pres.his*, *root_name_temp.his*, etc.
- The named history file contains run information and node/zone list
- Must use **node** or **nod2** macro to specify which nodes to output
