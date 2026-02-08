# PyFEHM Simulation Builder Skill

## Trigger Conditions

Use this skill when:
- Building a new FEHM simulation from scratch
- Debugging a failed FEHM simulation
- Understanding FEHM physics and equations
- Setting up grid, zones, macros, boundary conditions, or initial conditions
- Interpreting simulation errors or unexpected results

## Quick Reference

| Resource | Purpose |
|----------|---------|
| `PYTHON_API.md` | **Start here** — Overview of all PyFEHM modules and their APIs |
| `SIMULATION_CHECKLIST.md` | Minimum requirements for valid simulation |
| `MACROS.md` | Common macros with PyFEHM usage examples |
| `macros/INDEX.md` | Detailed FEHM macro reference (input file format) |
| `macros/*.md` | Individual macro documentation from FEHM manual |
| `ERROR_PATTERNS.md` | Known errors and diagnostic steps |
| `TIPS.md` | Lessons learned from past sessions |
| `equations/*.md` | FEHM physics and governing equations |

---

## When to Consult the Python API Guide

Read `PYTHON_API.md` when you need to:

### Understand Which Module Does What
PyFEHM is split across several modules with distinct responsibilities:
- **fdata** — simulation container, macro management, run control
- **fgrid** — grid creation (Cartesian, radial), spatial search, node/element access
- **fzone** — zone definition, `fix_*` boundary condition shortcuts
- **fboun** — time-varying boundary conditions (ramps, schedules)
- **fpost** — reading contour snapshots (`fcontour`) and time-series history (`fhistory`)
- **fvars** — fluid property lookups: density, viscosity, enthalpy, saturation curves

### Read Output from Simulations
**Always use `fpost`** — never write custom parsers for FEHM output files.
The API guide documents variable name mappings (e.g., CSV header `"Liquid Pressure (MPa)"` → `'P'`),
indexing conventions (0-indexed arrays vs 1-based node numbers), and format quirks
(surf format lacks coordinates — must read from `grid.inp`).

### Set Up Time-Varying BCs
Use `fboun` for boundaries that change over time (injection ramp-up, pressure schedules).
The API guide covers the `type` parameter (`'ti'` vs `'ti_linear'`), variable names
(`'pw'`, `'ft'`, `'dsw'`), and the relationship to FEHM's `boun` macro.

### Query Fluid Properties
The `fvars` module provides EOS lookups without running a simulation — useful for
computing injection rates, analytical comparisons, or validating reservoir conditions.

### Build a Radial Grid
The `radial=True` parameter in `dat.grid.make()` creates a 1-degree cylindrical wedge.
The API guide explains the coordinate transformation and how boundary zones map to
wellbore (XMIN) and outer boundary (XMAX).

---

## When to Consult Individual Macro Files

The `macros/` directory contains detailed documentation for each FEHM macro. **Read `macros/<macro_name>.md` when:**

### Setting Up a New Macro
- Check parameter meanings, units, and sign conventions
- Understand required vs optional parameters
- See input format examples

### Macro Has Multiple Modes
Many macros behave **completely differently** based on parameter values:
- `hflx`: `multiplier=0` → fixed heat flow; `multiplier>0` → temperature-dependent heat flow
- `flow`: `impedance=0` → fixed rate; `impedance>0` → pressure-dependent rate
- `pres`: different input formats for saturated vs two-phase conditions

**WARNING:** Getting these modes wrong can cause simulation crashes or silently wrong results.

### Debugging Unexpected Results
When a simulation runs but produces wrong values:
1. Identify which macro controls the problematic behavior
2. Read `macros/<macro_name>.md` to verify parameter interpretation
3. Check sign conventions (e.g., `hflx`: negative = heat INTO reservoir)

### PyFEHM Parameter Names Are Unclear
PyFEHM uses descriptive names that may not match FEHM names:
- PyFEHM `'multiplier'` → FEHM `QFLXM`
- PyFEHM `'impedance'` → FEHM `AIPED`

The macro files document the FEHM parameter names and their exact meanings.

### What Each Macro File Contains
- **Input format**: exact syntax for the FEHM input file
- **Parameter table**: all parameters with types, defaults, and descriptions
- **Physics**: equations and behavior for different parameter combinations
- **Examples**: sample input blocks
- **Notes**: gotchas, common mistakes, related macros

### Quick Lookup
Start with `macros/INDEX.md` which lists all macros organized by:
- Required vs optional
- Category (material properties, boundary conditions, output, etc.)
- Links to individual documentation files

---

## Workflow A: Building a New Simulation

