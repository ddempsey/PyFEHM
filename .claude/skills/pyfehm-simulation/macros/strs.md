# strs - Stress Calculations

**Status**: Optional

## Purpose

Enable stress and displacement calculations coupled with heat and mass transfer. Supports elastic and nonlinear material models with various boundary conditions.

## Input Format

```
strs
ISTRS  IHMS
[keywords and parameters]
...
tolerance
STRESS_TOL
end stress
```

## Control Parameters

| Variable | Format | Default | Description |
|----------|--------|---------|-------------|
| ISTRS | integer | | Stress solution flag: >0 enables stress |
| IHMS | integer | | Coupling flag: >0 couples stress with heat-mass equations |

## Keywords

### initcalc
Calculate initial stresses and displacements before simulation starts.

### bodyforce
Apply body force due to gravity. Requires direction of gravity = 3 in **ctrl** macro.

### strainout
Output optional strain information to output files.

### fem
Use finite element module for stress calculations (recommended).

### elastic
Use linear elastic material model.

```
elastic
JA  JB  JC  YOUNGS  POISSONS
```

| Variable | Format | Description |
|----------|--------|-------------|
| YOUNGS | real | Young's modulus (MPa) |
| POISSONS | real | Poisson's ratio |

### nonlinear
Use nonlinear material model with temperature-dependent properties.

```
nonlinear
NLINES
FILENAME
```

| Variable | Format | Description |
|----------|--------|-------------|
| NLINES | integer | Number of lines in property file |
| FILENAME | character | File containing E vs T data |

### biot
Apply Biot coefficient for poroelasticity.

```
biot
JA  JB  JC  ALPHA_BIOT  PCOLLAPSE
```

| Variable | Format | Description |
|----------|--------|-------------|
| ALPHA_BIOT | real | Biot coefficient (typically 0-1) |
| PCOLLAPSE | real | Pore collapse pressure (MPa), 0 to disable |

### stressboun
Define stress/displacement boundary conditions.

```
stressboun
JA  JB  JC  BOUNVAL  KQ
```

| Variable | Format | Description |
|----------|--------|-------------|
| BOUNVAL | real | Boundary value (displacement in m, or stress in MPa) |
| KQ | integer | Direction: 1/-1=x, 2/-2=y, 3/-3=z. Positive=displacement, negative=stress |

### Sub-keywords for stressboun

| Keyword | Description |
|---------|-------------|
| distributed | Distribute force proportional to area |
| lithostatic | Apply lithostatic stress (vertical direction) |
| lithograd | Apply stress gradient with depth |

For `lithograd`:
```
stressboun
lithograd  SDEPTH  GDEPTH
JA  JB  JC  BOUNVAL  KQ
```

| Variable | Format | Description |
|----------|--------|-------------|
| SDEPTH | real | Depth from surface to reference level (m) |
| GDEPTH | real | Z-coordinate of reference level in model (m) |

### tolerance
Set convergence tolerance for stress solution.

```
tolerance
STRESS_TOL
```

| Variable | Format | Description |
|----------|--------|-------------|
| STRESS_TOL | real | >0: reduction factor for residual, <0: absolute residual tolerance |

## Example: 3D Elastic with Boundary Conditions

```
strs
1 -3
initcalc
bodyforce
strainout
fem
elastic
    1        0        0    1.59e4       0.25

nonlinear
91
EvsT.txt
biot
    1        0        0    5.4e-5       0.

zone
    2 ! top, Z=300
       -1.e+15  +1.e+15  +1.e+15  -1.e+15  -1.e+15  +1.e+15  +1.e+15  -1.e+15
       +1.e+15  +1.e+15  -1.e+15  -1.e+15  +1.e+15  +1.e+15  -1.e+15  -1.e+15
       300.01   300.01   300.01   300.01   299.99   299.99   299.99   299.99

    3 ! bottom, Z=0
       -1.e+15  +1.e+15  +1.e+15  -1.e+15  -1.e+15  +1.e+15  +1.e+15  -1.e+15
       +1.e+15  +1.e+15  -1.e+15  -1.e+15  +1.e+15  +1.e+15  -1.e+15  -1.e+15
       0.1      0.1      0.1      0.1      -0.1     -0.1     -0.1     -0.1

stressboun
   -3        0        0       0.          3
stressboun
   -3        0        0       0.          2
stressboun
   -3        0        0       0.          1

zone
    4 ! back X=20
       19.99    20.01    20.01   19.99    19.99    20.01    20.01    19.99
       +1.e+15  +1.e+15  -1.e+15 -1.e+15  +1.e+15  +1.e+15  -1.e+15  -1.e+15
       300.01   300.01   300.01  300.01   -1.      -1.      -1.      -1.
    5 ! front X=0
       -0.01    +0.01    +0.01   -0.01    -0.01    +0.01    +0.01    -0.01
       +1.e+15  +1.e+15  -1.e+15 -1.e+15  +1.e+15  +1.e+15  -1.e+15  -1.e+15
       300.01   300.01   300.01  300.01   -1.      -1.      -1.      -1.

stressboun
   -4        0        0       0.          1
stressboun
   -5        0        0       0.          1

zone
    6 ! right, Y=0
       -1.e+15  +1.e+15  +1.e+15 -1.e+15  -1.e+15  +1.e+15  +1.e+15  -1.e+15
       0.01     0.01     -0.01   -0.01    0.01     0.01     -0.01    -0.01
       300.01   300.01   300.01  300.01   -1.      -1.      -1.      -1.
    7 ! left, Y=60
       -1.e+15  +1.e+15  +1.e+15 -1.e+15  -1.e+15  +1.e+15  +1.e+15  -1.e+15
       60.01    60.01    59.99   59.99    60.01    60.01    59.99    59.99
       300.01   300.01   300.01  300.01   -1.      -1.      -1.      -1.

stressboun
   -6        0        0       0.          2
stressboun
   -7        0        0       0.          2

tolerance
-1.e-3
end stress

```

This example:
- Enables coupled stress-heat-mass solution
- Calculates initial stresses
- Applies body force (gravity)
- Uses elastic material with E=1.59e4 MPa, nu=0.25
- Temperature-dependent E from file EvsT.txt
- Bottom (zone 3) is pinned in all directions
- Front/back (zones 4,5) constrained in X
- Left/right (zones 6,7) constrained in Y
- Tolerance set to absolute residual of 1e-3

## Notes

- Use Gauss quadrature (INTG > 0 in **sol** macro) with stress calculations
- The **ctrl** macro gravity direction must be set to 3 for bodyforce
- Zones for boundary conditions are typically thin slabs at domain boundaries
- Displacement boundary conditions (KQ > 0) prescribe node positions
- Stress boundary conditions (KQ < 0) prescribe applied forces
- The `end stress` keyword terminates the strs macro
- For thermal expansion, use the biot keyword with thermal coefficient
- Initial stress calculation (initcalc) is recommended for accurate results

