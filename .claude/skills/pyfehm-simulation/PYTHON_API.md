# PyFEHM Python API Guide

Overview of the Python modules that make up PyFEHM. This covers the objects you use
to build simulations (`fdata`, `fgrid`, `fzone`, `fboun`), query fluid properties
(`fvars`), and read output (`fpost`).

For FEHM macro syntax and parameter tables see `MACROS.md` and `macros/INDEX.md`.

---

## Module Map

| Module | Import | Purpose |
|--------|--------|---------|
| `fdata` | `from fdata import fdata, fmacro, fmodel, fzone, fboun` | Simulation container — grid, macros, BCs, run |
| `fgrid` | (accessed via `dat.grid`) | Grid creation, reading, node/element objects |
| `fzone` | (defined in `fdata.py`) | Zone definition, material assignment, BC shortcuts |
| `fpost` | `from fpost import fcontour, fhistory` | Parse contour and history output files |
| `fvars` | `from fvars import dens, visc, enth, sat, tsat` | Fluid property lookups (EOS) |

---

## 1. fdata — Simulation Container

`fdata` is the top-level object. It holds the grid, all macros, zones, time control,
output settings, and can write/run FEHM input files.

### Creation

```python
from fdata import fdata, fmacro, fmodel

dat = fdata()                         # empty simulation
dat = fdata(work_dir='path/to/dir')   # set working directory
```

### Key Properties

| Property | Type | Description |
|----------|------|-------------|
| `dat.grid` | `fgrid` | Grid object (see Section 2) |
| `dat.zone` | dict | Zones indexed by number or name: `dat.zone[0]`, `dat.zone['XMIN']` |
| `dat.zonelist` | list | All zone objects |
| `dat.tf` | float | Final simulation time (days) |
| `dat.dti` | float | Initial timestep (days) |
| `dat.dtmax` | float | Maximum timestep (days) |
| `dat.dtmin` | float | Minimum timestep (days) |
| `dat.cont` | object | Contour output settings |
| `dat.hist` | object | History output settings |
| `dat.files` | object | File path settings (`.root`, `.grid`, `.co2in`, etc.) |
| `dat.ctrl` | dict | Solver control parameters |
| `dat.sol` | dict | Solution method parameters |
| `dat.carb` | object | CO2 module control (`.on(iprtype=...)`) |
| `dat.nobr` | bool | No-breakout flag (needed for CO2 simulations) |
| `dat.output_times` | list | Specific contour output times (days) |

### Adding Macros

All physics is added through macros via `dat.add()`:

```python
# Material properties — applied to all nodes (zone 0) or a named zone
dat.add(fmacro('rock', param=(
    ('density', 2500), ('specific_heat', 1000), ('porosity', 0.1))))

dat.add(fmacro('perm', param=(
    ('kx', 1e-15), ('ky', 1e-15), ('kz', 1e-15))))

dat.add(fmacro('cond', param=(
    ('cond_x', 2.5), ('cond_y', 2.5), ('cond_z', 2.5))))

# Initial conditions
dat.add(fmacro('pres', param=(
    ('pressure', 10.0), ('temperature', 25.0), ('saturation', 1))))

# Source/sink — zone-specific
dat.add(fmacro('flow', zone='XMIN', param=(
    ('rate', -0.001), ('energy', -25.0), ('impedance', 0))))

# Relative permeability model
dat.add(fmodel('rlp', index=17, param=[0.05, 1, 1, 0, ...]))
```

**Zone targeting**: Pass `zone=` as an integer index, string name, or fzone object.
Omitting `zone` applies the macro to zone 0 (all nodes).

### Output Configuration

```python
# Contour (spatial snapshots)
dat.cont.variables = ['pressure', 'temperature']      # what to output
dat.cont.format = 'surf'                               # 'surf', 'tec', or 'avs'
dat.output_times = [0.1, 1.0, 10.0, 100.0]            # when (days)

# History (time series at selected nodes)
dat.hist.nodelist = [1, 51, 101]                       # which nodes
dat.hist.variables = ['pressure', 'temperature']
dat.hist.time_interval = 0.01                          # output interval (days)
```

