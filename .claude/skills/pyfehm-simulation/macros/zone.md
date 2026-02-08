# zone - Zone Definitions

**Status**: Optional but commonly used

## Purpose

Define geometric regions (zones) for convenient parameter assignment. Zones allow properties to be assigned to groups of nodes based on their spatial location rather than node numbers.

## Input Format

### Standard Format (3D - 8 corner points)

```
zone
IZONE
X1  X2  X3  X4  X5  X6  X7  X8
Y1  Y2  Y3  Y4  Y5  Y6  Y7  Y8
Z1  Z2  Z3  Z4  Z5  Z6  Z7  Z8
...
(blank line to end)
```

### Standard Format (2D - 4 corner points)

```
zone
IZONE
X1  X2  X3  X4
Y1  Y2  Y3  Y4
...
(blank line to end)
```

### Alternate Formats

```
zone
IZONE
list
XG  YG  [ZG]
...
(blank line to end coordinates)
```

```
zone
IZONE
nnum
NIN  NODE(1)  NODE(2)  ...  NODE(NIN)
```

```
zone
IZONE
xylist
TOL_ZONE  ZXY_MIN  ZXY_MAX
X  Y
...
(blank line to end coordinates)
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| IZONE | integer | Zone identification number |
| X1-X8 | real | X coordinates defining zone corners (m) |
| Y1-Y8 | real | Y coordinates defining zone corners (m) |
| Z1-Z8 | real | Z coordinates defining zone corners (m) |
| MACRO | character | Alternate input format: "list", "nnum", or "xylist" |
| XG, YG, ZG | real | Coordinates of node to include in zone (list format) |
| NIN | integer | Number of nodes in zone (nnum format) |
| NODE(i) | integer | Node numbers to include (nnum format) |
| TOL_ZONE | real | Column radius for xylist option (m) |
| ZXY_MIN | real | Minimum Z coordinate for xylist (m) |
| ZXY_MAX | real | Maximum Z coordinate for xylist (m) |

## Usage in Other Macros

Once zones are defined, they can be referenced in property macros using negative JA values:

```
perm
   -1          0          0       1.e-15      1.e-15      1.e-15
```

This assigns properties to zone 1 (JA = -1).

## Example: 2D Zones

```
zone
   1
    0.00     1000.00     1000.00       0.00
 1075.00     1074.00     1079.00    1080.00
   2
    0.000     1000.00     1000.00       0.00
  870.000      869.000     1074.00    1075.00

```

## Example: Using nnum Keyword

```
zone
   7
nnum
    1        100
   8
list
    0.          0.

```

Zone 7 consists of a single node (node 100).
Zone 8 consists of the node closest to coordinates (0, 0).

## Example: Using xylist for Columns

```
zone
    1
xylist
    0.5          0.        1000.
    0.          0.
    0.          1.0
    0.          1.5
    0.          2.0
    0.          3.0

```

Zone 1 includes all nodes within radius 0.5m of the listed XY coordinates, from Z=0 to Z=1000m.

## Notes

- The **zone** macro must precede any usage of zone references
- Zone can be called more than once; when reused, all previous zone definitions are cleared
- A node may be included in only one zone at a time
- Boundaries defined by coordinates may include nodes slightly outside due to volume from adjacent elements
- For **dpdp** and **dual** macros, zones 101-200 are automatically generated for matrix nodes
- Use the input check file (.chk) to verify zone assignments
- The **zonn** macro is similar but retains previous zone definitions between calls
