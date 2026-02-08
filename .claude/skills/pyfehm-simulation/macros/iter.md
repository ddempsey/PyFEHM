# iter - Iteration Parameters

**Status**: Optional (but recommended)

## Purpose

Control parameters for the linear equation solver and Newton-Raphson iteration. If unfamiliar with the FEHM linear equation solver routines, this macro should not be used.

## Input Format

```
iter
G1  G2  G3  TMCH  OVERF
IRDOF  ISLORD  IBACK  ICOUPL  RNMAX
```

## Parameters

### Group 1 - Solver Tolerances

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| G1 | real | 1.e-6 | Multiplier for linear convergence region of Newton-Raphson iteration |
| G2 | real | 1.e-6 | Multiplier for quadratic convergence region of Newton-Raphson iteration |
| G3 | real | 1.e-3 | Multiplier relating Newton-Raphson residuals to stopping criteria for linear solver |
| TMCH | real | 1.e-9 | Machine tolerance. If TMCH > 0, convergence by residual norm. If TMCH < 0, ABS(TMCH) is tolerance for each equation at each node. |
| OVERF | real | 1.1 | Over-relaxation factor for passive nodes in adaptive implicit method |

### Group 2 - Solver Control

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| IRDOF | integer | 0 | Reduced degree of freedom method (see table) |
| ISLORD | integer | 0 | Reordering parameter for equation ordering (see table) |
| IBACK | integer | 0 | SOR iterations: 0=none before solver, 1=SOR before solver, 2=SOR before solver and solver called twice |
| ICOUPL | integer | 0 | Number of SOR iterations in reduced degree of freedom methods |
| RNMAX | real | 1.0e+11 | Maximum CPU running time (minutes) before solution stops |

## Stopping Criteria Formula

The completion criteria for the linear solver is:

```
EPE = G3 × max(TMCH, max(F0, min(G1×SQRT(R²), G2×R²)))
```

where R² is the sum-squared of equation residuals, and F0 is SQRT(R0²)×EPM for the first iteration (EPM from **ctrl** macro).

## IRDOF Values

| IRDOF | Description |
|-------|-------------|
| 0 | Reduced degrees of freedom not required |
| 1 | Reduced DOF from 3 to 2 or 3 to 1 |
| 2 | Reduced DOF from 3 to 2 |
| 11 | Air only solution for isothermal air-water |
| -11 | Residual for air equation ignored with **airwater** |
| 13 | Liquid only solution for **airwater** |

## ISLORD Values - Equation Ordering

| ISLORD | 2 DOF | 3 DOF | 4 DOF | 6 DOF |
|--------|-------|-------|-------|-------|
| 0 | 1,2 | 1,2,3 | 1,2,3,4 | 1,2,3,4,5,6 |
| 1 | 2,1 | 1,3,2 | 1,3,2,4 | 1,4,2,5,3,6 |
| 2 | - | 2,1,3 | - | - |
| 3 | - | 2,3,1 | - | - |

Equations: 1=mass(water), 2=heat, 3=air. For double permeability, fracture equations precede matrix equations.

## Example

```
iter
   1.e-5      1.e-5      1.e-5      1.e-9        1.2
       1          0          0          2      200.0

```

In this example:
- Linear and quadratic convergence multipliers: 1.e-5
- Adaptive-implicit tolerance: 1.e-5
- Machine tolerance: 1.e-9
- Over-relaxation factor: 1.2
- Reduced DOF enabled (IRDOF=1)
- No reordering (ISLORD=0)
- No SOR before solver (IBACK=0)
- 2 SOR iterations for reduced DOF (ICOUPL=2)
- Max run time: 200 CPU minutes

## Notes

- TMCH < 0 (recommended) uses tolerance at each node for better convergence checking
- Reduced DOF can significantly speed up calculations for certain problem types
- RNMAX prevents runaway simulations
- Default values work for most problems
- Increase G1, G2, G3 for tighter convergence (slower but more accurate)
- Over-relaxation (OVERF > 1) can speed convergence for well-behaved problems
