# FEHM Error Patterns and Diagnostics

Common errors, their causes, and how to diagnose and fix them.

---

## How to Diagnose

### Step 1: Check Output File
```bash
# Look for errors and warnings
grep -iE "error|warning" simulation.outp | head -20

# Check timestep behavior
grep -i "timestep\|time step\|dt" simulation.outp | tail -20

# Look for convergence issues
grep -iE "convergence|iteration|cut" simulation.outp | tail -20

# Check for numerical problems
grep -iE "negative|nan|inf|overflow" simulation.outp | head -10
```

### Step 2: Check Simulation Progress
```bash
# See how far simulation progressed
grep -i "time =" simulation.outp | tail -10
```

### Step 3: Check Mass/Energy Balance
```bash
grep -iE "balance|mass|energy" simulation.outp | tail -10
```

---

## Error Patterns

### 1. Timestep Cuts

**Pattern in output**:
```
timestep cut at time X, dt reduced to Y
time step cut: reducing dt
```

**Possible Causes**:
- Boundary conditions too aggressive (large pressure jump)
- Initial conditions inconsistent with BCs
- Permeability too high or too low
- Capillary pressure causing saturation oscillation
- Phase transition instability

**Diagnostic Questions**:
- What time does the cut occur? (early = IC problem, later = BC or physics)
- How many cuts before failure? (few = severe problem, many = marginal)
- What variables are changing rapidly?

**Fixes**:
```python
# Reduce initial timestep
dat.dti = 0.001  # was 0.1

# Limit max timestep
dat.dtmax = 1.0  # was 10.0

# Smooth boundary conditions
# Instead of step change, use ramp:
dat.zone['well'].boun(times=[0, 1, 10], pressures=[10, 11, 12])

# Check permeability values (should be 1e-18 to 1e-12 m²)
print(f"Permeability: {dat.zone[0].permeability}")
```

---

### 2. Convergence Failure

**Pattern in output**:
```
convergence failure after N iterations
Newton iteration did not converge
```

**Possible Causes**:
- Nonlinear problem too stiff
- Poor initial guess (bad ICs)
- Unrealistic property values
- Missing physics (e.g., need capillary pressure)

**Fixes**:
```python
# Increase allowed iterations
dat.ctrl['max_iterations'] = 100  # default often 50

# Relax convergence tolerance (temporary for debugging)
dat.ctrl['newton_tol'] = 1e-4  # was 1e-6

# Use smaller timesteps
dat.dtmax = 0.1

# Check property values are physical
# - Porosity: 0.001 to 0.5
# - Permeability: 1e-20 to 1e-10 m²
# - Pressure: 0.1 to 100 MPa
# - Temperature: 0 to 350°C (liquid water)
```

---

### 3. Negative Saturation

**Pattern in output**:
```
negative saturation
saturation out of bounds
```

**Possible Causes**:
- Capillary pressure model issues
- Residual saturation set too high
- Numerical dispersion in transport
- Inconsistent relative perm/capillary models

**Fixes**:
```python
# Check residual saturations
# slr + sgr should be < 1.0
dat.rlp.parameters = {
    'slr': 0.1,   # not too high
    'sgr': 0.05,  # not too high
}

# Limit capillary pressure maximum
dat.cap.parameters['pmax'] = 1e6  # Pa

# Use compatible rel perm and cap pressure models
# (both van Genuchten, or both Brooks-Corey)
```

---

### 4. Mass Balance Errors

**Pattern in output**:
```
mass balance error: X%
cumulative mass error
```

**Possible Causes**:
- Boundary conditions inconsistent
- Large timesteps causing integration error
- Numerical precision issues

**Fixes**:
```python
# Reduce timestep
dat.dtmax = 1.0

# Check boundary conditions are consistent
# (e.g., inflow should approximately equal outflow at steady state)

# Verify no conflicting BCs on same zone
```

---

### 5. Simulation Hangs / Very Slow

**Possible Causes**:
- Extremely small timesteps (dt → 0)
- Linear solver not converging
- Very large grid with insufficient memory

**Diagnostic**:
```bash
# Check if timesteps are shrinking
grep -i "dt" simulation.outp | tail -20

# Check linear solver iterations
grep -i "linear\|gmres\|cg" simulation.outp | tail -10
```

**Fixes**:
```python
# Set minimum timestep
dat.dtmin = 1e-6  # days

# Try different linear solver
dat.ctrl['linear_solver'] = 'direct'  # or 'bicgstab'

# Reduce grid size for testing
```

---

### 6. Solver Fails at Start

**Pattern**: Simulation exits immediately or after first timestep.

**Possible Causes**:
- Missing required input (no ICs, no permeability)
- File path errors
- Grid connectivity issues
- Invalid parameter values

**Diagnostic Checklist**:
```python
# Check required components exist
print(f"Grid nodes: {dat.grid.n_nodes}")  # should be > 0
print(f"Rock macro: {len(dat.rock)}")     # should be > 0
print(f"Perm macro: {len(dat.perm)}")     # should be > 0
print(f"Pres macro: {len(dat.pres)}")     # should be > 0

# Check for NaN or invalid values
import numpy as np
for macro in [dat.rock, dat.perm, dat.pres]:
    for zone, values in macro.items():
        if np.any(np.isnan(values)) or np.any(np.isinf(values)):
            print(f"Invalid values in {macro} zone {zone}")
```

---

### 7. Output Files Missing or Empty

**Possible Causes**:
- Simulation failed before output time
- Output variables not specified
- Wrong file path

**Fixes**:
```python
# Verify output is configured
print(f"Cont variables: {dat.cont.variables}")
print(f"Hist variables: {dat.hist.variables}")

# Set early output time for debugging
dat.cont.times = [0.001, 0.01, 0.1, 1, 10]  # catch early failure

# Check files exist
import os
root = dat.files.root
print(f"Output exists: {os.path.exists(f'{root}.outp')}")
print(f"Contour exists: {os.path.exists(f'{root}.con')}")
```

---

### 8. Phase Transition Issues

**Pattern in output**:
```
phase change
vaporization
condensation
```

**Possible Causes**:
- Temperature crosses boiling curve
- Pressure drop causes flashing
- Injection of different phase fluid

**Considerations**:
- Phase transitions are physically real but numerically challenging
- May need smaller timesteps during transition
- Consider if two-phase is really needed

**Fixes**:
```python
# If single-phase is sufficient, constrain conditions:
# Keep T < 100°C for P ~ 0.1 MPa
# Or keep P high enough to prevent boiling

# If two-phase needed, ensure:
# - Relative permeability model is defined
# - Capillary pressure model is defined
# - Initial saturation is set
```

---

## Quick Reference: Where to Look

| Symptom | Check First |
|---------|-------------|
| Immediate crash | ICs, grid, file paths |
| Early time crash | ICs vs BCs mismatch, permeability |
| Mid-simulation crash | Phase transition, BC changes |
| Slow convergence | Property values, solver settings |
| Wrong answer | Units, zone assignments, BC signs |
| No flow | Permeability zero, no pressure gradient |
| Too much flow | Permeability too high, BC values |

---

## Unit Reminders

| Quantity | FEHM Units | SI Units | Conversion |
|----------|------------|----------|------------|
| Pressure | MPa | Pa | ×10⁶ |
| Permeability | m² | Darcy | ×9.87×10⁻¹³ |
| Temperature | °C | K | +273.15 |
| Time | days | seconds | ×86400 |
| Mass rate | kg/s | kg/s | 1 |
| Enthalpy | J/kg | J/kg | 1 |
| Conductivity | W/m/K | W/m/K | 1 |