For CO2 simulations, add `'co2s'` to contour variables to get CO2 saturation columns.

### Writing and Running

```python
dat.files.root = 'my_sim'
dat.write('my_sim.dat')                    # write input file only
dat.run('my_sim.dat', exe=FEHM_EXE, verbose=False)  # write + run
```

**Always use `verbose=False`** to avoid flooding context with FEHM console output.

### CO2 Module

```python
dat.nobr = True
dat.carb.on(iprtype=3)  # 1=CO2-only, 2=CO2-only(alt), 3=water+CO2, 4=water+CO2+air
dat.files.co2in = 'path/to/co2_interp_table.txt'

# CO2 initial conditions
dat.add(fmacro('co2pres', param=(
    ('pressure', 20.0), ('temperature', 60.0), ('phase', 1))))
dat.add(fmacro('co2frac', param=(
    ('water_rich_sat', 1.0), ('co2_rich_sat', 0.0),
    ('co2_mass_frac', 0.0), ('init_salt_conc', 0.0), ('override_flag', 1))))

# CO2 injection
dat.add(fmacro('co2flow', zone='XMIN', param=(
    ('rate', -0.001), ('energy', -60.0), ('impedance', 0), ('bc_flag', 6))))
```

---

## 2. fgrid — Grid Creation and Access

The grid is accessed through `dat.grid` after creating or reading a mesh.

### Creating a Grid

```python
# Cartesian
dat.grid.make(
    gridfilename='grid.inp',
    x=[0, 10, 20, 50, 100],     # node x-coordinates
    y=[0, 1],                     # y-coordinates
    z=[0, 1],                     # z-coordinates
)

# Radial wedge (1-degree cylindrical sector)
# x = radial distance, y forced to [-1,1], z = thickness
dat.grid.make(
    gridfilename='grid.inp',
    x=list(np.logspace(np.log10(0.5), np.log10(1000), 101)),
    y=[0, 1],       # overridden to [-1, 1] internally
    z=[0, 1],
    radial=True,     # transforms y -> y * x * tan(pi/360)
)
```

After `make()`, call `dat._add_boundary_zones()` to auto-create boundary zones.

### Reading an Existing Grid

```python
dat.grid.read('grid.inp')                    # FEHM format
dat.grid.read('grid.inp', full_connectivity=True)  # also read elements/connections
dat.grid.read('grid.inp', octree=True)       # build spatial search tree
```

### Grid Properties

| Property | Type | Description |
|----------|------|-------------|
| `dat.grid.nodelist` | list[fnode] | All nodes |
| `dat.grid.node` | dict | Nodes by index: `dat.grid.node[10]` |
| `dat.grid.connlist` | list[fconn] | Connections (requires `full_connectivity=True`) |
| `dat.grid.elemlist` | list[felem] | Elements (requires `full_connectivity=True`) |
| `dat.grid.number_nodes` | int | Total node count |
| `dat.grid.dimensions` | int | 2 or 3 |
| `dat.grid.xmin`, `xmax` | float | Domain extent in x |
| `dat.grid.ymin`, `ymax` | float | Domain extent in y |
| `dat.grid.zmin`, `zmax` | float | Domain extent in z |

### Node Objects (fnode)

```python
nd = dat.grid.node[10]
nd.index                 # 10
nd.position              # [x, y, z]
nd.connected_nodes       # list of connected fnode objects
```

### Spatial Search

```python
nd = dat.grid.node_nearest_point([50, 0.5, 0.5])   # nearest node to a point
nds = dat.grid.nodes_nearest_points([[0,0,0], [100,0,0]])  # vectorized
```

### Boundary Zones (auto-created)

After `dat._add_boundary_zones()`, these zones exist:

| Zone Name | Index | Contains |
|-----------|-------|----------|
| `XMIN` | 999 | All nodes at minimum x-coordinate |
| `XMAX` | 998 | All nodes at maximum x-coordinate |
| `YMIN` | 997 | All nodes at minimum y-coordinate |
| `YMAX` | 996 | All nodes at maximum y-coordinate |
| `ZMIN` | 995 | All nodes at minimum z-coordinate (3D only) |
| `ZMAX` | 994 | All nodes at maximum z-coordinate (3D only) |

