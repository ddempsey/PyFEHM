"""
1D Diffusion Verification: Heat Conduction and Darcy Flow

Problem: 1D diffusion in a slab 0 < x < L with swapped boundary conditions.
Based on CJ_conduction_3-4.md problem.

Heat Conduction:
    PDE: dT/dt = kappa * d²T/dx²
    IC:  T(x,0) = T1 + (T2 - T1) * x / L   (linear from T1 at x=0 to T2 at x=L)
    BCs: T(0,t) = T2, T(L,t) = T1  for t > 0  (swapped boundaries)

    The system evolves from linear IC toward steady state (reversed linear):
        T_ss(x) = T2 + (T1 - T2) * x / L

Darcy Flow (pressure diffusion):
    PDE: dP/dt = D * d²P/dx²  where D = k / (phi * mu * c_t)
    IC:  P(x,0) = P1 + (P2 - P1) * x / L
    BCs: P(0,t) = P2, P(L,t) = P1  for t > 0

Both problems have the same mathematical form. The analytical solution uses
a Fourier sine series where ONLY EVEN HARMONICS (n=2,4,6,...) contribute.

IMPLEMENTATION NOTES:
- Use grad macro to set linear initial conditions
- Use fix_temperature() for heat conduction boundary conditions (uses HFLX macro)
- Use fix_pressure() for pressure boundary conditions (uses FLOW macro)
- Water properties computed from FEHM's equation of state (fvars module)
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from glob import glob

# Add parent directory to path for PyFEHM imports
PYFEHM_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PYFEHM_ROOT)

# FEHM executable path
FEHM_EXE = os.path.join(PYFEHM_ROOT, 'bin', 'fehm.exe')

from fdata import fdata, fmacro
from fpost import fcontour


def analytical_solution_linear_ic(x, t, L, V1, V2, diffusivity, n_terms=200):
    """
    Analytical solution for 1D diffusion with linear IC and swapped BCs.

    IC:  V(x,0) = V1 + (V2 - V1) * x / L   (linear from V1 at x=0 to V2 at x=L)
    BCs: V(0,t) = V2, V(L,t) = V1  for t > 0  (swapped)

    Steady state: V_ss(x) = V2 + (V1 - V2) * x / L

    Only EVEN harmonics (n = 2, 4, 6, ...) contribute to the Fourier series.

    Parameters:
        x: spatial coordinate (array or scalar)
        t: time (scalar)
        L: domain length
        V1: initial value at x=0 (becomes BC at x=L)
        V2: initial value at x=L (becomes BC at x=0)
        diffusivity: thermal diffusivity kappa or hydraulic diffusivity D
        n_terms: number of Fourier terms (uses n = 2, 4, ..., n_terms)

    Returns:
        V(x,t): solution at given x and t
    """
    x = np.atleast_1d(x)

    # Steady state solution (reversed linear profile)
    V_ss = V2 + (V1 - V2) * x / L

    # Transient part: only even harmonics contribute
    # B_n = 4 * (V1 - V2) / (n * pi) for n = 2, 4, 6, ...
    u = np.zeros_like(x, dtype=float)

    for n in range(2, n_terms + 1, 2):  # n = 2, 4, 6, ...
        B_n = 4 * (V1 - V2) / (n * np.pi)
        decay = np.exp(-n**2 * np.pi**2 * diffusivity * t / L**2)
        mode = np.sin(n * np.pi * x / L)
        u += B_n * mode * decay

    return V_ss + u


def run_heat_conduction_test(work_dir='test_1d_heat', n_nodes_x=51):
    """
    Run 1D heat conduction simulation in PyFEHM.

    Uses grad macro for linear initial condition and fix_temperature()
    for fixed temperature boundary conditions (via HFLX macro).
    """
    print("\n" + "="*70)
    print(f"1D HEAT CONDUCTION (n_nodes_x = {n_nodes_x})")
    print("="*70)

    # Physical parameters
    L = 1.0  # domain length (m)
    T1 = 10.0  # initial temperature at x=0 (°C)
    T2 = 20.0  # initial temperature at x=L (°C)
    P0 = 0.1  # reference pressure (MPa) - low to avoid phase changes

    # Material properties
    rho_rock = 2500.0  # rock density (kg/m³)
    c_rock = 1000.0  # rock specific heat (J/kg/K)
    k_cond = 2.5  # thermal conductivity (W/m/K)
    phi = 0.01  # low porosity for effectively solid behavior

    # Effective thermal diffusivity (m²/s)
    rho_eff = (1 - phi) * rho_rock
    c_eff = c_rock
    kappa = k_cond / (rho_eff * c_eff)

    # Characteristic time scale: t_char = L² / kappa
    t_char = L**2 / kappa
    t_char_days = t_char / 86400

    print(f"\nPhysical parameters:")
    print(f"  Domain length L = {L} m")
    print(f"  T1 (initial at x=0) = {T1} °C")
    print(f"  T2 (initial at x=L) = {T2} °C")
    print(f"  Thermal diffusivity kappa = {kappa:.4e} m²/s")
    print(f"  Characteristic time L²/kappa = {t_char:.2f} s = {t_char_days:.4f} days")

    # Simulation time: run for 0.5 * characteristic time
    tf_days = 0.5 * t_char_days
    output_times = [f * t_char_days for f in [0.05, 0.1, 0.2, 0.3, 0.4, 0.5]]

    # Create simulation
    os.makedirs(work_dir, exist_ok=True)
    dat = fdata(work_dir=work_dir)

    # Create 1D grid
    dx = L / (n_nodes_x - 1)
    x_coords = [i * dx for i in range(n_nodes_x)]

    dat.grid.make(
        gridfilename=os.path.join(work_dir, 'grid.inp'),
        x=x_coords,
        y=[0, 0.1],
        z=[0, 0.1],
    )

    n_nodes_total = dat.grid.number_nodes
    print(f"\nGrid: {n_nodes_x} nodes in x, {n_nodes_total} total nodes")

    # Boundary zones
    dat._add_boundary_zones()

    # Rock properties
    rock = fmacro('rock', param=(
        ('density', rho_rock),
        ('specific_heat', c_rock),
        ('porosity', phi),
    ))
    dat.add(rock)

    # Low permeability (no flow)
    perm = fmacro('perm', param=(
        ('kx', 1e-20),
        ('ky', 1e-20),
        ('kz', 1e-20),
    ))
    dat.add(perm)

    # Thermal conductivity
    cond = fmacro('cond', param=(
        ('cond_x', k_cond),
        ('cond_y', k_cond),
        ('cond_z', k_cond),
    ))
    dat.add(cond)

    # Initial pressure (uniform, low)
    pres_init = fmacro('pres', param=(
        ('pressure', P0),
        ('temperature', T1),  # will be overwritten by grad
        ('saturation', 1),
    ))
    dat.add(pres_init)

    # Linear initial temperature gradient using grad macro
    grad_T = (T2 - T1) / L  # °C/m
    grad = fmacro('grad', zone=0, param=(
        ('reference_coord', 0.0),
        ('direction', 1),  # x-direction
        ('variable', 2),   # temperature
        ('reference_value', T1),
        ('gradient', grad_T),
    ))
    dat.add(grad)

    # Boundary conditions: fixed temperatures (swapped)
    # Left (x=0): fix at T2 = 20°C (was T1=10 initially)
    # Right (x=L): fix at T1 = 10°C (was T2=20 initially)
    # Use hflx macro with multiplier scaled to overcome conductive gradient
    # Q_cond = k * A * dT / dx, so multiplier must scale as 1/dx
    # Base multiplier of 5e-5 works for 21 nodes (dx=0.05)
    dx_ref = 0.05  # reference grid spacing (21 nodes)
    multiplier_base = 5e-5  # MW/°C at reference spacing
    multiplier = multiplier_base * (dx_ref / dx)
    print(f"  hflx multiplier = {multiplier:.4e} MW/°C (scaled for dx={dx:.3f})")
    dat.zone['XMIN'].fix_temperature(T2, multiplier=multiplier)
    dat.zone['XMAX'].fix_temperature(T1, multiplier=multiplier)

    # Time control
    dat.tf = tf_days
    dat.dti = 1e-6  # very small initial timestep for stability with hflx
    dat.dtmax = tf_days / 50  # smaller max timestep for accuracy
    dat.dtmin = 1e-12  # min timestep (days)

    # Contour output
    dat.cont.variables = ['pressure', 'temperature']
    dat.cont.format = 'surf'
    dat.output_times = output_times

    # File settings
    dat.files.root = 'heat_1d'
    input_file = os.path.join(work_dir, 'heat_1d.dat')

    print(f"\nRunning simulation...")
    dat.run(input_file, exe=FEHM_EXE, verbose=False)

    # Read results
    results = read_results(work_dir, 'heat_1d', 'temperature', x_coords,
                          L, T1, T2, kappa, 'heat')

    return results


def run_darcy_flow_test(work_dir='test_1d_darcy', n_nodes_x=51):
    """
    Run 1D Darcy flow (pressure diffusion) simulation in PyFEHM.

    Uses grad macro for linear initial condition and fix_pressure()
    for pressure boundary conditions.
    """
    print("\n" + "="*70)
    print(f"1D DARCY FLOW (n_nodes_x = {n_nodes_x})")
    print("="*70)

    # Physical parameters
    L = 1.0  # domain length (m)
    P1 = 1.0  # initial pressure at x=0 (MPa)
    P2 = 2.0  # initial pressure at x=L (MPa)
    T0 = 15.0  # isothermal temperature (°C)

    # Material properties
    phi = 0.1  # porosity
    k_perm = 1e-18  # permeability (m²) - very tight rock
    rho_rock = 2500.0  # rock density (kg/m³)
    c_rock = 1000.0  # rock specific heat (J/kg/K)

    # Water properties from FEHM's equation of state
    from fvars import dens, visc
    P_avg = (P1 + P2) / 2
    rho_l, _, _ = dens(P_avg, T0)
    drho_dP_l, _, _ = dens(P_avg, T0, derivative='P')
    mu_l, _, _ = visc(P_avg, T0)

    rho_water = float(rho_l) if np.isscalar(rho_l) else float(rho_l[0])
    drho_dP = float(drho_dP_l) if np.isscalar(drho_dP_l) else float(drho_dP_l[0])
    mu = float(mu_l) if np.isscalar(mu_l) else float(mu_l[0])

    # Compressibility from EOS
    c_water = (1/rho_water) * drho_dP  # 1/MPa (fluid compressibility)
    c_f_Pa = c_water * 1e-6  # convert to 1/Pa

    # Hydraulic diffusivity: D = k / (phi * mu * c_f)
    # Note: phi multiplies c_f only ONCE in the storage term
    D = k_perm / (phi * mu * c_f_Pa)

    # Characteristic time scale
    t_char = L**2 / D
    t_char_days = t_char / 86400

    print(f"\nPhysical parameters:")
    print(f"  Domain length L = {L} m")
    print(f"  P1 (initial at x=0) = {P1} MPa")
    print(f"  P2 (initial at x=L) = {P2} MPa")
    print(f"  Permeability k = {k_perm:.2e} m²")
    print(f"  Porosity = {phi}")
    print(f"  Water viscosity (from fvars) = {mu:.4e} Pa·s")
    print(f"  Water compressibility (from fvars) = {c_water:.4e} 1/MPa")
    print(f"  Hydraulic diffusivity D = {D:.4e} m²/s")
    print(f"  Characteristic time L²/D = {t_char:.2f} s = {t_char_days:.6f} days")

    # Simulation time
    tf_days = 0.5 * t_char_days
    output_times = [f * t_char_days for f in [0.001, 0.01, 0.1, 0.5]]

    # Create simulation
    os.makedirs(work_dir, exist_ok=True)
    dat = fdata(work_dir=work_dir)

    # Create 1D grid
    dx = L / (n_nodes_x - 1)
    x_coords = [i * dx for i in range(n_nodes_x)]

    dat.grid.make(
        gridfilename=os.path.join(work_dir, 'grid.inp'),
        x=x_coords,
        y=[0, 0.1],
        z=[0, 0.1],
    )

    n_nodes_total = dat.grid.number_nodes
    print(f"\nGrid: {n_nodes_x} nodes in x, {n_nodes_total} total nodes")

    # Boundary zones
    dat._add_boundary_zones()

    # Rock properties
    rock = fmacro('rock', param=(
        ('density', rho_rock),
        ('specific_heat', c_rock),
        ('porosity', phi),
    ))
    dat.add(rock)

    # Permeability
    perm = fmacro('perm', param=(
        ('kx', k_perm),
        ('ky', k_perm),
        ('kz', k_perm),
    ))
    dat.add(perm)

    # Low thermal conductivity (isothermal)
    cond = fmacro('cond', param=(
        ('cond_x', 0.001),
        ('cond_y', 0.001),
        ('cond_z', 0.001),
    ))
    dat.add(cond)

    # Initial conditions: pressure P1, temperature T0
    pres_init = fmacro('pres', param=(
        ('pressure', P1),
        ('temperature', T0),
        ('saturation', 1),
    ))
    dat.add(pres_init)

    # Linear initial pressure gradient using grad macro
    grad_P = (P2 - P1) / L  # MPa/m
    grad = fmacro('grad', zone=0, param=(
        ('reference_coord', 0.0),
        ('direction', 1),  # x-direction
        ('variable', 1),   # pressure
        ('reference_value', P1),
        ('gradient', grad_P),
    ))
    dat.add(grad)

    # Boundary conditions: fixed pressures (swapped) using fix_pressure
    # Left (x=0): fix at P2 = 2.0 MPa
    # Right (x=L): fix at P1 = 1.0 MPa
    dat.zone['XMIN'].fix_pressure(P2, T=T0)
    dat.zone['XMAX'].fix_pressure(P1, T=T0)

    # Time control
    dat.tf = tf_days
    dat.dti = tf_days / 100000  # initial timestep
    dat.dtmax = tf_days / 20  # max timestep
    dat.dtmin = 1e-10  # min timestep (days)

    # Contour output
    dat.cont.variables = ['pressure', 'temperature']
    dat.cont.format = 'surf'
    dat.output_times = output_times

    # File settings
    dat.files.root = 'darcy_1d'
    input_file = os.path.join(work_dir, 'darcy_1d.dat')

    print(f"\nRunning simulation...")
    dat.run(input_file, exe=FEHM_EXE, verbose=False)

    # Read results
    results = read_results(work_dir, 'darcy_1d', 'liquid pressure', x_coords,
                          L, P1, P2, D, 'pressure')

    return results


def read_results(work_dir, root, variable, x_coords, L, V1, V2, diffusivity, var_type):
    """Read FEHM contour output and compare to analytical solution."""

    # Read grid coordinates
    grid_file = os.path.join(work_dir, 'grid.inp')
    node_coords = {}
    with open(grid_file, 'r') as f:
        lines = f.readlines()
        i = 0
        while i < len(lines) and not lines[i].strip().startswith('coor'):
            i += 1
        i += 1
        if i < len(lines):
            n_nodes = int(lines[i].strip())
            i += 1
            for _ in range(n_nodes):
                if i >= len(lines):
                    break
                parts = lines[i].strip().split()
                if len(parts) >= 4:
                    node_num = int(parts[0])
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    node_coords[node_num] = (x, y, z)
                i += 1

    # Read contour files
    contour_pattern = os.path.join(work_dir, f'{root}*_sca_node.csv')
    contour_files = sorted(glob(contour_pattern))

    results = {
        'x': x_coords,
        'times': [],
        'numerical': [],
        'analytical': [],
        'diffusivity': diffusivity,
        'L': L,
        'V1': V1,
        'V2': V2,
        'var_type': var_type,
    }

    for cf in contour_files:
        basename = os.path.basename(cf)
        try:
            parts = basename.split('_days')[0].split('.')
            if len(parts) >= 2:
                time_str = '.'.join(parts[1:])
                time_days = float(time_str)
            else:
                continue
        except (IndexError, ValueError):
            continue

        if time_days <= 0:
            # Skip t=0 (initial condition) - analytical solution assumes BCs applied
            continue

        try:
            with open(cf, 'r') as f:
                lines = f.readlines()

            header = [h.strip().lower() for h in lines[0].strip().split(',')]

            var_col = None
            for i, h in enumerate(header):
                if variable.lower() in h:
                    var_col = i
                    break

            if var_col is None:
                continue

            node_data = []
            for line in lines[1:]:
                if not line.strip():
                    continue
                parts = line.strip().split(',')
                if len(parts) > var_col:
                    try:
                        node = int(parts[0].strip())
                        val = float(parts[var_col].strip())
                        node_data.append((node, val))
                    except ValueError:
                        continue

            if node_data:
                x_data = []
                v_data = []
                for node, val in node_data:
                    if node in node_coords:
                        x, y, z = node_coords[node]
                        x_data.append(x)
                        v_data.append(val)

                x_unique = sorted(set(x_data))
                v_avg = []
                for xi in x_unique:
                    v_at_x = [v for x, v in zip(x_data, v_data) if abs(x - xi) < 1e-6]
                    v_avg.append(np.mean(v_at_x))

                time_s = time_days * 86400
                v_analytical = analytical_solution_linear_ic(
                    np.array(x_unique), time_s, L, V1, V2, diffusivity
                )

                results['times'].append(time_days)
                results['numerical'].append((x_unique, v_avg))
                results['analytical'].append((x_unique, v_analytical))

        except Exception as e:
            print(f"Error reading {cf}: {e}")

    return results


def compute_errors(results):
    """Compute max absolute and RMS errors between numerical and analytical."""
    max_abs_error = 0
    max_rms_error = 0

    for (x_num, v_num), (x_ana, v_ana) in zip(results['numerical'], results['analytical']):
        v_num = np.array(v_num)
        v_ana = np.array(v_ana)

        # Exclude boundary points (which have fixed values)
        interior = (np.array(x_num) > 0.01) & (np.array(x_num) < 0.99)
        if np.sum(interior) > 0:
            errors = np.abs(v_num[interior] - v_ana[interior])
            max_abs_error = max(max_abs_error, np.max(errors))
            rms_error = np.sqrt(np.mean(errors**2))
            max_rms_error = max(max_rms_error, rms_error)

    return max_abs_error, max_rms_error


def create_comparison_plots(heat_results, darcy_results, save_path='test_1d_diffusion_results.png'):
    """Create comparison plots of numerical vs analytical solutions."""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Heat conduction plots
    ax1 = axes[0, 0]
    ax2 = axes[0, 1]

    if heat_results and heat_results['times']:
        L = heat_results['L']
        T1, T2 = heat_results['V1'], heat_results['V2']

        colors = plt.cm.plasma(np.linspace(0, 1, len(heat_results['times'])))

        for i, (t, (x_num, T_num), (x_ana, T_ana)) in enumerate(
                zip(heat_results['times'], heat_results['numerical'], heat_results['analytical'])):
            ax1.plot(x_ana, T_ana, '-', color=colors[i], linewidth=1.5, label=f't = {t:.4f} days')
            ax1.plot(x_num, T_num, 'o', color=colors[i], markersize=3)

            T_num_arr = np.array(T_num)
            T_ana_arr = np.array(T_ana)
            ax2.plot(x_num, T_num_arr - T_ana_arr, 'o-', color=colors[i], markersize=3, label=f't = {t:.4f} days')

        # Initial and steady state
        x_plot = np.linspace(0, L, 100)
        ax1.plot(x_plot, T1 + (T2 - T1) * x_plot / L, 'k--', linewidth=1, label='Initial')
        ax1.plot(x_plot, T2 + (T1 - T2) * x_plot / L, 'k:', linewidth=1, label='Steady state')

        ax1.set_xlabel('Position x (m)')
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Heat Conduction: Temperature Profiles\n(markers=numerical, lines=analytical)')
        ax1.legend(fontsize=7, loc='best')
        ax1.grid(True, alpha=0.3)

        ax2.set_xlabel('Position x (m)')
        ax2.set_ylabel('Temperature Error (°C)')
        ax2.set_title('Heat Conduction: Error (Numerical - Analytical)')
        ax2.legend(fontsize=7, loc='best')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

    # Darcy flow plots
    ax3 = axes[1, 0]
    ax4 = axes[1, 1]

    if darcy_results and darcy_results['times']:
        L = darcy_results['L']
        P1, P2 = darcy_results['V1'], darcy_results['V2']

        colors = plt.cm.plasma(np.linspace(0, 1, len(darcy_results['times'])))

        for i, (t, (x_num, P_num), (x_ana, P_ana)) in enumerate(
                zip(darcy_results['times'], darcy_results['numerical'], darcy_results['analytical'])):
            ax3.plot(x_ana, P_ana, '-', color=colors[i], linewidth=1.5, label=f't = {t:.6f} days')
            ax3.plot(x_num, P_num, 'o', color=colors[i], markersize=3)

            P_num_arr = np.array(P_num)
            P_ana_arr = np.array(P_ana)
            ax4.plot(x_num, P_num_arr - P_ana_arr, 'o-', color=colors[i], markersize=3, label=f't = {t:.6f} days')

        x_plot = np.linspace(0, L, 100)
        ax3.plot(x_plot, P1 + (P2 - P1) * x_plot / L, 'k--', linewidth=1, label='Initial')
        ax3.plot(x_plot, P2 + (P1 - P2) * x_plot / L, 'k:', linewidth=1, label='Steady state')

        ax3.set_xlabel('Position x (m)')
        ax3.set_ylabel('Pressure (MPa)')
        ax3.set_title('Darcy Flow: Pressure Profiles\n(markers=numerical, lines=analytical)')
        ax3.legend(fontsize=7, loc='best')
        ax3.grid(True, alpha=0.3)

        ax4.set_xlabel('Position x (m)')
        ax4.set_ylabel('Pressure Error (MPa)')
        ax4.set_title('Darcy Flow: Error (Numerical - Analytical)')
        ax4.legend(fontsize=7, loc='best')
        ax4.grid(True, alpha=0.3)
        ax4.axhline(y=0, color='k', linestyle='-', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    print(f"\nPlot saved to: {save_path}")


def run_convergence_study():
    """Run simulations at multiple resolutions to verify numerical convergence."""

    print("\n" + "="*70)
    print("GRID CONVERGENCE STUDY")
    print("="*70)

    script_dir = os.path.dirname(os.path.abspath(__file__))

    resolutions = [21, 51, 101]  # number of nodes in x
    heat_errors = []
    darcy_errors = []

    for n_nodes in resolutions:
        print(f"\n--- Resolution: {n_nodes} nodes ---")

        # Heat conduction
        heat_dir = os.path.join(script_dir, f'test_1d_heat_n{n_nodes}')
        heat_results = run_heat_conduction_test(heat_dir, n_nodes_x=n_nodes)
        max_abs, max_rms = compute_errors(heat_results)
        heat_errors.append((n_nodes, max_abs, max_rms))
        print(f"  Heat: max_abs_error = {max_abs:.6f} °C, max_rms_error = {max_rms:.6f} °C")

        # Darcy flow
        darcy_dir = os.path.join(script_dir, f'test_1d_darcy_n{n_nodes}')
        darcy_results = run_darcy_flow_test(darcy_dir, n_nodes_x=n_nodes)
        max_abs, max_rms = compute_errors(darcy_results)
        darcy_errors.append((n_nodes, max_abs, max_rms))
        print(f"  Darcy: max_abs_error = {max_abs:.6f} MPa, max_rms_error = {max_rms:.6f} MPa")

    # Print convergence summary
    print("\n" + "="*70)
    print("CONVERGENCE SUMMARY")
    print("="*70)

    print("\nHeat Conduction:")
    print(f"  {'Nodes':<10} {'Max Abs Error':<20} {'Max RMS Error':<20} {'Ratio to prev'}")
    for i, (n, abs_err, rms_err) in enumerate(heat_errors):
        if i > 0:
            ratio = heat_errors[i-1][1] / abs_err if abs_err > 0 else float('inf')
            print(f"  {n:<10} {abs_err:<20.6f} {rms_err:<20.6f} {ratio:.2f}")
        else:
            print(f"  {n:<10} {abs_err:<20.6f} {rms_err:<20.6f} -")

    print("\nDarcy Flow:")
    print(f"  {'Nodes':<10} {'Max Abs Error':<20} {'Max RMS Error':<20} {'Ratio to prev'}")
    for i, (n, abs_err, rms_err) in enumerate(darcy_errors):
        if i > 0:
            ratio = darcy_errors[i-1][1] / abs_err if abs_err > 0 else float('inf')
            print(f"  {n:<10} {abs_err:<20.6f} {rms_err:<20.6f} {ratio:.2f}")
        else:
            print(f"  {n:<10} {abs_err:<20.6f} {rms_err:<20.6f} -")

    return heat_errors, darcy_errors


if __name__ == '__main__':
    print("="*70)
    print("PyFEHM 1D Diffusion Verification Tests")
    print("="*70)
    print("\nProblem: 1D diffusion with swapped boundary conditions")
    print("  - Initial: linear profile V1 at x=0 to V2 at x=L")
    print("  - BCs: V(0,t) = V2, V(L,t) = V1 (swapped)")
    print("  - Solution: Fourier sine series (only even harmonics)")

    # Run convergence study
    heat_errors, darcy_errors = run_convergence_study()

    # Create plots for highest resolution
    script_dir = os.path.dirname(os.path.abspath(__file__))
    n_nodes = 101

    heat_dir = os.path.join(script_dir, f'test_1d_heat_n{n_nodes}')
    darcy_dir = os.path.join(script_dir, f'test_1d_darcy_n{n_nodes}')

    # Re-read results for plotting
    heat_results = None
    darcy_results = None

    if os.path.exists(heat_dir):
        from fvars import dens, visc
        # Recreate heat results for plotting
        L = 1.0
        T1, T2 = 10.0, 20.0
        rho_rock, c_rock, k_cond, phi = 2500.0, 1000.0, 2.5, 0.01
        kappa = k_cond / ((1 - phi) * rho_rock * c_rock)
        dx = L / (n_nodes - 1)
        x_coords = [i * dx for i in range(n_nodes)]
        heat_results = read_results(heat_dir, 'heat_1d', 'temperature', x_coords,
                                   L, T1, T2, kappa, 'heat')

    if os.path.exists(darcy_dir):
        L = 1.0
        P1, P2, T0 = 1.0, 2.0, 15.0
        phi, k_perm = 0.1, 1e-18
        P_avg = (P1 + P2) / 2
        rho_l, _, _ = dens(P_avg, T0)
        drho_dP_l, _, _ = dens(P_avg, T0, derivative='P')
        mu_l, _, _ = visc(P_avg, T0)
        rho_water = float(rho_l) if np.isscalar(rho_l) else float(rho_l[0])
        drho_dP = float(drho_dP_l) if np.isscalar(drho_dP_l) else float(drho_dP_l[0])
        mu = float(mu_l) if np.isscalar(mu_l) else float(mu_l[0])
        c_water = (1/rho_water) * drho_dP
        c_f_Pa = c_water * 1e-6  # fluid compressibility in 1/Pa
        D = k_perm / (phi * mu * c_f_Pa)
        dx = L / (n_nodes - 1)
        x_coords = [i * dx for i in range(n_nodes)]
        darcy_results = read_results(darcy_dir, 'darcy_1d', 'liquid pressure', x_coords,
                                    L, P1, P2, D, 'pressure')

    save_path = os.path.join(script_dir, 'test_1d_diffusion_results.png')
    create_comparison_plots(heat_results, darcy_results, save_path)
