# dual - Dual Porosity Formulation

**Status**: Optional

## Purpose

Dual porosity formulation. There are three sets of parameter values at any nodal position:
- Nodes 1 to N represent the fracture nodes
- Nodes N+1 to 2N the first matrix material
- Nodes 2N+1 to 3N the second matrix material

When zones are used with the **dual** macro, additional zones are automatically generated. See instructions for the macro **zone** for a more detailed description.

The **dual** parameters are only defined for the first N nodes.

## Input Format

```
dual
IDUALP
JA  JB  JC  VOLFD1
JA  JB  JC  VOLFD2
JA  JB  JC  APUVD
```

## Parameters

### Group 1 - Solution Control

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| IDUALP | integer | | Solution descriptor: 0=information read but not used, ≠0=dual porosity solution implemented. For IDUALP=2, permeabilities and conductivities are scaled by volume fraction (k = vf * k). |

### Group 2 - Fracture Volume Fraction

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop |
| VOLFD1 | real | 0.001 | Volume fraction for fracture portion of the continuum |

### Group 3 - First Matrix Volume Fraction

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop |
| VOLFD2 | real | 0.5 | Volume fraction for the first matrix portion of the continuum |

### Group 4 - Matrix Length Scale

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop |
| APUVD | real | 5.0 | Length scale for the matrix nodes (m) |

## Physics

The volume fractions are related to the total volume by:

```
VOLFD1 + VOLFD2 + VOLFD3 = 1.0
```

where VOLFD3 is the volume fraction of the second matrix node.

If permeability model IRLP = 4 is selected in control statement **rlp**, VOLFD1 is calculated from RP15 (fracture porosity) in that control statement.

## Example

```
dual
    1
    1        140        1       0.006711409

    1        140        1       0.335570470

    1        140        1        0.10

```

In this example:
- Dual porosity solution is implemented for all nodes 1-140
- Volume fraction for fractures is ~0.67%
- Volume fraction for first matrix portion is ~33.6%
- Implied second matrix fraction is ~65.7%
- Length scale for matrix nodes is 0.1 m

## Notes

- Creates two additional sets of nodes for matrix continua
- Original nodes (1 to N) become fracture nodes
- First set of new nodes (N+1 to 2N) become first matrix nodes
- Second set of new nodes (2N+1 to 3N) become second matrix nodes
- Properties must be defined for all three continua
- Use **dpdp** for simpler double porosity without the third continuum
