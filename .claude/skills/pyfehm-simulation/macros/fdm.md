# fdm - Finite Difference Grid

**Status**: REQUIRED if macros **coor** and **elem** not used

## Purpose

Finite difference input. Generates regular structured grids without requiring explicit coordinate and element input.

## Input Format

Three modes available based on KEYWORD:

### Block Mode ("block")
```
fdm
block
NX  NY  NZ
X0  Y0  Z0
MB  DX  DY  DZ
...
(blank line to end each direction)
```

### Point Mode ("poin")
```
fdm
poin
NX  NY  NZ
MB  X  (or Y or Z)
...
(blank line to end each direction)
```

### MODFLOW Mode ("modf")
```
fdm
modf
MODCHAR
```

## Parameters

### Group 1 - Keyword

| Variable | Format | Description |
|----------|--------|-------------|
| KEYWORD | character*4 | Format of input: "block", "poin", or "modf" |

### For "modf" Mode

| Variable | Format | Description |
|----------|--------|-------------|
| MODCHAR | character*132 | Name of MODFLOW geometry data file |

### For "block" or "poin" Modes

| Variable | Format | Description |
|----------|--------|-------------|
| NX | integer | Number of divisions in x direction |
| NY | integer | Number of divisions in y direction |
| NZ | integer | Number of divisions in z direction |

### For "block" Mode Only

| Variable | Format | Description |
|----------|--------|-------------|
| X0 | real | Coordinate of x origin point (m) |
| Y0 | real | Coordinate of y origin point (m) |
| Z0 | real | Coordinate of z origin point (m) |
| MB | integer | Division number. If negative, spacing is proportional to assigned spacings. |
| DX | real | Node spacing in x direction (m) |
| DY | real | Node spacing in y direction (m) |
| DZ | real | Node spacing in z direction (m) |

### For "poin" Mode Only

| Variable | Format | Description |
|----------|--------|-------------|
| MB | integer | Division number. If negative, code spaces proportionally. |
| X, Y, Z | real | Coordinate value (m) for each direction |

## Input Structure

Group 4 is repeated for each NX, NY, and NZ:
- All X data are input first
- Followed by Y data
- Followed by Z data
- Each direction terminated by a blank line

## Example

```
fdm
block
    1        1       50
   0.        0.       0.
    1       1.0       þ

    1       1.0

    1       0.002
  -50       0.002

```

In this example using "block" format:
- 1 division in X and Y, 50 divisions in Z
- Origin at (0, 0, 0)
- X direction: 1 division with 1.0 m spacing
- Y direction: 1 division with 1.0 m spacing
- Z direction: 50 divisions each with 0.002 m spacing (proportional)

## Notes

- The fdm macro is an alternative to coor + elem for simple structured grids
- "block" mode is most common for regular grids
- "poin" mode allows specifying exact coordinate locations
- "modf" mode imports MODFLOW geometry
- Total number of nodes = (NX+1) × (NY+1) × (NZ+1) for typical grids
- Node numbering is sequential: X varies fastest, then Y, then Z
- For 2D problems, set the unused direction to 1 division
