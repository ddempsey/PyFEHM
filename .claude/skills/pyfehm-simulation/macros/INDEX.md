# FEHM Macros Reference Index

This directory contains detailed reference files for FEHM macros, extracted from the FEHM V3.1.0 Users Manual.

## Quick Reference

### Required Macros

| Macro | Description | Condition |
|-------|-------------|-----------|
| [coor](coor.md) | Node coordinate data | Required if `fdm` not used |
| [cond](cond.md) | Thermal conductivity | Required for non-isothermal problems |
| [ctrl](ctrl.md) | Program control parameters | Always required |
| [elem](elem.md) | Element node data | Required if `fdm` not used |
| [fdm](fdm.md) | Finite difference grid | Required if `coor`/`elem` not used |
| [flow](flow.md) or [boun](boun.md) | Flow boundary conditions | Required for flow problems |
| [hyco](hyco.md) or [perm](perm.md) | Permeability/hydraulic conductivity | Required |
| [init](init.md) or [pres](pres.md) | Initial conditions | Required if no restart file |
| [rlp](rlp.md) or [rlpm](rlpm.md) | Relative permeability | Required for 2-phase problems |
| [rock](rock.md) | Rock properties | Always required |
| [time](time.md) | Time stepping | Always required |
| [stop](stop.md) | End of input | Always required |

### By Category

#### Rock/Material Properties
- [cond](cond.md) - Thermal conductivity
- [anpe](anpe.md) - Anisotropic permeability (cross terms)
- [perm](perm.md) - Permeability (diagonal)
- [ppor](ppor.md) - Pressure-dependent porosity
- [rock](rock.md) - Rock density, specific heat, porosity
- [vcon](vcon.md) - Variable thermal conductivity

#### Initial/Boundary Conditions
- [boun](boun.md) - Time-dependent boundary conditions
- [conv](conv.md) - Head to pressure conversion
- [flow](flow.md) - Mass/energy sources and sinks
- [grad](grad.md) - Gradient initial conditions
- [hflx](hflx.md) - Heat flow boundary conditions
- [init](init.md) - Initial values (global)
- [pres](pres.md) - Initial pressure/temperature/saturation

#### Multiphase/Components
- [adif](adif.md) - Air-water vapor diffusion
- [airwater](airwater.md) - Isothermal air-water two-phase
- [carb](carb.md) - CO2 simulation
- [eos](eos.md) - Equation of state
- [ngas](ngas.md) - Non-condensible gas (air)
- [rlp](rlp.md) - Relative permeability
- [rlpm](rlpm.md) - Relative permeability (alternative input)

#### Transport
- [cden](cden.md) - Concentration-dependent density
- [cflx](cflx.md) - Solute molar flow through zone
- [trac](trac.md) - Solute transport
- [rxn](rxn.md) - Chemical reactions

#### Grid/Geometry
- [coor](coor.md) - Node coordinates
- [conn](conn.md) - Print node connections (diagnostic)
- [elem](elem.md) - Element definitions
- [fdm](fdm.md) - Finite difference grid generation
- [zone](zone.md) - Zone definitions
- `zonn` - Zone definitions (alternate)

#### Output Control
- [chea](chea.md) - Convert output to head
- [cont](cont.md) - Contour plot output
- [flxz](flxz.md) - Zone flow output
- [hist](hist.md) - History output
- [node](node.md) - Node output selection

#### Solver/Numerics
- [bous](bous.md) - Boussinesq approximation
- [ctrl](ctrl.md) - Control parameters
- [impf](impf.md) - Timestep control by variable change
- [iter](iter.md) - Iteration parameters
- [sol](sol.md) - Solver specifications
- [time](time.md) - Time stepping

#### Specialized Models
- [dual](dual.md) - Dual porosity
- [dpdp](dpdp.md) - Double porosity/double permeability
- [gdpm](gdpm.md) - Generalized dual porosity
- [strs](strs.md) - Stress calculations
- `well` / `rive` - Well/river package

## Macros Documented

### From UM Part 1 (Sections 6.2.6-6.2.20)

