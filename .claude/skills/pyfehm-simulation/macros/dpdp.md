# dpdp - Double Porosity/Double Permeability

**Status**: Optional

## Purpose

Double porosity / double permeability formulation. There are two sets of parameter values at any nodal position: nodes 1 to N represent the fracture nodes and nodes N+1 to 2N the matrix material. When zones are used with the **dpdp** macro, additional zones are automatically generated. See instructions for the macro **zone** for a more detailed description.

The **dpdp** parameters are only defined for the first N nodes.

## Input Format

```
dpdp
IDPDP
JA  JB  JC  VOLFD1
JA  JB  JC  APUV1
```

## Parameters

### Group 1 - Solution Control

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| IDPDP | integer | | Solution descriptor: 0=information read but not used, ≠0=dpdp solution implemented |

### Group 2 - Volume Fraction

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop |
| VOLFD1 | real | 1.0 | Volume fraction for fracture node |

### Group 3 - Spacing

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop |
| APUV1 | real | 10.0 | Half spacing between fractures (m). See TRANSFLAG in macros **mptr** and **ptrk**. |

## Physics

The volume fraction VOLFD1 is related to the total volume by:

```
VOLFD1 + VOLFD2 = 1.0
```

where VOLFD2 is the volume fraction of the matrix node.

If permeability model IRLP = 4 is selected in control statement **rlp**, VOLFD1 is calculated from RP15 (fracture porosity) in that control statement.

## Example

```
dpdp
    1
    1        140        1       0.005

    1        140        1        0.10

```

In this example:
- Dual porosity/permeability solution is implemented for all nodes 1-140
- Fractional volume in the fractures is 0.005 (0.5% of total volume)
- Half spacing between fractures (length scale for matrix nodes) is 0.1 m

## Notes

- The dpdp macro creates a duplicate set of nodes for the matrix continuum
- When using zones with dpdp, matrix zones are automatically created
- Original nodes (1 to N) become fracture nodes
- New nodes (N+1 to 2N) become matrix nodes
- Rock, perm, and other properties must be defined for both fracture and matrix nodes
