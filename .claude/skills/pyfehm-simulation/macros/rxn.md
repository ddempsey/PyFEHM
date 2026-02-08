# rxn - Chemical Reactions

**Status**: Optional

## Purpose

Define chemical reactions between components for reactive transport simulations. Used in conjunction with the **trac** macro. Supports equilibrium speciation reactions and multiple kinetic reaction models.

## Input Format (Simplified)

```
rxn
NCPLX  NUMRXN
NGROUPS
GROUP(ICPNT), ICPNT = 1, NCPNT
...
IDCPNT  CPNTNAM  IFXCONC  CPNTPRT  CPNTGS
...
IDCPLX  CPLXNAM  CPLXPRT
...
IDIMM  IMMNAM  IMMPRT
...
IDVAP  VAPNAM  VAPPRT
...
ISKIP
RSDMAX
HEADING
LOGKEQ
CKEQ  HEQ  (or lookup table)
...
STOIC
...
IDRXN
JA  JB  JC
[kinetic parameters based on IDRXN]
...
```

## Key Parameters

### Group 1-6: Component/Complex Definition

| Variable | Format | Description |
|----------|--------|-------------|
| NCPLX | integer | Number of aqueous complexes (equilibrium reactions) |
| NUMRXN | integer | Number of kinetic reactions |
| NGROUPS | integer | Number of solution groups for coupling |
| GROUP | integer | Coupling group membership for each component |
| IDCPNT | integer | Total aqueous component ID (1, 2, 3...) |
| CPNTNAM | character | Component name (e.g., "Sulfate", "Co", "Fe") |
| IFXCONC | integer | 1=total conc in trac, 2=log free-ion (for pH) |
| CPNTPRT | integer | Print flag: 0=print, 1=no print |
| CPNTGS | real | Initial guess for speciation (recommend 1.0e-9) |
| IDCPLX | integer | Aqueous complex ID (101, 102...) |
| CPLXNAM | character | Complex name (e.g., "CoEDTA", "H2SO4") |
| IDIMM | integer | Immobile component ID |
| IMMNAM | character | Immobile name (e.g., "Calcite", "Co[adsorbed]") |
| IDVAP | integer | Vapor component ID |
| VAPNAM | character | Vapor name (e.g., "CO2[gas]") |

### Group 7-11: Equilibrium Parameters

| Variable | Format | Description |
|----------|--------|-------------|
| ISKIP | integer | 0=calculate at all nodes (recommended), 1=skip converged |
| RSDMAX | real | Speciation tolerance (recommend 1e-9) |
| LOGKEQ | integer | 0=K given as K, 1=K given as log K |
| CKEQ | real | Equilibrium constant for each complex |
| HEQ | real | Enthalpy of reaction (for temperature dependence) |
| STOIC | real | Stoichiometry matrix (components × complexes) |

### Group 12+: Kinetic Reactions

| Variable | Format | Description |
|----------|--------|-------------|
| IDRXN | integer | Kinetic reaction model type (see below) |
| JA, JB, JC | integer | Node range for reaction (1 0 0 = all nodes) |

## Kinetic Reaction Models (IDRXN)

### IDRXN = 1: Linear Kinetic Reaction

Adsorption/desorption with linear isotherm approach.

| Parameter | Description |
|-----------|-------------|
| IAQUEOUS | Aqueous component/complex number |
| IIMMOBILE | Immobile component number |
| KD | Distribution coefficient (kg water/kg rock) |
| RATE | Mass transfer coefficient (1/hr) |

### IDRXN = 2: Langmuir Kinetic Reaction

| Parameter | Description |
|-----------|-------------|
| IAQUEOUS | Aqueous component/complex number |
| IIMMOBILE | Immobile component number |
| DISTCOEFF | Distribution coefficient (kg water/moles) |
| RATE | Mass transfer coefficient (1/hr) |
| MAXCONC | Maximum sorbed concentration (moles/kg rock) |

### IDRXN = 3: General Kinetic Reaction

Reversible reaction with forward and reverse rates.

