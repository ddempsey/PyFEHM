# Dual Porosity and Double Permeability

FEHM supports fractured media through dual porosity (DP) and double permeability (DK) formulations.

---

## Conceptual Model

### Dual Porosity
- **Fracture continuum**: High permeability, low storage
- **Matrix continuum**: Low permeability, high storage
- Flow occurs primarily in fractures
- Matrix exchanges mass/energy with fractures

### Double Permeability
- Extension of dual porosity
- Allows flow in both fracture AND matrix continua
- Matrix blocks can communicate with each other

---

## Volume Fractions

### Definitions
```
V_total = V_f + V_m
```

Where:
- `V_f` = fracture volume
- `V_m` = matrix volume

Volume fractions:
```
v_f = V_f / V_total
v_m = V_m / V_total = 1 - v_f
```

### Fracture Porosity vs Bulk Porosity
```
φ_bulk = v_f φ_f + v_m φ_m
```

Typically:
- `v_f` ≈ 0.001-0.1
- `φ_f` ≈ 0.1-1.0
- `φ_m` ≈ 0.01-0.3

---

## Transfer Terms

### Mass Transfer (Fracture-Matrix)
```
q_fm = σ (k_m / μ) (P_f - P_m)
```

Where:
- `σ` = shape factor (m⁻²)
- `k_m` = matrix permeability
- `P_f`, `P_m` = fracture and matrix pressures

### Shape Factor
For slab-like matrix blocks:
```
σ = 12 / L²
```

For cubic blocks:
```
σ = 60 / L²
```

Where `L` is characteristic block dimension.

### Energy Transfer
```
q_e,fm = σ K_m (T_f - T_m) + h q_fm
```

Where:
- `K_m` = matrix thermal conductivity
- First term = conduction
- Second term = advective energy transfer

---

## Dual Porosity Equations

### Fracture Mass Balance
```
v_f ∂(φ_f ρ S)_f/∂t + ∇·(ρ v_f) = v_f q_f + q_fm
```

### Matrix Mass Balance
```
v_m ∂(φ_m ρ S)_m/∂t = v_m q_m - q_fm
```

Note: No flow divergence term in matrix (no matrix-matrix flow).

### Fracture Energy Balance
```
v_f ∂A_e,f/∂t + ∇·(h ρ v_f - K_f ∇T_f) = v_f q_e,f + q_e,fm
```

### Matrix Energy Balance
```
v_m ∂A_e,m/∂t = v_m q_e,m - q_e,fm
```

---

## Double Permeability Equations

### Fracture System
Same as dual porosity.

### Matrix System (with matrix-matrix flow)
```
v_m ∂(φ_m ρ S)_m/∂t + ∇·(ρ v_m) = v_m q_m - q_fm
```

The matrix now has its own Darcy flow term.

### Coupling
Both systems solved simultaneously with transfer terms coupling them.

---

## MINC (Multiple Interacting Continua)

### Concept
Discretize matrix into nested shells to capture:
- Transient diffusion into matrix
- Skin effects
- Non-uniform matrix properties

### Shell Volumes
```
V_1 = outer shell (contacts fracture)
V_2 = next inner shell
...
V_n = innermost shell
```

### Transfer Between Shells
```
q_i,i+1 = σ_i (k_i / μ) (P_i - P_{i+1})
```

### When to Use MINC
- Matrix diffusion timescale > simulation timestep
- Large matrix blocks (slow equilibration)
- Accurate early-time behavior needed

---

## Practical Considerations

### Estimating Shape Factor
From fracture spacing `s`:
```
σ ≈ 4n / s²
```

Where `n` = number of fracture sets (1, 2, or 3).

### Matrix Block Size
```
L = 2 / (fracture_density)
```

Or from fracture spacing:
```
L ≈ s
```

### Time Scales
Matrix equilibration time:
```
τ_m = L² μ / (σ k_m)
```

If `τ_m >> Δt`, consider MINC.

---

## PyFEHM Implementation

### Enable Dual Porosity
```python
# Set up dual porosity
dat.dpdp.on = True

# Fracture volume fraction
dat.dpdp.vf = 0.01

# Matrix properties
dat.dpdp.rock_matrix(density=2600, specific_heat=1000, porosity=0.05)
dat.dpdp.perm_matrix(kx=1e-18, ky=1e-18, kz=1e-18)

# Shape factor
dat.dpdp.sigma = 0.1  # m^-2
```

### Fracture Properties
```python
# Set fracture properties on main zones
dat.zone['fracture'].rock(density=2500, specific_heat=1000, porosity=0.5)
dat.zone['fracture'].perm(kx=1e-12, ky=1e-12, kz=1e-12)
```

### Double Permeability
```python
dat.dpdp.type = 'double'  # vs 'dual' for dual porosity only
```

### MINC
```python
dat.dpdp.minc = True
dat.dpdp.n_shells = 5
dat.dpdp.shell_volumes = [0.1, 0.2, 0.2, 0.2, 0.3]  # fractions
```

---

## Common Issues

### 1. Timestep Cuts
Dual porosity can cause convergence issues when:
- Large contrast between fracture and matrix properties
- Very small fracture volume fraction
- Large shape factor (rapid transfer)

**Fix**: Reduce initial timestep, use smaller shape factor.

### 2. Mass Balance Errors
Check that volume fractions sum to 1:
```
v_f + v_m = 1
```

### 3. Missing Matrix Properties
Must define properties for BOTH continua.

### 4. Transfer Coefficient
If transfer too slow: increase σ
If convergence problems: decrease σ

---

## Typical Values

| Parameter | Range | Notes |
|-----------|-------|-------|
| Fracture spacing | 0.1-10 m | Determines L |
| v_f | 0.001-0.1 | Fracture volume fraction |
| φ_f | 0.1-1.0 | Fracture porosity |
| φ_m | 0.01-0.3 | Matrix porosity |
| k_f | 10⁻¹²-10⁻⁹ m² | Fracture permeability |
| k_m | 10⁻²⁰-10⁻¹⁵ m² | Matrix permeability |
| σ | 0.01-100 m⁻² | Shape factor |
