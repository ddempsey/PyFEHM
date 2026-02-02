# FEHM Macros Reference

This document covers common FEHM macros and their PyFEHM implementation.

---

## Rock Properties

### `rock` - Rock Density, Specific Heat, Porosity

**Purpose**: Define solid matrix properties for accumulation terms.

**Parameters**:
| Parameter | Units | Description |
|-----------|-------|-------------|
| density | kg/m³ | Rock grain density |
| specific_heat | J/kg/K | Rock specific heat capacity |
| porosity | - | Void fraction (0-1) |

**PyFEHM**:
```python
dat.zone[0].rock(
    density=2500,        # kg/m³
    specific_heat=1000,  # J/kg/K
    porosity=0.1
)

# Zone-specific
dat.zone['aquifer'].rock(density=2650, specific_heat=800, porosity=0.25)
dat.zone['caprock'].rock(density=2700, specific_heat=900, porosity=0.01)
```

**Typical Values**:
| Rock Type | Density | Specific Heat | Porosity |
|-----------|---------|---------------|----------|
| Sandstone | 2650 | 800-900 | 0.1-0.3 |
| Shale | 2700 | 800-1000 | 0.01-0.1 |
| Limestone | 2710 | 900 | 0.05-0.2 |
| Granite | 2750 | 790 | 0.001-0.01 |

---

## Flow Properties

### `perm` - Permeability

**Purpose**: Define intrinsic permeability tensor.

**Parameters**:
| Parameter | Units | Description |
|-----------|-------|-------------|
| kx | m² | Permeability in x-direction |
| ky | m² | Permeability in y-direction |
| kz | m² | Permeability in z-direction |

**PyFEHM**:
```python
# Isotropic
dat.zone[0].perm(kx=1e-15, ky=1e-15, kz=1e-15)

# Anisotropic (horizontal >> vertical)
dat.zone[0].perm(kx=1e-14, ky=1e-14, kz=1e-16)

# Zone shortcut
dat.zone['aquifer'].permeability = 1e-14  # isotropic
```

**Unit Conversions**:
| From | To m² | Factor |
|------|-------|--------|
| Darcy | m² | 9.87×10⁻¹³ |
| milliDarcy | m² | 9.87×10⁻¹⁶ |

### `cond` - Thermal Conductivity

**Purpose**: Define heat conduction properties.

**Parameters**:
| Parameter | Units | Description |
|-----------|-------|-------------|
| cond_x | W/m/K | Conductivity in x |
| cond_y | W/m/K | Conductivity in y |
| cond_z | W/m/K | Conductivity in z |

**PyFEHM**:
```python
dat.zone[0].cond(cond_x=2.5, cond_y=2.5, cond_z=2.5)
```

---

## Initial Conditions

### `pres` - Initial Pressure and Temperature

**Purpose**: Set uniform initial conditions.

**Parameters**:
| Parameter | Units | Description |
|-----------|-------|-------------|
| pressure | MPa | Initial fluid pressure |
| temperature | °C | Initial temperature |
| saturation | - | Initial liquid saturation (0-1) |

**PyFEHM**:
```python
# Single phase
dat.zone[0].pres(pressure=10, temperature=25)

# Two phase
dat.zone[0].pres(pressure=10, temperature=25, saturation=0.8)
```

### `grad` - Gradient Initial Conditions

**Purpose**: Set spatially varying initial conditions.

**Parameters**:
| Parameter | Units | Description |
|-----------|-------|-------------|
| ref_point | m | Reference coordinates [x, y, z] |
| ref_pressure | MPa | Pressure at reference point |
| ref_temperature | °C | Temperature at reference point |
| pressure_grad | MPa/m | Pressure gradient [dP/dx, dP/dy, dP/dz] |
| temperature_grad | °C/m | Temperature gradient |

**PyFEHM**:
```python
dat.zone[0].grad(
    ref_point=[0, 0, 0],
    ref_pressure=10.0,        # MPa at origin
    ref_temperature=25.0,     # °C at origin
    pressure_grad=[0, 0, -0.01],    # hydrostatic (~10 MPa/km)
    temperature_grad=[0, 0, 0.03]   # geothermal (~30 °C/km)
)
```

---

## Boundary Conditions

### `flow` - Mass/Energy Source

**Purpose**: Inject or extract mass and energy.

**Parameters**:
| Parameter | Units | Description |
|-----------|-------|-------------|
| mass_rate | kg/s | Mass flow rate (+ injection, - extraction) |
| enthalpy | J/kg | Specific enthalpy of injected fluid |
| impedance | Pa·s/kg | Flow impedance (optional) |

**PyFEHM**:
```python
# Fixed rate injection
dat.zone['well'].flow(mass_rate=1.0, enthalpy=1e5)  # 1 kg/s, ~24°C water

# Extraction (production)
dat.zone['producer'].flow(mass_rate=-0.5)  # enthalpy from reservoir

# With impedance (productivity index)
dat.zone['well'].flow(mass_rate=1.0, enthalpy=1e5, impedance=1e6)
```