| Parameter | Description |
|-----------|-------------|
| NIMMOBILE | Number of immobile components in reaction |
| NAQUEOUS | Number of aqueous species in reaction |
| NVAPOR | Number of vapor species in reaction |
| KFOR | Forward rate constant |
| KREV | Reverse rate constant |
| IIMMOBILE | Immobile component IDs |
| IMSTOIC | Immobile stoichiometry |
| IAQUEOUS | Aqueous component IDs |
| AQSTOIC | Aqueous stoichiometry |

### IDRXN = 4: Dual Monod Biodegradation

Microbial degradation with substrate and electron acceptor.

| Parameter | Description |
|-----------|-------------|
| NAQUEOUS | Number of aqueous species (2-5) |
| SUBSTRATE | Substrate component number |
| ELECACC | Electron acceptor component number |
| BIOMASS | Immobile biomass component number |
| KS | Monod half-max for substrate |
| KA | Monod half-max for electron acceptor |
| DECAY | Microbial decay coefficient (1/hr) |
| QM | Maximum substrate utilization rate |
| YIELD | Microbial yield coefficient |

### IDRXN = 5: Radioactive Decay

| Parameter | Description |
|-----------|-------------|
| HALFLIFE | Half-life (years) |
| RXNTYPE | Phase: 0=solid, 1=liquid, -1=vapor |
| PARENT | Parent component number |
| DAUGHTER | Daughter component number (0 if not modeled) |

### IDRXN = 6: Kinetic Henry's Law

| Parameter | Description |
|-----------|-------------|
| IAQUEOUS | Aqueous component number |
| IVAPOR | Vapor component number |
| KH | Henry's law constant |
| RATE | Mass transfer rate (1/hr) |

### IDRXN = 7, 8: Precipitation/Dissolution

| Parameter | Description |
|-----------|-------------|
| IIMMOBILE | Dissolving mineral component |
| NAQUEOUS | Number of aqueous species |
| IAQUEOUS | Aqueous component IDs in solubility product |
| IMSTOIC | Immobile stoichiometry |
| AQSTOIC | Aqueous stoichiometry |
| SOLUBILITY | Solubility product |
| RATE | Reaction rate (moles/m²s) |
| SAREA | Mineral surface area (m²/m³ rock) |

## Example: Linear Kinetic Sorption

```
rxn
** NCPLX   NUMRXN **
2          4
** GROUP **
2
1 0 1
0 1 0
** IDCPNT   CPNTNAM   IFXCONC   CPNTPRT   CPNTGS **
1          Co        0         0         1.0e-9
2          Fe        0         0         1.0e-9
3          EDTA      0         0         1.0e-9
** IDCPLX   CPLXNAM   CPLXPRT **
101        CoEDTA    0
102        FeEDTA    0
** IDIMM    IMMNAM    IMMPRT **
1          CoEDTA[s] 0
2          FeEDTA[s] 0
3          Cobalt[s] 0
** ISKIP **
0
** RSDMAX **
1e-9
** Chemical Information **
** LOGKEQ **
0
** CKEQ      HEQ **
1.0e18       0
6.31e27      0
** STOIC **
1.0          0.0       1.0
0.0          1.0       1.0
** IDRXN **
1
** JA       JB        JC **
1          0         0
** IAQ     IMMOBILE **
1          3
** KD **
5.07
** RATE **
1.0

```

## Example: Calcite Dissolution

This example corresponds to the trac macro example on page 192-193.

```
rxn
0          1
** IDRXN **
7
** JA       JB        JC **
1          0         0
** IIMMOBILE **
2
** NAQUEOUS **
1
** IAQUEOUS **
1
** IMSTOIC **
-1.0
** AQSTOIC **
1.0
** SOLUBILITY **
6.26e-5
** RATE **
1.e-8
** SAREA **
1000.

```

## Notes

- The **rxn** macro must be used with the **trac** macro
- Component numbering in rxn must match species defined in trac
- Aqueous complexes are numbered starting at 101
- Use "lookup" keyword for temperature-dependent K values
- Stoichiometry: positive = reactant, negative = product, 0 = not involved
- For conservative tracers, rxn is not needed (use trac alone)
- Group coupling improves convergence for fast reactions
- RSDMAX of 1e-9 is recommended for most problems

