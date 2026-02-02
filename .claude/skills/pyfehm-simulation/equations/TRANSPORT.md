# Solute and Reactive Transport Equations

FEHM solves advection-dispersion equations for solute transport, with options for reactive transport and particle tracking.

---

## Solute Transport Equation

### General Form
```
∂/∂t (φ S_l ρ_l C) + ∇·(C f_m - φ S_l ρ_l D ∇C) = q_s + R
```

Where:
- `C` = solute concentration (kg/kg or mol/kg)
- `f_m` = mass flux from Darcy flow
- `D` = dispersion tensor (m²/s)
- `q_s` = source/sink term
- `R` = reaction terms

### Dispersion Tensor
```
D_ij = α_T |v| δ_ij + (α_L - α_T) v_i v_j / |v| + D_m τ δ_ij
```

Where:
- `α_L` = longitudinal dispersivity (m)
- `α_T` = transverse dispersivity (m)
- `D_m` = molecular diffusion coefficient (m²/s)
- `τ` = tortuosity factor
- `v` = pore velocity vector
- `|v|` = velocity magnitude

### Simplified 1D Form
```
∂C/∂t + v ∂C/∂x = D_L ∂²C/∂x² + R
```

Where `D_L = α_L v + D_m τ`.

---

## Sorption Models

Sorption retards solute transport via equilibrium partitioning between fluid and solid phases.

### Linear Isotherm
```
C_s = K_d C
```

Where:
- `C_s` = sorbed concentration (kg/kg solid)
- `K_d` = distribution coefficient (m³/kg)

Retardation factor:
```
R_f = 1 + (1-φ) ρ_s K_d / (φ S_l ρ_l)
```

### Freundlich Isotherm
```
C_s = K_f C^n
```

Where:
- `K_f` = Freundlich coefficient
- `n` = Freundlich exponent (n < 1 typical)

### Langmuir Isotherm
```
C_s = (K_l C_max C) / (1 + K_l C)
```

Where:
- `K_l` = Langmuir constant
- `C_max` = maximum sorption capacity

---

## Reactive Transport

### Multi-Component System
For component `i`:
```
∂/∂t (φ S_l C_i^aq + φ S_g C_i^vap + C_i^imm) + ∇·J_i = R_i
```

Where:
- `C_i^aq` = aqueous concentration
- `C_i^vap` = vapor concentration
- `C_i^imm` = immobile (sorbed + precipitated)
- `J_i` = total flux (advective + dispersive)
- `R_i` = reaction rate

### Reaction Types

#### First-Order Decay
```
R = -λ C
```

Where `λ` is decay constant (1/s). Half-life: `t_1/2 = ln(2)/λ`.

#### Kinetic Sorption
```
∂C_s/∂t = k_f C - k_b C_s
```

Where:
- `k_f` = forward rate constant
- `k_b` = backward rate constant

At equilibrium: `K_d = k_f / k_b`.

#### Monod Kinetics (Biodegradation)
```
R = -v_max C / (K_m + C) × B
```

Where:
- `v_max` = maximum reaction rate
- `K_m` = half-saturation constant
- `B` = biomass concentration

#### Precipitation/Dissolution
```
R = k (1 - Ω)
```

Where:
- `k` = rate constant
- `Ω` = saturation index (Ω > 1 supersaturated, Ω < 1 undersaturated)

---

## Particle Tracking

FEHM includes a Lagrangian particle tracking method as an alternative to solving the ADE.

### Particle Motion
```
x(t+Δt) = x(t) + v Δt + ξ √(2D Δt)
```

Where:
- `v` = advective velocity from flow solution
- `ξ` = random number (normal distribution)
- `D` = dispersion coefficient

### Residence Time Distribution
Particle arrival times at outlet give breakthrough curve:
```
C(t) ∝ dN/dt
```

Where `N` is cumulative particles arrived.

### Retardation in Particle Tracking
Particles delayed by factor `R_f`:
```
t_arrival = R_f × t_advective
```

Or probabilistic approach: particle "stuck" for random time based on sorption.

### Matrix Diffusion
For fractured media, particles can diffuse into matrix:
```
P_enter = 1 - exp(-k_md Δt)
```

Residence time in matrix follows:
```
t_matrix ~ (penetration_depth)² / D_matrix
```

### Radioactive Decay
During transport:
```
P_survive = exp(-λ t_travel)
```

### Chain Decay
For decay chains (e.g., U-238 → Th-234 → ...):
```
∂C_i/∂t = -λ_i C_i + λ_{i-1} C_{i-1}
```

---

## Discretization

### Control Volume Method
For node `i`:
```
V_i ∂(φ S C)_i/∂t + Σ_j F_ij = V_i (q_s + R)_i
```

### Advective Flux
Upwind scheme:
```
F_adv,ij = max(Q_ij, 0) C_i + min(Q_ij, 0) C_j
```

Where `Q_ij` is volumetric flow rate between nodes.

### Dispersive Flux
```
F_disp,ij = -D_ij A_ij (C_j - C_i) / d_ij
```

### TVD Schemes
For sharp fronts, FEHM supports Total Variation Diminishing schemes to reduce numerical dispersion.

---

## PyFEHM Implementation

### Basic Solute Transport
```python
# Enable transport
dat.trac.on = True

# Define species
dat.trac.add_species('tracer')

# Set dispersivity
dat.trac.alpha_L = 10.0  # longitudinal (m)
dat.trac.alpha_T = 1.0   # transverse (m)
dat.trac.diffusion = 1e-9  # molecular diffusion (m²/s)

# Initial concentration
dat.zone[0].trac_conc('tracer', 0.0)

# Injection concentration
inlet_zone.trac_conc('tracer', 1.0)
```

### Sorption
```python
# Linear sorption
dat.trac.species['tracer'].sorption = 'linear'
dat.trac.species['tracer'].Kd = 1e-3  # m³/kg

# Freundlich
dat.trac.species['tracer'].sorption = 'freundlich'
dat.trac.species['tracer'].Kf = 1e-3
dat.trac.species['tracer'].n = 0.8
```

### Radioactive Decay
```python
dat.trac.species['tracer'].half_life = 30.17 * 365.25  # Cs-137 in days
```

### Particle Tracking
```python
# Enable particle tracking
dat.ptrk.on = True
dat.ptrk.n_particles = 1000

# Release location
dat.ptrk.release_zone = inlet_zone

# Output
dat.ptrk.output_times = [1, 10, 100, 365]
```

---

## Numerical Considerations

### Peclet Number
```
Pe = v Δx / D
```

- `Pe < 2`: Stable central differencing
- `Pe > 2`: Need upwinding or TVD

### Courant Number
```
Co = v Δt / Δx
```

- `Co < 1` required for explicit schemes
- Implicit schemes stable for larger Co but may be diffusive

### Grid Peclet Guideline
For accurate fronts without excessive numerical dispersion:
```
Δx < 2 α_L
```