**Enthalpy Reference**:
| Temperature | Enthalpy (liquid) |
|-------------|-------------------|
| 20°C | 84 kJ/kg |
| 50°C | 209 kJ/kg |
| 100°C | 419 kJ/kg |
| 200°C | 852 kJ/kg |

### `hflx` - Heat Flux

**Purpose**: Apply heat flux boundary condition.

**Parameters**:
| Parameter | Units | Description |
|-----------|-------|-------------|
| heat_flux | W/m² | Heat flux (+ into domain) |

**PyFEHM**:
```python
# Basal heat flux
dat.zone['bottom'].hflx(heat_flux=0.06)  # 60 mW/m² typical
```

### Zone Shortcuts for Fixed Conditions

**Purpose**: Fix pressure and/or temperature at boundary.

**PyFEHM**:
```python
# Fix pressure only
dat.zone['inlet'].fix_pressure(12)  # MPa

# Fix pressure and temperature
dat.zone['inlet'].fix_pressure(12, temperature=30)

# Fix temperature only
dat.zone['boundary'].fix_temperature(100)  # °C
```

### `boun` - Time-Varying Boundaries

**Purpose**: Specify boundaries that change with time.

**PyFEHM**:
```python
# Ramp up injection over time
times = [0, 10, 100, 365]      # days
rates = [0, 0.5, 1.0, 1.0]     # kg/s
enthalpies = [1e5, 1e5, 1e5, 1e5]  # J/kg

dat.zone['well'].boun(times=times, mass_rates=rates, enthalpies=enthalpies)
```

---

## Transport

### `trac` - Solute Transport

**Purpose**: Enable and configure solute transport.

**PyFEHM**:
```python
# Enable transport
dat.trac.on = True

# Add species
dat.trac.add_species('tracer')

# Dispersivity
dat.trac.alpha_L = 10.0   # longitudinal (m)
dat.trac.alpha_T = 1.0    # transverse (m)
dat.trac.diffusion = 1e-9 # molecular diffusion (m²/s)

# Initial concentration
dat.zone[0].trac_conc('tracer', 0.0)

# Injection concentration
dat.zone['inlet'].trac_conc('tracer', 1.0)

# Sorption
dat.trac.species['tracer'].sorption = 'linear'
dat.trac.species['tracer'].Kd = 1e-3  # m³/kg
```

---

## Multiphase

### `rlp` - Relative Permeability

**Purpose**: Define relative permeability model.

**Models**: `linear`, `corey`, `van_genuchten`, `brooks_corey`

**PyFEHM**:
```python
# Linear model
dat.rlp.type = 'linear'
dat.rlp.parameters = {
    'slr': 0.1,   # residual liquid saturation
    'sgr': 0.05   # residual gas saturation
}

# van Genuchten
dat.rlp.type = 'van_genuchten'
dat.rlp.parameters = {
    'slr': 0.1,
    'sgr': 0.05,
    'n': 2.0,
    'm': 0.5
}
```

### `cap` - Capillary Pressure

**Purpose**: Define capillary pressure model.

**PyFEHM**:
```python
dat.cap.type = 'van_genuchten'
dat.cap.parameters = {
    'p0': 1000,    # entry pressure (Pa)
    'n': 2.0,
    'slr': 0.1,
    'pmax': 1e6    # maximum capillary pressure (Pa)
}
```

---

## Control Parameters

### Time Control

```python
dat.tf = 365.25      # final time (days)
dat.dti = 0.001      # initial timestep (days)
dat.dtmax = 10.0     # maximum timestep (days)
dat.dtmin = 1e-8     # minimum timestep (days)
```

### Solver Control

```python
dat.ctrl['max_iterations'] = 50      # max Newton iterations
dat.ctrl['newton_tol'] = 1e-6        # convergence tolerance
dat.ctrl['linear_solver'] = 'gmres'  # linear solver type
```

---

## Output Control

### Contour Output (Spatial)

```python
dat.cont.variables = ['pressure', 'temperature', 'saturation', 'permeability']
dat.cont.format = 'tecplot'           # or 'avs', 'surfer'
dat.cont.time_interval = 10           # output every 10 days
dat.cont.times = [1, 10, 100, 365]    # specific output times
```

### History Output (Point)

```python
dat.hist.variables = ['pressure', 'temperature', 'flow']
dat.hist.nodes = [1, 50, 100]         # node numbers
dat.hist.time_interval = 0.1          # days
```

### Available Output Variables

| Variable | Description |
|----------|-------------|
| `pressure` | Fluid pressure |
| `temperature` | Temperature |
| `saturation` | Liquid saturation |
| `permeability` | Permeability field |
| `porosity` | Porosity field |
| `velocity` | Darcy velocity |
| `density` | Fluid density |
| `concentration` | Solute concentration |
| `head` | Hydraulic head |

---

## File Management

```python
# Set root filename
dat.files.root = 'my_simulation'

# This creates:
# - my_simulation.dat (input file)
# - my_simulation.outp (output/log)
# - my_simulation.con (contour output)
# - my_simulation.his (history output)

# Write input file without running
dat.write('my_simulation.dat')

# Write and run
dat.run('my_simulation.dat', verbose=False)
```
