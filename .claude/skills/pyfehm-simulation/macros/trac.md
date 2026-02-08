# trac - Solute Transport

**Status**: Optional

## Purpose

Define solute transport parameters for simulating contaminant migration, reactive transport, and tracer studies. Supports multiple species with various sorption models.

## Input Format (Simplified)

```
trac
[userc] ANO  AWC  EPC  UPWGTA
DAYCS  DAYCF  DAYHF  DAYHS
IACCMX  DAYCM  DAYCMM  DAYCMX  NPRTTRC
[tpor]
[JA  JB  JC  PS_TRAC]
NSPECI
[ldsp]
[dspl/dspv/dspb]
MFLAG  SEHDIFF  TCX  TCY  TCZ
...
(blank line to end models)
JA  JB  JC  ITRCDSP
ICNS  [SPNAM]
IADSF  A1ADSF  A2ADSF  BETADF  [MFLAG  DIFFM  TCX  TCY  TCZ]
...
JA  JB  JC  ITRCD
[HENRY_MODEL parameters if Henry's Law species]
JA  JB  JC  ANQO
JA  JB  JC  CNSK  T1SK  T2SK
```

## Key Parameters

### Group 1 - Global Control

| Variable | Format | Description |
|----------|--------|-------------|
| KEYWORD | character | Optional "userc" for user subroutine |
| ANO | real | Initial solute concentration for all species (moles/kg fluid) |
| AWC | real | Implicitness factor: >1.0 = 2nd order, ≤1.0 = 1st order |
| EPC | real | Equation tolerance for convergence |
| UPWGTA | real | Upstream weighting: <0.5 → 0.5, >1.0 → 1.0 |

### Group 2 - Time Control

| Variable | Format | Description |
|----------|--------|-------------|
| DAYCS | real | Time when solute solution is enabled (days) |
| DAYCF | real | Time when solute solution is disabled (days) |
| DAYHF | real | Time when flow solution is disabled (days) |
| DAYHS | real | Time when flow solution is enabled (days) |

### Group 3 - Iteration Control

| Variable | Format | Description |
|----------|--------|-------------|
| IACCMX | integer | Maximum iterations for solute solution |
| DAYCM | real | Time step multiplier for solute |
| DAYCMM | real | Initial time step for solute (days) |
| DAYCMX | real | Maximum time step for solute (days) |
| NPRTTRC | integer | Print interval for .trc file |

### Species Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| NSPECI | integer | Number of solutes simulated |
| ICNS | integer | Phase: -2=Henry's Law (gas conc), -1=vapor, 0=solid, 1=liquid, 2=Henry's Law (liquid conc) |
| SPNAM | character | Species name (optional) |
| IADSF | integer | Sorption model: 0=conservative, 1=linear, 2=Freundlich, 3=modified Freundlich, 4=Langmuir |
| A1ADSF, A2ADSF | real | Sorption parameters (α₁, α₂) |
| BETADF | real | β parameter in sorption model |
| DIFFM | real | Molecular diffusion coefficient (m²/s) |
| TCX, TCY, TCZ | real | Dispersivity in x, y, z directions (m) |

### Source/Sink Control

| Variable | Format | Description |
|----------|--------|-------------|
| ANQO | real | Initial concentration at nodes (supersedes ANO) |
| CNSK | real | Injection concentration (moles/kg). If <0, fixed concentration |
| T1SK | real | Time injection begins (days) |
| T2SK | real | Time injection ends (days). If <0, zero-solute-flux at sink nodes |

## Sorption Models

| IADSF | Model | Formula |
|-------|-------|---------|
| 0 | Conservative | No sorption |
| 1 | Linear | Cs = α₁·C |
| 2 | Freundlich | Cs = α₁·C^β |
| 3 | Modified Freundlich | Cs = α₁·C/(α₂ + C^β) |
| 4 | Langmuir | Cs = α₁·α₂·C/(1 + α₂·C) |

## Example: Two Species Transport

```
trac
    0          1       1.e-7        .5
    1.       1.e20        1.      1000.
   50        1.2    1.1574e-6   1.1574e-3          1
    2
    1
    0        0.        0.        1.       0     1.e-9    0.0067       0.       0.

    1          0          0          1

    1          0          0       6.26e-5

    0
    1          0          0        2.e-5

```

This example:
- Two species
- Species 1: liquid, conservative (IADSF=0), with diffusion 1e-9 m²/s and x-dispersivity 0.0067m
- Initial concentration 6.26e-5 moles/kg
- Species 2: solid, initial concentration 2e-5 moles/kg

## Notes

- Injection nodes must be specified in the **flow** macro with appropriate sources
- Use **rxn** macro for chemical reactions between species
- The .trc file contains breakthrough curve data
- Dispersivity should typically be on the order of 0.1× the model scale
- For steady-state flow with transient transport, use DAYHF/DAYHS to freeze flow
- Output written to .trc and AVS concentration files
- For particle tracking alternative, see **ptrk** or **sptr** macros
