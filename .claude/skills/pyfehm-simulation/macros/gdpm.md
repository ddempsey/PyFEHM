# gdpm - Generalized Dual Porosity Model

**Status**: Optional

## Purpose

Data to define parameters in the Generalized Dual Porosity Model formulation. GDPM allows multiple matrix layers with different properties, providing more accurate representation of matrix diffusion than simple dual porosity.

## Input Format

```
gdpm
GDPM_FLAG  NGDPMNODES
NGDPM_LAYERS(I)  VFRAC_PRIMARY(I)  (GDPM_X(I,J), J=1,NGDPM_LAYERS(I))
...
(blank line to end model definitions)

JA  JB  JC  IGDPM
...
(blank line to end)
```

## Parameters

### Group 1 - Model Control

| Variable | Format | Description |
|----------|--------|-------------|
| GDPM_FLAG | integer | Model flag: 0=GDPM not used, 1=parallel fracture geometry, 2=spherical geometry |
| NGDPMNODES | integer | Total number of matrix nodes in simulation |

### Group 2 - Layer Definition (repeated for each model)

| Variable | Format | Description |
|----------|--------|-------------|
| NGDPM_LAYERS(I) | integer | Number of matrix nodes for this model. All primary nodes assigned this model will have NGDPM_LAYERS matrix nodes. |
| VFRAC_PRIMARY(I) | real | Fraction of total control volume assigned to primary (fracture) porosity. The remainder (1-VFRAC_PRIMARY) is divided among dual porosity nodes. |
| GDPM_X(I,J) | real | Matrix discretization distances for the matrix nodes (m). Grid points placed at these values to discretize matrix block. Must be NGDPM_LAYERS values in ascending order. |

### Group 3 - Node Assignment

| Variable | Format | Description |
|----------|--------|-------------|
| JA, JB, JC | integer | Standard node loop |
| IGDPM | integer | Model number from Group 2. Default is 0 (no dual porosity at that primary node). |

## Geometry Types

### GDPM_FLAG = 1 (Parallel Fractures)
- Final GDPM_X value is distance to centerline between fractures
- Matrix diffusion occurs perpendicular to fracture planes

### GDPM_FLAG = 2 (Spherical)
- Fractured medium at exterior of idealized spherical block
- Transport occurs into the block
- Final GDPM_X value is the radius of the sphere

## Node Numbering

- Original nodes (1 to NEQ_PRIMARY) retain their numbers and become fracture nodes
- Matrix nodes are assigned numbers from NEQ_PRIMARY + 1 to NEQ_PRIMARY + NGDPMNODES
- Zone numbers for matrix nodes: ZONE_DPADD + zone number of corresponding fracture node

## Example

```
gdpm
    1                1479
   29    .0001     .001      .002      .003      .004      .006      .009
         .02901    .03901    .04901    .05901    .09902    .19904    .29906
         .39908    .49910    .59912    .69914    .79916    .89918    .99920
        1.4993    1.9994    2.4995    2.9996    3.4997    3.9998    4.4999
        5.0000

    1         0        0        1

```

In this example:
- Parallel fracture geometry (GDPM_FLAG=1)
- 1479 total matrix nodes in simulation
- 29 matrix layers with specified discretization distances
- Volume fraction 0.0001 for primary (fracture) porosity
- Discretization points from 0.001 m to 5.0 m (half-spacing = 5 m)
- Model 1 applied to all primary nodes (node 1, JB=0, JC=0 shortcut)

## Notes

- GDPM provides more accurate matrix diffusion than simple **dual** or **dpdp**
- User must assign rock, hydrologic, and transport properties for matrix nodes
- Zone assignment facilitates property assignment to matrix nodes
- For output, contour files show only primary nodes
- History and .out files report values for both primary and matrix nodes
- The number of matrix layers affects accuracy and computational cost
- Finer discretization near fracture-matrix interface improves accuracy
