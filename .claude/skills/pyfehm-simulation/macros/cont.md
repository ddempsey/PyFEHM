# cont - Contour Plot Data Output

**Status**: Optional

## Purpose

Control contour data output format, timestep intervals, and time intervals for visualization. Supports AVS, TECPLOT, SURFER, and native FEHM formats.

## Input Format

### Simple Format
```
cont
NCNTR  CONTIM
```

### Extended Format
```
cont
ALTC  NCNTR  CONTIM  [time]
CHDUM
...
endcont
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| ALTC | character | Output format: `avs`, `avsx`, `fehm`, `free`, `surf`, `tec` |
| NCNTR | integer | Output every NCNTR timesteps |
| CONTIM | real | Output every CONTIM days |
| KEYWORD | character | Optional `time` - use time in filename instead of call number |

## Output Format Options

| Format | Description |
|--------|-------------|
| `avs` | AVS UCD format |
| `avsx` | AVS Express format |
| `fehm` | FEHM binary format |
| `free` | Free format ASCII |
| `surf` | SURFER format |
| `tec` | TECPLOT format |

## Output Variable Keywords (CHDUM)

Enter one keyword per line, terminated by `endcont` or `end cont`:

| Keyword | Description |
|---------|-------------|
| `formatted` / `f` | ASCII format output |
| `material` / `m` | Material properties |
| `liquid` / `l` | Liquid phase values |
| `vapor` / `va` | Vapor phase values |
| `geo` / `g` | Geometry (coordinates and connectivity) |
| `grid` / `gr` | Grid in tecplot format |
| `concentration` / `c` | Solute concentrations |
| `capillary` / `ca` | Capillary pressure |
| `co2` | CO2 saturation values |
| `density` / `de` | Fluid density |
| `displacement` / `di` | Displacements (stress) |
| `flux` / `fl` | Node flux |
| `fwater` / `fw` | Water fraction |
| `head` / `h` | Hydraulic head |
| `hydrate` / `hy` | Hydrate values |
| `permeability` / `pe` | Permeability field |
| `porosity` / `po` | Porosity field |
| `pressure` / `p` | Pressure values |
| `saturation` / `s` | Saturation values |
| `source` / `so` | Source values |
| `temperature` / `t` | Temperature values |
| `velocity` / `ve` | Darcy velocity |
| `wt` | Water table elevation |
| `xyz` / `x` | Node coordinates |
| `zone` / `z` | Zone numbers |
| `nodit` / `n` | Don't output at dit times |

## Zone-Specific Output

After `zone` keyword:
```
zone
NSURF
IZONE_SURF(1) IZONE_SURF(2) ... IZONE_SURF(NSURF)
```

## Example 1: Simple Binary Output

```
cont
  100       1.e20

```

Output FEHM binary every 100 timesteps and at 1.e20 days.

## Example 2: AVS Format with Multiple Variables

```
cont
avs       100       1.e20
mat
con
liquid
velocity
pressure
temp
formatted
endavs

```

Output AVS format files including:
- Material properties
- Concentrations
- Liquid phase data
- Velocity vectors
- Pressure
- Temperature
- In ASCII format

## Notes

- Contour data output when EITHER interval criterion is satisfied
- Keywords must start in first column
- `geo` and `zone` keywords cannot be used together
- For transport solutions, concentration output requires `nspeci` definition in `trac` macro
