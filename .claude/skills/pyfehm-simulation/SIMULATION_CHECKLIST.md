# FEHM Simulation Checklist

Use this checklist to ensure all required components are present before running a simulation.

---

## Required Components

### 1. Grid Definition
- [ ] Grid created or loaded
- [ ] Appropriate resolution for problem
- [ ] Correct coordinate system and units

```python
# Create new grid
dat.grid.make('my_grid', type='xyz',
              origin=[0, 0, 0],
              nodelist=[[0, 100, 200], [0, 50], [0, -10, -20]])

# Or load existing
dat.grid.read('existing.fehm')
```

### 2. Zone Assignments
- [ ] Zone 0 exists (all nodes) - automatic
- [ ] Named zones for regions needing different properties
- [ ] Boundary zones for BCs

```python
# Create zones from geometry
inlet = dat.grid.zone(rect=[[0, 0], [0, 50], [-20, 0]])
inlet.name = 'inlet'

# Or from node lists
special_zone = dat.grid.zone(nodelist=[1, 2, 3, 4, 5])
```

### 3. Rock Properties (`rock` macro)
- [ ] Density defined (kg/m³)
- [ ] Specific heat defined (J/kg/K)
- [ ] Porosity defined (0-1)

```python
dat.zone[0].rock(
    density=2500,        # kg/m³
    specific_heat=1000,  # J/kg/K
    porosity=0.1
)
```

### 4. Permeability (`perm` macro)
- [ ] Permeability assigned to all zones
- [ ] Values physically reasonable (typically 10⁻¹⁸ to 10⁻¹² m²)
- [ ] Anisotropy if needed (kx, ky, kz)

```python
dat.zone[0].perm(kx=1e-15, ky=1e-15, kz=1e-15)  # m²
```

### 5. Initial Conditions
- [ ] Initial pressure defined
- [ ] Initial temperature defined (if non-isothermal)
- [ ] Initial saturation defined (if multiphase)

```python
# Uniform ICs
dat.zone[0].pres(pressure=10, temperature=25)  # MPa, °C

# Or gradient
dat.zone[0].grad(
    ref_point=[0, 0, 0],
    ref_pressure=10,
    ref_temperature=25,
    pressure_grad=[0, 0, -0.01],  # MPa/m (hydrostatic)
    temperature_grad=[0, 0, 0.03]  # °C/m (geothermal)
)
```

### 6. Boundary Conditions
- [ ] At least one BC that drives flow
- [ ] Inlet/outlet or source/sink defined
- [ ] BC type appropriate (Dirichlet vs Neumann)

```python
# Fixed pressure (Dirichlet)
dat.zone['inlet'].fix_pressure(12, temperature=30)
dat.zone['outlet'].fix_pressure(10, temperature=25)

# Mass source (Neumann)
dat.zone['well'].flow(mass_rate=0.1, enthalpy=1e5)  # kg/s, J/kg
```

### 7. Time Control
- [ ] Final time set (`dat.tf`)
- [ ] Initial timestep reasonable (optional)
- [ ] Max timestep set if needed (optional)

```python
dat.tf = 365.25        # final time (days)
dat.dti = 0.01         # initial timestep (days)
dat.dtmax = 10.0       # max timestep (days)
```

### 8. Output Specification
- [ ] Contour output variables selected
- [ ] History output variables selected (optional)
- [ ] Output frequency appropriate

```python
# Contour (spatial) output
dat.cont.variables = ['pressure', 'temperature', 'saturation']
dat.cont.time_interval = 10  # output every 10 days

# History (point) output
dat.hist.variables = ['pressure', 'temperature']
dat.hist.nodes = [1, 100, 500]  # specific nodes
```

### 9. File Paths
- [ ] Root filename set
- [ ] Working directory accessible

```python
dat.files.root = 'my_simulation'
```

---

## Optional Components

### Thermal Conductivity (`cond`)
```python
dat.zone[0].cond(cond_x=2.5, cond_y=2.5, cond_z=2.5)  # W/m/K
```

### Relative Permeability/Capillary Pressure (`rlp`)
```python
# For multiphase simulations
dat.rlp.type = 'van_genuchten'
dat.rlp.parameters = {'slr': 0.1, 'sgr': 0.05, 'n': 2.0}
```

### Solute Transport (`trac`)
```python
dat.trac.on = True
dat.trac.add_species('tracer')
dat.trac.alpha_L = 10.0  # dispersivity
```

### Dual Porosity (`dpdp`)
```python
dat.dpdp.on = True
dat.dpdp.vf = 0.01
```

### Stress Coupling (`strs`)
```python
dat.strs.on = True
```

---

## Pre-Run Verification

Before calling `dat.run()`:

### 1. Check Grid
```python
print(f"Nodes: {dat.grid.n_nodes}")
print(f"Elements: {dat.grid.n_elements}")
print(f"Zones: {list(dat.zone.keys())}")
```

### 2. Verify Properties Assigned
```python
# Check that key macros are populated
print(f"Rock macro zones: {len(dat.rock)}")
print(f"Perm macro zones: {len(dat.perm)}")
print(f"Pres macro zones: {len(dat.pres)}")
```

### 3. Validate BCs
```python
# List fixed pressure/temperature zones
for z in dat.zone.values():
    if hasattr(z, '_fix_pressure') and z._fix_pressure:
        print(f"Zone {z.name}: P={z._fix_pressure}")
```

### 4. Check Time Settings
```python
print(f"Final time: {dat.tf}")
print(f"Initial dt: {dat.dti}")
print(f"Max dt: {dat.dtmax}")
```

---

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| No permeability | No flow, static solution | Add `perm` macro |
| No initial conditions | Solver fails immediately | Add `pres` or `grad` |
| Missing rock properties | Wrong accumulation | Add `rock` macro |
| No driving BC | Static solution | Add pressure difference or source |
| Unrealistic values | Timestep cuts, NaN | Check unit conversions |
| Wrong zone assignment | Properties not applied | Verify zone contains expected nodes |

---

## Minimal Working Example

```python
from fdata import fdata

# Create simulation object
dat = fdata()

# 1. Grid
dat.grid.make('simple', type='xyz',
              origin=[0, 0, 0],
              nodelist=[[0, 10, 20, 30, 40, 50],
                        [0, 10],
                        [0, -5]])

# 2. Zones
inlet = dat.grid.zone(rect=[[0, 0], [0, 10], [-5, 0]])
inlet.name = 'inlet'
outlet = dat.grid.zone(rect=[[50, 50], [0, 10], [-5, 0]])
outlet.name = 'outlet'

# 3. Rock properties
dat.zone[0].rock(density=2500, specific_heat=1000, porosity=0.1)

# 4. Permeability
dat.zone[0].perm(kx=1e-14, ky=1e-14, kz=1e-14)

# 5. Initial conditions
dat.zone[0].pres(pressure=10, temperature=25)

# 6. Boundary conditions
dat.zone['inlet'].fix_pressure(11, temperature=25)
dat.zone['outlet'].fix_pressure(10, temperature=25)

# 7. Time control
dat.tf = 100  # days

# 8. Output
dat.cont.variables = ['pressure', 'temperature']

# 9. Files
dat.files.root = 'simple_flow'

# Run (always verbose=False)
dat.run('simple_flow.dat', verbose=False)
```
