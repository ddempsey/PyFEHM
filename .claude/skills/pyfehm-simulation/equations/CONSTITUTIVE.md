# Constitutive Relationships

FEHM uses various constitutive equations to describe fluid and rock properties as functions of pressure, temperature, and saturation.

---

## Thermodynamic Properties of Water

### Density
Liquid water density as function of P and T:
```
ρ_l = ρ_l(P, T)
```

Approximation (valid near 25°C, 0.1 MPa):
```
ρ_l ≈ ρ_0 [1 - β_T (T - T_0) + β_P (P - P_0)]
```

Where:
- `ρ_0` ≈ 1000 kg/m³
- `β_T` ≈ 2.1×10⁻⁴ K⁻¹ (thermal expansion)
- `β_P` ≈ 4.5×10⁻¹⁰ Pa⁻¹ (compressibility)

FEHM uses detailed EOS tables for full P-T range.

### Viscosity
Dynamic viscosity:
```
μ_l = μ_l(T)
```

Approximation:
```
μ_l ≈ 2.414×10⁻⁵ × 10^(247.8/(T+133.15))  [Pa·s]
```

With T in °C.

### Enthalpy
Specific enthalpy:
```
h_l = h_l(P, T)
```

Approximation:
```
h_l ≈ c_p (T - T_ref)
```

Where `c_p` ≈ 4186 J/kg/K for liquid water.

### Steam Properties
For two-phase and superheated conditions:
```
ρ_g = P M_w / (Z R T)
```

Where:
- `M_w` = 0.018 kg/mol (water molecular weight)
- `R` = 8.314 J/mol/K
- `Z` = compressibility factor

Steam enthalpy includes latent heat:
```
h_g = h_l(T_sat) + h_fg(T_sat) + c_p,g (T - T_sat)
```

---

## Relative Permeability

Relative permeability reduces effective permeability based on saturation.

### Linear Model
```
k_rl = (S_l - S_lr) / (1 - S_lr - S_gr)    for S_l > S_lr
k_rg = (S_g - S_gr) / (1 - S_lr - S_gr)    for S_g > S_gr
```

Where:
- `S_lr` = residual liquid saturation
- `S_gr` = residual gas saturation

### Corey Model
```
k_rl = S_e^n_l
k_rg = (1 - S_e)^n_g
```

Where effective saturation:
```
S_e = (S_l - S_lr) / (1 - S_lr - S_gr)
```

Typical exponents: `n_l` = 2-4, `n_g` = 2-3.

### van Genuchten-Mualem Model
```
k_rl = S_e^0.5 [1 - (1 - S_e^(1/m))^m]²
k_rg = (1 - S_e)^0.5 (1 - S_e^(1/m))^(2m)
```

Where `m = 1 - 1/n`, and `n` is van Genuchten parameter.

### Brooks-Corey Model
```
k_rl = S_e^((2+3λ)/λ)
k_rg = (1 - S_e)² (1 - S_e^((2+λ)/λ))
```

Where `λ` is pore size distribution index.

---

## Capillary Pressure

Capillary pressure relates phase pressures:
```
P_cap = P_g - P_l
```

### Linear Model
```
P_cap = P_cap,max (1 - S_e)
```

### van Genuchten Model
```
P_cap = P_0 [(S_e^(-1/m) - 1)]^(1/n)
```

Or inverse form:
```
S_e = [1 + (P_cap/P_0)^n]^(-m)
```

Where:
- `P_0` = air entry pressure (Pa)
- `n`, `m` = shape parameters (m = 1 - 1/n)

### Brooks-Corey Model
```
P_cap = P_d S_e^(-1/λ)
```

Where `P_d` is displacement pressure.

---

## Stress-Dependent Properties

When stress coupling is enabled, porosity and permeability vary with effective stress.

### Porosity-Stress Relationship
```
φ = φ_0 exp[-c_φ (σ' - σ'_0)]
```

Where:
- `φ_0` = reference porosity
- `c_φ` = pore compressibility (Pa⁻¹)
- `σ'` = effective stress
- `σ'_0` = reference effective stress

### Permeability-Porosity Relationship

