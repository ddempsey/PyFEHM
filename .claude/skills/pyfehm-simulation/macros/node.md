# node - Node Output Selection

**Status**: Optional

## Purpose

Specify the node numbers for which detailed output is desired. The **node** macro has been modified to allow multiple instances (results are cumulative) and to allow definition of "output zones" for use with macro **hist**.

Only a single input format/keyword can be used for each instance of the node macro.

## Input Format

### Format 1: Direct Node List
```
node
M
MN(1)  MN(2)  ...  MN(M)
X  Y  Z  (for each MN < 0)
```

### Format 2: Block Specification
```
node
block
JA  JB  JC
...
(blank line to end)
```

### Format 3: Output Zone Specification
```
node
azone
JA  JB  JC
...
(blank line to end)
```

## Parameters

### Format 1 Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| M | integer | Number of nodes for output. If M ≤ 0, pressure and temperature written to output for all nodes but no nodal values in history files. |
| MN | integer | Node numbers for output. If MN(I) < 0, coordinates are used to find closest node. |
| X, Y, Z | real | Coordinates for finding closest node (one line for each MN < 0). For 2D, set Z = 0. |

### Format 2 & 3 Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| KEYWORD | character*5 | 'block' for JA,JB,JC node specification, 'azone' for output zone specification |
| JA, JB, JC | integer | Standard node loop (or zone number if negative) |

## Output Zones

The 'azone' keyword allows a single node to be included in multiple output zones. Output zones are used with the **hist** macro to produce volume-weighted averages.

## Examples

### Example 1: Two Specific Nodes
```
node
    2
   50        88

```
Output for nodes 50 and 88.

### Example 2: Node by Coordinates
```
node
    2
   50       -88
  100.     1000.        0.

```
Output for node 50 and the node closest to coordinates (100, 1000, 0) m.

### Example 3: Block of Nodes
```
node
block
    1       100       10
   -3         0        0

```
Output for nodes 1, 11, 21, 31, 41, 51, 61, 71, 81, 91 and for nodes defined by zone 3.

### Example 4: Output Zones
```
node
azone
    1       100       10
   -3         0        0

```
First output zone contains nodes 1, 11, 21, 31, 41, 51, 61, 71, 81, 91.
Second output zone contains nodes from zone 3.

## Notes

- Multiple node macro calls are cumulative
- Use M ≤ 0 to get full output without specifying individual nodes
- History output (**hist** macro) requires nodes to be selected via **node**
- Output zones enable volume-weighted averaging in history output
- Zone numbers are specified as negative JA values
- For 2D problems, Z coordinate is typically set to 0
- Node output goes to the .outp file at each print interval
