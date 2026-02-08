# sol - Solver Specifications

**Status**: Optional

## Purpose

Define the type of solution required and the element integration type. Controls whether a coupled heat-mass solution or heat-only solution is performed.

## Input Format

```
sol
NTT  INTG
```

## Parameters

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| NTT | integer | 1 | Solution type: NTT > 0 = coupled heat-mass solution, NTT ≤ 0 = heat transfer only solution |
| INTG | integer | -1 | Element integration type: INTG ≤ 0 = Lobatto (node point) quadrature, INTG > 0 = Gauss quadrature |

## Integration Types

| INTG Value | Quadrature | Recommended For |
|------------|------------|-----------------|
| ≤ 0 | Lobatto (node point) | Heat and mass problems without stress |
| > 0 | Gauss | Problems requiring stress solution |

## Example

```
sol
    1         -1

```

In this example:
- Coupled heat-mass solution (NTT = 1)
- Lobatto quadrature (INTG = -1), recommended for non-stress problems

## Heat Transfer Only Example

```
sol
    0         -1

```

For pure heat conduction problems without fluid flow.

## Notes

- If not specified, defaults are NTT = 1 (coupled) and INTG = -1 (Lobatto)
- Lobatto quadrature is more efficient for most heat and mass transfer problems
- Gauss quadrature is strongly recommended when using the **strs** macro for stress calculations
- For isothermal problems, NTT = 1 is still appropriate (coupled mass solution)
- Heat-only mode (NTT ≤ 0) ignores fluid flow and solves only the energy equation