### Step 1: Gather Requirements
Before writing code, understand:
- **Domain**: geometry, dimensions, materials
- **Physics**: isothermal? multiphase? solute transport?
- **Boundary conditions**: fixed P/T, injection/extraction, flux
- **Initial conditions**: uniform, gradient, equilibrium
- **Output**: what variables, how often, where

### Step 2: Follow the Checklist
Read `SIMULATION_CHECKLIST.md` and ensure ALL required components:
1. Grid definition
2. Zone assignments
3. Rock properties (`rock` macro)
4. Permeability (`perm` macro)
5. Initial conditions (`pres` or `grad`)
6. Boundary conditions (`flow`, `hflx`, or zone methods)
7. Time control (`dat.tf`, optionally `dat.dtmax`)
8. Output specification (`dat.cont`, `dat.hist`)
9. File paths (`dat.files.root`)

### Step 3: Build Incrementally
```python
from fdata import *

# 1. Create data object
dat = fdata()

# 2. Define grid
dat.grid.make('grid_name', type='xyz',
              origin=[0,0,0],
              nodelist=[...])

# 3. Create zones (after grid)
zone_inlet = dat.grid.zone(rect=[...])
zone_inlet.name = 'inlet'

# 4. Assign properties via macros
dat.zone[0].rock(density=2500, specific_heat=1000, porosity=0.1)
dat.zone[0].perm(kx=1e-15, ky=1e-15, kz=1e-15)

# 5. Set ICs and BCs
dat.zone[0].pres(pressure=10, temperature=25)
zone_inlet.fix_pressure(10.1, temperature=25)

# 6. Configure time and output
dat.tf = 365.25  # final time in days
dat.dtmax = 1.0  # max timestep
dat.cont.variables = ['pressure', 'temperature']
dat.hist.variables = ['pressure', 'temperature']

# 7. Set file paths and write
dat.files.root = 'my_simulation'
dat.run('my_simulation.dat', verbose=False)
```

### Step 4: Execute with verbose=False
**ALWAYS** run simulations with `verbose=False`:
```python
dat.run('input.dat', verbose=False)
```

Then grep the output file for problems:
```bash
grep -iE "error|warning|cut|convergence" *.outp | head -30
```

---

## Workflow B: Debugging a Failed Simulation

### Step 1: Examine Output File
```bash
# Look for errors and warnings
grep -iE "error|warning|cut" simulation.outp | head -30

# Check timestep behavior
grep -i "timestep" simulation.outp | tail -20

# Look for convergence issues
grep -i "convergence\|iteration" simulation.outp | tail -20
```

### Step 2: Check Common Issues
Consult `ERROR_PATTERNS.md` for:
- Timestep cuts (BCs too aggressive, bad ICs, unrealistic permeability)
- Negative saturation (capillary pressure problems)
- Convergence failure (nonlinear solver struggling)
- Mass balance errors (boundary condition inconsistency)

### Step 3: Verify Checklist
Re-read `SIMULATION_CHECKLIST.md`. Missing components often cause cryptic failures:
- No initial conditions → solver starts from zero → crash
- No permeability → no flow → unexpected behavior
- Inconsistent units → wildly wrong numbers

### Step 4: Check Macro Documentation
If the error involves a specific macro (e.g., `hflx`, `flow`, `pres`):
1. Read `macros/<macro_name>.md` for that macro
2. Verify parameter values match intended behavior
3. Check for multi-mode macros where parameter combinations change behavior
4. Confirm sign conventions (positive/negative meanings)

**Example:** A simulation crashed with "timestep less than daymin" when using `hflx`.
Reading `macros/hflx.md` revealed that `multiplier=1.0` triggers temperature-dependent
mode (extracting ~25 MW) instead of the intended fixed heat flow mode (`multiplier=0`).

### Step 5: Consult Physics
If errors relate to unexpected physical behavior, read relevant equations:
- `equations/FLOW_ENERGY.md` for mass/energy conservation
- `equations/CONSTITUTIVE.md` for property models
- `equations/TRANSPORT.md` for solute/particle issues
- `equations/FRACTURE.md` for dual porosity problems

### Step 6: Apply Failure Protocol
**After 2-3 consecutive failed attempts:**
1. **STOP** attempting automatic fixes
2. Summarize what was tried and why it failed
3. Show relevant error messages from `.outp`
4. Ask user for guidance or domain knowledge
5. Document resolution in `TIPS.md` when solved

---

## Workflow C: Appending Tips

When an error is resolved through debugging:

### Step 1: Identify the Lesson
- What was the symptom?
- What was the root cause?
- What fixed it?
- What should be remembered?

