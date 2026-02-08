# rock - Rock Properties

**Status**: REQUIRED

## Purpose

Assign rock density, specific heat, and porosity to nodes in the model. These properties are fundamental to all FEHM simulations.

## Input Format

```
rock
JA  JB  JC  DENRD  CPRD  PSD
...
(blank line to end)
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| JA | integer | First node (or -zone_number for zone assignment) |
| JB | integer | Last node (ignored for zone assignment) |
| JC | integer | Node increment (ignored for zone assignment) |
| DENRD | real | Rock density (kg/m³) |
| CPRD | real | Rock specific heat (MJ/kg·K). If CPRD > 1, the code assumes units are J/(kg·K) and multiplies by 10⁻⁶ |
| PSD | real | Porosity (0-1) |

## Negative Porosity Behavior

If the code encounters a negative porosity, the node at which the negative porosity occurs is effectively removed from the model:
- Geometric connections from that node to other nodes are removed
- The volume associated with the node acts as a barrier to flow
- The node may still be assigned properties but they have no effect on simulation results

## Example

```
rock
    1        140          1       2563.       1010.       0.35

```

In this example:
- Nodes 1 through 140 (increment 1)
- Rock density = 2563 kg/m³
- Rock specific heat = 1010 J/(kg·K) (note: > 1 so interpreted as J/(kg·K))
- Porosity = 0.35 (35%)

## Zone Assignment Example

```
rock
   -1          0          0       2650.       1000.       0.10
   -2          0          0       2500.        800.       0.25

```

In this example:
- Zone 1: density 2650 kg/m³, specific heat 1000 J/(kg·K), porosity 10%
- Zone 2: density 2500 kg/m³, specific heat 800 J/(kg·K), porosity 25%

## Notes

- This macro is always required for FEHM simulations
- Porosity affects storage capacity and transport
- Rock density is used in stress calculations and body force (gravity) calculations
- Specific heat affects thermal response of the system
- For saturated problems, effective properties account for both rock and fluid
- Common rock densities: granite ~2700, sandstone ~2300-2500, shale ~2400-2800 kg/m³
- Common specific heats: 800-1000 J/(kg·K) for most rocks
