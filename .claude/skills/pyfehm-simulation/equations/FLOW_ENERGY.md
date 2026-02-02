# Flow and Energy Equations

FEHM solves coupled mass and energy conservation equations for multiphase, multicomponent flow in porous media.

---

## Mass Conservation

### Single-Phase Flow
The mass accumulation term for phase `l`:

```
A_m = φ ρ_l S_l
```

Where:
- `φ` = porosity
- `ρ_l` = density of phase l (kg/m³)
- `S_l` = saturation of phase l

### Mass Flux (Darcy's Law)
The mass flux for phase `l`:

```
f_m,l = -ρ_l (k k_rl / μ_l) (∇P_l - ρ_l g ∇z)
```

Where:
- `k` = intrinsic permeability tensor (m²)
- `k_rl` = relative permeability of phase l
- `μ_l` = dynamic viscosity (Pa·s)
- `P_l` = phase pressure (Pa)
- `g` = gravitational acceleration (m/s²)
- `z` = elevation (m)

### General Mass Balance
```
∂A_m/∂t + ∇·f_m = q_m
```

Where `q_m` is the mass source/sink term (kg/m³/s).

---

## Energy Conservation

### Energy Accumulation
```
A_e = (1-φ) ρ_r c_r T + φ Σ_l (ρ_l S_l u_l)
```

Where:
- `ρ_r` = rock density (kg/m³)
- `c_r` = rock specific heat (J/kg/K)
- `T` = temperature (°C or K)
- `u_l` = specific internal energy of phase l (J/kg)

### Energy Flux
Energy transport includes advection and conduction:

```
f_e = Σ_l (h_l f_m,l) - K_eff ∇T
```

Where:
- `h_l` = specific enthalpy of phase l (J/kg)
- `K_eff` = effective thermal conductivity (W/m/K)

### Effective Thermal Conductivity
```
K_eff = (1-φ) K_r + φ (S_l K_l + S_g K_g)
```

### General Energy Balance
```
∂A_e/∂t + ∇·f_e = q_e
```

Where `q_e` is the energy source/sink (W/m³).

---

## Multiphase (Water-Air) System

### Phase Pressures
```
P_g = P_l + P_cap
```

Where `P_cap` is capillary pressure.

### Air Mass Conservation
For noncondensible gas (air) component:

```
∂/∂t [φ (ρ_a,l S_l + ρ_a,g S_g)] + ∇·(ρ_a,l v_l + ρ_a,g v_g) = q_a
```

Where:
- `ρ_a,l` = dissolved air mass concentration in liquid
- `ρ_a,g` = air density in gas phase
- `v_l`, `v_g` = Darcy velocities

### Water Mass Conservation
```
∂/∂t [φ (ρ_w,l S_l + ρ_w,g S_g)] + ∇·(ρ_w,l v_l + ρ_w,g v_g) = q_w
```

### Henry's Law (Air Dissolution)
```
ρ_a,l = H_a P_a
```

Where `H_a` is Henry's constant for air in water.

---

## Isothermal Air-Water Equations

When temperature effects are negligible, the system reduces to:

### Liquid Phase
```
∂/∂t (φ ρ_l S_l) + ∇·(ρ_l v_l) = q_l
```

### Gas Phase
```
∂/∂t (φ ρ_g S_g) + ∇·(ρ_g v_g) = q_g
```

### Saturation Constraint
```
S_l + S_g = 1
```

---

## Discretized Form

FEHM uses finite volume discretization with:

### Transmissibility
Between nodes `i` and `j`:

```
T_ij = A_ij / d_ij × (k k_r / μ)_ij
```

Where:
- `A_ij` = interface area
- `d_ij` = distance between nodes
- Properties evaluated at upstream node (upwinding)

### Discrete Mass Balance
```
V_i (A_m,i^(n+1) - A_m,i^n) / Δt + Σ_j T_ij (P_i - P_j - ρ g Δz_ij) = Q_i
```

### Time Discretization
FEHM uses fully implicit time stepping:
- All terms evaluated at new time level `n+1`
- Newton-Raphson iteration for nonlinear system
- Automatic timestep control based on convergence

---

## Boundary Conditions

### Pressure BC (Dirichlet)
Fixed pressure at boundary:
```
P = P_boundary
```

Implemented via `fix_pressure()` or large-volume nodes.

### Temperature BC (Dirichlet)
Fixed temperature:
```
T = T_boundary
```

Implemented via `fix_temperature()`.

### Mass Flux BC (Neumann)
Specified mass inflow/outflow:
```
q_m = m_dot / V_node  (kg/m³/s)
```

Implemented via `flow` macro.

### Heat Flux BC (Neumann)
Specified heat flux:
```
q_e = q_dot / V_node  (W/m³)
```

Implemented via `hflx` macro.

### No-Flow BC
Default boundary condition (zero flux):
```
∇P · n = 0
```

---

## Key Assumptions

1. **Local thermal equilibrium**: Rock and fluid at same temperature
2. **Darcy flow**: Valid for low Reynolds number (Re < 1)
3. **Immiscible phases**: Sharp interface between liquid and gas
4. **Rigid rock matrix**: Porosity constant (unless stress coupling enabled)
5. **No chemical reactions**: Pure flow/transport (unless reactive transport enabled)

---

## PyFEHM Implementation

### Setting Up Flow Problem
```python
# Rock properties (affects accumulation)
dat.zone[0].rock(density=2500, specific_heat=1000, porosity=0.1)

# Permeability (affects flux)
dat.zone[0].perm(kx=1e-15, ky=1e-15, kz=1e-15)

# Initial conditions
dat.zone[0].pres(pressure=10, temperature=25, saturation=1.0)

# Boundary conditions
inlet_zone.fix_pressure(12, temperature=25)
outlet_zone.fix_pressure(10, temperature=25)
```

### Enabling Air-Water
```python
dat.carb.iprtype = 1  # Enable noncondensible gas
```

### Controlling Solver
```python
dat.ctrl['max_iterations'] = 50
dat.ctrl['newton_tol'] = 1e-6
```