| Macro | File | Section |
|-------|------|---------|
| adif | [adif.md](adif.md) | 6.2.6 |
| airwater | [airwater.md](airwater.md) | 6.2.7 |
| anpe | [anpe.md](anpe.md) | 6.2.8 |
| boun | [boun.md](boun.md) | 6.2.9 |
| bous | [bous.md](bous.md) | 6.2.10 |
| carb | [carb.md](carb.md) | 6.2.11 |
| cden | [cden.md](cden.md) | 6.2.12 |
| cflx | [cflx.md](cflx.md) | 6.2.13 |
| chea | [chea.md](chea.md) | 6.2.15 |
| cond | [cond.md](cond.md) | 6.2.16 |
| conn | [conn.md](conn.md) | 6.2.17 |
| cont | [cont.md](cont.md) | 6.2.18 |
| conv | [conv.md](conv.md) | 6.2.19 |
| coor | [coor.md](coor.md) | 6.2.20 |

### From UM Part 2 (Sections 6.2.21-6.2.71)

| Macro | File | Section |
|-------|------|---------|
| ctrl | [ctrl.md](ctrl.md) | 6.2.21 |
| dpdp | [dpdp.md](dpdp.md) | 6.2.22 |
| dual | [dual.md](dual.md) | 6.2.23 |
| elem | [elem.md](elem.md) | 6.2.25 |
| eos | [eos.md](eos.md) | 6.2.26 |
| fdm | [fdm.md](fdm.md) | 6.2.28 |
| flow | [flow.md](flow.md) | 6.2.30 |
| flxz | [flxz.md](flxz.md) | 6.2.36 |
| gdpm | [gdpm.md](gdpm.md) | 6.2.41 |
| grad | [grad.md](grad.md) | 6.2.42 |
| hflx | [hflx.md](hflx.md) | 6.2.45 |
| hist | [hist.md](hist.md) | 6.2.46 |
| hyco | [hyco.md](hyco.md) | 6.2.47 |
| impf | [impf.md](impf.md) | 6.2.49 |
| init | [init.md](init.md) | 6.2.50 |
| iter | [iter.md](iter.md) | 6.2.53 |
| ngas | [ngas.md](ngas.md) | 6.2.61 |
| node | [node.md](node.md) | 6.2.63 |
| perm | [perm.md](perm.md) | 6.2.67 |
| ppor | [ppor.md](ppor.md) | 6.2.69 |
| pres | [pres.md](pres.md) | 6.2.70 |

### From UM Part 3 & 4 (Sections 6.2.72-6.2.98)

| Macro | File | Section |
|-------|------|---------|
| rlp | [rlp.md](rlp.md) | 6.2.77 |
| rlpm | [rlpm.md](rlpm.md) | 6.2.78 |
| rock | [rock.md](rock.md) | 6.2.79 |
| rxn | [rxn.md](rxn.md) | 6.2.80 |
| sol | [sol.md](sol.md) | 6.2.83 |
| stop | [stop.md](stop.md) | 6.2.85 |
| strs | [strs.md](strs.md) | 6.2.85 |
| time | [time.md](time.md) | 6.2.90 |
| trac | [trac.md](trac.md) | 6.2.91 |
| vcon | [vcon.md](vcon.md) | 6.2.94 |
| zone | [zone.md](zone.md) | 6.2.97 |

## Macros Pending

The following macros are documented in the user manual but not yet in this reference:

**From Part 2**: dvel (6.2.24), exrl (6.2.27), finv (6.2.29), flo2 (6.2.31), flo3 (6.2.32), floa (6.2.33), flxn (6.2.34), flxo (6.2.35), fper (6.2.37), ftsc (6.2.38), frlp (6.2.39), gdkm (6.2.40), hcon (6.2.43), head (6.2.44), ice/meth (6.2.48), intg (6.2.51), isot (6.2.52), itfc (6.2.54), itup (6.2.55), iupk (6.2.56), ivfc (6.2.57), mdnode (6.2.58), mptr (6.2.59), nfinv (6.2.60), nobr (6.2.62), nod2 (6.2.64), nod3 (6.2.65), nrst (6.2.66), pest (6.2.68), ptrk (6.2.71)

**From Part 3**: para, phys, ptrk, renu, rest, rflo, rich, rive/well, sptr, stea

**From Part 4**: subm, svar, szna/napl, text, thic, user, vapl, weli, wgtu, wflo, wtsi, zeol, zonn

## Common Input Pattern

Most property macros use the JA/JB/JC node loop pattern:

```
macro_name
JA  JB  JC  PARAM1  PARAM2  ...
...
(blank line to end)
```

Where:
- **JA** = First node (or -zone_number for zone assignment)
- **JB** = Last node (ignored for zone assignment)
- **JC** = Node increment (ignored for zone assignment)

To assign to all nodes: set JA=1, JB=N (total nodes), JC=1
Or: set JA=1, JB=JC=0 (shortcut)
