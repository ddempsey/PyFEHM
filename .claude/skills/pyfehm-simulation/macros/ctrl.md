# ctrl - Program Control Parameters

**Status**: REQUIRED

## Purpose

Assign various control parameters needed for equation solvers and matrix solver routines. Suggested values for the control parameters are shown in `{}` in the table.

## Input Format

```
ctrl
MAXIT  EPM  NORTH  MAXSOLVE  ACCM
JA  JB  JC  NAR
AAW  AGRAV  UPWGT
IAMM  AIAA  DAYMIN  DAYMAX
ICNL  LDA
```

## Parameters

### Group 1 - Solver Control

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| MAXIT | integer | {10} | Maximum number of iterations for Newton cycle. If MAXIT < 0 then max iterations is ABS(MAXIT) but minimum is set to 2. |
| EPM | real | {1.e-5} | Tolerance for Newton cycle (nonlinear equation tolerance). Note: EPM gets overwritten by TMCH in ITER macro if defined. |
| NORTH | integer | {8 for gmre, 1 for bcgs} | Number of orthogonalizations in linear equation solver. Increase for complicated problems (e.g., 80 for fully coupled stress). |
| MAXSOLVE | integer | {100} | Maximum number of solver iterations per Newton iteration. |
| ACCM | character*4 | | Acceleration method: `bcgs` (biconjugate gradient stabilized) for isothermal saturated flow, `gmre` (generalized minimum residual) for all other problems. |

### Group 2 - Node Loop

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| JA, JB, JC | integer | | Standard node loop (JA=first, JB=last, JC=increment) |
| NAR | integer | {1} | Order of partial Gauss elimination (1 or 2 recommended). Larger values increase memory but may be necessary for convergence. |

### Group 3 - Numerical Scheme

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| AAW | real | {1} | Implicitness factor. AAW ≤ 1 uses standard implicit. AAW > 1 uses second-order implicit. |
| AGRAV | integer | | Direction of gravity: 0=none, 1=X, 2=Y, 3=Z. Uses 9.81 m/s² when AGRAV ≠ 0. |
| UPWGT | real | {1.0} | Upstream weighting. Values < 0.5 set to 0.5, values > 1.0 set to 1.0. |

### Group 4 - Time Stepping

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| IAMM | integer | {7-10} | Max iterations for which timestep will multiply. If exceeded, timestep not increased. Set IAMM ≤ MAXIT. |
| AIAA | real | 1 | Time step multiplier {1.2-2.0} |
| DAYMIN | real | 1.0e-05 | Minimum time step size (days) |
| DAYMAX | real | 30.0 | Maximum time step size (days) |

### Group 5 - Geometry and Storage

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| ICNL | integer | | Geometry: 0=3D, 1=X-Y plane, 2=X-Z plane, 3=Y-Z plane, 4=X-Y radial (radius=X), 5=X-Z radial (radius=X), 6=Y-Z radial (radius=Y) |
| LDA | integer | 0 | External storage of geometric coefficients (-2 to +8, see notes) |

## LDA Values

| LDA | Description |
|-----|-------------|
| -2 | Coefficients calculated and saved unformatted on file |
| -1 | Coefficients calculated and saved formatted on file |
| 0 | Coefficients calculated and not saved |
| +1 | Coefficients read from file, not calculated |
| +2 | Coefficients read unformatted from file |
| +5 | Coefficients read from file, re-saved unformatted |
| +6 | Coefficients read from file, re-saved formatted |
| +7 | Coefficients read unformatted, re-saved unformatted |
| +8 | Coefficients read unformatted, re-saved formatted |

Note: If LDA > 0, the `nfinv` macro is ignored as well as information from `elem` and `coor`.

## Example

```
ctrl
   40        1.e-7        8        24        gmre
    1         140        1         1

  1.0         0.0       1.0
   40         1.2       0.1       60.0
    1           0

```

This example:
- Max 40 Newton iterations, tolerance 1.e-7
- 8 orthogonalizations in linear solver, max 24 solver iterations
- Using gmre acceleration method
- NAR=1 for nodes 1-140
- Standard implicit (AAW=1), no gravity, full upstream weighting
- Time step multiplies after 40 iterations, multiplier 1.2
- Min timestep 0.1 days, max 60 days
- 2D X-Y plane geometry (ICNL=1), coefficients calculated and not saved

## Notes

- For older input files where MAXSOLVE and ACCM not input, defaults are ACCM=gmre and MAXSOLVE=3*NORTH
- The ctrl macro is required for every FEHM simulation
- GMRE is recommended for most problems; BCGS for isothermal steady-state saturated flow