#### Kozeny-Carman
```
k/k_0 = (φ/φ_0)³ ((1-φ_0)/(1-φ))²
```

#### Power Law
```
k/k_0 = (φ/φ_0)^n
```

Typical `n` = 3-8.

#### Exponential
```
k = k_0 exp[c_k (σ' - σ'_0)]
```

Where `c_k` is permeability compressibility.

---

## Thermal Conductivity

### Temperature Dependence
```
K = K_0 (T_0/T)^a
```

Where `a` ≈ 0.5-1.0 for most rocks.

### Saturation Dependence
```
K_eff = K_dry + √S_l (K_sat - K_dry)
```

Or geometric mean:
```
K_eff = K_dry^(1-S_l) × K_sat^S_l
```

### Parallel/Series Models
Parallel (upper bound):
```
K_eff = (1-φ) K_r + φ (S_l K_l + S_g K_g)
```

Series (lower bound):
```
1/K_eff = (1-φ)/K_r + φ/(S_l K_l + S_g K_g)
```

---

## Gas Properties (Non-Condensible)

### Ideal Gas Law
```
ρ_a = P_a M_a / (R T)
```

Where:
- `P_a` = partial pressure of air
- `M_a` = 0.029 kg/mol (air molecular weight)

### Air Viscosity
```
μ_a ≈ 1.8×10⁻⁵ (T/293)^0.7  [Pa·s]
```

### Henry's Law (Dissolution)
```
x_a = P_a / H
```

Where:
- `x_a` = mole fraction of dissolved air
- `H` = Henry's constant (Pa)

For air in water at 25°C: `H` ≈ 8.6×10⁹ Pa.

---

## CO₂ Properties

FEHM includes detailed CO₂ EOS for carbon sequestration applications.

### Density
Uses Span-Wagner equation of state:
```
ρ_CO2 = f(P, T)
```

Critical point: T_c = 31.1°C, P_c = 7.38 MPa.

### Solubility
Uses Duan-Sun model:
```
x_CO2 = f(P, T, salinity)
```

See PyFEHM `fvars.mco2()` function.

---

## PyFEHM Implementation

### Rock Properties
```python
dat.zone[0].rock(
    density=2500,        # kg/m³
    specific_heat=1000,  # J/kg/K
    porosity=0.1
)
```

### Permeability
```python
# Isotropic
dat.zone[0].perm(kx=1e-15, ky=1e-15, kz=1e-15)

# Anisotropic
dat.zone[0].perm(kx=1e-14, ky=1e-14, kz=1e-16)
```

### Relative Permeability
```python
# Set model type
dat.rlp.type = 'van_genuchten'  # or 'corey', 'linear'

# Parameters
dat.rlp.parameters = {
    'slr': 0.1,    # residual liquid saturation
    'sgr': 0.05,   # residual gas saturation
    'n': 2.0,      # van Genuchten n
    'm': 0.5       # van Genuchten m
}
```

### Capillary Pressure
```python
dat.cap.type = 'van_genuchten'
dat.cap.parameters = {
    'p0': 1000,    # air entry pressure (Pa)
    'n': 2.0,
    'slr': 0.1
}
```

### Thermal Conductivity
```python
dat.zone[0].cond(
    cond_x=2.5,  # W/m/K
    cond_y=2.5,
    cond_z=2.5
)
```

---

## Typical Property Values

| Property | Material | Value | Units |
|----------|----------|-------|-------|
| Porosity | Sandstone | 0.1-0.3 | - |
| Porosity | Shale | 0.01-0.1 | - |
| Porosity | Fractured rock | 0.001-0.01 | - |
| Permeability | Sandstone | 10⁻¹⁵-10⁻¹² | m² |
| Permeability | Shale | 10⁻²¹-10⁻¹⁸ | m² |
| Permeability | Fracture | 10⁻¹²-10⁻⁹ | m² |
| Rock density | Most rocks | 2300-2800 | kg/m³ |
| Specific heat | Most rocks | 800-1200 | J/kg/K |
| Thermal conductivity | Sandstone | 2-4 | W/m/K |
| Thermal conductivity | Shale | 1-2 | W/m/K |
