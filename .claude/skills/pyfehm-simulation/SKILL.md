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
| `SIMULATION_CHECKLIST.md` | Minimum requirements for valid simulation |
| `MACROS.md` | Common macros with usage examples |
| `ERROR_PATTERNS.md` | Known errors and diagnostic steps |
| `TIPS.md` | Lessons learned from past sessions |
| `equations/*.md` | FEHM physics and governing equations |

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

### Step 4: Consult Physics
If errors relate to unexpected physical behavior, read relevant equations:
- `equations/FLOW_ENERGY.md` for mass/energy conservation
- `equations/CONSTITUTIVE.md` for property models
- `equations/TRANSPORT.md` for solute/particle issues
- `equations/FRACTURE.md` for dual porosity problems

### Step 5: Apply Failure Protocol
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
├── SKILL.md                    # This file
├── equations/
│   ├── FLOW_ENERGY.md          # Mass, energy, air-water conservation
│   ├── TRANSPORT.md            # Solute, reactive transport, particles
│   ├── CONSTITUTIVE.md         # EOS, relative perm, capillary pressure
│   └── FRACTURE.md             # Dual porosity/double permeability
├── SIMULATION_CHECKLIST.md     # Required simulation components
├── MACROS.md                   # Common macros and usage
├── TIPS.md                     # Appendable troubleshooting tips
└── ERROR_PATTERNS.md           # Known error patterns and solutions
```

---

## See Also

- PyFEHM documentation and examples in the repository
- FEHM user manual for detailed macro syntax
- `fdata.py`, `fgrid.py`, `fzone.py` for implementation details