Access: `dat.zone['XMIN']`, `dat.zone[999]`.

---

## 3. fzone — Zones, Materials, and Boundary Conditions

Zones group nodes for assigning properties and boundary conditions.

### Zone Types

```python
from fdata import fzone

# Rectangular zone (defined by bounding box, nodes assigned from grid)
zn = fzone(index=10, type='rect', name='aquifer')
zn.rect = [[x0, x1], [y0, y1], [z0, z1]]

# Node-list zone (explicit node membership)
zn = fzone(index=11, type='nnum', name='well_nodes')
zn.nodelist = [1, 2, 3, 4]

# Add to simulation
dat.add(zn)
```

### Zone Properties

| Property | Type | Description |
|----------|------|-------------|
| `zn.index` | int | Zone number |
| `zn.name` | str | Zone name |
| `zn.nodelist` | list | Nodes in zone |
| `zn.type` | str | `'rect'`, `'list'`, or `'nnum'` |

### Boundary Condition Shortcuts

These methods generate the appropriate FEHM macros internally. The zone must be
added to an `fdata` object first.

```python
# Fixed pressure (uses flow macro with high impedance)
dat.zone['XMIN'].fix_pressure(P=20.0, T=60.0)

# Fixed temperature (uses hflx macro with high multiplier)
# WARNING: multiplier must scale inversely with grid spacing for accuracy
dat.zone['ZMAX'].fix_temperature(T=100.0, multiplier=1e10)

# Fixed heating rate (uses hflx with multiplier=0)
# Positive Q = heat INTO reservoir (sign handled internally)
dat.zone['heater'].fix_heating_rate(Q=0.001)  # 1 kW = 0.001 MW

# Fixed displacement (uses stressboun macro)
dat.zone['XMIN'].fix_displacement(direction='x', displacement=0.0)

# Roller BC (zero normal displacement, auto-detects direction from zone name)
dat.zone['XMIN'].roller()

# Free surface (zero normal stress)
dat.zone['ZMAX'].free_surface()
```

---

## 4. fboun — Time-Varying Boundary Conditions

`fboun` wraps FEHM's `boun` macro for boundary conditions that change over time.

### Basic Usage

```python
from fdata import fboun

boun = fboun(
    zone=['injection'],            # zone name(s) or fzone object(s)
    type='ti',                     # 'ti' = step changes, 'ti_linear' = linear ramp
    times=[0, 10, 100, 365],       # time points (days)
    variable=[
        ['pw', 20.0, 22.0, 25.0, 25.0],    # pressure at each time
        ['ft', 60.0, 60.0, 80.0, 80.0],    # temperature at each time
    ]
)
dat.add(boun)
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `zone` | list | Zone(s) — names, indices, or fzone objects |
| `type` | str | `'ti'` (piecewise constant) or `'ti_linear'` (linearly interpolated) |
| `times` | list[float] | Time points in days |
| `variable` | list[list] | Each sub-list: `[var_name, val_at_t0, val_at_t1, ...]` |

### Common Variable Names

| Name | Description | Units |
|------|-------------|-------|
| `pw` | Pressure (water) | MPa |
| `ft` | Temperature | °C |
| `dsw` | Saturation change rate | 1/day |
| `sw` | Water saturation | fraction |
| `t` | Temperature (alt) | °C |

### Example: Ramped Injection

```python
# Linearly ramp injection rate from 0 to full over 30 days, then hold
boun = fboun(
    zone=[dat.zone['well']],
    type='ti_linear',
    times=[0, 30, 365],
    variable=[
        ['dsw', 0.0, -1.0, -1.0],      # saturation change rate
        ['ft', 60.0, 60.0, 60.0],       # constant temperature
    ]
)
dat.add(boun)
```

---

## 5. fpost — Output Parsing

**Always use fpost** to read FEHM output. Never write custom parsers.

### fcontour — Spatial Snapshots

Reads contour CSV/AVS files (one per output time).

```python
from fpost import fcontour

