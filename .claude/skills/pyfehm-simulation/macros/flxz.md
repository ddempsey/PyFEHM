# flxz - Zone Flow Output

**Status**: Optional

## Purpose

Output total flow through a zone. When invoked, the following output is given at every heat and mass transfer time step:
- Sum of all source flow rates for each zone
- Sum of all sink flow rates for each zone
- Net quantity passing through each zone
- Net source/sink quantity for each zone

## Input Format

```
flxz [KEYWORD]
NFLXZ
IFLXZ(1)  IFLXZ(2)  ...  IFLXZ(NFLXZ)
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| KEYWORD | character | Optional: 'liquid mass', 'vapor mass', 'thermal energy' to specify output type. Default outputs all active quantities. |
| NFLXZ | integer | Number of zones for which output is written |
| IFLXZ | integer | Zone numbers for which water mass flow output is written (NFLXZ zones) |

## Keywords

| Keyword | Output |
|---------|--------|
| liquid mass | Liquid mass flow rates only |
| vapor mass | Vapor mass flow rates only |
| thermal energy | Thermal energy flow rates only |
| (none) | All active quantities in simulation |

## Example

```
flxz water
    3
    1         6        10

```

In this example:
- Water (liquid mass) flow output requested
- 3 zones for output
- Output for zones 1, 6, and 10

## Output

For each specified zone at each timestep, output includes:
- Total source rate (kg/s or MW for energy)
- Total sink rate (kg/s or MW for energy)
- Net rate through zone boundary
- Net source/sink within zone

## Notes

- Zones must be defined using the **zone** macro prior to using this macro
- Useful for monitoring mass/energy balance across zone boundaries
- Helps verify boundary conditions and identify leakage paths
- Output written to the main output file (.outp)
- Multiple zones can be monitored simultaneously
- Keywords must follow the macro name on the same line
