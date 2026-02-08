# cflx - Solute Molar Flow Through Zone

**Status**: Optional

## Purpose

Output total moles of liquid solute moving through specified zones. Vapor solute molar flows are currently not available.

## Output Generated

At every solute timestep, outputs:
- Sum of all solute source flow rates for each zone
- Sum of all solute sink rates for each zone
- Sum of all solute entering each zone
- Sum of all solute leaving each zone
- Net source/sink (boundary) solute flow for each zone

## Input Format

```
cflx [OPTIONS]
CFLXZ
ICFLXZ(1) ICFLXZ(2) ... ICFLXZ(CFLXZ)
```

## Options on Macro Line

Specify which flows to output (space-separated on macro line):

| Option | Description |
|--------|-------------|
| 1 | Source |
| 2 | Sink |
| 3 | Net in |
| 4 | Net out |
| 5 | Boundary |

If no options specified, all five values are output.

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| CFLXZ | integer | Number of zones for output |
| ICFLXZ | integer | Zone numbers for output (CFLXZ values) |

## Prerequisites

- Zones must be defined using macro `zone` prior to using this macro

## Example

```
cflx
    3
    1         6        10

```

Output solute flow information (all five values) through zones 1, 6, and 10.

### With Options

```
cflx 1 3 5
    2
    5        12

```

Output only source (1), net in (3), and boundary (5) flows for zones 5 and 12.

## Notes

- Useful for mass balance analysis
- Only liquid phase solute tracking
- Output appears in the output file at each solute timestep