cont = fcontour('path/to/root*_sca_node.csv')   # wildcard for all times
```

| Property / Method | Returns | Description |
|-------------------|---------|-------------|
| `cont.times` | ndarray | Sorted array of output times (days) |
| `cont.variables` | list[str] | Available variable names |
| `cont[time]` | dict | Data at given time: `{var_name: ndarray}` |
| `cont[time]['P']` | ndarray | Pressure array (0-indexed, one value per node) |

**Variable name mappings** (FEHM column header → fcontour key):

| CSV Header | Key | Notes |
|------------|-----|-------|
| Liquid Pressure (MPa) | `'P'` | |
| Vapor Pressure (MPa) | `'P_vap'` | |
| Temperature (deg C) | `'T'` | |
| node | `'n'` | Node numbers (1-based values in a 0-indexed array) |
| Water Saturation | `'water'` or `'saturation'` | Format-dependent |
| Super-Critical/Liquid CO2 Saturation | `'co2_liquid'` (surf) or `'co2_sc_liquid'` (tec) | |
| Gaseous CO2 Saturation | `'co2_gas'` | |

**Critical**: Contour arrays are **0-indexed**. FEHM node 1 is at array index 0.
To get the value for a specific node: `cont[t]['P'][node.index - 1]`.

**Surf format does not include coordinates**. The `'n'` variable gives node numbers,
but `'x'`, `'y'`, `'z'` are not available. Read coordinates from `grid.inp` and
map via node number:

```python
# Read grid coordinates
node_x = {}  # {node_number: x_coordinate}
with open('grid.inp') as f:
    lines = f.readlines()
    # parse coor block...

# Map to contour data
node_nums = cont[t]['n']
x_all = np.array([node_x[int(n)] for n in node_nums])
P_all = cont[t]['P']
```

### fhistory — Time Series

Reads history `*_his.dat` files (one file per variable).

```python
from fpost import fhistory

hist = fhistory('path/to/root_presWAT_his.dat')
```

| Property / Method | Returns | Description |
|-------------------|---------|-------------|
| `hist.times` | ndarray | Sorted time array (days) |
| `hist.variables` | list[str] | Available variable names |
| `hist.nodes` | list[int] | Node numbers with data (FEHM ordering) |
| `hist[var_name]` | dict | `{node_number: ndarray}` time series |
| `hist['P'][1]` | ndarray | Pressure time series at node 1 |

**Variable name mappings** (history file suffix → fhistory key):

| File Suffix | Key |
|-------------|-----|
| `presWAT` | `'P'` |
| `presVAP` | `'P_vap'` |
| `presCAP` | `'P_cap'` |
| `presCO2` | `'P_co2'` |
| `temp` | `'T'` |
| `satr` | `'saturation'` |
| `denWAT` | `'density'` |
| `co2md` | `'massfrac_co2_aq'` |
| `co2mf` | `'massfrac_co2_free'` |
| `co2mt` | `'mass_co2'` |
| `co2sg` | `'saturation_co2g'` |
| `co2sl` | `'saturation_co2l'` |

**Node ordering**: FEHM orders history columns by node number (ascending), not by
the order nodes were specified in the input. `fhistory` handles this — just use
the node number directly: `hist['P'][node_id]`.

### Typical Output Reading Pattern

```python
from fpost import fcontour, fhistory

# Pressure profiles at each output time
cont = fcontour(os.path.join(work_dir, f'{root}*_sca_node.csv'))
for t in cont.times:
    if t <= 0: continue
    P = cont[t]['P']
    # ... process

# Pressure history at injection node
hist = fhistory(os.path.join(work_dir, f'{root}_presWAT_his.dat'))
inj_node = min(hist.nodes)           # smallest node = XMIN
P_vs_t = hist['P'][inj_node]         # ndarray
times = hist.times                    # ndarray
```

---

## 6. fvars — Fluid Property Lookups

Standalone functions that call FEHM's equation-of-state correlations.
Useful for computing injection rates, analytical comparisons, or sanity checks.

```python
from fvars import dens, visc, enth, sat, tsat
```

### Functions

**`dens(P, T, derivative='')`** — Density

```python
rho_l, rho_v, rho_co2 = dens(20.0, 60.0)
# rho_l  = liquid water density (kg/m³)
# rho_v  = water vapor density (kg/m³)
# rho_co2 = CO2 density (kg/m³)

