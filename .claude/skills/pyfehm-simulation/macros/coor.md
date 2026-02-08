# coor - Node Coordinate Data

**Status**: REQUIRED (if macro `fdm` is not used)

## Purpose

Define node coordinates for the finite element mesh. These data are usually created by a mesh generation program, then cut and copied into the input file or a separate geometry data input file. The mesh must be a right-handed coordinate system.

## Input Format

```
coor
N
MB  CORD1  CORD2  CORD3
...
(blank line to end)
```

## Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| N | integer | Number of nodes in the grid |
| MB | integer | Node number. If MB < 0, the difference between abs(MB) and the previously read abs(MB) is used to generate intermediate values by interpolation |
| CORD1 | real | X-coordinate of node MB (m) |
| CORD2 | real | Y-coordinate of node MB (m) |
| CORD3 | real | Z-coordinate of node MB (m) |

## Notes

- X, Y, and Z coordinates must be entered even if problem is not 3D
- Version 2.30+ supports formatted or unformatted coordinate files
- Negative node numbers trigger linear interpolation between specified nodes
- Section is terminated by a blank line

## Example

```
coor
   140
     1       0.         200.           0.
     2      20.         200.           0.
    -7      100.        200.           0.
     8       0.         180.           0.
    -14     100.        180.           0.
   140     100.           0.           0.

```

In this example:
- 140 total nodes
- Node 1 at (0, 200, 0) meters
- Nodes 3-7 are interpolated between nodes 2 and 7
- Negative node numbers indicate interpolation should fill gaps