### Step 2: Append to TIPS.md
Read current `TIPS.md`, then append:
```markdown
### [YYYY-MM-DD] [Context] Brief title

**Symptom**: What went wrong
**Root Cause**: Why it happened
**Resolution**: What fixed it
**Remember**: Key takeaway for future
```

### Step 3: Write Updated File
Use the Edit or Write tool to append the new tip.

---

## Execution Rules

### Always Use verbose=False
```python
# CORRECT
dat.run('input.dat', verbose=False)

# INCORRECT - floods context with output
dat.run('input.dat')
dat.run('input.dat', verbose=True)
```

### Grep for Errors
After any simulation run:
```bash
grep -iE "error|warning|cut|convergence|negative" *.outp | head -30
```

### Check Return Status
```python
import subprocess
result = subprocess.run(['fehm', 'input.dat'], capture_output=True)
if result.returncode != 0:
    print("Simulation failed")
```

---

## Failure Protocol

### When to Invoke
- Same error appears after 2-3 fix attempts
- Error message is unclear or undocumented
- Fix requires domain expertise you lack

### What to Do
1. **STOP** - Do not continue attempting fixes
2. **Summarize** - List what was tried:
   ```
   Attempted fixes:
   1. Reduced timestep from 1.0 to 0.1 → still failing
   2. Changed initial pressure from 10 to 1 MPa → same error
   3. Verified grid connectivity → appears correct
   ```
3. **Show Evidence** - Provide error context:
   ```
   From simulation.outp:
   > timestep cut at time 0.001, dt reduced to 1e-6
   > convergence failure after 50 iterations
   ```
4. **Ask User** - Request specific help:
   ```
   I've tried reducing timesteps and checking ICs but the simulation
   still fails at early time. Do you have insight into:
   - Expected pressure range for this problem?
   - Whether the permeability values are realistic?
   - Any known issues with this geometry?
   ```
5. **Document** - When resolved, add to `TIPS.md`

---

## Directory Contents

```
.claude/skills/pyfehm-simulation/
├── SKILL.md                    # This file — workflows and when to read what
├── PYTHON_API.md               # Python API tour: fdata, fgrid, fzone, fboun, fpost, fvars
├── SIMULATION_CHECKLIST.md     # Required simulation components
├── MACROS.md                   # Common macros with PyFEHM examples
├── ERROR_PATTERNS.md           # Known error patterns and solutions
├── TIPS.md                     # Appendable troubleshooting tips
├── equations/                  # FEHM physics and governing equations
│   ├── FLOW_ENERGY.md          # Mass, energy, air-water conservation
│   ├── TRANSPORT.md            # Solute, reactive transport, particles
│   ├── CONSTITUTIVE.md         # EOS, relative perm, capillary pressure
│   └── FRACTURE.md             # Dual porosity/double permeability
└── macros/                     # Detailed FEHM macro reference (from UM)
    ├── INDEX.md                # Macro index and quick reference
    ├── boun.md                 # Time-dependent boundary conditions
    ├── cond.md                 # Thermal conductivity
    ├── cont.md                 # Contour output control
    ├── coor.md                 # Node coordinates
    └── ...                     # Many more macro files
```

---

## See Also

- `PYTHON_API.md` for the full Python API tour (fdata, fgrid, fzone, fboun, fpost, fvars)
- FEHM user manual for detailed macro syntax
- Source files `fdata.py`, `fgrid.py`, `fpost.py`, `fvars.py` for implementation details

---

## Skill Maintenance

**IMPORTANT**: When modifying PyFEHM code, update this skill to stay in sync.

### When to Update the Skill

Update skill documentation when:
- **Adding new methods** to `fzone`, `fdata`, or other classes (e.g., `fix_heating_rate()`)
- **Changing method signatures** or behavior
- **Discovering new error patterns** during debugging
- **Learning lessons** that should be preserved in `TIPS.md`

### What to Update

| Change Type | Update Location |
|-------------|-----------------|
| New zone method (e.g., `fix_*`) | `MACROS.md` → Zone Shortcuts section |
| New macro support | `MACROS.md` → relevant section |
| New error pattern | `ERROR_PATTERNS.md` |
| Debugging lesson | `TIPS.md` |
| New macro file | `macros/INDEX.md` + create `macros/<name>.md` |

### Why This Matters

Without updates, the skill teaches outdated patterns:
- Users manually configure macros instead of using safe wrapper methods
- Hard-won lessons from debugging sessions are lost
- New features remain undiscovered

**Example**: We added `fix_heating_rate()` to prevent the `hflx` multiplier bug, but without
documenting it here, future sessions would still use the risky manual approach.