# Derivatives
drho_l_dT, _, _ = dens(20.0, 60.0, derivative='T')   # ∂ρ/∂T
drho_l_dP, _, _ = dens(20.0, 60.0, derivative='P')   # ∂ρ/∂P
```

**`visc(P, T, derivative='')`** — Viscosity

```python
mu_l, mu_v, mu_co2 = visc(20.0, 60.0)
# mu_l   = liquid water viscosity (Pa·s)
# mu_v   = water vapor viscosity (Pa·s)
# mu_co2 = CO2 viscosity (Pa·s * 1e-6, check units)
```

**`enth(P, T, derivative='')`** — Enthalpy

```python
h_l, h_v, h_co2 = enth(20.0, 60.0)
# h_l   = liquid water enthalpy (J/kg)
# h_v   = water vapor enthalpy (J/kg)
# h_co2 = CO2 enthalpy (J/kg)
```

**`sat(T)`** — Saturation pressure from temperature

```python
P_sat, dPsat_dT = sat(100.0)   # returns (0.1013 MPa, derivative)
```

**`tsat(P)`** — Saturation temperature from pressure

```python
T_sat, dTsat_dP = tsat(0.1013)  # returns (100.0 °C, derivative)
```

**`fluid_column(z, Tgrad, Tsurf, Psurf, iterations=3)`** — Hydrostatic column

```python
from fvars import fluid_column

z = np.linspace(0, 3000, 100)        # depths (m)
props_l, props_v, props_co2 = fluid_column(
    z, Tgrad=0.03, Tsurf=15.0, Psurf=0.1, iterations=3)
# Each array: columns = [P(MPa), T(°C), ρ(kg/m³), h(J/kg), μ(Pa·s)]
```

**`mco2(P, T, nc=0.)`** — CO2 solubility in water

```python
from fvars import mco2

solubility = mco2(20.0, 60.0)       # kg CO2 / kg H2O
solubility = mco2(20.0, 60.0, nc=1.0)  # with 1 mol/kg NaCl
```

### Typical Usage

```python
# Compute equal-volume CO2 injection rate from a water rate
rho_w, _, rho_co2 = dens(P0, T0)
Q_co2 = Q_water * (float(rho_co2[0]) / float(rho_w[0]))

# Get water viscosity for analytical Darcy flow
_, mu_w_arr, _ = visc(P0, T0)
mu_w = float(mu_w_arr[0])  # Pa·s
```

---

## Quick Reference: Common Workflows

### Minimal Simulation Setup

```python
from fdata import fdata, fmacro
dat = fdata(work_dir='my_dir')

# Grid
dat.grid.make(gridfilename='grid.inp', x=[0,100,200,...], y=[0,1], z=[0,1])
dat._add_boundary_zones()

# Properties
dat.add(fmacro('rock', param=(('density',2500),('specific_heat',1000),('porosity',0.1))))
dat.add(fmacro('perm', param=(('kx',1e-15),('ky',1e-15),('kz',1e-15))))
dat.add(fmacro('cond', param=(('cond_x',2.5),('cond_y',2.5),('cond_z',2.5))))
dat.add(fmacro('pres', param=(('pressure',10.0),('temperature',25.0),('saturation',1))))

# BCs, time, output
dat.zone['XMIN'].fix_pressure(12.0, T=25.0)
dat.tf = 365.0; dat.dti = 0.01; dat.dtmax = 1.0
dat.cont.variables = ['pressure','temperature']; dat.cont.format = 'surf'
dat.output_times = [1, 10, 100, 365]
dat.hist.nodelist = [1]; dat.hist.variables = ['pressure']; dat.hist.time_interval = 0.1
dat.files.root = 'test'

dat.run('test.dat', exe='path/to/fehm.exe', verbose=False)
```

### Reading Results After Simulation

```python
from fpost import fcontour, fhistory

# Spatial data
cont = fcontour('my_dir/test*_sca_node.csv')
P_final = cont[cont.times[-1]]['P']          # pressure at final time

# Time series
hist = fhistory('my_dir/test_presWAT_his.dat')
plt.plot(hist.times, hist['P'][1])           # pressure vs time at node 1
```
